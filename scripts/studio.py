#!/usr/bin/env python3
"""Build the Design Studio page: design/studio.html

Shows how your carousels and quote graphics will look, in Carousel Studio's layouts, with live
controls for your name, colors and fonts. Open the page in any browser. When you like it, press
"Copy my settings" and paste the result into the chat. Or just tell the engine what you want in
plain words.

Usage: python3 scripts/studio.py
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import engine_lib as E  # noqa: E402
import carousel_studio as CS  # noqa: E402
for _s in (sys.stdout, sys.stderr):  # Windows consoles can choke on curly quotes and emoji; never crash on printing
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

CSS_UI = """
body{display:block;background:#f1efec;color:#1c1b1f;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0}
#app{display:grid;grid-template-columns:330px 1fr;min-height:100vh}
#panel{position:sticky;top:0;height:100vh;overflow:auto;background:#fff;border-right:1px solid #ddd;padding:18px 18px 40px;box-sizing:border-box}
#panel h1{font-size:18px;margin:0 0 4px}
#panel p.sub{font-size:12px;color:#666;margin:0 0 14px;line-height:1.4}
#panel h3{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:#777;margin:18px 0 8px}
#panel label{display:block;font-size:12px;margin:8px 0 3px;color:#444}
#panel input[type=text],#panel select{width:100%;padding:7px 8px;border:1px solid #ccc;border-radius:6px;font-size:13px;background:#fff;box-sizing:border-box}
.crow{display:flex;gap:8px;align-items:center;margin:6px 0}
.crow span{flex:1;font-size:12px;color:#444}
.crow input[type=color]{width:38px;height:28px;border:1px solid #ccc;border-radius:5px;padding:0;background:none}
.crow input[type=text]{width:86px!important;font-family:ui-monospace,monospace}
.pal{display:flex;flex-wrap:wrap;gap:6px}
.pal button{border:1px solid #ccc;background:#fff;border-radius:6px;padding:4px 8px;font-size:11px;cursor:pointer;display:flex;align-items:center;gap:6px}
.pal i{display:inline-block;width:12px;height:12px;border-radius:50%;border:1px solid rgba(0,0,0,.2)}
.chk{display:flex;gap:8px;align-items:center;font-size:12px;margin:5px 0}
#out{width:100%;height:120px;margin-top:8px;font:11px ui-monospace,monospace;border:1px solid #ccc;border-radius:6px;padding:6px;box-sizing:border-box}
#copy{margin-top:10px;width:100%;padding:11px;border:0;border-radius:8px;background:#1c1b1f;color:#fff;font-size:14px;font-weight:600;cursor:pointer}
#main{padding:22px 26px 80px;overflow:auto;min-width:0}
#main h1.top{font-size:20px;margin:0 0 4px}
#main p.lead{font-size:13px;color:#555;margin:0 0 18px;max-width:640px;line-height:1.45}
.sect{background:#fff;border:1px solid #e1ded8;border-radius:12px;padding:16px 18px 18px;margin-bottom:22px}
.sect header{margin-bottom:12px}
.sect h2{font-size:17px;margin:0}
.sect .vibe{font-size:12.5px;color:#555;margin-top:3px}
.row{display:flex;gap:14px;overflow-x:auto;padding-bottom:6px;align-items:flex-start}
.cell{flex:none}
.thumb{width:calc(1080px * var(--s));height:calc(1350px * var(--s));box-shadow:0 2px 10px rgba(0,0,0,.14);border-radius:4px;overflow:hidden;position:relative}
.thumb .sio{transform:scale(var(--s));transform-origin:0 0;position:absolute;left:0;top:0}
.lab{font-size:11.5px;color:#666;margin-top:6px;max-width:calc(1080px * var(--s))}
.lab b{color:#222}
h2.grp{font-size:13px;letter-spacing:.1em;text-transform:uppercase;color:#777;margin:26px 0 10px}
#stage{--s:.22}
.note{font-size:12px;color:#666;margin-top:8px;line-height:1.4}
@media (max-width:900px){#app{grid-template-columns:1fr}#panel{position:static;height:auto}}
"""

JS = r"""
var S = __STATE__;
var SAMPLEPIC = __SAMPLEPIC__;
var FONTS = __FONTS__, PAIRS = __PAIRS__, PALS = __PALS__, PICS = __PICS__, SAMPLE = __SAMPLE__, BYL = __BYL__;
var VIBE = {editorial:'Clean and calm, with big readable type.', 'photo-story':'Photo-led. These layouts use your own photos, so add some to brand/photos to use them.', bold:'Loud type and big shapes.', soft:'Gentle and warm, with handwritten touches.'};
var $ = function(id){return document.getElementById(id)};
var COLS=[['bg','Background'],['ink','Text'],['accent','Main accent'],['accent2','Soft accent'],['muted','Muted text'],['bg_dark','Dark background']];
function mix(a,b,t){try{var x=[1,3,5].map(function(i){return parseInt(a.substr(i,2),16)}),y=[1,3,5].map(function(i){return parseInt(b.substr(i,2),16)});
  return '#'+x.map(function(v,i){var n=Math.round(v*t+y[i]*(1-t));return ('0'+n.toString(16)).slice(-2)}).join('').toUpperCase()}catch(e){return a}}
function theme(){
  var c=S.colors, f=S.fonts, fam=FONTS.filter(function(x){return x.family===f.heading})[0], ws=(fam&&fam.weights)||[700];
  var low=ws.filter(function(w){return w<=700}), hw=low.length?Math.max.apply(null,low):ws[0];
  return {id:'brand',name:'My brand',colors:{bg:c.bg,ink:c.ink,accent:c.accent,accent2:c.accent2,muted:c.muted,dark:c.bg_dark||c.ink,paper:mix(c.bg,'#FFFFFF',.45)},
    fonts:{head:f.heading,body:f.body,script:f.accent||'Caveat'},head_weight:hw,head_case:'none',head_track:'-0.01em',kicker:'script',quote_italic:true,radius:30};
}
function slideFor(role, layoutId, pi){
  var d=layoutId&&CarouselStudio.BY_ID[layoutId];
  var s=Object.assign({role:role},SAMPLE[role]||{},layoutId&&BYL[layoutId]||{});
  if(layoutId) s.layout=layoutId;
  if(d&&d.photos>0&&PICS.length){ s.photo={src:PICS[pi.n++%PICS.length],x:50,y:30,zoom:1}; if(d.photos>1) s.photo2={src:PICS[pi.n++%PICS.length],x:50,y:30,zoom:1}; }
  return s;
}
function thumb(slide, plan, i, n, label){
  var ctx={i:i,n:n,theme:theme(),name:S.name,handle:S.handle||S.name,show_handle:true,show_numbers:!!S.show_page_numbers,show_swipe:!!S.show_swipe,photoUrl:function(x){return x}};
  var id=CarouselStudio.layoutFor(slide,plan), d=CarouselStudio.BY_ID[id];
  return '<div class="cell"><div class="thumb">'+CarouselStudio.render(slide,ctx,plan)+'</div><div class="lab"><b>'+label+'</b> '+(d?d.name:id)+(SAMPLEPIC&&slide.photo?' <i>(sample photo)</i>':'')+'</div></div>';
}
function gallery(){
  var h='<h1 class=top>How your carousels will look</h1><p class=lead>Every carousel and quote graphic is made with these layouts, in your name, colors and fonts. Each carousel in a pack gets one of the looks below, and you can change any slide later.'+(SAMPLEPIC?' The photo layouts show a sample picture. To use them, add your own photos to the brand/photos folder.':'')+'</p>';
  var pi={n:0};
  Object.keys(CarouselStudio.LOOKS).forEach(function(k){
    var plan={look:k}, roles=CarouselStudio.ROLES, cells='';
    roles.forEach(function(r,i){cells+=thumb(slideFor(r,null,pi),plan,i,roles.length,r)});
    h+='<section class=sect><header><h2>'+CarouselStudio.LOOKS[k].name+' look</h2><div class=vibe>'+(VIBE[k]||'')+'</div></header><div class=row>'+cells+'</div></section>';
  });
  h+='<h2 class=grp>All '+CarouselStudio.LAYOUTS.length+' layouts</h2>';
  var groups={}; CarouselStudio.LAYOUTS.forEach(function(d){(groups[d.group]=groups[d.group]||[]).push(d)});
  var n=0;
  Object.keys(groups).forEach(function(g){
    var cells='';
    groups[g].forEach(function(d){n++; var role=d.roles[0]; cells+=thumb(slideFor(role,d.id,pi),{},role==='close'?6:role==='cover'?0:2,7,n)});
    h+='<section class=sect><header><h2>'+g+'</h2></header><div class=row>'+cells+'</div></section>';
  });
  return h;
}
var pending=0;
function apply(){ if(pending) return; pending=requestAnimationFrame(function(){pending=0; draw()}); }
function draw(){
  $('stage').innerHTML=gallery();
  var fams=[S.fonts.heading,S.fonts.body,S.fonts.accent||'Caveat'], loads=[];
  fams.forEach(function(f){[400,500,600,700,800].forEach(function(w){loads.push(document.fonts.load(w+" 24px '"+f+"'").catch(function(){}))});loads.push(document.fonts.load("italic 700 24px '"+f+"'").catch(function(){}))});
  Promise.all(loads).then(function(){document.querySelectorAll('#stage .sio').forEach(function(e){CarouselStudio.fit(e)})});
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
  h+='<h3>Details</h3><p class=note>Photo layouts need your own photos. Put them in the brand/photos folder, or add them inside the carousel editor.</p><div class=chk><input type=checkbox id=photos_auto> Use my photos (brand/photos) on cover, closing, and quote slides</div><div class=chk><input type=checkbox id=swipe> Show the swipe arrow</div><div class=chk><input type=checkbox id=pagenum> Show page numbers</div>';
  h+='<button id=copy>Copy my settings</button><textarea id=out readonly placeholder="Your settings appear here"></textarea>';
  h+='<p class=note>Paste this into the chat and say "save my design." You can also skip this and just describe what you want in plain words.</p>';
  $('panel').innerHTML='<h1>Design Studio</h1><p class=sub>Pick your name, colors and fonts. Every carousel and quote graphic is made in them.</p>'+h;
  $('pals').innerHTML=PALS.map(function(p,i){var c=p.colors;return '<button data-i='+i+' title="'+p.mood+'"><i style="background:'+c.accent+'"></i><i style="background:'+c.accent2+'"></i>'+p.name+'</button>'}).join('');
  $('name').value=S.name;$('handle').value=S.handle;$('swipe').checked=!!S.show_swipe;$('photos_auto').checked=!(S.photos&&S.photos.auto===false);$('pagenum').checked=!!S.show_page_numbers;
  syncColorUI();
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
  $('photos_auto').onchange=function(){S.photos=S.photos||{};S.photos.auto=this.checked};
  $('swipe').onchange=function(){S.show_swipe=this.checked;apply()};
  $('pagenum').onchange=function(){S.show_page_numbers=this.checked;apply()};
  $('copy').onclick=function(){var o={name:S.name,handle:S.handle,colors:S.colors,fonts:S.fonts,show_swipe:S.show_swipe,show_page_numbers:S.show_page_numbers,photos:S.photos};
    var txt=JSON.stringify(o);$('out').value=txt;
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(txt).then(function(){$('copy').textContent='Copied. Paste it in the chat.'},function(){$('out').select()})}else{$('out').select()}
    setTimeout(function(){$('copy').textContent='Copy my settings'},2500)};
}
build();wire();draw();
"""


def main():
    brand = E.load_brand()
    palettes = E.load_json(E.DESIGN / "palettes.json", {"palettes": []})["palettes"]
    fonts = E.font_catalog()
    pics = ["../brand/photos/" + p.name for p in E.list_photos()]
    sample_pic = not pics
    if sample_pic:
        pics = ["sample-photo.jpg"]

    state = {k: brand.get(k) for k in ("name", "handle", "colors", "fonts", "show_swipe", "show_page_numbers", "photos")}
    state["photos"] = state["photos"] or {}
    js = (JS.replace("__STATE__", json.dumps(state)).replace("__FONTS__", json.dumps(fonts["families"]))
          .replace("__PAIRS__", json.dumps(fonts["pairings"])).replace("__PALS__", json.dumps(palettes))
          .replace("__PICS__", json.dumps(pics)).replace("__SAMPLEPIC__", "true" if sample_pic else "false").replace("__SAMPLE__", json.dumps(CS.SAMPLE))
          .replace("__BYL__", json.dumps(CS.SAMPLE_BY_LAYOUT)))

    page = (
        '<!doctype html><html><head><meta charset="utf-8"><title>Design Studio</title>'
        '<link rel="stylesheet" href="fonts/fonts.css"><link rel="stylesheet" href="carousel-studio/layouts.css">'
        "<style>" + E.custom_fonts_css() + "\n" + CSS_UI + "</style>"
        '<script src="carousel-studio/layouts.js"></script></head><body>'
        '<div id="app"><aside id="panel"></aside><main id="main"><div id="stage"></div></main></div>'
        "<script>" + js + "</script></body></html>"
    )
    out = E.DESIGN / "studio.html"
    out.write_text(page, encoding="utf-8")
    print(f"Design Studio ready: {out}")


if __name__ == "__main__":
    main()
