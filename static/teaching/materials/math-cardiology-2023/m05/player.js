(function () {
'use strict';
function nextIndex(data, i, action) {
 const n=data.pages.length, p=data.pages[i], f=data.frames[p.frame-1];
 if(action==='next')return Math.min(n-1,i+1);
 if(action==='prev')return Math.max(0,i-1);
 if(action==='first')return 0;
 if(action==='last')return n-1;
 if(action==='replay')return f.start;
 if(action==='complete')return f.end;
 if(action==='nextTopic')return data.frames[Math.min(data.frames.length-1,p.frame)].start;
 if(action==='prevTopic')return data.frames[Math.max(0,p.frame-2)].start;
 return i;
}
function keyAction(e) {
 if(e.target.closest('select,input,textarea,[contenteditable="true"]')||e.altKey||e.ctrlKey||e.metaKey)return null;
 if((e.key===' '||e.key==='Enter')&&e.target.closest('button,a,summary'))return null;
 const map={ArrowRight:e.shiftKey?'nextTopic':'next',ArrowLeft:e.shiftKey?'prevTopic':'prev',PageDown:'next',PageUp:'prev',' ':'next',Home:'first',End:'last'};
 if(e.key==='Enter'&&e.target.id==='stage')return 'next';
 return map[e.key]||(e.key.toLowerCase()==='f'?'fullscreen':null);
}
function parseHash(data, hash) {
 const params=new URLSearchParams(String(hash||'').replace(/^#/,''));
 if(params.has('frame')) {
  const frame=data.frames.find(f=>f.id===params.get('frame'));
  if(!frame)return 0;
  const value=Number(params.get('step')||1),step=Number.isFinite(value)?Math.trunc(value):1;
  return Math.max(frame.start,Math.min(frame.end,frame.start+step-1));
 }
 const raw=Number(params.get('page')||1),page=Number.isFinite(raw)?Math.trunc(raw):1;
 return Math.max(0,Math.min(data.pages.length-1,page-1));
}
function stateHash(data,index) {
 const page=data.pages[index],frame=data.frames[page.frame-1];
 return frame.id?'#frame='+encodeURIComponent(frame.id)+'&step='+page.step:'#page='+(index+1);
}
function initializePlayer(doc, env) {
 const el=id=>doc.getElementById(id), status=el('viewer-status'), message=el('viewer-message');
 function showStatus(text, failed=false) {
  if(message)message.textContent=text;
  if(status){status.hidden=false;status.dataset.state=failed?'error':'loading';}
 }
 function imageFailed(){showStatus('The slide image could not be displayed. Try another slide, or open the slide PDF or printable handout.',true);}
 try {
  const data=JSON.parse(el('deck-data').textContent);
  if(!Array.isArray(data.pages)||!data.pages.length||!Array.isArray(data.frames)||!data.frames.length)throw new Error('Empty slide data');
  const image=el('page'),stage=el('stage');
  let index=parseHash(data,env.location.hash);
  el('lecture-title').textContent=data.title;
  for(const frame of data.frames){const option=doc.createElement('option');option.value=String(frame.start);option.textContent=frame.frame+'. '+frame.title;el('topics').append(option);}
  image.addEventListener('load',()=>{if(status)status.hidden=true;});
  image.addEventListener('error',imageFailed);
  function draw(){
   const page=data.pages[index],frame=data.frames[page.frame-1];
   const notes=el('section-notes');if(notes&&frame.notes){notes.href=frame.notes.href;notes.textContent='Notes: '+frame.notes.title+' (p. '+frame.notes.page+')';}
   const guide=el('section-guide');if(guide&&frame.notes)guide.href='index.html#section-'+frame.notes.id;
   const resources=el('topic-resources');
   if(resources){resources.replaceChildren();for(const item of frame.modules||[]){const link=doc.createElement('a');link.href=item.href;link.textContent=item.title;resources.append(link);}resources.hidden=!(frame.modules||[]).length;}
   showStatus('Loading slide '+page.frame+' of '+data.frames.length+'.');
   image.alt=page.title+'; step '+page.step+' of '+page.steps;image.src=page.src;
   el('transcript').textContent=page.text;el('topics').value=String(data.frames[page.frame-1].start);
   el('position').textContent='Slide '+page.frame+' / '+data.frames.length+' · Step '+page.step+' / '+page.steps;
   el('prev').disabled=index===0;el('next').disabled=index===data.pages.length-1;
   try{env.history.replaceState(null,'',stateHash(data,index));}catch(e){/* A restricted history API does not prevent presentation. */}
   if(image.complete&&image.naturalWidth>0&&status)status.hidden=true;
  }
  function move(action){index=nextIndex(data,index,action);draw();}
  for(const name of ['next','prev','replay','complete'])el(name).addEventListener('click',()=>move(name));
  el('topics').addEventListener('change',e=>{index=Number(e.target.value);draw();});
  async function full(){try{if(doc.fullscreenElement)await doc.exitFullscreen();else await doc.documentElement.requestFullscreen();}catch(e){el('position').textContent='Full screen unavailable. Use the browser full-screen command.';}}
  el('fullscreen').addEventListener('click',full);
  stage.addEventListener('click',e=>{const rect=stage.getBoundingClientRect();move(e.clientX-rect.left<rect.width*.18?'prev':'next');});
  doc.addEventListener('keydown',e=>{const action=keyAction(e);if(!action)return;e.preventDefault();if(action==='fullscreen')full();else move(action);});
  if(env.addEventListener)env.addEventListener('hashchange',()=>{index=parseHash(data,env.location.hash);draw();});
  for(const name of ['next','prev','replay','complete','fullscreen','topics'])el(name).disabled=false;
  draw();
  return {move,draw};
 } catch(e) {
  showStatus('Interactive navigation could not start. The initial slide is included in this file; use the slide PDF or printable handout for the full presentation.',true);
  return null;
 }
}
if(typeof module!=='undefined'&&module.exports)module.exports={nextIndex,keyAction,parseHash,stateHash,initializePlayer};
if(typeof document!=='undefined')initializePlayer(document,globalThis);
}());
