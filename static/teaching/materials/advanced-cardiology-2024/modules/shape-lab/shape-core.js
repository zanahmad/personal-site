/* Original planar curve teaching core. Same equations as companion.py. No dependencies. */
'use strict';
const ShapeCore = (() => {
  const norm = p => Math.hypot(p[0],p[1]);
  function points(p){if(!Array.isArray(p)||p.length<3||p.length>4096||p.some(q=>!Array.isArray(q)||q.length!==2||q.some(v=>!Number.isFinite(v)||Math.abs(v)>1e4)))throw Error('Supply 3–4096 finite 2D points.');return p;}
  function rms(x,y){points(x);points(y);if(x.length!==y.length)throw Error('Paired arrays need equal lengths.');return Math.sqrt(x.reduce((s,p,i)=>s+(p[0]-y[i][0])**2+(p[1]-y[i][1])**2,0)/x.length);}
  function radius(x){return Math.sqrt(x.reduce((s,p)=>s+p[0]**2+p[1]**2,0)/x.length);}
  function resample(p,n){points(p);if(!Number.isInteger(n)||n<8||n>32)throw Error('Choose 8–32 landmarks.');const lengths=p.map((q,i)=>norm([p[(i+1)%p.length][0]-q[0],p[(i+1)%p.length][1]-q[1]]));if(Math.min(...lengths)<1e-10)throw Error('Adjacent vertices must be distinct.');const s=[0];for(const d of lengths)s.push(s.at(-1)+d);let j=0;return Array.from({length:n},(_,i)=>{const q=i*s.at(-1)/n;while(j<p.length-1&&s[j+1]<=q)j++;const a=(q-s[j])/lengths[j],k=(j+1)%p.length;return p[j].map((v,b)=>(1-a)*v+a*p[k][b]);});}
  function prepare(x,y,{center=true,rotate=true,normalize=false,shift=0,reverse=false}={}){
    points(x);points(y);if(x.length!==y.length||!Number.isInteger(shift))throw Error('Use paired arrays and an integer cyclic shift.');const n=x.length;
    x=x.map(p=>p.slice());y=Array.from({length:n},(_,j)=>y[((shift+(reverse?-j:j))%n+n)%n].slice());
    if(center){for(const a of [x,y]){const m=[0,0];for(const p of a){m[0]+=p[0]/n;m[1]+=p[1]/n;}for(const p of a){p[0]-=m[0];p[1]-=m[1];}}}
    const sx=radius(x),sy=radius(y);if(Math.min(sx,sy)<1e-8)throw Error('Both arrays need nonzero spread about the chosen origin.');
    if(normalize){x=x.map(p=>p.map(v=>v/sx));y=y.map(p=>p.map(v=>v/sy));}
    let theta=0,unique=true;if(rotate){let a=0,b=0;for(let i=0;i<n;i++){a+=y[i][0]*x[i][0]+y[i][1]*x[i][1];b+=y[i][0]*x[i][1]-y[i][1]*x[i][0];}unique=Math.hypot(a,b)>1e-12*n*radius(x)*radius(y);theta=unique?Math.atan2(b,a):0;const c=Math.cos(theta),s=Math.sin(theta);y=y.map(p=>[c*p[0]-s*p[1],s*p[0]+c*p[1]]);}
    return {x,y,angle:theta,rotationUnique:unique,unit:normalize?'dimensionless':'mm',sourceRadius:sx,targetRadius:sy};
  }
  const kernel=r=>r>=1?0:(1-r)**4*(4*r+1);
  function solveWithCondition(k,d){
    const n=k.length,a=k.map((row,i)=>[...row,...Array.from({length:n},(_,j)=>i===j?1:0),...d[i]]);
    for(let i=0;i<n;i++){let pivot=i;for(let j=i+1;j<n;j++)if(Math.abs(a[j][i])>Math.abs(a[pivot][i]))pivot=j;
      if(Math.abs(a[pivot][i])<1e-12)throw Error('Singular or ill-conditioned landmark system. Spread points or reduce support radius.');
      [a[i],a[pivot]]=[a[pivot],a[i]];const t=a[i][i];for(let c=0;c<2*n+2;c++)a[i][c]/=t;
      for(let j=0;j<n;j++)if(j!==i){const q=a[j][i];for(let c=0;c<2*n+2;c++)a[j][c]-=q*a[i][c];}}
    const kinf=Math.max(...k.map(row=>row.reduce((s,v)=>s+Math.abs(v),0))),invnorm=Math.max(...a.map(row=>row.slice(n,2*n).reduce((s,v)=>s+Math.abs(v),0)));
    const condition=kinf*invnorm;if(!Number.isFinite(condition)||condition>1e8)throw Error('Interpolation matrix is ill-conditioned; no field was fitted.');
    return {w:a.map(row=>row.slice(2*n)),condition};
  }
  function fit(x,y,ell){
    points(x);points(y);if(x.length!==y.length||x.length>32||!Number.isFinite(ell)||ell<=1e-6||ell>1e4)throw Error('Invalid landmark arrays or support radius.');
    const n=x.length,dist=x.map(p=>x.map(q=>Math.hypot(p[0]-q[0],p[1]-q[1])));
    for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)if(dist[i][j]<Math.max(1e-7,ell*1e-4))throw Error('Source landmarks are coincident or too close; move them apart.');
    const k=dist.map(row=>row.map(v=>kernel(v/ell))),d=x.map((p,i)=>p.map((v,b)=>y[i][b]-v)),s=solveWithCondition(k,d);
    let residual=0;for(let i=0;i<n;i++){const q=[-d[i][0],-d[i][1]];for(let j=0;j<n;j++){q[0]+=k[i][j]*s.w[j][0];q[1]+=k[i][j]*s.w[j][1];}residual=Math.max(residual,norm(q));}
    if(residual>1e-8*Math.max(1,Math.sqrt(d.reduce((v,p)=>v+p[0]**2+p[1]**2,0))))throw Error('Interpolation solve failed its residual check.');
    const speedBound=s.w.reduce((v,p)=>v+norm(p),0),lipschitz=135/(64*ell)*speedBound;
    if(lipschitz>40)throw Error('Edit exceeds the lab stiffness bound. Reduce displacement or support interaction.');
    return {x:x.map(p=>p.slice()),w:s.w,ell,condition:s.condition,residual,speedBound,lipschitz};
  }
  function evaluate(field,zx,zy){let vx=0,vy=0,a=0,b=0,c=0,d=0;const ell=field.ell;
    for(let j=0;j<field.x.length;j++){const dx=zx-field.x[j][0],dy=zy-field.x[j][1],r=Math.hypot(dx,dy)/ell;if(r>=1)continue;
      const h=1-r,k=h**4*(4*r+1),g=-20*h**3/(ell*ell),wx=field.w[j][0],wy=field.w[j][1];vx+=k*wx;vy+=k*wy;a+=wx*g*dx;b+=wx*g*dy;c+=wy*g*dx;d+=wy*g*dy;}
    return [vx,vy,a,b,c,d];
  }
  function rhs(field,s,out){for(let i=0;i<s.length;i+=7){const [u,v,a,b,c,d]=evaluate(field,s[i],s[i+1]);out[i]=u;out[i+1]=v;out[i+2]=a*s[i+2]+b*s[i+4];out[i+3]=a*s[i+3]+b*s[i+5];out[i+4]=c*s[i+2]+d*s[i+4];out[i+5]=c*s[i+3]+d*s[i+5];out[i+6]=a+d;}return out;}
  function integrate(field,z,steps=128,{duration=1,frames=0}={}){
    points(z);if(!Number.isInteger(steps)||steps<1||steps>8192||!Number.isFinite(duration)||Math.abs(duration)>1||frames&&steps%frames)throw Error('Invalid RK4 controls.');
    const s=Float64Array.from(z.flatMap(p=>[...p,1,0,0,1,0])),a=new Float64Array(s.length),b=a.slice(),c=a.slice(),d=a.slice(),tmp=a.slice(),h=duration/steps,history=frames?[s.slice()]:[];
    for(let k=0;k<steps;k++){rhs(field,s,a);for(let i=0;i<s.length;i++)tmp[i]=s[i]+h*a[i]/2;rhs(field,tmp,b);for(let i=0;i<s.length;i++)tmp[i]=s[i]+h*b[i]/2;rhs(field,tmp,c);for(let i=0;i<s.length;i++)tmp[i]=s[i]+h*c[i];rhs(field,tmp,d);for(let i=0;i<s.length;i++)s[i]+=h/6*(a[i]+2*b[i]+2*c[i]+d[i]);if(frames&&(k+1)%(steps/frames)===0)history.push(s.slice());}
    if(s.some(v=>!Number.isFinite(v)))throw Error('Nonfinite RK4 state.');return {state:s,history};
  }
  function statePoints(s){const p=[];for(let i=0;i<s.length;i+=7)p.push([s[i],s[i+1]]);return p;}
  function determinants(s){const a=[];for(let i=0;i<s.length;i+=7)a.push(s[i+2]*s[i+5]-s[i+3]*s[i+4]);return a;}
  function naive(field,z,t){return z.map(p=>{const a=evaluate(field,...p);return [p[0]+t*a[0],p[1]+t*a[1]];});}
  function naiveDet(field,z,t){return z.map(p=>{const a=evaluate(field,...p);return (1+t*a[2])*(1+t*a[5])-t*t*a[3]*a[4];});}
  function maxGap(a,b){let d=0;for(let i=0;i<a.length;i++)d=Math.max(d,Math.hypot(a[i][0]-b[i][0],a[i][1]-b[i][1]));return d;}
  function signedArea(p){return p.reduce((s,q,i)=>s+q[0]*p[(i+1)%p.length][1]-q[1]*p[(i+1)%p.length][0],0)/2;}
  function crossings(p){let count=0;const cross=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
    for(let i=0;i<p.length;i++)for(let j=i+2;j<p.length;j++){if(i===0&&j===p.length-1)continue;const a=p[i],b=p[(i+1)%p.length],c=p[j],d=p[(j+1)%p.length];if(cross(a,b,c)*cross(a,b,d)<-1e-14&&cross(c,d,a)*cross(c,d,b)<-1e-14)count++;}return count;}
  return {points,rms,radius,resample,prepare,kernel,fit,evaluate,integrate,statePoints,determinants,naive,naiveDet,maxGap,signedArea,crossings};
})();
if(typeof module!=='undefined')module.exports=ShapeCore;
