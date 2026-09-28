/* One click plays a bounded conceptual sequence, then holds for the learner. */
(() => {
'use strict';
const M=window.CountMath, $=id=>document.getElementById(id);
const colors={success:'#a855f7',failure:'#14b8a6',count:'#eab308',exposure:'#38bdf8',ink:'#f3f5fb',muted:'#a9bad2',line:'#3b4e6b'};
const escape=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const mode=location.pathname.endsWith('classroom.html')?'classroom':'details';
const states=window.LESSON[mode];
let current=0,last=null,simulation=null,run=0;
const attrs=o=>Object.entries(o).map(([k,v])=>`${k}="${escape(v)}"`).join(' ');
function text(key,x,y,value,size=22,color=colors.ink,anchor='middle'){return `<text ${attrs({'data-key':key,x,y,'font-size':size,fill:color,'text-anchor':anchor})} style="fill:${color}">${escape(value)}</text>`;}
function rect(key,x,y,w,h,fill,stroke='none',radius=4,extra={}){return `<rect ${attrs({'data-key':key,x,y,width:w,height:h,fill,stroke,rx:radius,...extra})}/>`;}
function line(key,x1,y1,x2,y2,stroke=colors.line,dash=''){return `<line ${attrs({'data-key':key,x1,y1,x2,y2,stroke,'stroke-width':2,'stroke-dasharray':dash})}/>`;}
function circle(key,x,y,r,fill,label='',stroke='none',opacity=1){const labelColor=[colors.count,colors.exposure,colors.failure,'#22c55e','#f97316'].includes(fill)?'#112236':'#fff';return `<g data-key="${escape(key)}" transform="translate(${x},${y})" opacity="${opacity}"><circle r="${r}" fill="${fill}" stroke="${stroke}" stroke-width="3"/>${label?`<text text-anchor="middle" dominant-baseline="central" font-size="${Math.min(r*1.15,20)}" style="fill:${labelColor};font-weight:650">${escape(label)}</text>`:''}</g>`;}
const num=(v,d=3)=>Number(v).toFixed(d).replace(/0+$/,'').replace(/\.$/,'');
function coin(key,x,y,side,color,r=55){
 return `<g data-key="${key}" transform="translate(${x},${y})"><g data-motion="coin-face"><circle r="${r}" fill="#182b3b" stroke="${color}" stroke-width="5"/><circle r="${r-8}" fill="none" stroke="${color}" stroke-width="1.5" opacity=".5"/><text text-anchor="middle" dominant-baseline="central" font-size="${r*.82}" style="fill:${color};font-weight:650">${side}</text></g></g>`;
}
function dieFace(value,x,y,color){
 const dots={1:[[0,0]],2:[[-18,-18],[18,18]],3:[[-18,-18],[0,0],[18,18]],4:[[-18,-18],[18,-18],[-18,18],[18,18]],5:[[-18,-18],[18,-18],[0,0],[-18,18],[18,18]],6:[[-18,-21],[18,-21],[-18,0],[18,0],[-18,21],[18,21]]};
 return `<g data-key="die-face-${value}" transform="translate(${x},${y})"><rect x="-39" y="-39" width="78" height="78" rx="13" fill="#e9eff5" stroke="${color}" stroke-width="4"/>${dots[value].map(([a,b])=>`<circle cx="${a}" cy="${b}" r="5.5" fill="#172438"/>`).join('')}</g>`;
}
function bernoulli(p){
 const prob=p.p??.5,stage=p.stage??0,experiment=p.experiment??'coin';
 const values=stage>=2||['values','mean','square','variance'].includes(p.focus),success=colors.count,failure=colors.exposure;
 const initial=stage<0||p.focus==='trial';
 if(experiment==='die'){
  const wins=p.successOutcomes??[5,6];let out='';
  if(initial){
   for(let v=1;v<=6;v++)out+=dieFace(v,200+(v-1)*140,175,colors.line);
   return out+text('die-outcomes',550,300,'Six equally likely outcomes',30,colors.ink);
  }
  out+=text('yeslabel',350,45,`Success: ${p.successLabel??'5 or 6'}`,28,success)+text('nolabel',790,45,'Failure: any other face',28,failure);
  let wi=0,fi=0;
  for(let v=1;v<=6;v++){
   const isWin=wins.includes(v),index=isWin?wi++:fi++;
   const x=isWin?280+index*140:720+(index%2)*140,y=isWin?175:130+Math.floor(index/2)*120;
   out+=dieFace(v,x,y,isWin?success:failure);
  }
  if(values)out+=text('yes-value',350,290,'I = 1',34,success)+text('no-value',790,320,'I = 0',34,failure);
  if(stage>=1)out+=text('p',350,370,`p = ${wins.length}/6 = 1/3`,28,success)+text('q',790,370,'q = 4/6 = 2/3',28,failure);
  return out;
 }
 if(initial)return coin('coin-heads',550,175,'H',success,67)+text('trial-label',550,302,'Flip one coin',31,colors.ink);
 let out=coin('coin-heads',335,145,p.successSymbol??'H',success)+coin('coin-tails',765,145,p.failureSymbol??'T',failure);
 out+=text('yeslabel',335,242,`Heads: success`,28,success)+text('nolabel',765,242,'Tails: failure',28,failure);
 if(values)out+=text('yes-value',335,294,'I = 1',32,success)+text('no-value',765,294,'I = 0',32,failure);
 if(stage>=1){out+=text('p',335,values?344:303,`p = ${num(prob)}`,27,success)+text('q',765,values?344:303,`q = ${num(1-prob)}`,27,failure);
  out+=rect('pbar',210,385,680*prob,13,success)+rect('qbar',210+680*prob,385,680*(1-prob),13,failure);
 }
 return out;
}
function sequence(p){
 const n=Math.min(p.displayCount??p.n??5,12),k=p.k??2,stage=p.stage??0;
 const pattern=Array.isArray(p.pattern)?p.pattern:Array.from({length:n},(_,i)=>i<k?1:0);
 const revealed=p.concealed?0:(p.revealCount??p.revealed??n);
 const success=p.experiment==='coin'?colors.count:colors.success,failure=p.experiment==='coin'?colors.exposure:colors.failure;
 const trialName=p.experiment==='coin'?'coin flips':p.experiment==='cereal'?'cereal boxes':'trials';
 let out=text('slots',550,46,p.concealed?(p.populationN?`View the first ${n} positions of ${p.populationN} shuffled objects`:`${k} successes · ${n-k} failures`):`${(p.n??5)>n?`First ${n} of ${p.n}`:p.n??5} ${trialName}`,26);
 for(let i=0;i<n;i++){let x=550+(i-(n-1)/2)*76,v=pattern[i]??0;
 out+=text('index'+i,x,105,`i = ${i+1}`,17,colors.muted);
 const focusSuccess=p.focus==='success'&&v,focusFailure=p.focus==='failure'&&!v,highlight=Array.isArray(p.highlight)&&p.highlight.includes(i);
 out+=circle('trial'+i,x,172,27,i<revealed?(v?success:failure):colors.line,i<revealed?String(v):'?',highlight||focusSuccess||focusFailure?colors.count:'none');
 if(stage>=1&&!p.dependent&&!p.concealed&&!['sum','independence','mean','variance'].includes(p.focus)){const show=p.focus==='success'?!!v:true;out+=text('factor'+i,x,245,i<revealed&&show?(v?'p':'q'):'',26,v?success:failure);}
 if(i<n-1&&stage>=3&&!p.dependent&&!p.concealed)out+=text('times'+i,x+38,244,'×',20,colors.muted);
 }
 if(p.concealed&&p.focus==='position')out+=text('summing',550,328,`Any fixed position: ${p.populationK??k} chances out of ${p.populationN??n}`,27,colors.count);
 else if(!p.concealed&&p.focus==='sum')out+=text('summing',550,328,(p.n??n)>n?`I₁ + ⋯ + I${String(p.n).replace(/\d/g,d=>'₀₁₂₃₄₅₆₇₈₉'[Number(d)])} = X`:`${pattern.slice(0,revealed).join(' + ')}${revealed<n?' + …':''} = ${pattern.slice(0,revealed).reduce((a,b)=>a+b,0)}`,27,colors.count);
 if(p.focus==='pairs'){
  const a=550-(n-1)/2*76,b=a+76;
  out+=`<path data-key="one-pair" d="M${a},212 Q${(a+b)/2},290 ${b},212" fill="none" stroke="${colors.count}" stroke-width="3"/>`;
  out+=text('pair-label',550,345,'Each pair contributes a covariance term',26,colors.count);
 }
 return out;
}
function combos(n,k){const rows=[];function visit(a,start){if(a.length===k){rows.push(a);return;}for(let i=start;i<n;i++)visit([...a,i],i+1);}visit([],0);return rows;}
function combinations(p){
 const n=Math.min(p.n??5,7),k=Math.min(p.k??2,n),rows=combos(n,k),visible=Math.min(rows.length,p.showCount??p.visible??rows.length,21);
 let out=text('choose',550,34,`Choose ${k} success positions among ${n}`,26);
 const cols=rows.length>10?3:2;
 if(p.focus==='ordered'){
  let out=text('choose',550,38,'Choosing positions in order counts each pair twice',27);
  for(let j=0;j<rows.length;j++){
   const x=170+(j%5)*190,y=132+Math.floor(j/5)*150;
   out+=text('ordered'+j,x,y,`(${rows[j].map(v=>v+1).join(', ')})`,28,colors.success);
   out+=text('reverse'+j,x,y+42,`(${rows[j].slice().reverse().map(v=>v+1).join(', ')})`,28,colors.failure);
   out+=text('same'+j,x,y+76,'same two positions',14,colors.muted);
  }
  return out+text('combtotal',550,408,'20 ordered choices ÷ 2 orders per pair = 10 different success-position sets',22,colors.count);
 }
 for(let j=0;j<visible;j++){
  const col=j%cols,row=Math.floor(j/cols),x=cols===3?125+col*350:215+col*500,y=82+row*(cols===3?43:58);
  out+=text('label'+j,x-65,y+5,String(j+1).padStart(2,'0'),18,colors.muted);
  for(let i=0;i<n;i++)out+=circle('comb'+j+'-'+i,x+i*(cols===3?40:50),y,cols===3?15:19,rows[j].includes(i)?colors.success:colors.failure,rows[j].includes(i)?'1':'0',j===(p.highlight??-1)?colors.count:'none');
 }
 out+=text('combtotal',550,397,`${visible} ${visible===1?'arrangement':'arrangements'}${visible<rows.length?' shown':` = ${M.choose(n,k)} choices`}`,25,colors.count);
 return out;
}
function pascal(p){
 const max=Math.min(p.row??p.rows??(p.stage??3)+2,7),r=p.highlightRow??p.targetRow??max,c=p.highlightCol??p.targetCol??Math.floor(r/2);
 let out='';
 for(let i=0;i<=max;i++){
  out+=text('row-name'+i,175,38+i*46,`n = ${i}`,16,colors.muted,'end');
  for(let j=0;j<=i;j++){
   if(i===max&&p.revealCol!==undefined&&j>p.revealCol)continue;
   const x=550+(j-i/2)*95,y=32+i*46,target=i===r&&j===c;
   const exclude=p.focus==='left-parent',include=p.focus==='right-parent';
   const parent=i===r-1&&(exclude?j===c:include?j===c-1:(j===c-1||j===c));
   out+=circle(`pascal-${i}-${j}`,x,y,20,target?colors.count:parent?colors.success:'#1b2b44',target&&(exclude||include)?'?':String(M.choose(i,j)),target?colors.count:'none');
   if(target&&c>0&&c<r){
    if(!exclude)out+=line('parent-left',x-47.5,y-28,x-12,y-20,colors.success);
    if(!include)out+=line('parent-right',x+47.5,y-28,x+12,y-20,colors.success);
   }
  }
 }
 const msg=p.focus==='left-parent'?`Exclude the new position: choose ${c} from ${r-1} → ${M.choose(r-1,c)}`:p.focus==='right-parent'?`Include the new position: choose ${c-1} more from ${r-1} → ${M.choose(r-1,c-1)}`:p.focus==='row-total'?`Row ${max} sums to ${2**max} = 2^${max} binary sequences`:c>0&&c<r?`${M.choose(r-1,c-1)} + ${M.choose(r-1,c)} = ${M.choose(r,c)}   ·   add the two parents`:'Each boundary has one possible choice.';
 out+=text('identity',550,408,msg,22,colors.count);
 return out;
}
function histogram(kind,p,ref=null){
 if(p.unknownParameter){
  const left=165,right=935,bottom=320,width=(right-left)/7;
  let out=line('unknown-axis',left,bottom,right,bottom)+text('unknown-axis-label',550,390,'Number of claims, k',26,colors.muted);
  for(let k=0;k<=6;k++){
   const x=left+(k+.5)*width;out+=text('unknown-k'+k,x,bottom+32,k,24,colors.muted);
   if(k===2||k===4){out+=rect('unknown-bar'+k,x-32,166,64,154,'#26304a',colors.count,5,{'stroke-dasharray':'6 6'});out+=text('unknown-value'+k,x,242,'?',34,colors.count);}
  }
  return out+text('unknown-compare',550,75,'Compare P(X = 2) and P(X = 4)',29,colors.ink);
 }
 const max=p.maxK??(kind==='poisson'?18:Math.min(p.n??10,20)),d=M.distribution(kind,p,max);
 const other=ref?M.distribution(ref.kind,ref.params,max):null;
 const lim=kind==='hypergeom'&&p.n===10?.62:kind==='poisson'||p.lambda===3?.34:p.n===50?.32:Math.max(.3,...d.probabilities)*1.12;
 const left=92,right=1020,top=65,bottom=334,w=(right-left)/(max+1);
 const moments=/mean|variance|moment/.test(p.focus??'')||p.showMoments===true;
 let out=text('prob-label',left,25,simulation?'Probability / relative frequency':'Probability',21,colors.muted,'start');
 if(ref)out+=text('model-parameters',right,25,kind==='hypergeom'?`N = ${p.N} · K = ${p.K} · n = ${p.n}`:`n = ${p.n} · p = ${num(p.p,4)} · np = ${num(p.n*p.p)}`,20,colors.ink,'end');
 for(let j=0;j<=4;j++){let y=bottom-(bottom-top)*j/4;out+=line('grid'+j,left,y,right,y)+text('tick'+j,left-12,y+5,num(lim*j/4,2),15,colors.muted,'end');}
 for(let k=0;k<=max;k++){
  const x=left+(k+.14)*w,v=d.probabilities[k]??0,h=v/lim*(bottom-top);
  let fill=colors.success;
  if(p.cereal){const high=p.region==='miss'||p.highlight==='miss',cutoff=p.cutoff??4;fill=p.region==='none'?colors.failure:(high?k>cutoff:k<=cutoff)?colors.success:colors.failure;}
  else if(p.focus==='tail')fill=(p.tailFrom!==undefined?k>=p.tailFrom:k>(p.cutoff??p.k??4))?colors.count:colors.success;
  else if(p.highlightK!==undefined||p.k!==undefined)fill=k===(p.highlightK??p.k)?colors.count:colors.success;
  out+=rect('bar'+k,x,bottom-h,w*.7,h,fill);
  if(other){const hy=(other.probabilities[k]??0)/lim*(bottom-top);out+=line('ref'+k,x,bottom-hy,x+w*.7,bottom-hy,colors.exposure);}
  if(simulation){const hy=(simulation.frequencies[k]??0)/lim*(bottom-top);out+=circle('empirical'+k,x+w*.35,bottom-hy,4,colors.count);}
  if(max<=20||k%2===0)out+=text('k'+k,x+w*.35,bottom+25,k,16,colors.muted);
 }
 const mx=left+(d.mean+.49)*w;
 if(p.cereal){const cut=left+((p.cutoff??4)+1)*w;out+=line('cutoff',cut,top,cut,bottom,colors.ink,'3 5')+text('cutoff-label',right,48,`Reject if X ≤ ${p.cutoff??4}`,17,colors.muted,'end');}
 if(moments){out+=line('mean',mx,top,mx,bottom,colors.count,'5 5');
  out+=text('mean-label',Math.min(Math.max(mx,200),900),top-12,`mean = ${num(d.mean)}`,21,colors.count);
 }
 out+=text('x-label',550,391,moments?`Count, k   ·   variance = ${num(d.variance)}`:'Count, k',24,colors.muted);
 if(d.overflowProbability>1e-10)out+=text('tail',right,414,`P(X > ${max}) = ${d.overflowProbability.toExponential(2)} (not drawn)`,16,colors.muted,'end');
 return out;
}
function lotp(p){
 const focus=p.focus??'weighted',showSuccess=focus!=='partition',showFailure=['branch-failure','weighted','marginal'].includes(focus),weighted=['weighted','marginal'].includes(focus);
 let out=text('start',95,215,'First draw',24,colors.ink);
 out+=line('branch-s',170,205,365,110,colors.success)+line('branch-f',170,225,365,315,colors.failure);
 out+=circle('first-s',390,105,25,colors.success,'S')+circle('first-f',390,315,25,colors.failure,'F');
 out+=text('first-prob-s',255,122,'4/10',25,colors.success)+text('first-prob-f',255,320,'6/10',25,colors.failure);
 out+=text('first-label-s',495,111,'Success',23,colors.success)+text('first-label-f',495,321,'Failure',23,colors.failure);
 if(showSuccess)out+=text('conditional-s',740,111,'Next S: 3/9',27,colors.success);
 if(showFailure)out+=text('conditional-f',740,321,'Next S: 4/9',27,colors.success);
 if(weighted){out+=line('merge-s',850,115,960,200,colors.count)+line('merge-f',850,290,960,220,colors.count)+text('merged',1000,220,'4/10',29,colors.count);}
 return out;
}
function urn(p){
 if(p.mode==='lotp')return lotp(p);
 const N=p.N??250,K=p.K??50,n=p.n??12,k=p.k??Math.min(n,Math.round(n*K/N)),stage=p.stage??0;
 const showSample=stage>=1&&p.focus!=='population';
 const ds=Math.min(k,p.drawnSuccess??p.selectedSuccess??(showSample?k:0));
 const df=Math.min(n-k,p.drawnFailure??p.selectedFailure??(stage>=2?n-k:0));
 const total=ds+df,cols=N>100?25:Math.min(20,N),count=Math.min(N,400),spacing=N>250?20:N>100?23:29;
 const rad=N>250?6:N>100?8:10,origin=80;
 const skittles=p.experiment==='skittles'||N===250;
 let out=text('population',335,31,`Population: N = ${N}`,26,colors.count);
 out+=text('popcolors',335,67,skittles?`${K} purple · ${N-K} not purple`:`${K} successes · ${N-K} failures`,24,colors.muted);
 if(p.focus!=='population')out+=text('sampletitle',877,31,`Sample: n = ${n}`,26,colors.count);
 for(let i=0;i<count;i++){
  const success=i<K,selected=success?i<ds:(i-K)<df;
  const color=success?colors.success:skittles?['#ef4444','#f97316','#eab308','#22c55e'][(i-K)%4]:colors.failure;
  const originalX=origin+(i%cols)*spacing,originalY=105+Math.floor(i/cols)*spacing;
  const j=success?i:ds+i-K;
  const sampleCols=n>12?10:6,sampleX=(n>12?720:775)+(j%sampleCols)*(n>12?37:40),sampleY=155+Math.floor(j/sampleCols)*75;
  if(selected&&!p.replacement){out+=circle('hole'+i,originalX,originalY,rad,'#15233a','',colors.line,.5);out+=circle('object'+i,sampleX,sampleY,17,color,success?'S':'F',colors.count);}
  else out+=circle('object'+i,originalX,originalY,rad,color,rad>=10?(success?'S':'F'):'',selected?colors.count:'none');
  if(selected&&p.replacement)out+=circle('copy'+i,sampleX,sampleY,17,color,success?'S':'F',colors.count);
 }
 out+=line('divider',700,83,700,347,colors.line);
 if(total)out+=text('remaining',335,384,p.replacement?`${N} remain after replacement`:`${N-total} remain`,26,colors.muted);
 if(showSample&&total)out+=text('drawn',877,333,skittles?`${ds} purple + ${df} not purple`:`${ds} successes + ${df} failures`,23,colors.muted);
 if(showSample&&total)out+=text('samplecount',877,376,`${total} selected`,26,colors.count);
 return out;
}
function rain(p){
 const rate=p.rate??300,area=p.area??1,t=p.seconds??.01,lambda=p.lambda??rate*area*t,stage=p.stage??0;
 const focus=p.focus??'window',withRate=['rate','exposure-window','units','exactly-two','moments','exposure'].includes(focus),withMean=['units','moments','exposure'].includes(focus);
 let out=withRate?text('rate',550,34,`Rate: ${rate} drops / (ft² · second)`,26,colors.exposure):'';
 const x=325,y=75,size=280;
 out+=rect('ground',x,y,size,size,'#13293c',colors.exposure,0);
 if(focus==='cells'){const cols=10,rows=5;for(let i=1;i<cols;i++)out+=line('gridv'+i,x+i*size/cols,y,x+i*size/cols,y+size,'#284357');for(let i=1;i<rows;i++)out+=line('gridh'+i,x,y+i*size/rows,x+size,y+i*size/rows,'#284357');}
 const n=p.count??p.drops??(stage===0?0:stage===1?1:3);
 const locations=[[.18,.25],[.74,.66],[.47,.46],[.81,.15],[.13,.83],[.62,.88]];
 for(let i=0;i<n;i++){const [a,b]=locations[i%locations.length];out+=circle('drop'+i,x+size*a,y+size*b,9,colors.exposure);}
 out+=text('area',465,393,`Area A = ${area} ft²`,24,colors.exposure);
 out+=text('time',845,144,`Time: ${t} seconds`,27,colors.exposure);
 if(withMean)out+=text('lambda',845,224,`Mean count: λ = ${num(lambda)}`,29,colors.exposure);
 if(focus==='exactly-two')out+=text('count',845,264,`Observed count: X = ${n}`,29,colors.count);
 else if(!withMean)out+=text('count',845,264,'Count the drops',28,colors.count);
 return out;
}
function summary(p={}){
 const rows=[['Bernoulli','One success/failure trial'],['Binomial','Independent trials; same p'],['Hypergeometric','Sample without replacement'],['Poisson','Events in a fixed window']];
 let out='';
 rows.forEach((r,i)=>{const x=55+(i%2)*540,y=20+Math.floor(i/2)*193,color=i===3?colors.exposure:colors.success;
  const active=(p.focus??'models')==='models'||['bernoulli','binomial','hypergeometric','poisson'][i]===p.focus;
  out+=rect('card'+i,x,y,500,163,active?'#192b43':'#101b2b',active?color:colors.line,14);
  out+=text('model'+i,x+250,y+58,r[0],30,color)+text('experiment'+i,x+250,y+112,r[1],24,colors.ink);
 });
 return out;
}
function foundations(p){
 const mode=p.mode??'independence',focus=p.focus??'',stage=p.stage??0;
 if(mode==='independence'){
  let out=text('trial-2',600,35,'Second trial',28,colors.ink)+text('first-label',128,212,'First trial',26,colors.ink);
  out+=text('second-success',480,86,'Success',25,colors.success)+text('second-failure',720,86,'Failure',25,colors.failure);
  out+=text('first-success',273,180,'Success',25,colors.success)+text('first-failure',273,310,'Failure',25,colors.failure);
  const learned=/given|learn|row|condition/.test(focus)||stage>=1;
  for(let row=0;row<2;row++)for(let col=0;col<2;col++){
   const x=380+col*240,y=115+row*130,dim=learned&&row===1;
   out+=rect(`cell-${row}-${col}`,x,y,200,110,dim?'#101d30':'#1d304a',learned&&row===0?colors.count:colors.line,10);
   out+=text(`prob-${row}-${col}`,x+100,y+65,learned?(row===0?'1/2':'—'):'1/4',32,dim?colors.line:colors.ink);
  }
  return out;
 }
 if(mode==='dependent'){
  let out=line('x-axis',250,320,850,320)+line('y-axis',550,350,550,75);
  out+=text('x-label',890,325,'X',28,colors.ink)+text('y-label',550,45,'Y',28,colors.ink);
  [-1,0,1].forEach((v,i)=>{const x=315+i*235,y=v===0?320:125,selected=/zero|given/.test(focus)&&v===0;
   out+=text('tick-x'+i,x,361,v,23,colors.muted)+circle('point'+i,x,y,13,selected?colors.count:colors.success);
   out+=text('pair'+i,v===0?x+68:x,y-32,`(${v}, ${v*v})`,27,selected?colors.count:colors.ink);
  });
  out+=text('tick-y',512,132,'1',24,colors.muted);
  if(/zero|given/.test(focus))out+=line('given-zero',550,309,550,160,colors.count,'5 5');
  return out;
 }
 if(mode==='deviations'){
  let out=text('center-a',330,84,'Center X around its mean',27,colors.ink)+text('center-b',780,84,'Center Y around its mean',27,colors.ink);
  out+=line('axis-a',100,238,560,238)+line('axis-b',580,238,1040,238);
  out+=line('mean-a',240,220,240,258,colors.muted)+line('mean-b',800,220,800,258,colors.muted);
  out+=text('mean-a-label',240,300,'E[X]',25,colors.muted)+text('mean-b-label',800,300,'E[Y]',25,colors.muted);
  out+=line('arrow-a',240,220,450,220,colors.success)+circle('value-a',450,238,11,colors.success);
  out+=line('arrow-b',800,220,675,220,colors.failure)+circle('value-b',675,238,11,colors.failure);
  out+=text('dev-a',350,186,'A = X − E[X]',27,colors.success)+text('dev-b',760,186,'B = Y − E[Y]',27,colors.failure);
  return out;
 }
 if(mode==='square'){
  const x=365,y=52,a=220,b=105;
  let out=text('top-a',x+a/2,y-18,'A',28,colors.success)+text('top-b',x+a+b/2,y-18,'B',28,colors.failure);
  out+=text('left-a',x-27,y+a/2+8,'A',28,colors.success)+text('left-b',x-27,y+a+b/2+8,'B',28,colors.failure);
  out+=rect('a-square',x,y,a,a,'#372455',colors.line,0)+text('a-square-label',x+a/2,y+a/2+12,'A²',34,colors.success);
  out+=rect('b-square',x+a,y+a,b,b,'#153f42',colors.line,0)+text('b-square-label',x+a+b/2,y+a+b/2+10,'B²',29,colors.failure);
  out+=rect('cross-ab',x+a,y,b,a,stage>=2?'#514923':'#17283c',stage>=2?colors.count:colors.line,0)+rect('cross-ba',x,y+a,a,b,stage>=2?'#514923':'#17283c',stage>=2?colors.count:colors.line,0);
  if(stage>=2)out+=text('ab-label',x+a+b/2,y+a/2+10,'AB',29,colors.count)+text('ba-label',x+a/2,y+a+b/2+10,'BA',29,colors.count);
  return out;
 }
 if(mode==='copies'){
  if(p.id==='symmetric-dependent'){
   let out=text('symmetric-a',350,60,'A',29,colors.ink)+text('symmetric-b',650,60,'B = A',29,colors.ink)+text('symmetric-product',920,60,'AB',29,colors.count);
   [-1,1].forEach((v,i)=>{const y=160+i*150;out+=circle('sym-a'+i,350,y,42,colors.success,v)+circle('sym-b'+i,650,y,42,colors.success,v)+text('sym-product'+i,920,y+10,'1',32,colors.count)+text('sym-prob'+i,135,y+8,'Chance 1/2',24,colors.muted);});
   return out;
  }
  let out=text('independent-label',310,59,'Independent copies',27,colors.ink)+text('copy-label',810,59,'The same variable twice',27,colors.ink);
  out+=circle('coin-a',230,188,45,colors.success,'X₁')+circle('coin-b',390,188,45,colors.failure,'X₂');
  out+=circle('copy-a',730,188,45,colors.success,'X')+circle('copy-b',890,188,45,colors.success,'X');
  out+=line('copy-link',776,188,844,188,colors.count);
  out+=text('independent-values',310,313,'Outcomes may differ',25,colors.muted)+text('copy-values',810,313,'Outcomes always match',25,colors.count);
  return out;
 }
 return '';
}
function cerealSetup(p={}){
 const prob=p.p??.15,view=p.boxMode??'closed',sample=view==='sample',expected=view==='expectation'||sample;
 const actual=p.actualCount??0,cutoff=p.cutoff??4,mean=50*prob,compare=!!p.compareCutoff;
 // These positions are illustrative integer outcomes, never rounded expectations.
 const prizeOrder=[3,11,27,34,46,5,18,22,39,43],prizes=new Set(prizeOrder.slice(0,actual));
 let out=text('box-count',550,38,sample?'One possible sample of 50 boxes':'50 independent cereal boxes',29,colors.count);
 for(let i=0;i<50;i++){
  const x=56+(i%10)*51,y=78+Math.floor(i/10)*43,win=prizes.has(i);
  const fill=sample?(win?colors.success:colors.failure):'#192b43';
  out+=rect('box'+i,x,y,38,35,fill,sample?'none':colors.line,4)+line('box-top'+i,x+2,y+7,x+36,y+7,sample?'#112236':colors.line);
  out+=text('box-mark'+i,x+19,y+26,sample?(win?'P':'–'):'?',18,sample?(win?'#fff':'#112236'):colors.muted);
  if(!sample&&view!=='closed'){
   out+=rect('box-chance-track'+i,x+3,y+30,32,3,colors.line,'none',1);
   out+=rect('box-chance'+i,x+3,y+30,32*prob,3,colors.success,'none',1);
  }
 }
 if(view==='closed')return out+text('cereal-setup-label',805,147,'Prize or no prize?',30,colors.ink)+text('cereal-setup-count',805,202,'X counts the prizes',25,colors.muted);
 if(sample){
  out+=text('cereal-context',805,102,'An illustrative outcome',23,colors.muted);
  out+=text('cereal-observed',805,151,`${actual} prizes`,42,colors.success);
  out+=text('cereal-expectation',805,204,`Expected: 50 × ${num(prob,2)} = ${num(mean,1)}`,25,colors.count);
  out+=text('cereal-true-rate',805,238,`True prize chance: ${num(100*prob,0)}% per box`,21,colors.muted);
  out+=text('cereal-decision',805,282,actual<=cutoff?`${actual} ≤ ${cutoff}: reject the claim`:`${actual} > ${cutoff}: do not reject`,25,colors.ink);
 }else{
  out+=text('cereal-context',805,102,'Each unopened box',23,colors.muted);
  out+=text('cereal-probability',805,148,`${num(100*prob,0)}% chance of a prize`,30,colors.success);
  out+=text('cereal-chance-label',805,175,'Strips show chances, not partial prizes.',15,colors.muted);
  if(expected){
   out+=text('cereal-expectation',805,220,`50 × ${num(prob,2)} = ${num(mean,1)}`,32,colors.count);
   out+=text('cereal-average-label',805,253,'Expected prizes across repeated samples',18,colors.muted);
   if(compare)out+=text('cereal-decision',805,282,`Reject when X ≤ ${cutoff}`,25,colors.ink);
  }
 }
 if(expected){
  const x=v=>70+80*v;
  out+=line('cereal-count-axis',x(0),370,x(12),370,colors.line);
  out+=text('cereal-axis-caption',70,347,'Prize count',17,colors.muted,'start');
  out+=text('cereal-axis-extent',1030,347,'0–12 shown; X can be 0–50',16,colors.muted,'end');
  for(let count=0;count<=12;count+=2)out+=line('cereal-count-tick'+count,x(count),366,x(count),376,colors.line)+(compare&&count===cutoff?'':text('cereal-count-value'+count,x(count),395,String(count),17,colors.muted));
  out+=`<g data-key="cereal-mean-marker" transform="translate(${x(mean)},327)"><line x1="0" y1="0" x2="0" y2="43" stroke="${colors.count}" stroke-width="3"/><circle r="5" fill="${colors.count}"/>`+text('cereal-mean-label',0,-10,`Mean ${num(mean,1)}`,21,colors.count)+`</g>`;
  if(compare)out+=`<g data-key="cereal-cutoff-marker" transform="translate(${x(cutoff)},370)"><line x1="0" y1="-23" x2="0" y2="12" stroke="${colors.ink}" stroke-width="3"/><circle r="4" fill="${colors.ink}"/>`+text('cereal-cutoff-label',0,35,`Cutoff ${cutoff}`,18,colors.ink)+`</g>`;
 }
 return out;
}
function draw(s){const p=s.params??{};switch(s.visual){
 case'foundations':return foundations({...p,id:s.id});
 case'bernoulli':return bernoulli(p);
 case'sequence':return sequence({...p,dependent:p.dependent||/hypergeometric|marginal|variance-(covariances|pair-count)/.test(s.id)});
 case'combinations':return combinations(p);
 case'pascal':return pascal(p);
 case'cereal':return p.view==='boxes'||p.stage<0?cerealSetup(p):histogram('binomial',{n:50,p:.05,...p,cereal:true,maxK:20});
 case'binomial':return histogram('binomial',{n:5,p:.5,...p});
 case'urn':case'hypergeom':return urn(p);
 case'hyperlimit':return histogram('hypergeom',{N:40,K:20,n:10,...p},{kind:'binomial',params:{n:p.n??10,p:(p.K??20)/(p.N??40)}});
 case'rain':return rain(p);
 case'poisson':return histogram('poisson',{lambda:3,...p,maxK:18});
 case'poissonlimit':{const n=p.n??50,l=p.lambda??3;return histogram('binomial',{...p,n,p:l/n,lambda:l,maxK:18},{kind:'poisson',params:{lambda:l}});}
 case'summary':return summary(p);default:return sequence(p);
}}
// Patch the held picture in place. Unchanged objects keep their DOM identity and
// position; a click never fades the whole board or replays unchanged labels.
function syncNode(target,source){
 for(const a of [...target.attributes])if(!source.hasAttribute(a.name))target.removeAttribute(a.name);
 for(const a of [...source.attributes])if(target.getAttribute(a.name)!==a.value)target.setAttribute(a.name,a.value);
 if(!source.children.length){if(target.textContent!==source.textContent)target.textContent=source.textContent;return;}
 for(let i=0;i<source.childNodes.length;i++){
  const fresh=source.childNodes[i],held=target.childNodes[i];
  if(!held){target.appendChild(fresh.cloneNode(true));continue;}
  if(held.nodeType!==fresh.nodeType||held.nodeName!==fresh.nodeName)target.replaceChild(fresh.cloneNode(true),held);
  else if(fresh.nodeType===1)syncNode(held,fresh);
  else if(held.textContent!==fresh.textContent)held.textContent=fresh.textContent;
 }
 while(target.childNodes.length>source.childNodes.length)target.lastChild.remove();
}
function picture(s,replay=false){
 const svg=$('picture'),family=v=>['urn','hypergeom'].includes(v)?'urn':v;
 svg.getAnimations({subtree:true}).forEach(a=>a.cancel());
 svg.querySelectorAll('[data-transient]').forEach(e=>e.remove());
 const old=new Map([...svg.children].map(e=>[e.dataset.key||e.id,{el:e,box:e.getBoundingClientRect(),fill:e.getAttribute('fill')??e.querySelector('circle,rect')?.getAttribute('fill')} ]));
 const draft=document.createElementNS('http://www.w3.org/2000/svg','svg');
 draft.innerHTML=`<title id="visual-title">${escape(s.title)}</title><desc id="visual-desc">${escape(s.body)}</desc>`+draw(s);
 const retained=new Set(),changes=[];
 for(const fresh of [...draft.children]){
  const key=fresh.dataset.key||fresh.id,previous=old.get(key);
  let node;
  if(previous&&previous.el.tagName===fresh.tagName){node=previous.el;syncNode(node,fresh);retained.add(node);changes.push({node,previous});}
  else{node=fresh;changes.push({node,previous:null});}
  svg.appendChild(node);
 }
 for(const {el} of old.values())if(!retained.has(el)&&el.parentElement===svg)el.remove();
 if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
 const settledBoxes=new Map(changes.map(({node})=>[node,node.getBoundingClientRect()]));
 const same=family(last?.visual)===family(s.visual),coinTrial=s.visual==='bernoulli'&&(s.params?.experiment??'coin')==='coin';
 const dieSort=s.visual==='bernoulli'&&s.params?.experiment==='die'&&s.params?.stage===0&&last?.params?.stage===-1;
 for(const {node,previous} of changes){
  if(node.tagName==='title'||node.tagName==='desc')continue;
  const key=node.dataset.key??'';
  if(!previous){
   if(coinTrial&&key==='coin-tails'){
    const from=old.get('coin-heads')?.box,b=settledBoxes.get(node),dx=from?from.left+from.width/2-b.left-b.width/2:-215;
    node.animate([{transform:`translate(${dx}px,0)`,opacity:0},{offset:.25,opacity:1},{transform:'translate(0,0)',opacity:1}],{duration:760,delay:120,easing:'cubic-bezier(.2,.7,.2,1)',composite:'add',fill:'backwards'});
   }else{
    const face=/^die-face-/.test(key),delay=face?Number(key.slice(-1))*45:node.tagName==='text'&&!same?120:0;
    node.animate([{opacity:0},{opacity:1}],{duration:face?400:320,delay,fill:'backwards'});
   }
   continue;
  }
  // Retain labels and shapes in place; move only the objects being operated on.
  if(node.tagName==='text')continue;
  const b=settledBoxes.get(node),dx=previous.box.left-b.left,dy=previous.box.top-b.top;
  if(node.tagName==='rect'&&key.startsWith('bar')&&b.height>0&&Math.abs(previous.box.height-b.height)>1){
   node.style.transformBox='fill-box';node.style.transformOrigin='center bottom';
   node.animate([{transform:`scaleY(${previous.box.height/b.height})`},{transform:'scaleY(1)'}],{duration:750,easing:'cubic-bezier(.22,.7,.2,1)',composite:'add'});
  }else if(Math.abs(dx)>1||Math.abs(dy)>1){
   const delay=dieSort?Number(key.slice(-1))*30:0;
   node.animate([{transform:`translate(${dx}px,${dy}px)`},{transform:'translate(0,0)'}],{duration:dieSort?850:700,delay,easing:'cubic-bezier(.22,.7,.2,1)',composite:'add',fill:'backwards'});
  }
  const painted=node.hasAttribute('fill')?node:node.querySelector('circle,rect'),fill=painted?.getAttribute('fill');
  if(fill&&previous.fill!==fill)painted.animate([{fill:previous.fill??'transparent'},{fill}],{duration:450});
 }
 if(coinTrial&&(s.params?.stage<0||(s.params?.stage===0&&last?.params?.stage<0)||replay)){
  for(const [i,face] of [...svg.querySelectorAll('[data-motion="coin-face"]')].entries()){
   face.style.transformBox='fill-box';face.style.transformOrigin='center';
   face.animate([{transform:'scaleX(1) rotate(-8deg)'},{offset:.25,transform:'scaleX(.06) rotate(0deg)'},{offset:.5,transform:'scaleX(1) rotate(5deg)'},{offset:.75,transform:'scaleX(.06) rotate(0deg)'},{transform:'scaleX(1) rotate(0deg)'}],{duration:820,delay:i*120,easing:'ease-in-out'});
  }
 }
 if(s.visual==='pascal'&&s.params?.focus==='sum'){
  const r=s.params.highlightRow,c=s.params.highlightCol,x=550+(c-r/2)*95,y=32+r*46;
  const target=svg.querySelector(`[data-key="pascal-${r}-${c}"] text`);
  if(target)target.animate([{opacity:0},{opacity:1}],{duration:180,delay:800,fill:'both'});
  [[c-1,-47.5,0],[c,47.5,420]].forEach(([j,dx,delay])=>{
   const el=document.createElementNS('http://www.w3.org/2000/svg','text');
   el.dataset.transient='parent';el.setAttribute('x',x+dx);el.setAttribute('y',y-46);el.setAttribute('text-anchor','middle');el.setAttribute('dominant-baseline','central');el.setAttribute('font-size','26');el.style.fill=colors.success;el.textContent=M.choose(r-1,j);svg.appendChild(el);
   const a=el.animate([{transform:'translate(0px,0px)',opacity:0},{offset:.1,transform:'translate(0px,0px)',opacity:1},{offset:.9,transform:`translate(${-dx}px,46px)`,opacity:1},{transform:`translate(${-dx}px,46px)`,opacity:0}],{duration:380,delay,fill:'both',easing:'ease-in-out'});a.onfinish=()=>el.remove();
  });
 }
}
function equation(s){
 const host=$('equation'),source=s.eq||'';
 if(host.dataset.source===source)return;
 host.getAnimations({subtree:true}).forEach(a=>a.cancel());
 const leaves=el=>[...el.querySelectorAll('.katex-html span')].filter(n=>!n.children.length&&n.textContent.trim());
 const old=leaves(host).map(n=>({text:n.textContent,box:n.getBoundingClientRect(),used:false}));
 host.dataset.source=source;host.classList.toggle('is-empty',!source);
 if(!source){host.replaceChildren();return;}
 try{katex.render(source,host,{displayMode:true,throwOnError:true,strict:'ignore',trust:false,macros:{'\\E':'\\mathbb{E}','\\Var':'\\operatorname{Var}','\\Cov':'\\operatorname{Cov}','\\Prob':'\\mathbb{P}','\\Bin':'\\operatorname{Bin}','\\Bernoulli':'\\operatorname{Bernoulli}'}});}
 catch(e){host.textContent=source;console.error('Equation '+s.id+': '+e.message);return;}
 if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
 // Carry shared terms to their next positions. New terms enter after the picture
 // begins to move; never dissolve one complete formula over another formula.
 const glyphs=leaves(host);
 // Relative offsets also move inline KaTeX glyphs; CSS transforms do not.
 // Batch geometry reads before writing animations to avoid a layout per glyph.
 glyphs.forEach(node=>{node.style.position='relative';});
 const positions=glyphs.map(node=>({node,box:node.getBoundingClientRect()}));
 for(const {node,box:b} of positions){
  const previous=old.filter(x=>!x.used&&x.text===node.textContent).sort((a,c)=>Math.abs(a.box.left-b.left)-Math.abs(c.box.left-b.left))[0];
  if(previous){previous.used=true;const dx=previous.box.left-b.left,dy=previous.box.top-b.top;
   if(Math.abs(dx)>1||Math.abs(dy)>1)node.animate([{left:`${dx}px`,top:`${dy}px`},{left:'0px',top:'0px'}],{duration:680,easing:'cubic-bezier(.2,.7,.2,1)'});
  }else node.animate([{opacity:0,top:'5px'},{opacity:1,top:'0px'}],{duration:430,delay:old.length?250:390,fill:'backwards'});
 }
}
function simSpec(s){let p=s.params??{};if(s.visual==='hyperlimit')return {kind:'hypergeom',params:{N:40,K:20,n:10,...p,maxK:p.n??10}};
 if(s.visual==='poissonlimit')return {kind:'binomial',params:{n:p.n??50,p:(p.lambda??3)/(p.n??50),maxK:18}};
 if(s.visual==='poisson')return {kind:'poisson',params:{lambda:p.lambda??3,maxK:18}};return null;}
const beats=(window.LESSON.beats?.[mode]||states.map(s=>({id:s.id,title:s.title,section:s.section,frames:[s.id],intervals:[0]})))
 .map(b=>({...b,indices:b.frames.map(id=>states.findIndex(s=>s.id===id))}));
const frameBeat=new Map();beats.forEach((b,i)=>b.indices.forEach(j=>frameBeat.set(j,i)));
let beatIndex=0,playing=false,paused=false,timer=null,timerDue=0,timerRemaining=0,timerAction=null,generation=0,frameCursor=0;
function snapshot(){return {beatIndex,beatCount:beats.length,playing,paused,frameCursor,beatId:beats[beatIndex].id};}
function controls(){
 const beat=beats[beatIndex],unfinished=current!==beat.indices.at(-1);
 $('counter').textContent=`${beatIndex+1} / ${beats.length}`;$('jump').value=beatIndex;
 $('previous').disabled=beatIndex===0&&!playing;
 $('next').disabled=beatIndex===beats.length-1&&!unfinished&&!playing;
 $('next').textContent=playing?'Finish →':unfinished?'Play →':'Next →';
 $('next').setAttribute('aria-label',playing?'Finish this animation':unfinished?'Play this explanation':'Next explanation');
 if($('pause')){$('pause').disabled=!playing;$('pause').textContent=paused?'Continue':'Pause';$('pause').setAttribute('aria-label',paused?'Continue this animation':'Pause this animation');}
 if($('playback-status'))$('playback-status').textContent=paused?'Paused':playing?'Playing sequence':'Ready';
 $('sample').disabled=playing;$('clear-samples').disabled=playing;
 window.lessonState={mode,index:current,id:states[current].id,count:states.length,visual:states[current].visual,...snapshot()};
}
// Match semantic content, not slide numbers: the two versions use different orders.
const switchStorageKey='counting-models.version-switch.v1';
let arrivalSwitch=null;
try{arrivalSwitch=JSON.parse(sessionStorage.getItem(switchStorageKey)||'null');}catch{}
function correspondingFrame(source,targetMode){
 const target=window.LESSON[targetMode],byId=id=>target.find(s=>s.id===id);
 if(byId(source.id))return source.id;
 if(source.visual==='poissonlimit'){
  const sameTopic=target.filter(s=>s.visual==='poissonlimit'&&s.anchor===source.anchor);
  const sameSize=(sameTopic.length?sameTopic:target).find(s=>s.visual==='poissonlimit'&&s.params.n===source.params.n);
  if(sameSize)return sameSize.id;
 }
 if(targetMode==='classroom'){
  if(source.visual==='pascal')return 'binomial-theorem';
  if(source.anchor==='poisson-moments')return 'poisson-moments';
  if(source.anchor==='hypergeometric-moments'&&source.id.startsWith('variance-'))return 'hypergeometric-variance';
  if(source.visual==='hyperlimit')return 'hyperlimit-large';
  if(source.id==='poisson-normalization')return 'poisson-pmf';
  if(source.id.startsWith('cereal-cutoff-'))return 'cereal-two-errors';
 }
 const canonical=window.LESSON.details,origin=canonical.findIndex(s=>s.id===source.id);
 let candidates=target.filter(s=>s.anchor===source.anchor);
 if(!candidates.length)candidates=target.filter(s=>s.section===source.section);
 if(!candidates.length)candidates=target;
 const sameVisual=candidates.filter(s=>s.visual===source.visual);
 if(sameVisual.length)candidates=sameVisual;
 return candidates.reduce((best,s)=>{
  const distance=id=>{const i=canonical.findIndex(f=>f.id===id);return i<0||origin<0?Infinity:Math.abs(i-origin);};
  return distance(s.id)<distance(best.id)?s:best;
 }).id;
}
function updateVersionLinks(source){
 for(const [targetMode,id,file] of [['classroom','class-link','classroom.html'],['details','detail-link','detailed.html']]){
  let targetId=targetMode===mode?source.id:correspondingFrame(source,targetMode);
  // An immediate round trip restores a detailed substep that has no exact match.
  if(targetMode!==mode&&arrivalSwitch?.to===mode&&arrivalSwitch.toId===source.id&&arrivalSwitch.from===targetMode&&window.LESSON[targetMode].some(s=>s.id===arrivalSwitch.fromId))targetId=arrivalSwitch.fromId;
  const link=$(id);link.href=file+'#'+encodeURIComponent(targetId);link.dataset.stateId=targetId;
  if(targetMode===mode){link.setAttribute('aria-current','page');link.title='Current version';}
  else{link.removeAttribute('aria-current');link.title='Continue at the corresponding explanation';}
 }
}
function paint(i,replay=false){
 current=Math.max(0,Math.min(states.length-1,i));const s=states[current],beat=beats[frameBeat.get(current)??beatIndex];
 if(!replay)simulation=null;
 $('title').textContent=beat?.title??s.title;$('section').textContent=s.section;$('explanation').textContent=beat?.caption??s.body;
 const noteSteps=[...new Map((beat?.indices??[current]).map(j=>{const f=states[j];return [(f.notes??f.body),`${f.title}\n${f.notes??f.body}`];})).values()];
 $('speaker-text').textContent=noteSteps.join('\n\n');
 $('version').textContent=mode==='classroom'?'Class & test review':'Detailed explanations';
 const legend=document.querySelector('.legend'),p=s.params??{};
 let key='';
 if(s.visual==='cereal'){
  const cut=p.cutoff??4,region=p.region;
  if(p.view==='boxes'){
   if(p.boxMode!=='closed')key=`<span class="success">Purple: ${p.boxMode==='sample'?'observed prizes':'prize chance in each box'}</span>${['expectation','sample'].includes(p.boxMode)?'<span class="count">Gold: expected count</span>':''}${p.compareCutoff?'<span>White: decision cutoff</span>':''}`;
  }else key=p.stage<0?'':region==='none'?'<span class="failure">■ Binomial probabilities</span>':`<span class="success">■ Error event: X ${region==='miss'?'>':'≤'} ${cut}</span><span class="failure">■ Other counts</span>`;
 }else if(['binomial','hyperlimit','poissonlimit','poisson'].includes(s.visual)){
  const law=s.visual==='hyperlimit'?'Hypergeometric':s.visual==='poisson'?'Poisson':'Binomial';
  key=`<span class="success">■ ${law} probabilities</span>${p.k!==undefined||p.highlightK!==undefined?'<span class="count">■ Selected count</span>':''}${s.visual.endsWith('limit')?`<span class="exposure">— ${s.visual==='hyperlimit'?'Binomial':'Poisson'} comparison</span>`:''}`;
 }else if(s.visual==='rain')key='<span class="exposure">● Raindrop</span><span class="count">X: number of drops</span>';
 else if(s.visual==='pascal')key='<span class="success">Parents</span><span class="count">New entry</span>';
 else if(['urn','hypergeom'].includes(s.visual)&&p.mode!=='lotp')key=(p.experiment==='skittles'||p.N===250)?'<span class="success">● Purple: success</span><span class="failure">● Not purple: failure</span>':'<span class="success">● S: success</span><span class="failure">● F: failure</span>';
 else if(p.experiment==='skittles')key='<span class="success">● Purple: success</span><span class="failure">● Any other color: failure</span>';
 else if(p.experiment==='cereal')key='<span class="success">● Prize: success</span><span class="failure">● No prize: failure</span>';
 else if(p.experiment==='coin')key='<span class="count">● H: heads (success)</span><span class="exposure">● T: tails (failure)</span>';
 else if(p.experiment==='die')key='<span class="count">● 5 or 6: success</span><span class="exposure">● 1, 2, 3, or 4: failure</span>';
 else if(s.visual!=='summary'&&s.visual!=='foundations'&&p.stage!==-1)key='<span class="success">● S: success</span><span class="failure">● F: failure</span>';
 if(p.view!=='boxes'&&/mean|variance|moment/.test(p.focus??'')&&['cereal','binomial','poisson','hyperlimit','poissonlimit'].includes(s.visual))key+='<span class="count">⋮ Expected count</span>';
 if(legend.innerHTML!==key)legend.innerHTML=key;
 updateVersionLinks(s);
 const note=window.NOTES_MAP?.[s.anchor];
 $('notes-link').href='https://zanahmad.com/files/independence-bernoulli-binomial-2026-09-28.pdf'+(note?'#page='+note.page:'');
 $('notes-link').textContent=note?`Notes §${note.section}: ${note.title} ↗`:'Read the lecture notes ↗';
 $('simulation').hidden=!simSpec(s)||!(p.focus==='simulation'||p.allowSimulation===true);$('sample-caption').textContent='Exact laws are shown first. Simulation estimates them.';
 picture(s,replay);equation(s);last=s;
 const hash='#'+encodeURIComponent(s.id);history.replaceState(null,'',hash);$('copy-link').href=hash;
 controls();
}
function cancelSequence(){
 generation++;clearTimeout(timer);timer=null;timerAction=null;playing=false;paused=false;
 document.querySelectorAll('#lesson').forEach(el=>el.getAnimations({subtree:true}).forEach(a=>a.cancel()));
}
function show(i,replay=false){cancelSequence();const target=Math.max(0,Math.min(states.length-1,i));beatIndex=frameBeat.get(target)??0;frameCursor=beats[beatIndex].indices.indexOf(target);paint(target,replay);}
function schedule(action,delay){
 clearTimeout(timer);timerAction=action;timerRemaining=delay;timerDue=performance.now()+delay;const token=generation;
 timer=setTimeout(()=>{timer=null;if(token===generation&&!paused)action();},delay);
}
function runFrame(cursor){
 const beat=beats[beatIndex];frameCursor=cursor;paint(beat.indices[cursor]);
 const final=cursor===beat.indices.length-1;
 schedule(()=>{if(final){playing=false;paused=false;timerAction=null;controls();}else runFrame(cursor+1);},final?1100:Math.max(450,beat.intervals?.[cursor]??1500));
}
function playBeat(index,cursor=0){
 cancelSequence();beatIndex=Math.max(0,Math.min(beats.length-1,index));$('speaker').open=false;
 if(matchMedia('(prefers-reduced-motion: reduce)').matches){show(beats[beatIndex].indices.at(-1));return;}
 playing=true;runFrame(Math.min(cursor,beats[beatIndex].indices.length-1));
}
function finish(){const end=beats[beatIndex].indices.at(-1);show(end);}
function advance(d){
 $('speaker').open=false;
 if(d<0){show(beats[Math.max(0,beatIndex-1)].indices.at(-1));return;}
 if(playing){finish();return;}
 const beat=beats[beatIndex],at=beat.indices.indexOf(current);
 if(at>=0&&at<beat.indices.length-1)playBeat(beatIndex,at+1);
 else if(beatIndex<beats.length-1)playBeat(beatIndex+1);
}
function togglePause(){
 if(!playing)return;
 if(paused){paused=false;document.querySelector('#lesson').getAnimations({subtree:true}).filter(a=>a.playState==='paused').forEach(a=>a.play());if(timerAction)schedule(timerAction,timerRemaining);}
 else{paused=true;timerRemaining=Math.max(0,timerDue-performance.now());clearTimeout(timer);timer=null;document.querySelector('#lesson').getAnimations({subtree:true}).forEach(a=>a.pause());}
 controls();
}
$('jump').innerHTML=beats.map((b,i)=>`<option value="${i}">${i+1}. ${escape(b.section)} · ${escape(b.title)}</option>`).join('');
$('jump').addEventListener('change',e=>playBeat(Number(e.target.value)));
$('next').onclick=()=>advance(1);$('previous').onclick=()=>advance(-1);$('replay').onclick=()=>playBeat(beatIndex);
if($('pause'))$('pause').onclick=togglePause;
for(const [targetMode,id] of [['classroom','class-link'],['details','detail-link']])$(id).addEventListener('click',()=>{
 if(targetMode===mode)return;
 try{sessionStorage.setItem(switchStorageKey,JSON.stringify({from:mode,fromId:states[current].id,to:targetMode,toId:$(id).dataset.stateId}));}catch{}
});
$('fullscreen').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();
document.addEventListener('keydown',e=>{
 if(e.key===' '&&playing&&!/INPUT|SELECT|TEXTAREA|SUMMARY/.test(e.target.tagName)){e.preventDefault();togglePause();return;}
 if(/INPUT|SELECT|TEXTAREA|BUTTON|SUMMARY/.test(e.target.tagName))return;
 if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();advance(1);}
 if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();advance(-1);}
 if(e.key==='Home'){e.preventDefault();show(0);}if(e.key==='End'){e.preventDefault();show(states.length-1);}
 if(e.key.toLowerCase()==='f')$('fullscreen').click();if(e.key.toLowerCase()==='r')$('replay').click();
});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&playing&&!paused)togglePause();});
$('sample').onclick=()=>{const spec=simSpec(states[current]);if(!spec||playing)return;const seed=20260930+run++;simulation=M.simulate(spec.kind,spec.params,2000,seed);picture(states[current]);$('sample-caption').textContent=`2,000 samples · seed ${seed} · sample mean ${num(simulation.mean)} · sample variance ${num(simulation.variance)}${simulation.overflowCount?` · ${simulation.overflowCount} above displayed range`:''}`;};
$('clear-samples').onclick=()=>{simulation=null;picture(states[current]);$('sample-caption').textContent='Exact laws are shown first. Simulation estimates them.';};
window.addEventListener('hashchange',()=>{const id=decodeURIComponent(location.hash.slice(1)),i=states.findIndex(s=>s.id===id),b=beats.findIndex(b=>b.id===id);if(i>=0)show(i);else if(b>=0)playBeat(b);});
const initialId=decodeURIComponent(location.hash.slice(1)),initial=states.findIndex(s=>s.id===initialId),initialBeat=beats.findIndex(b=>b.id===initialId);
show(initial>=0?initial:initialBeat>=0?beats[initialBeat].indices[0]:0);
// Flat frame access remains available for legacy links and exhaustive math/layout
// checks. Student navigation uses the much shorter conceptual sequence list.
window.Deck={states,beats,show,advance,playBeat,finish,togglePause,correspondingFrame,getPlayback:snapshot,getSimulation:()=>simulation};
})();
