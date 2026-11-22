#!/usr/bin/env python3
"""Build the Design Studio page: design/studio.html

Shows every carousel layout with your brand applied, with live controls for colors,
fonts, size, and layout. Open the page in any browser. When you like it, press
"Copy my settings" and paste the result into the chat. Or just tell the engine what
you want in plain words.

Usage: python3 scripts/studio.py
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import engine_lib as E  # noqa: E402

SAMPLE = [
    {"type": "cover", "kicker": "Your topic", "headline": "A headline that makes you stop **scrolling**", "sub": "One short line that sets up the swipe."},
    {"type": "point", "kicker": "01", "headline": "One idea per slide.", "body": "Keep it short enough to read in three seconds, then let the next slide do the next job."},
    {"type": "list", "headline": "Three things to try", "items": ["Say the thing plainly", "Give one **small** next step", "End with one action"]},
    {"type": "versus", "headline": "Quick truth", "left": "I need more followers first", "right": "I need one clear message first"},
    {"type": "quote", "text": "A line so good people screenshot it.", "attribution": "Your name"},
    {"type": "close", "headline": "Ready for the next step?", "cta": "Follow for more"},
]

CSS_UI = """
body{display:block;background:#f1efec;color:#1c1b1f;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
#app{display:grid;grid-template-columns:330px 1fr;min-height:100vh}
#panel{position:sticky;top:0;height:100vh;overflow:auto;background:#fff;border-right:1px solid #ddd;padding:18px 18px 40px}
#panel h1{font-size:18px;margin-bottom:4px}
#panel p.sub{font-size:12px;color:#666;margin-bottom:14px;line-height:1.4}
#panel h3{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:#777;margin:18px 0 8px}
#panel label{display:block;font-size:12px;margin:8px 0 3px;color:#444}
#panel input[type=text],#panel select{width:100%;padding:7px 8px;border:1px solid #ccc;border-radius:6px;font-size:13px;background:#fff}
.crow{display:flex;gap:8px;align-items:center;margin:6px 0}
.crow span{flex:1;font-size:12px;color:#444}
.crow input[type=color]{width:38px;height:28px;border:1px solid #ccc;border-radius:5px;padding:0;background:none}
.crow input[type=text]{width:86px!important;font-family:ui-monospace,monospace}
.pal{display:flex;flex-wrap:wrap;gap:6px}
.pal button{border:1px solid #ccc;background:#fff;border-radius:6px;padding:4px 8px;font-size:11px;cursor:pointer;display:flex;align-items:center;gap:6px}
.pal i{display:inline-block;width:12px;height:12px;border-radius:50%;border:1px solid rgba(0,0,0,.2)}
.chk{display:flex;gap:8px;align-items:center;font-size:12px;margin:5px 0}
#out{width:100%;height:120px;margin-top:8px;font:11px ui-monospace,monospace;border:1px solid #ccc;border-radius:6px;padding:6px}
#copy{margin-top:10px;width:100%;padding:11px;border:0;border-radius:8px;background:#1c1b1f;color:#fff;font-size:14px;font-weight:600;cursor:pointer}
#main{padding:22px 26px 80px;overflow:auto}
.sect{background:#fff;border:1px solid #e1ded8;border-radius:12px;padding:16px 18px 18px;margin-bottom:22px}
.sect header{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;margin-bottom:12px}
.sect h2{font-size:17px}
.sect .vibe{font-size:12.5px;color:#555;margin-top:3px}
.sect .best{font-size:11.5px;color:#888;margin-top:2px}
.picks{display:flex;gap:14px;font-size:12px;white-space:nowrap}
.picks label{display:flex;gap:5px;align-items:center;cursor:pointer}
.row{display:flex;gap:12px;overflow-x:auto;padding-bottom:6px}
.thumb{flex:none;width:calc(var(--w) * var(--s));height:calc(var(--h) * var(--s));box-shadow:0 2px 10px rgba(0,0,0,.14);border-radius:4px;overflow:hidden}
.thumb .slide{transform:scale(var(--s));transform-origin:0 0}
#stage{--s:.27}
.decor{display:none}
#stage[data-theme=playful] .decor-playful,#stage[data-theme=botanical] .decor-botanical,#stage[data-theme=minimal] .decor-minimal,#stage[data-theme=bold] .decor-bold{display:block}
#stage[data-level=none] .decor{display:none!important}
#stage[data-level=light] .dc:not([data-i="0"]):not([data-i="1"]){display:none}
#stage.hide-swipe .swipe{visibility:hidden}
#stage.hide-pagenum .pagenum{visibility:hidden}
.note{font-size:12px;color:#666;margin-top:8px;line-height:1.4}
"""

JS = r"""
var S = __STATE__;
var FONTS = __FONTS__, PAIRS = __PAIRS__, PALS = __PALS__, LAYOUTS = __LAYOUTS__;
var SIZES = {portrait:[1080,1350], square:[1080,1080], story:[1080,1920]};
var $ = function(id){return document.getElementById(id)};
function lin(c){c/=255;return c<=0.03928?c/12.92:Math.pow((c+0.055)/1.055,2.4)}
function lum(h){var r=parseInt(h.substr(1,2),16),g=parseInt(h.substr(3,2),16),b=parseInt(h.substr(5,2),16);return .2126*lin(r)+.7152*lin(g)+.0722*lin(b)}
function contrast(a,b){var x=lum(a),y=lum(b);var hi=Math.max(x,y),lo=Math.min(x,y);return (hi+.05)/(lo+.05)}
function onc(bg){return contrast(bg,'#FFFFFF')>=contrast(bg,'#141414')?'#FFFFFF':'#141414'}
function stack(fam){var f=FONTS.filter(function(x){return x.family===fam})[0];var cat=f?f.category:'sans';
  var tail={serif:'Georgia, serif',script:'cursive',mono:'monospace'}[cat]||'Arial, sans-serif';return "'"+fam+"', "+tail}
var COLS=[['bg','Background'],['ink','Text'],['accent','Main accent'],['accent2','Soft accent'],['muted','Muted text'],['bg_dark','Dark background']];

function fitScale(){var m=$('main');var avail=m.clientWidth-52-38-4*12;var s=Math.max(.12,Math.min(.3,avail/(6*1080)));$('stage').style.setProperty('--s',s.toFixed(4))}
window.addEventListener('resize',fitScale);
function apply(){
  var st=$('stage'), c=S.colors, wh=SIZES[S.size]||SIZES.portrait;
  fitScale();
  var v={'--w':wh[0]+'px','--h':wh[1]+'px','--bg':c.bg,'--ink':c.ink,'--accent':c.accent,'--accent2':c.accent2,'--muted':c.muted,'--bg-dark':c.bg_dark,
    '--on-accent':onc(c.accent),'--on-accent2':onc(c.accent2),'--on-dark':onc(c.bg_dark),
    '--font-head':stack(S.fonts.heading),'--font-body':stack(S.fonts.body),'--font-accent':stack(S.fonts.accent||S.fonts.heading)};
  for(var k in v) st.style.setProperty(k,v[k]);
  st.setAttribute('data-theme',S.decor_theme);st.setAttribute('data-level',S.decor);
  document.querySelectorAll('.texture').forEach(function(e){e.className='texture'+(S.bg_style&&S.bg_style!=='flat'?' t-'+S.bg_style:'')});
  document.querySelectorAll('.thumb .slide').forEach(function(e){e.className=e.className.replace(/\bhl-\w+/g,'').trim();if(S.highlight&&S.highlight!=='layout')e.classList.add('hl-'+S.highlight)});
  st.classList.toggle('hide-swipe',!S.show_swipe);
  st.classList.toggle('hide-pagenum',!S.show_page_numbers);
  document.querySelectorAll('.b-handle').forEach(function(e){e.textContent=S.handle||S.name});
  document.querySelectorAll('.b-name').forEach(function(e){e.textContent=S.name});
  var fams=[S.fonts.heading,S.fonts.body,S.fonts.accent||S.fonts.heading], loads=[];
  fams.forEach(function(f){[400,500,600,700,800].forEach(function(w){loads.push(document.fonts.load(w+" 24px '"+f+"'").catch(function(){}))})});
  Promise.all(loads).then(function(){window.fitAll&&window.fitAll()});
  render();
}
function opt(list,sel){return list.map(function(x){return '<option'+(x===sel?' selected':'')+'>'+x+'</option>'}).join('')}
function build(){
  var h='';
  h+='<h3>Your brand</h3><label>Brand name</label><input type=text id=name><label>Handle</label><input type=text id=handle>';
  h+='<h3>Colors</h3><div class=pal id=pals></div>';
  COLS.forEach(function(p){h+='<div class=crow><span>'+p[1]+'</span><input type=color id=c_'+p[0]+'><input type=text id=t_'+p[0]+'></div>'});
  h+='<h3>Fonts</h3><label>Starter pairing</label><select id=pair><option value="">Pick a pairing</option>'+PAIRS.map(function(p){return '<option>'+p.name+'</option>'}).join('')+'</select>';
  var fam=FONTS.map(function(f){return f.family});
  h+='<label>Headlines</label><select id=f_heading>'+opt(fam,S.fonts.heading)+'</select><label>Body text</label><select id=f_body>'+opt(fam,S.fonts.body)+'</select><label>Handwritten or accent</label><select id=f_accent>'+opt(fam,S.fonts.accent||S.fonts.heading)+'</select>';
  h+='<p class=note>Have your own brand fonts? Put the font files in brand/fonts/ and tell the engine the font name.</p>';
  h+='<h3>Size</h3><select id=size><option value=portrait>Portrait 4:5 (best for Instagram)</option><option value=square>Square 1:1</option><option value=story>Story 9:16</option></select>';
  h+='<h3>Decorations</h3><label>Amount</label><select id=decor><option value=none>None</option><option value=light>Light touch</option><option value=rich>Rich</option></select>';
  h+='<label>Style</label><select id=decor_theme><option value=playful>Playful doodles</option><option value=botanical>Botanical and soft</option><option value=minimal>Minimal</option><option value=bold>Bold shapes</option></select>';
  h+='<label>Background texture</label><select id=bg_style><option value=flat>Flat color</option><option value=mesh>Soft gradient glow</option><option value=grain>Film grain</option><option value=paper>Paper</option><option value=dots>Dots</option><option value=stripes>Stripes</option><option value=waves>Waves</option><option value=grid>Grid</option></select>';
  h+='<label>Highlighted words</label><select id=highlight><option value=layout>Layout default</option><option value=underline>Wavy underline</option><option value=circle>Hand-drawn circle</option><option value=marker>Highlighter</option><option value=box>Solid box</option></select>';
  h+='<div class=chk><input type=checkbox id=photos_auto> Use my photos (brand/photos) on cover, closing, and quote slides</div>';
  h+='<h3>Details</h3><div class=chk><input type=checkbox id=swipe> Show "Swipe" hint</div><div class=chk><input type=checkbox id=pagenum> Show page numbers</div>';
  h+='<button id=copy>Copy my settings</button><textarea id=out readonly placeholder="Your settings appear here"></textarea>';
  h+='<p class=note>Paste this into the chat and say "save my design." You can also skip this and just describe what you want in plain words.</p>';
  $('panel').innerHTML='<h1>Design Studio</h1><p class=sub>Pick a look, tweak it, and every carousel and quote graphic is made in it.</p>'+h;
  $('pals').innerHTML=PALS.map(function(p,i){var c=p.colors;return '<button data-i='+i+' title="'+p.mood+'"><i style="background:'+c.accent+'"></i><i style="background:'+c.accent2+'"></i>'+p.name+'</button>'}).join('');
  $('name').value=S.name;$('handle').value=S.handle;$('size').value=S.size;$('swipe').checked=!!S.show_swipe;$('decor').value=S.decor;$('decor_theme').value=S.decor_theme;$('bg_style').value=S.bg_style;$('highlight').value=S.highlight;$('photos_auto').checked=!(S.photos&&S.photos.auto===false);$('pagenum').checked=!!S.show_page_numbers;
  COLS.forEach(function(p){$('c_'+p[0]).value=S.colors[p[0]];$('t_'+p[0]).value=S.colors[p[0]]});
}
function syncColorUI(){COLS.forEach(function(p){$('c_'+p[0]).value=S.colors[p[0]];$('t_'+p[0]).value=S.colors[p[0]]})}
function wire(){
  $('name').oninput=function(){S.name=this.value;apply()};
  $('handle').oninput=function(){S.handle=this.value;apply()};
  COLS.forEach(function(p){var k=p[0];
    $('c_'+k).oninput=function(){S.colors[k]=this.value.toUpperCase();$('t_'+k).value=S.colors[k];apply()};
    $('t_'+k).onchange=function(){var v=this.value.trim();if(/^#[0-9a-fA-F]{6}$/.test(v)){S.colors[k]=v.toUpperCase();$('c_'+k).value=S.colors[k];apply()}else{this.value=S.colors[k]}};
  });
  document.querySelectorAll('#pals button').forEach(function(b){b.onclick=function(){S.colors=JSON.parse(JSON.stringify(PALS[+b.dataset.i].colors));syncColorUI();apply()}});
  $('pair').onchange=function(){var p=PAIRS.filter(function(x){return x.name===$('pair').value})[0];if(p){S.fonts={heading:p.heading,body:p.body,accent:p.accent};$('f_heading').value=p.heading;$('f_body').value=p.body;$('f_accent').value=p.accent;apply()}};
  ['heading','body','accent'].forEach(function(k){$('f_'+k).onchange=function(){S.fonts[k]=this.value;apply()}});
  $('size').onchange=function(){S.size=this.value;apply()};
  $('decor').onchange=function(){S.decor=this.value;apply()};
  $('decor_theme').onchange=function(){S.decor_theme=this.value;apply()};
  $('bg_style').onchange=function(){S.bg_style=this.value;apply()};
  $('highlight').onchange=function(){S.highlight=this.value;apply()};
  $('photos_auto').onchange=function(){S.photos=S.photos||{};S.photos.auto=this.checked};
  $('swipe').onchange=function(){S.show_swipe=this.checked;apply()};
  $('pagenum').onchange=function(){S.show_page_numbers=this.checked;apply()};
  $('copy').onclick=function(){var o={name:S.name,handle:S.handle,colors:S.colors,fonts:S.fonts,size:S.size,layouts:S.layouts,show_swipe:S.show_swipe,show_page_numbers:S.show_page_numbers,decor:S.decor,decor_theme:S.decor_theme,bg_style:S.bg_style,highlight:S.highlight,photos:S.photos};
    var txt=JSON.stringify(o);$('out').value=txt;
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(txt).then(function(){$('copy').textContent='Copied. Paste it in the chat.'},function(){$('out').select()})}else{$('out').select()}
    setTimeout(function(){$('copy').textContent='Copy my settings'},2500)};
}
function render(){
  document.querySelectorAll('.sect input[data-kind]').forEach(function(i){
    var arr=S.layouts[i.dataset.kind]||[];i.checked=arr.indexOf(i.dataset.layout)>-1});
}
function picks(){
  document.querySelectorAll('.sect input[data-kind]').forEach(function(i){
    i.onchange=function(){var k=i.dataset.kind,l=i.dataset.layout,arr=S.layouts[k]||(S.layouts[k]=[]);
      var at=arr.indexOf(l);if(i.checked&&at<0)arr.push(l);if(!i.checked&&at>-1)arr.splice(at,1)}});
}
build();wire();picks();apply();
"""


def main():
    brand = E.load_brand()
    layouts = E.list_layouts()
    palettes = E.load_json(E.DESIGN / "palettes.json", {"palettes": []})["palettes"]
    fonts = E.font_catalog()

    show = dict(brand)
    show["_studio"] = True
    show.update({"handle": "@@HANDLE@@", "name": "@@NAME@@", "show_handle": True, "cta_label": brand.get("cta_label", "Follow for more")})
    logo = E.logo_uri(brand)
    sections = []
    sample = [dict(s) for s in SAMPLE]
    E.assign_photos(sample, brand)  # shows the buyer's real photos when they have some
    for name, meta in layouts.items():
        slides_html = ""
        for i, s in enumerate(sample):
            s = dict(s)
            s["_seed"] = "studio"
            if s["type"] == "close":
                s["cta"] = brand.get("cta_label") or s["cta"]
            body = E.build_slide(s, i, len(SAMPLE), show, name, "carousel", logo)
            body = body.replace("@@HANDLE@@", '<i class="b-handle" style="font-style:normal"></i>').replace("@@NAME@@", '<i class="b-name" style="font-style:normal"></i>')
            slides_html += f'<div class="thumb">{body}</div>'
        sections.append(
            f'<section class="sect"><header><div><h2>{meta["label"]}</h2>'
            f'<div class="vibe">{meta.get("vibe", "")}</div><div class="best">Best for: {meta.get("best_for", "")}</div></div>'
            f'<div class="picks"><label><input type="checkbox" data-kind="carousel" data-layout="{name}"> Use for carousels</label>'
            f'<label><input type="checkbox" data-kind="quote" data-layout="{name}"> Use for quote graphics</label></div></header>'
            f'<div class="row">{slides_html}</div></section>'
        )

    state = {k: brand[k] for k in ("name", "handle", "colors", "fonts", "size", "layouts", "show_swipe", "show_page_numbers", "decor", "decor_theme", "bg_style", "highlight", "photos")}
    js = (JS.replace("__STATE__", json.dumps(state)).replace("__FONTS__", json.dumps(fonts["families"]))
          .replace("__PAIRS__", json.dumps(fonts["pairings"])).replace("__PALS__", json.dumps(palettes))
          .replace("__LAYOUTS__", json.dumps(list(layouts))))

    import decor as _decor
    css = [E.base_css(), _decor.DECOR_CSS, E._TONE_HL_CSS] + [E.layout_css(n) for n in layouts] + [E.custom_fonts_css(), CSS_UI]
    page = (
        '<!doctype html><html><head><meta charset="utf-8"><title>Design Studio</title>'
        '<link rel="stylesheet" href="fonts/fonts.css"><style>' + "\n".join(css) + "</style></head><body>"
        '<div id="app"><aside id="panel"></aside><main id="main"><div id="stage">' + "".join(sections) +
        "</div></main></div><script>" + E._FIT_JS + "</script><script>" + js + "</script></body></html>"
    )
    out = E.DESIGN / "studio.html"
    out.write_text(page, encoding="utf-8")
    print(f"Design Studio ready: {out}")


if __name__ == "__main__":
    main()
