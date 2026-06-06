"""Static HTML/JS for the visual annotator (kept separate to keep annotate.py small)."""

HTML = """<!doctype html><html lang="pt-br"><head><meta charset="utf-8">
<title>atos · anotador de atos de fala</title>
<style>
 :root{color-scheme:dark}
 body{font:16px/1.5 system-ui,sans-serif;background:#0f1115;color:#e6e6e6;margin:0;padding:20px;max-width:900px;margin:0 auto}
 header{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:14px}
 button{background:#1c1f26;color:#e6e6e6;border:1px solid #333;border-radius:6px;padding:6px 10px;cursor:pointer;font-size:14px}
 button:hover{background:#272b34}
 #text{font-size:22px;line-height:1.7;background:#161922;padding:18px;border-radius:10px;user-select:text;cursor:text;white-space:pre-wrap}
 #actbar{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}
 #actbar button{padding:6px 12px}
 .span{display:flex;align-items:center;gap:8px;background:#161922;padding:6px 10px;border-radius:6px;margin:4px 0}
 .span button{margin-left:auto;padding:2px 8px}
 .badge{padding:2px 8px;border-radius:5px;color:#000;font-weight:600;font-size:13px}
 mark{border-radius:4px;color:#000;padding:0 2px}
 #preview{background:#161922;padding:14px;border-radius:10px;font-size:18px;line-height:1.7;white-space:pre-wrap;margin-top:10px}
 #status{margin-left:auto;color:#9fd}
 h4{margin:16px 0 4px;color:#9aa}
 .hint{color:#778;font-size:13px}
</style></head><body>
<header>
 <button onclick="go(-1)">◀ anterior</button>
 <strong id="pos">–</strong>
 <button onclick="go(1)">próximo ▶</button>
 <span id="progress" class="hint"></span>
 <span id="status"></span>
</header>
<div class="hint">selecione um trecho com o mouse e clique no ato (ou teclas 1–9). setas ← → navegam. salva sozinho.</div>
<h4>texto</h4>
<div id="text"></div>
<h4>atos</h4>
<div id="actbar"></div>
<h4>spans deste exemplo</h4>
<div id="spans"></div>
<h4>prévia</h4>
<div id="preview"></div>
<script>
let S={rows:[],acts:[],idx:0}; let pending=null;
const COLORS=["#8ecae6","#ffb703","#90be6d","#f94144","#bdb2ff","#fb8500","#43aa8b","#f9c74f","#ff8fab","#a0c4ff","#d4a373","#caffbf","#ffd6a5"];
function colorFor(a){const i=S.acts.indexOf(a);return COLORS[(i<0?0:i)%COLORS.length];}
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function curr(){return S.rows[S.idx]||{text:'',spans:[]};}
async function load(){const r=await fetch('/api/state');const j=await r.json();S.rows=j.rows;S.acts=j.acts;render();}
function render(){
 const row=curr();
 document.getElementById('pos').textContent=(S.idx+1)+' / '+S.rows.length;
 const ann=S.rows.filter(r=>r.spans&&r.spans.length).length;
 document.getElementById('progress').textContent=ann+' anotados';
 document.getElementById('text').textContent=row.text;
 const ab=document.getElementById('actbar');ab.innerHTML='';
 S.acts.forEach((a,i)=>{const b=document.createElement('button');b.textContent=(i<9?(i+1)+' ':'')+a;b.style.borderLeft='6px solid '+COLORS[i%COLORS.length];b.onclick=()=>addSpan(a);ab.appendChild(b);});
 const sl=document.getElementById('spans');sl.innerHTML='';
 (row.spans||[]).forEach((sp,j)=>{const d=document.createElement('div');d.className='span';
   d.innerHTML='<span class="badge" style="background:'+colorFor(sp.act)+'">'+esc(sp.act)+'</span> '+esc(sp.quote);
   const x=document.createElement('button');x.textContent='✕';x.onclick=()=>{row.spans.splice(j,1);render();save();};d.appendChild(x);sl.appendChild(d);});
 document.getElementById('preview').innerHTML=previewHtml(row);
}
function previewHtml(row){let html='',cur=0;const t=row.text;for(const sp of(row.spans||[])){const i=t.indexOf(sp.quote,cur);if(i<0)continue;html+=esc(t.slice(cur,i));html+='<mark style="background:'+colorFor(sp.act)+'">'+esc(t.slice(i,i+sp.quote.length))+'</mark>';cur=i+sp.quote.length;}html+=esc(t.slice(cur));return html;}
document.addEventListener('mouseup',()=>{const node=document.getElementById('text').firstChild;const sel=window.getSelection();if(!sel.rangeCount||sel.isCollapsed)return;const r=sel.getRangeAt(0);if(r.startContainer!==node||r.endContainer!==node)return;let s=r.startOffset,e=r.endOffset;if(s>e){const t=s;s=e;e=t;}pending={start:s,quote:curr().text.slice(s,e)};});
function addSpan(act){if(!pending||!pending.quote){document.getElementById('status').textContent='selecione um trecho primeiro';return;}const row=curr();row.spans=row.spans||[];row.spans.push({quote:pending.quote,act:act,_start:pending.start});row.spans.sort((a,b)=>(a._start||0)-(b._start||0));pending=null;window.getSelection().removeAllRanges();render();save();}
function go(d){S.idx=Math.max(0,Math.min(S.rows.length-1,S.idx+d));render();}
let saveT=null;function save(){clearTimeout(saveT);saveT=setTimeout(doSave,500);}
async function doSave(){const payload={rows:S.rows.map(r=>({text:r.text,spans:(r.spans||[]).map(s=>({quote:s.quote,act:s.act}))}))};const r=await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const j=await r.json();document.getElementById('status').textContent='salvo · '+j.valid+' válidos · '+j.errors.length+' erro(s)';}
document.addEventListener('keydown',(e)=>{if(e.target.tagName==='INPUT')return;if(e.key==='ArrowRight')go(1);else if(e.key==='ArrowLeft')go(-1);else if(/^[1-9]$/.test(e.key)){const i=parseInt(e.key)-1;if(i<S.acts.length)addSpan(S.acts[i]);}});
load();
</script></body></html>"""
