#!/usr/bin/env python3
"""Build one visual page (a Claude artifact) with every piece in a batch.

Usage: python3 scripts/build_artifact.py outputs/<batch-folder>

Writes outputs/_pages/<batch>/index.html plus m/ (images and videos)
and files.json (the list of files to publish beside the page).
"""
import json, re, html, csv, shutil, os, glob, sys
HERE=os.path.dirname(os.path.abspath(__file__))
R=os.path.abspath(sys.argv[1]); A=os.path.join(os.path.dirname(R),"_pages",os.path.basename(R))  # outside the batch so other scripts never scan it
shutil.rmtree(A,ignore_errors=True); os.makedirs(A)
e=html.escape
import base64, subprocess, tempfile, hashlib
sys.path.insert(0,HERE)
def _ffmpeg():
    try:
        import animate; return animate.find_ffmpeg()
    except Exception:
        return shutil.which("ffmpeg")
def data_uri(path):
    ext=os.path.splitext(path)[1].lower(); mime={".png":"image/png",".jpg":"image/jpeg",".mp4":"video/mp4",".pdf":"application/pdf"}[ext]
    return "data:"+mime+";base64,"+base64.b64encode(open(path,"rb").read()).decode()
def light_uri(path):
    """A lighter JPEG copy for showing on the page (the full PNG is published beside the page for downloads)."""
    ff=_ffmpeg()
    if not ff: return data_uri(path)
    out=tempfile.mktemp(suffix=".jpg")
    r=subprocess.run([ff,"-y","-loglevel","error","-i",path,"-q:v","4",out])
    return data_uri(out) if r.returncode==0 and os.path.exists(out) else data_uri(path)
def publish_copy(src,rel):
    dst=os.path.join(A,"f",rel); os.makedirs(os.path.dirname(dst),exist_ok=True); shutil.copy(src,dst); return "f/"+rel
def small_video(path):
    # Everything is embedded in the page, so shrink videos to keep the page light.
    ff=_ffmpeg()
    if not ff: return None
    out=tempfile.mktemp(suffix=".mp4")
    r=subprocess.run([ff,"-y","-loglevel","error","-i",path,"-vf","scale=540:-2","-c:v","libx264","-crf","30","-preset","veryfast","-pix_fmt","yuv420p","-an","-movflags","+faststart",out])
    return out if r.returncode==0 and os.path.exists(out) else None
def inline(t):
    t=e(t)
    t=re.sub(r"\*\*(.+?)\*\*",r"<strong>\1</strong>",t)
    return t
def md(text):
    out=[];lst=None
    def close():
        nonlocal lst
        if lst: out.append(f"</{lst}>"); lst=None
    for raw in text.strip("\n").split("\n"):
        l=raw.rstrip()
        if not l.strip(): close(); continue
        m=re.match(r"^(#{1,3}) (.*)",l)
        if m:
            close(); n=len(m.group(1))+1; out.append(f"<h{n}>{inline(m.group(2))}</h{n}>"); continue
        m=re.match(r"^\s*[-*] (.*)",l)
        if m:
            if lst!="ul": close(); out.append("<ul>"); lst="ul"
            out.append(f"<li>{inline(m.group(1))}</li>"); continue
        m=re.match(r"^\s*\d+\. (.*)",l)
        if m:
            if lst!="ol": close(); out.append("<ol>"); lst="ol"
            out.append(f"<li>{inline(m.group(1))}</li>"); continue
        if l.startswith("   ") and lst:  # nested detail line
            out.append(f"<li class='sub'>{inline(l.strip().lstrip('- '))}</li>"); continue
        close()
        m=re.match(r"^(\d+)/ (.*)",l)
        if m: out.append(f"<p class='tn'><span>{m.group(1)}</span>{inline(m.group(2))}</p>"); continue
        m=re.match(r"^([A-Z][A-Za-z ()]{1,40}):\s*(.*)$",l)
        if m and m.group(1) in ("Angle","Where","Type","Document","Image","Board","Link","Best paired with","Length","Style","Hook (first 3 seconds)","Hook (first 2 seconds)","Next step","Caption","Filming note","Music mood","Search terms for stock footage","Title","Description","Recommended","Subtitle","Subject","Preview","Post","First comment","Script","On-screen text","Frame 1","Tags","Chapters","Pinned comment"):
            out.append(f"<p class='meta'><b>{e(m.group(1))}</b> {inline(m.group(2))}</p>"); continue
        out.append(f"<p>{inline(l)}</p>")
    close(); return "\n".join(out)
_cnt={}
def nid(prefix):
    key=(MP,prefix); _cnt[key]=_cnt.get(key,0)+1
    return f"p-{MP}{prefix}-{_cnt[key]:02d}"
def card(title,raw,kicker="",body=None,copy=None,pid=""):
    c=e(copy if copy is not None else raw,quote=True)
    return f"""<article class="card"{(' id="'+pid+'"') if pid else ""}><header><div><span class="k">{e(kicker)}</span><h3>{e(title)}</h3></div><button class="copy" data-copy="{c}">Copy</button></header><div class="body">{body if body is not None else md(raw)}</div></article>"""
def cardbody(raw):  # for copying, strip heading line
    return raw
def split_pieces(path,default,prefix):
    txt=open(path).read()
    chunks=[c.strip("\n") for c in re.split(r"\n---\n",txt) if c.strip()]
    pieces=[];label=None;n=0
    for c in chunks:
        lines=c.split("\n")
        while lines and lines[0].startswith("# "):
            label=lines[0][2:]; lines=lines[1:]
            while lines and not lines[0].strip(): lines=lines[1:]
        body="\n".join(lines)
        if not body.strip(): continue
        n+=1
        m=re.match(r"^## (.*)",lines[0])
        title=m.group(1) if m else f"{prefix} {n}"
        if m: body="\n".join(lines[1:])
        pieces.append((title,body,label))
    return pieces
NAV=[];SUF="";MP="";LABEL="";SECN=[0]
def section(id,title,intro,inner,cls=""):
    if not re.sub(r"<[^>]+>","",inner).strip() and "<img" not in inner: return ""
    id=id+SUF; title=title+(" ("+LABEL+")" if SUF else "")
    NAV.append((id,title))
    SECN[0]+=1
    base,_,tail=title.partition(" (")
    ws=base.rsplit(" ",1)
    h2=(e(ws[0])+" <em>"+e(ws[1])+"</em>" if len(ws)==2 else "<em>"+e(base)+"</em>")+(" ("+e(tail) if tail else "")
    return f'<section id="{id}" class="sec {cls}"><div class="wrap"><div class="sh"><p class="eb">{SECN[0]:02d} &middot; Section</p><h2>{h2}</h2><p>{e(intro)}</p></div>{inner}</div></section>'


def refresh():
    """Make every image and video match the latest plans (including edits made in Carousel Studio) before the page is built."""
    if os.environ.get("SIO_SKIP_REFRESH"): return
    subprocess.run([sys.executable,HERE+"/carousel_studio.py","pack",R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    ff=_ffmpeg()
    cfg=json.load(open(os.path.dirname(HERE)+"/config.json")) if os.path.exists(os.path.dirname(HERE)+"/config.json") else {}
    if not ff or not (cfg.get("video") or {}).get("enabled",True): return
    def sig(files):
        h=hashlib.sha1(b"video-v2")  # bump when video rendering changes so old videos are redone
        for f in sorted(files): h.update(open(f,"rb").read())
        return h.hexdigest()
    jobs=[]
    for d in sorted(glob.glob(R+"/*/carousels/*/")):
        imgs=glob.glob(d+"slide-*.png"); mp4=d+"carousel-animated.mp4"; mark=d+".animated-sig"
        if imgs and (not os.path.exists(mp4) or not os.path.exists(mark) or open(mark).read()!=sig(imgs)): jobs.append((d,sig(imgs),mark))
    for d in sorted(glob.glob(R+"/*/quote-graphics/")):
        imgs=glob.glob(d+"quote-*.png"); mark=d+".animated-sig"
        if imgs and (not os.path.exists(d+"animated") or not os.path.exists(mark) or open(mark).read()!=sig(imgs)): jobs.append((d,sig(imgs),mark))
    for d,sg,mark in jobs:
        print("Updating video for",os.path.relpath(d,R),flush=True)
        r=subprocess.run([sys.executable,HERE+"/animate.py",d],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if r.returncode==0: open(mark,"w").write(sg)
refresh()
sources=sorted(d for d in glob.glob(R+"/[0-9][0-9]-*/") if os.path.isdir(d))
secs=[];reviews=[]
for S in sources:
    S=S.rstrip("/")
    slug0=os.path.basename(S)
    LABEL=re.sub(r"^\d+-","",slug0).replace("-"," ")
    if len(sources)>1: SUF="-"+slug0[:2]; MP=slug0[:2]+"-"
    if os.path.exists(S+"/00-review.md"): reviews.append((LABEL,open(S+"/00-review.md").read()))
    # Visuals: carousels
    cdirs=sorted(glob.glob(S+"/carousels/*/"))
    inner=""
    for d in cdirs:
        slug=os.path.basename(d.rstrip("/")); j=json.load(open(d+"carousel.json"))
        imgs=sorted(glob.glob(d+"slide-*.png")); tags=""
        kebab=re.sub(r"[^a-z0-9]+","-",j["title"].lower().replace("'","")).strip("-") or slug
        for p in imgs:
            nn=os.path.basename(p)[6:8]
            orig=publish_copy(p,f"{MP}{slug}/slide-{nn}.png")
            tags+=f'<button class="slide" data-full="1" data-name="{kebab}-slide-{nn}.png" data-orig="{orig}"><img src="{light_uri(p)}" alt="{e(j["title"])} slide {nn}"></button>'
        vid="";vbtn=""
        if os.path.exists(d+"carousel-animated.mp4"):
            sv=small_video(d+"carousel-animated.mp4")
            if sv:
                vid=f'<details class="vid"><summary>Watch the swipe-through video</summary><video controls preload="metadata" playsinline src="{data_uri(sv)}"></video></details>'
            vsrc=publish_copy(d+"carousel-animated.mp4",f"{MP}{slug}.mp4")
            vbtn=f'<button class="dl" data-dl="video" data-name="{kebab}-swipe.mp4" data-src="{vsrc}">Download video (MP4)</button>'
        pbtn=f'<button class="dl" data-dl="pdf" data-name="{kebab}.pdf" data-src="{publish_copy(d+"carousel.pdf",MP+slug+".pdf")}">Download PDF</button>' if os.path.exists(d+"carousel.pdf") else ""
        dlrow=f'<div class="dlrow"><button class="dl" data-dl="zip" data-name="{kebab}-slides.zip">Download all slides</button>{pbtn}{vbtn}</div>'
        cap=open(d+"caption.md").read().strip()
        phrase=e('Open my carousel editor for the carousel "'+j['title']+'"',quote=True)
        cid=nid('car')
        inner+=f'<article class="card car" id="{cid}"><header><div><span class="k">Carousel, {len(imgs)} slides</span><h3>{e(j["title"])}</h3></div><button class="copy" data-copy="{e(cap,quote=True)}">Copy caption</button></header><div class="strip">{tags}</div>{dlrow}<div class="edit"><button class="copy studio" data-copy="{phrase}" data-toast="Copied. Now paste it into your chat with Claude and the Carousel Studio opens.">Edit in Carousel Studio</button><p>Click the button, then paste it into your chat with Claude. Claude opens the Carousel Studio for this carousel, where you can change the words, layouts, colors and photos. When you are done, export in the editor, then say <b>&ldquo;I&rsquo;m done editing&rdquo;</b> to Claude. That updates this page with your changes. Until you say it, this page keeps showing the old version.</p></div>{vid}<div class="body capt"><h4>Caption</h4>{md(cap)}</div></article>'
    secs.append(section("carousels","Carousels","Swipe posts for Instagram and Facebook. Tap a slide to enlarge it.",inner))
    # quotes
    qj=json.load(open(S+"/quote-graphics/quotes.json"))["quotes"] if os.path.exists(S+"/quote-graphics/quotes.json") else []
    tags=""
    for i,q in enumerate(qj,1):
        f=f"quote-{i:02d}.png"
        qid=nid('quote')
        tags+=f'<div class="qwrap"><button class="qcell" id="{qid}" data-full="1" data-name="quote-{i:02d}.png" data-orig="{publish_copy(S+"/quote-graphics/"+f,MP+"quotes/"+f)}"><img src="{light_uri(S+"/quote-graphics/"+f)}" alt="{e(q["text"].replace("**",""))}"></button><button class="dl qdl" data-dl="img" data-name="quote-{i:02d}.png" aria-label="Download quote {i}">Download</button></div>'
    secs.append(section("quotes","Quote graphics","Single-line images. Tap one to enlarge it.",f'<div class="dlrow"><button class="dl" data-dl="zipq" data-name="quote-graphics.zip">Download all quotes</button></div><div class="qgrid">{tags}</div>' if tags else ''))

    # Reels
    inner=""
    for p in sorted(glob.glob(S+"/reels/reel-*.md")):
        raw=open(p).read(); spoken=open(p.replace(".md",".spoken.txt")).read().strip()
        t=raw.split("\n")[0][2:]
        body=md("\n".join(raw.split("\n")[1:]))
        inner+=card(t,raw,"Reel, about 30 seconds",body=body+f'<div class="spoken"><h4>Teleprompter copy</h4><p>{e(spoken).replace(chr(10)+chr(10),"</p><p>")}</p></div>',copy=spoken,pid=nid("reel"))
    secs.append(section("reels","Talking reels","Scripts to film or paste into HeyGen. Copy gives you the clean spoken words only.",inner))
    inner=""
    for p in sorted(glob.glob(S+"/short-videos/video-*.md")):
        raw=open(p).read(); spoken=open(p.replace(".md",".spoken.txt")).read().strip()
        t=raw.split("\n")[0][2:]
        inner+=card(t,raw,"Short video, faceless",body=md("\n".join(raw.split("\n")[1:])),copy=spoken,pid=nid("short"))
    secs.append(section("shorts","Short videos","Faceless spinoffs for TikTok, Reels and Shorts. Copy gives you the voiceover.",inner))

    def multi(id,title,intro,fn,kicker,prefix):
        inner=""
        if not os.path.exists(S+"/"+fn): return
        for t,b,lab in split_pieces(S+"/"+fn,"",prefix):
            if lab: inner+=f'<h3 class="sub">{e(lab)}</h3>'
            pre={"threads":"thr","notes":"note","facebook":"fb","linkedin":"li","pinterest":"pin","emails":"email"}.get(id)
            if id=="instagram": pre="story" if t.lower().startswith("story") else "igp"
            inner+=card(t,b,kicker,pid=nid(pre) if pre else "")
        secs.append(section(id,title,intro,inner))
    multi("threads","Threads","Threads for Threads or X.","threads.md","Thread","Thread")
    multi("notes","Substack notes","Short standalone posts.","notes.md","Note","Note")
    multi("instagram","Instagram posts and Stories","Captions and Story sequences.","instagram-posts.md","Instagram","Item")
    multi("facebook","Facebook posts","Longer posts and quick community questions.","facebook-posts.md","Facebook","Post")
    multi("linkedin","LinkedIn posts","Text posts and carousel documents.","linkedin-posts.md","LinkedIn","Post")
    multi("pinterest","Pinterest pins","Pins with titles, descriptions and the image to pin.","pinterest-pins.md","Pin","Pin")
    multi("emails","Emails","Emails to your list.","emails.md","Email","Email")
    inner=""
    for p in sorted(glob.glob(S+"/substack-articles/*.md")):
        raw=open(p).read(); t=raw.split("\n")[0][2:]
        inner+=card(t,raw,"Substack article",body=md("\n".join(raw.split("\n")[1:])),pid=nid("sub"))
    secs.append(section("substack","Substack articles","Full articles.",inner))
    inner=""
    for p in sorted(glob.glob(S+"/blog/*.md")):
        raw=open(p).read()
        fm=re.match(r"---\n(.*?)\n---\n(.*)",raw,re.S)
        meta=fm.group(1); rest=fm.group(2).strip(); t=rest.split("\n")[0][2:]
        mh="".join(f"<p class='meta'><b>{e(k)}</b> {e(v)}</p>" for k,v in (l.split(": ",1) for l in meta.split("\n") if ": " in l))
        inner+=card(t,rest,"Blog post",body=f'<div class="seo">{mh}</div>'+md("\n".join(rest.split("\n")[1:])),pid=nid("blog"))
    secs.append(section("blog","Blog posts","Posts written for search, with the SEO details at the top of each.",inner))
    inner=""
    if os.path.exists(S+"/youtube.md"): inner+=card("YouTube titles and description",open(S+"/youtube.md").read(),"YouTube",body=md("\n".join(open(S+"/youtube.md").read().split("\n")[1:])),pid=nid("yt"))
    if os.path.exists(S+"/talking-points.md"): inner+=card("Talking points cheat sheet",open(S+"/talking-points.md").read(),"For Lives, Stories and DMs",body=md("\n".join(open(S+"/talking-points.md").read().split("\n")[1:])))
    secs.append(section("youtube","YouTube and talking points","Titles, description and tags for the full episode, plus a cheat sheet to riff from.",inner))

# calendar
rows=[r for r in csv.DictReader(open(R+"/content-calendar.csv")) if r["day"]]
days={}
for r in rows: days.setdefault((r["day"],r["date"],r["weekday"]),[]).append(r)
inner='<div class="cal">'
for (d,date,wd),rs in sorted(days.items(),key=lambda x:int(x[0][0])):
    inner+=f'<div class="day"><div class="dh"><b>Day {d}</b><span>{e(wd)} {e(date)}</span></div>'
    for r in rs:
        tgt="p-"+((r["file"].split("/")[0][:2]+"-") if len(sources)>1 else "")+r["id"]
        inner+=f'<a class="item st-{e(r["stage"])}" href="#{tgt}" data-go="{tgt}"><span class="tm">{e(r["time"])}</span><div><b>{e(r["format"])}</b> on {e(r["platform"])}<br><span class="hk">{e(r["hook"])}</span><span class="open">Open this piece</span></div><span class="pill">{e(r["stage"])}</span></a>'
    inner+='</div>'
inner+='</div>'
plan=json.load(open(R+"/plan.json"))
bank=[p for p in plan["pieces"] if p.get("status")=="bank"]
inner+='<h3 class="sub">Saved in the bank for later</h3><div class="bank">'+"".join(f'<div><b>{e(p["format"])}</b> · {e(p["hook"])}</div>' for p in bank)+'</div>'
secs.append(section("calendar","30-day calendar",f"{len(rows)} pieces scheduled across {len(days)} posting days (Monday to Saturday), starting {rows[0]['date']}. {len(bank)} more are banked.",inner))

SUF="";MP=""
for LABEL,rev in reviews:
    secs.append(section("review","Check before you post","Names, wording and approvals to confirm.",card("Review list",rev,"Read this first",body=md("\n".join(rev.split("\n")[1:]))),"review"))
    break
navh="".join(f'<a href="#{i}">{t}</a>' for i,t in NAV)
plan=json.load(open(R+"/plan.json"))
plan_title=plan.get("title","Your content").replace(" pack","")
fc={}
for p in plan["pieces"]: fc[p["format"]]=fc.get(p["format"],0)+1
names=[("carousel","carousels"),("quote","quote graphics"),("reel","reels"),("short-video","short videos"),("thread","threads"),("note","notes"),("instagram-post","Instagram posts"),("story","Stories"),("facebook-post","Facebook posts"),("linkedin-post","LinkedIn posts"),("pinterest-pin","pins"),("substack-article","articles"),("blog","blog posts"),("email","emails")]
stats="".join(f"<span><b>{fc[k]}</b>{e(t)}</span>" for k,t in names if k in fc)+f"<span><b>{len(plan['pieces'])}</b>pieces in all</span>"
brand=json.load(open(os.path.dirname(HERE)+"/brand/brand.json")) if os.path.exists(os.path.dirname(HERE)+"/brand/brand.json") else {}
fonts=brand.get("fonts",{})
D=fonts.get("heading","Playfair Display"); B=fonts.get("body","Inter"); H=fonts.get("accent","Caveat")
single={"Archivo Black","Bebas Neue","DM Serif Display","Caveat","Dancing Script"}
def gf(f,w): return "family="+f.replace(" ","+")+(":wght@"+w if w else "")
link="https://fonts.googleapis.com/css2?"+"&".join([("family="+D.replace(" ","+")+":ital,wght@0,400;0,700;1,400" if D in ("Lora","Playfair Display") else gf(D,"" if D in single else "400;700")),gf(B,"400;500;700"),("family=Cormorant+Garamond:ital,wght@0,500;1,500" if H=="Cormorant Garamond" else gf(H,"600" if H in ("Caveat",) else ""))])+"&display=swap"
tpl=open(HERE+"/artifact_template.html").read()

def _rgb(h): h=h.lstrip("#"); return [int(h[i:i+2],16) for i in (0,2,4)]
def _hex(c): return "#%02X%02X%02X"%tuple(max(0,min(255,round(x))) for x in c)
def mix(a,b,t): return _hex([x*(1-t)+y*t for x,y in zip(_rgb(a),_rgb(b))])
def lum(h):
    r,g,bl=[(v/255)**2.2 for v in _rgb(h)]; return .2126*r+.7152*g+.0722*bl
cols=brand.get("colors",{})
def C(k,d): return (cols.get(k) or d).upper()
bg=C("bg","#F5F5F5"); ink=C("ink","#131313"); acc=C("accent","#C8102E"); acc2=C("accent2","#DACBF4"); mut=C("muted","#76766F"); dk=C("bg_dark","#131313")
# A dark brand gets a light reading page under a dark hero: off-white ground, dark ink, and a deeper
# accent that stays readable on light. A brand can set these in brand.json under "page".
pg=brand.get("page") or {}
if lum(bg)<.2:
    lbg=(pg.get("light_bg") or "#F5F5F5").upper(); link_=(pg.get("light_ink") or dk).upper()
    lmut=(pg.get("light_muted") or mix(link_,"#FFFFFF",.35)).upper()
    lacc=(pg.get("light_accent") or mix(acc2,"#000000",.62)).upper()
    page_light=dict(bg=lbg,ink=link_,mut=lmut,acc=lacc,surf="#FFFFFF",line=mix(lbg,link_,.14),acc2=acc2)
else:
    page_light=dict(bg=bg,ink=ink,mut=mut,acc=acc,surf="#FFFFFF",line=mix(bg,ink,.12),acc2=acc2)
L=page_light
rep={"{{C_SURFACE}}":L["surf"],"{{C_BG}}":L["bg"],"{{C_INK}}":L["ink"],"{{C_MUTED}}":L["mut"],"{{C_LINE}}":L["line"],"{{C_ACCENT}}":L["acc"],"{{C_ACCENT_INK}}":"#FFFFFF" if lum(L["acc"])<.18 else "#131313","{{C_ACC2}}":L["acc2"],"{{C_ACC2_INK}}":("#F5F5F5" if lum(L["acc2"])<.3 else "#131313"),"{{SCRIPT}}":acc2,
"{{D_BG}}":dk,"{{D_SURFACE}}":mix(dk,"#FFFFFF",.07),"{{D_LINE}}":mix(dk,"#FFFFFF",.17),"{{D_ACCENT}}":(acc if lum(bg)<.2 else (acc2 if lum(acc)<.2 else mix(acc,"#FFFFFF",.4))),"{{D_ACC2}}":mix(dk,"#FFFFFF",.14)}
if lum(bg)<.2:
    # Dark brand: commit to one look (dark hero, light page) so it matches the brand board in any viewer theme.
    tpl="\n".join(l for l in tpl.split("\n") if not (l.startswith("@media (prefers-color-scheme: dark){:root") or l.startswith(':root[data-theme="dark"]{')))
for k,v in rep.items(): tpl=tpl.replace(k,v)
tpl=tpl.replace("{{FONT_LINK}}",link).replace("{{FONT_DISPLAY}}",D).replace("{{FONT_BODY}}",B).replace("{{FONT_HAND}}",H).replace("{{DW}}",str(fonts.get("heading_weight") or ("400" if D in single else "700")))
_w=plan_title.rsplit(" ",1)
h1=(e(_w[0])+" <em>"+e(_w[1])+"</em>") if len(_w)==2 else e(plan_title)
out=tpl.replace("{{TITLE_H1}}",h1).replace("{{NAV}}",navh).replace("{{BODY}}","\n".join(secs)).replace("{{TITLE}}",e(plan_title)).replace("{{STATS}}",stats)
open(A+"/index.html","w").write(out)
files=[{"path":os.path.relpath(p,A)} for p in sorted(glob.glob(A+"/f/**/*",recursive=True)) if os.path.isfile(p)]
json.dump(files,open(A+"/files.json","w"))
print("Page:",A+"/index.html"); print("Assets:",len(files),"files; list in",A+"/files.json")
