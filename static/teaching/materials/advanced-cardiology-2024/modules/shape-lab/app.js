/* Accessible local interaction; no network, storage, or external libraries. */
'use strict';
(() => {
 const C=ShapeCore,$=id=>document.getElementById(id),NS='http://www.w3.org/2000/svg';
 let data,rawX,rawY,result=null,selected=0,drag=null,timer=null,playing=false,raf=0,last=0;
 const reduced=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 const el=(tag,attrs={},text)=>{const x=document.createElementNS(NS,tag);for(const [k,v]of Object.entries(attrs))x.setAttribute(k,String(v));if(text!==undefined)x.textContent=text;return x;};
 const num=v=>Number.isFinite(v)?(Math.abs(v)<1e-4&&v!==0?v.toExponential(2):v.toFixed(4)):'not finite';
 const opts=()=>({center:$('center').checked,rotate:$('rotate').checked,normalize:$('normalize').checked,shift:Number($('shift').value),reverse:$('reverse').checked});
 const active=()=> $('editcurve').value==='source'?rawX:rawY;
 function setStatus(text,kind=''){const x=$('status');x.textContent=text;x.className='notice'+(kind?' '+kind:'');}
 function pause(){playing=false;cancelAnimationFrame(raf);$('play').textContent='Play';}
 function dirty(){pause();clearTimeout(timer);result=null;$('play').disabled=true;$('time').disabled=true;for(const id of ['metric','naive-end','flow-end'])$(id).textContent='—';$('diagnostics').replaceChildren();$('naive').replaceChildren();$('flow').replaceChildren();setStatus('Edits changed the experiment. Recomputing the field and numerical diagnostics…');}
 function requestBuild(){dirty();clearTimeout(timer);timer=setTimeout(build,40);}
 function selectors(){const n=rawX.length;$('shift').max=n-1;$('shift').value=((Number($('shift').value)||0)%n+n)%n;selected=Math.min(selected,n-1);$('selected').replaceChildren(...Array.from({length:n},(_,i)=>{const o=document.createElement('option');o.value=i;o.textContent=String(i);return o;}));$('selected').value=selected;editFields();}
 function editFields(){const p=active()[selected];$('selected').value=selected;$('editx').value=p[0].toFixed(3);$('edity').value=p[1].toFixed(3);}
 function path(p,project,closed=false){return p.map((q,i)=>(i?'L':'M')+project(q).map(v=>v.toFixed(3)).join(',')).join(' ')+(closed?' Z':'');}
 function frame(svg,width,height,bound,unit){svg.replaceChildren();const margin=44,size=Math.min(width-2*margin,height-2*margin),x0=(width-size)/2,y0=(height-size)/2;
  const proj=p=>[x0+size*(p[0]+bound)/(2*bound),y0+size*(bound-p[1])/(2*bound)];
  const defs=el('defs'),clip=el('clipPath',{id:svg.id+'-clip'});clip.append(el('rect',{x:x0,y:y0,width:size,height:size}));defs.append(clip);svg.append(defs);
  for(const v of [-bound,-bound/2,0,bound/2,bound]){const a=proj([v,0]),b=proj([0,v]);svg.append(el('text',{x:a[0],y:y0+size+22,'text-anchor':'middle','font-size':13,fill:'#385469'},num(v).replace(/\.0000$/,'')));svg.append(el('text',{x:x0-9,y:b[1]+5,'text-anchor':'end','font-size':13,fill:'#385469'},num(v).replace(/\.0000$/,'')));}
  svg.append(el('rect',{x:x0,y:y0,width:size,height:size,fill:'none',stroke:'#acbdc8'}));svg.append(el('text',{x:width/2,y:height-6,'text-anchor':'middle','font-size':14,fill:'#142f46'},'x ('+unit+')'));svg.append(el('text',{x:8,y:17,'font-size':14,fill:'#142f46'},'y ('+unit+')'));
  const group=el('g',{'clip-path':'url(#'+svg.id+'-clip)'});svg.append(group);return {proj,group,x0,y0,size,bound};}
 function drawEditor(){const svg=$('editor'),f=frame(svg,640,440,32,'mm');for(const [p,color,dash]of [[rawX,'#536877','3 5'],[rawY,'#ac3c00','9 5']])f.group.append(el('path',{d:path(p,f.proj,true),fill:'none',stroke:color,'stroke-width':2,'stroke-dasharray':dash}));
  active().forEach((p,i)=>{const q=f.proj(p),g=el('g',{'data-index':i});const h=el('circle',{cx:q[0],cy:q[1],r:i===selected?7:5,fill:i===selected?'#142f46':'white',stroke:'#142f46','stroke-width':2,tabindex:0,role:'button','aria-label':`${$('editcurve').value} landmark ${i}, x ${p[0].toFixed(2)} y ${p[1].toFixed(2)} millimetres. Arrow keys edit.`,'data-index':i});g.append(h);g.append(el('text',{x:q[0]+9,y:q[1]-8,'font-size':12,fill:'#142f46','pointer-events':'none'},i));f.group.append(g);});
  $('raw-status').textContent=`Source polygon: ${C.crossings(rawX)} strict segment crossings. Target polygon: ${C.crossings(rawY)}. Raw edits are in mm; alignment is applied afterward.`;
 }
 function setPoint(i,x,y){const p=active();p[i]=[Math.max(-30,Math.min(30,x)),Math.max(-30,Math.min(30,y))];selected=i;editFields();drawEditor();}
 function editorXY(event){const svg=$('editor'),rect=svg.getBoundingClientRect();const x=(event.clientX-rect.left)*640/rect.width,y=(event.clientY-rect.top)*440/rect.height;return [(x-144)/352*64-32,32-(y-44)/352*64];}
 function dense(p,n=8){return p.flatMap((q,i)=>Array.from({length:n},(_,j)=>q.map((v,b)=>v+(p[(i+1)%p.length][b]-v)*j/n)));}
 function build(){try{
  const prepared=C.prepare(rawX,rawY,opts()),{x,y}=prepared,r=C.radius(x),field=C.fit(x,y,Number($('support').value)*r);
  const maxCoord=Math.max(...x.flat().map(Math.abs),...y.flat().map(Math.abs)),bound=Math.max(r*1.8,maxCoord*1.2),grid=[];
  for(let j=0;j<9;j++){const q=bound*(-.9+1.8*j/8);for(let k=0;k<25;k++)grid.push([q,bound*(-.9+1.8*k/24)]);for(let k=0;k<25;k++)grid.push([bound*(-.9+1.8*k/24),q]);}
  const curve=dense(x),all=[...x,...curve,...grid],steps=64*Math.max(2,Math.ceil(4*field.lipschitz/64));
  const coarse=C.integrate(field,all,steps),fine=C.integrate(field,all,2*steps,{frames:64}),end=C.statePoints(fine.state),back=C.integrate(field,end.slice(0,x.length),2*steps,{duration:-1});
  const gap=C.maxGap(C.statePoints(coarse.state),end),inverse=C.maxGap(C.statePoints(back.state),x);let jacError=0,minAll=Infinity;
  for(const s of fine.history){for(let i=0;i<s.length;i+=7){const det=s[i+2]*s[i+5]-s[i+3]*s[i+4],expected=Math.exp(s[i+6]);jacError=Math.max(jacError,Math.abs(det-expected)/Math.max(expected,1e-12));minAll=Math.min(minAll,det);}}
  const passed=gap<2e-5*r&&inverse<2e-5*r&&jacError<1e-4&&minAll>0;
  result={...prepared,field,all,curve,grid,bound,steps:2*steps,history:fine.history,gap,inverse,jacError,minAll,passed,endpoint:C.rms(end.slice(0,x.length),y),naiveEndpoint:C.rms(C.naive(field,x,1),y)};
  $('metric').textContent=num(C.rms(x,y));$('unit').textContent=prepared.unit;$('naive-end').textContent=num(result.naiveEndpoint);$('flow-end').textContent=num(result.endpoint);$('play').disabled=false;$('time').disabled=false;$('time').value=0;
  let message=passed?'Sampled numerical checks pass. Exact-flow orientation follows from the smooth field; these finite checks do not certify global numerical injectivity.':'Numerical check warning: do not infer a valid numerical deformation. Reduce the edit or support interaction and inspect the diagnostics.';
  if(!prepared.rotationUnique&&opts().rotate)message+=' The rotation optimum is nonunique; angle zero was selected.';
  if(C.crossings(rawX)||C.crossings(rawY))message+=' An edited polygon self-intersects; a diffeomorphic flow does not repair its topology.';
  setStatus(message,passed?'':'warn');draw();
 }catch(e){result=null;$('play').disabled=true;$('time').disabled=true;setStatus('Flow disabled: '+e.message+' No regularization or replacement field was applied.','error');}}
 function draw(){if(!result)return;const t=Number($('time').value)/64,R=result,index=Number($('time').value),s=R.history[index],flow=C.statePoints(s),naive=C.naive(R.field,R.all,t),n=R.x.length,m=R.curve.length;$('time-label').textContent=t.toFixed(3);
  for(const [id,p,color]of [['naive',naive,'#2459a6'],['flow',flow,'#00695c']]){const f=frame($(id),600,460,R.bound,R.unit);for(let j=0;j<18;j++){const line=p.slice(n+m+j*25,n+m+(j+1)*25);f.group.append(el('path',{d:path(line,f.proj),fill:'none',stroke:'#8ba0ad','stroke-width':.8}));}
   f.group.append(el('path',{d:path(R.x,f.proj,true),fill:'none',stroke:'#536877','stroke-width':1.6,'stroke-dasharray':'3 5'}));f.group.append(el('path',{d:path(R.y,f.proj,true),fill:'none',stroke:'#ac3c00','stroke-width':2,'stroke-dasharray':'9 5'}));f.group.append(el('path',{d:path(p.slice(n,n+m),f.proj,true),fill:'none',stroke:color,'stroke-width':3}));for(const q of p.slice(0,n)){const a=f.proj(q);f.group.append(el('circle',{cx:a[0],cy:a[1],r:3,fill:color}));}}
  const naiveMin=Math.min(...C.naiveDet(R.field,R.all,t)),flowMin=Math.min(...C.determinants(s)),sourceArea=C.signedArea(R.x),np=naive.slice(0,n),fp=flow.slice(0,n);
  const rows=[['Coordinate-map min det DFₜ',num(naiveMin),naiveMin<=0?'A sampled singularity or orientation reversal is detected.':'Positive at sampled points only.'],['Flow min det DΦₜ',num(flowMin),'Computed variational Jacobian at this time.'],['Flow min det over cached states',num(R.minAll),'All sampled positions and 65 stored times.'],['Coordinate / flow curve area',`${num(C.signedArea(np))} / ${num(C.signedArea(fp))}`,'Signed landmark-polygon area in '+(R.unit==='mm'?'mm²':'normalized units²')+'.'],['Coordinate / flow polygon crossings',`${C.crossings(np)} / ${C.crossings(fp)}`,'Strict intersections in the landmark polygon; degeneracies may be missed.'],['Time-refinement position gap',num(R.gap),`${R.steps/2} versus ${R.steps} RK4 steps; maximum over displayed samples.`],['Inverse-flow position gap',num(R.inverse),'Forward then backward integration of landmarks.'],['Jacobian exponential identity gap',num(R.jacError),'Max relative |det A − exp(log J)| over cached samples.'],['Interpolation matrix condition ∞',num(R.field.condition),'No ridge term; ill-conditioned systems are disabled.'],['Field interpolation max residual',num(R.field.residual),'Initial velocity fit, not final flow endpoint matching.'],['Global Lipschitz upper bound',num(R.field.lipschitz),'Conservative analytic field bound; not a fitted energy.']];
  $('diagnostics').replaceChildren(...rows.map(row=>{const tr=document.createElement('tr');row.forEach((v,i)=>{const q=document.createElement(i?'td':'th');if(!i)q.scope='row';q.textContent=v;tr.append(q);});return tr;}));
 }
 function preset(name){pause();$('count').value=16;$('shift').value=0;$('reverse').checked=false;$('normalize').checked=false;$('center').checked=true;$('rotate').checked=true;$('support').value=1.2;$('support-label').textContent='1.2';$('source').value='lobed';$('target').value='bean';
  if(name==='identity')$('target').value='lobed';if(name==='pose')$('target').value='posed';if(name==='scale')$('target').value='scaled';if(name==='halfturn'){$('source').value='circle';$('target').value='circle';$('shift').value=8;$('rotate').checked=false;$('support').value=2;$('support-label').textContent='2.0';}if(name==='reverse'){$('target').value='lobed';$('reverse').checked=true;$('rotate').checked=false;}
  rawX=C.resample(data.curves[$('source').value].points,16);rawY=C.resample(data.curves[$('target').value].points,16);selected=0;selectors();drawEditor();requestBuild();}
 function tick(now){if(!playing)return;if(now-last>(reduced?180:70)){last=now;const k=Number($('time').value);if(k>=64){pause();return;}$('time').value=k+1;draw();}raf=requestAnimationFrame(tick);}
 try{data=JSON.parse($('dataset').textContent);for(const id of ['source','target'])for(const [key,value]of Object.entries(data.curves)){const o=document.createElement('option');o.value=key;o.textContent=value.label;$(id).append(o);}
  for(const id of ['source','target'])$(id).addEventListener('change',()=>{const p=C.resample(data.curves[$(id).value].points,Number($('count').value));if(id==='source')rawX=p;else rawY=p;selectors();drawEditor();requestBuild();});
  $('count').addEventListener('change',()=>{rawX=C.resample(rawX,Number($('count').value));rawY=C.resample(rawY,Number($('count').value));selectors();drawEditor();requestBuild();});
  for(const id of ['shift','center','rotate','normalize','reverse'])$(id).addEventListener('change',requestBuild);
  $('support').addEventListener('input',()=>{$('support-label').textContent=Number($('support').value).toFixed(1);});$('support').addEventListener('change',requestBuild);
  $('editcurve').addEventListener('change',()=>{editFields();drawEditor();});$('selected').addEventListener('change',()=>{selected=Number($('selected').value);editFields();drawEditor();});
  $('apply').addEventListener('click',()=>{const x=Number($('editx').value),y=Number($('edity').value);if(!Number.isFinite(x)||!Number.isFinite(y))return;setPoint(selected,x,y);requestBuild();});
  $('editor').addEventListener('pointerdown',e=>{const h=e.target.closest('[data-index]');if(!h)return;selected=Number(h.dataset.index);drag={pointer:e.pointerId};$('editor').setPointerCapture(e.pointerId);dirty();editFields();e.preventDefault();});
  $('editor').addEventListener('pointermove',e=>{if(!drag||drag.pointer!==e.pointerId)return;const p=editorXY(e);setPoint(selected,...p);});
  const endDrag=()=>{if(drag){drag=null;requestBuild();}};$('editor').addEventListener('pointerup',endDrag);$('editor').addEventListener('pointercancel',endDrag);
  $('editor').addEventListener('keydown',e=>{const h=e.target.closest('[data-index]');if(!h||!['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.key))return;e.preventDefault();const i=Number(h.dataset.index),p=active()[i],a=e.shiftKey?2.5:.25;setPoint(i,p[0]+(e.key==='ArrowRight'?a:e.key==='ArrowLeft'?-a:0),p[1]+(e.key==='ArrowUp'?a:e.key==='ArrowDown'?-a:0));const next=$('editor').querySelector('circle[data-index="'+i+'"]');if(next)next.focus();requestBuild();});
  $('preset').addEventListener('change',()=>preset($('preset').value));$('reset').addEventListener('click',()=>{$('preset').value='default';preset('default');});$('time').addEventListener('input',()=>{pause();draw();});
  $('play').addEventListener('click',()=>{if(playing){pause();return;}if(Number($('time').value)===64)$('time').value=0;playing=true;$('play').textContent='Pause';last=0;raf=requestAnimationFrame(tick);});
  $('export').addEventListener('click',()=>{const payload={format:'shape-lab-experiment-v1',raw_source_mm:rawX,raw_target_mm:rawY,controls:{...opts(),support_ratio:Number($('support').value),count:rawX.length},time:Number($('time').value)/64,computed:result?{paired_RMS:C.rms(result.x,result.y),unit:result.unit,flow_endpoint_RMS:result.endpoint,naive_endpoint_RMS:result.naiveEndpoint,steps:result.steps,refinement_gap:result.gap,inverse_gap:result.inverse,jacobian_gap:result.jacError,min_sampled_det:result.minAll}:null};const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='shape-experiment.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  preset('default');
 }catch(e){setStatus('The laboratory could not initialize: '+e.message+'. Use the PDF notes and Python companion.','error');}
})();
