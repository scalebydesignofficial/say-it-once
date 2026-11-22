"""CSS and JS that make a slide animate. Only used when a page is built in animation mode.

Everything uses the independent CSS properties `translate`, `scale`, `rotate` and `opacity`, so the
final frame is exactly the same as the still image, and layout transforms are never disturbed.
Time is controlled from outside with window.seek(seconds), so frames can be captured one by one.
"""

ANIM_CSS = """
html.anim .w{display:inline-block}
html.anim .w.g{display:inline}
html.anim .nb{display:inline-block;white-space:nowrap}
html.anim .an{animation-duration:.7s;animation-timing-function:cubic-bezier(.2,.75,.2,1);animation-fill-mode:backwards}
html.anim .an-up{animation-name:aUp}
@keyframes aUp{from{opacity:0;translate:0 calc(var(--u) * 3.6)}to{opacity:1;translate:0 0}}
html.anim .an-fade{animation-name:aFade}
@keyframes aFade{from{opacity:0}to{opacity:1}}
html.anim .an-pop{animation-name:aPop;animation-timing-function:cubic-bezier(.3,1.55,.5,1)}
@keyframes aPop{from{opacity:0;scale:.3}to{opacity:1;scale:1}}
html.anim .an-slide{animation-name:aSlide}
@keyframes aSlide{from{opacity:0;translate:calc(var(--u) * -7) 0}to{opacity:1;translate:0 0}}
html.anim .an-rise{animation-name:aRise}
@keyframes aRise{from{opacity:0;translate:0 calc(var(--u) * 9)}to{opacity:1;translate:0 0}}
html.anim .dc[data-a="draw"] .s{stroke-dasharray:1;animation:aDraw .95s ease-out backwards}
@keyframes aDraw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
html.anim .dc svg{animation:aBob 3.4s ease-in-out infinite alternate}
@keyframes aBob{from{translate:0 calc(var(--u) * -.8)}to{translate:0 calc(var(--u) * .8)}}
html.anim .photo-bg .photo{animation:aKen var(--dur) linear both}
@keyframes aKen{from{scale:1}to{scale:1.14}}
html.anim .layout--glow .deco,html.anim .layout--spotlight .deco{animation:aPulse 3.6s ease-in-out infinite alternate}
@keyframes aPulse{from{scale:1}to{scale:1.1}}
html.anim .texture.t-mesh{animation:aDrift 6s ease-in-out infinite alternate}
@keyframes aDrift{from{translate:calc(var(--u) * -2) 0;scale:1.08}to{translate:calc(var(--u) * 2) calc(var(--u) * 1.5);scale:1.08}}
"""

ANIM_JS = r"""
window.seek=function(t){document.getAnimations().forEach(function(a){a.pause();a.currentTime=t*1000;});};
window.buildAnim=function(){
  var sl=document.querySelector('.slide'); if(!sl) return;
  var LEAD=window.__LEAD||0.35, settle=0;
  function put(el,delay,kind,dur){
    if(!el) return; el.classList.add('an','an-'+kind); el.style.animationDelay=delay.toFixed(3)+'s';
    if(dur) el.style.animationDuration=dur+'s';
    var e=delay+(dur||0.7); if(e>settle) settle=e;
  }
  function split(el){
    var out=[];
    (function walk(n){
      Array.prototype.slice.call(n.childNodes).forEach(function(c){
        if(c.nodeType===3){
          var frag=document.createDocumentFragment();
          var txt=c.textContent, prev=c.previousSibling;
          /* punctuation glued to a highlight (like a period) must stay on the same line as it, so group them */
          var gm=txt.match(/^(\S+)([\s\S]*)$/);
          if(gm && prev && prev.nodeType===1 && prev.tagName!=='BR' && prev.querySelectorAll('.w').length<=3){
            var grp=document.createElement('span'); grp.className='nb';
            n.insertBefore(grp,prev); grp.appendChild(prev);
            var gs=document.createElement('span'); gs.className='w g'; gs.textContent=gm[1];
            grp.appendChild(gs); out.push(gs); txt=gm[2];
          }
          txt.split(/(\s+)/).forEach(function(p){
            if(!p) return;
            if(/^\s+$/.test(p)){ frag.appendChild(document.createTextNode(p)); }
            else { var sp=document.createElement('span'); sp.className='w'; sp.textContent=p; frag.appendChild(sp); out.push(sp); }
          });
          n.replaceChild(frag,c);
        } else if(c.nodeType===1 && c.tagName!=='BR'){ walk(c); }
      });
    })(el);
    return out;
  }
  function seq(el,start,step,maxTotal,kind){
    var w=split(el), n=w.length||1, st=Math.min(step,maxTotal/n);
    w.forEach(function(s,i){ put(s,start+i*st,kind||'up',0.55); });
    return start+n*st;
  }
  var t=LEAD;
  put(sl.querySelector('.top'),t,'fade',0.6);
  var k=sl.querySelector('.kicker'); if(k){ put(k,t+0.1,'pop',0.55); t+=0.35; }
  var h=sl.querySelector('.headline'); if(h) t=seq(h,t+0.05,0.1,1.1)+0.12;
  var q=sl.querySelector('.qtext'); if(q) t=seq(q,t+0.05,0.085,1.7)+0.12;
  var sn=sl.querySelector('.stat-num'); if(sn){ put(sn,t,'pop',0.75); t+=0.6; }
  var lb=sl.querySelector('.stat-label'); if(lb) t=seq(lb,t,0.09,0.9)+0.1;
  var sub=sl.querySelector('.sub,.body'); if(sub) t=seq(sub,t,0.045,1.2)+0.1;
  var at=sl.querySelector('.attr'); if(at){ put(at,t,'up',0.6); t+=0.3; }
  var lis=sl.querySelectorAll('.items li,.checks li');
  Array.prototype.forEach.call(lis,function(li,i){ put(li,t+i*0.24,'slide',0.6); });
  if(lis.length) t+=lis.length*0.24+0.2;
  var va=sl.querySelector('.vs-a'), vb=sl.querySelector('.vs-b');
  if(va){ put(va,t,'up',0.6); t+=0.5; } if(vb){ put(vb,t,'pop',0.7); t+=0.5; }
  var cta=sl.querySelector('.cta'); if(cta){ put(cta,t+0.05,'pop',0.7); t+=0.5; }
  put(sl.querySelector('.bottom'),t,'fade',0.6);
  var dcs=sl.querySelectorAll('.dc');
  Array.prototype.forEach.call(dcs,function(dc,i){
    var d=LEAD+0.35+i*0.22;
    if(dc.getAttribute('data-a')==='draw'){
      var p=dc.querySelectorAll('.s'); Array.prototype.forEach.call(p,function(x){ x.style.animationDelay=d.toFixed(3)+'s'; });
      if(d+0.95>settle) settle=d+0.95;
    } else { put(dc,d,'pop',0.7); }
  });
  window.__settle=settle;
};
"""
