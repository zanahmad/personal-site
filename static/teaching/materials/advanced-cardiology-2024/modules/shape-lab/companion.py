"""Planar landmarks and compact-support ambient flow. Original teaching code.
Coordinates are mm unless normalize=True, then dimensionless; time is homotopy time.
Run: python companion.py --out results.json. Requires NumPy only.
"""
from pathlib import Path
import argparse
import json
import numpy as np


def points(a):
    a=np.asarray(a,dtype=float)
    if a.ndim!=2 or a.shape[1]!=2 or not 3<=len(a)<=4096 or not np.isfinite(a).all() or np.abs(a).max()>1e4:
        raise ValueError('Supply 3–4096 finite 2D coordinates with magnitude at most 10000.')
    return a


def rms(x,y):
    x,y=points(x),points(y)
    if x.shape!=y.shape: raise ValueError('Paired arrays must have the same shape.')
    return float(np.sqrt(np.mean(np.sum((x-y)**2,axis=1))))


def resample(p,n):
    p=points(p)
    if isinstance(n,bool) or not isinstance(n,(int,np.integer)) or not 8<=n<=32: raise ValueError('Choose 8–32 landmarks.')
    e=np.roll(p,-1,axis=0)-p; d=np.linalg.norm(e,axis=1)
    if np.min(d)<1e-10: raise ValueError('Adjacent vertices must be distinct; omit a duplicate closing endpoint.')
    s=np.r_[0,np.cumsum(d)]; q=np.arange(n)*s[-1]/n; j=np.searchsorted(s,q,side='right')-1
    return p[j]+((q-s[j])/d[j])[:,None]*e[j]


def prepare(x,y,center=True,rotate=True,normalize=False,shift=0,reverse=False):
    x,y=points(x).copy(),points(y).copy()
    if x.shape!=y.shape: raise ValueError('Paired arrays must have the same shape.')
    if isinstance(shift,bool) or not isinstance(shift,(int,np.integer)): raise ValueError('Shift must be an integer.')
    n=len(x); y=y[(shift+(-1 if reverse else 1)*np.arange(n))%n]
    if center: x-=x.mean(axis=0); y-=y.mean(axis=0)
    # Rotation/scale are about the displayed origin; toggles remain independent.
    sx=float(np.sqrt(np.mean(np.sum(x*x,axis=1)))); sy=float(np.sqrt(np.mean(np.sum(y*y,axis=1))))
    if min(sx,sy)<1e-8: raise ValueError('Both arrays require nonzero spread about the selected origin.')
    if normalize: x/=sx; y/=sy
    theta=0.; unique=True
    if rotate:
        a=float(np.sum(y[:,0]*x[:,0]+y[:,1]*x[:,1])); b=float(np.sum(y[:,0]*x[:,1]-y[:,1]*x[:,0]))
        unique=np.hypot(a,b)>1e-12*np.linalg.norm(x)*np.linalg.norm(y)
        theta=float(np.arctan2(b,a)) if unique else 0.
        c,s=np.cos(theta),np.sin(theta); y=y@np.array([[c,s],[-s,c]])
    return x,y,{'angle_radians':theta,'rotation_unique':bool(unique),'unit':'dimensionless' if normalize else 'mm','source_radius':sx,'target_radius':sy}


def kernel(r):
    z=np.maximum(1-np.asarray(r),0.)
    return z**4*(4*np.asarray(r)+1)


class Field:
    """u(z)=sum_j w_j phi(|z-x_j|/ell), interpolating paired displacement.
    No regularization. Coincident/ill-conditioned configurations are rejected.
    """
    def __init__(self,x,y,ell):
        self.x=points(x).copy(); y=points(y)
        if self.x.shape!=y.shape or len(x)>32: raise ValueError('Use equal arrays of at most 32 landmarks.')
        if not np.isfinite(ell) or ell<=1e-6 or ell>1e4: raise ValueError('Support radius must be finite and positive.')
        self.ell=float(ell); d=np.linalg.norm(self.x[:,None]-self.x[None,:],axis=2)
        if np.min(d+np.eye(len(x))*1e9)<max(1e-7,ell*1e-4): raise ValueError('Source landmarks are coincident or too close for a stable fit.')
        k=kernel(d/ell); self.condition=float(np.linalg.cond(k,np.inf))
        if not np.isfinite(self.condition) or self.condition>1e8: raise ValueError('Interpolation matrix is ill-conditioned; spread points or reduce support radius.')
        self.w=np.linalg.solve(k,y-self.x)
        self.residual=float(np.max(np.linalg.norm(k@self.w-(y-self.x),axis=1)))
        if self.residual>1e-8*max(1,float(np.linalg.norm(y-self.x))): raise ValueError('Interpolation solve failed its residual check.')
        self.speed_bound=float(np.sum(np.linalg.norm(self.w,axis=1)))
        self.lipschitz_bound=135/(64*ell)*self.speed_bound
        if self.lipschitz_bound>40: raise ValueError('This edit exceeds the lab stiffness bound; reduce the displacement or support interaction.')

    def evaluate(self,z):
        z=np.asarray(z,dtype=float)
        d=z[:,None,:]-self.x[None,:,:]; r=np.linalg.norm(d,axis=2)/self.ell; h=np.maximum(1-r,0.)
        v=(h**4*(4*r+1))@self.w
        grad=-20*h[:,:,None]**3*d/self.ell**2
        du=np.einsum('ja,mjb->mab',self.w,grad)
        return v,du

    def rhs(self,s):
        v,d=self.evaluate(s[:,:2]); a=s[:,2:6].reshape(-1,2,2)
        return np.column_stack([v,np.einsum('mab,mbc->mac',d,a).reshape(-1,4),np.trace(d,axis1=1,axis2=2)])


def integrate(field,z,steps=128,duration=1.,frames=0):
    z=points(z)
    if isinstance(steps,bool) or not isinstance(steps,(int,np.integer)) or steps<1 or steps>8192: raise ValueError('Choose 1–8192 RK4 steps.')
    if not np.isfinite(duration) or abs(duration)>1: raise ValueError('Duration must lie in [-1,1].')
    if frames and steps%frames: raise ValueError('Steps must be divisible by frame intervals.')
    s=np.column_stack([z,np.tile([1.,0.,0.,1.,0.],(len(z),1))]); h=duration/steps; history=[s.copy()] if frames else []
    for i in range(steps):
        a=field.rhs(s); b=field.rhs(s+h*a/2); c=field.rhs(s+h*b/2); d=field.rhs(s+h*c)
        s+=h/6*(a+2*b+2*c+d)
        if not np.isfinite(s).all(): raise FloatingPointError('Nonfinite RK4 state.')
        if frames and (i+1)%(steps//frames)==0: history.append(s.copy())
    return s,np.array(history) if frames else None


def determinant(s):
    return s[:,2]*s[:,5]-s[:,3]*s[:,4]


def diagnostics(field,z,steps=128):
    coarse,_=integrate(field,z,steps); fine,_=integrate(field,z,2*steps)
    back,_=integrate(field,fine[:,:2],2*steps,duration=-1.)
    j=determinant(fine); expected=np.exp(fine[:,6]); scale=max(1e-12,float(np.sqrt(np.mean(np.sum(z*z,axis=1)))))
    return {'steps':2*steps,'refinement_max_position':float(np.max(np.linalg.norm(coarse[:,:2]-fine[:,:2],axis=1))),
            'inverse_max_position':float(np.max(np.linalg.norm(back[:,:2]-z,axis=1))),
            'minimum_sampled_det':float(np.min(j)),
            'jacobian_identity_relative_error':float(np.max(np.abs(j-expected)/np.maximum(expected,1e-12))),
            'refinement_relative_to_radius':float(np.max(np.linalg.norm(coarse[:,:2]-fine[:,:2],axis=1))/scale),
            'scope':'Finite sample and time-refinement diagnostics; not a global numerical injectivity certificate.'}


def load_dataset():
    return json.loads(Path(__file__).with_name('curves.json').read_text())


def experiment(raw_x,raw_y,controls):
    options={k:controls.get(k,v) for k,v in dict(center=True,rotate=True,normalize=False,shift=0,reverse=False).items()}
    x,y,meta=prepare(raw_x,raw_y,**options); radius=float(np.sqrt(np.mean(np.sum(x*x,axis=1))))
    support=float(controls.get('support_ratio',1.2))
    if not .6<=support<=2: raise ValueError('Support ratio must lie in [0.6,2].')
    field=Field(x,y,support*radius); bound=max(radius*1.8,float(max(np.abs(x).max(),np.abs(y).max()))*1.2)
    grid=[]
    for q in np.linspace(-.9*bound,.9*bound,9):
        grid.extend([[q,z] for z in np.linspace(-.9*bound,.9*bound,25)])
        grid.extend([[z,q] for z in np.linspace(-.9*bound,.9*bound,25)])
    curve=np.array([p+(x[(i+1)%len(x)]-p)*j/8 for i,p in enumerate(x) for j in range(8)])
    samples=np.vstack([x,curve,grid]); steps=64*max(2,int(np.ceil(4*field.lipschitz_bound/64)))
    coarse,_=integrate(field,samples,steps); fine,history=integrate(field,samples,2*steps,frames=64)
    back,_=integrate(field,fine[:len(x),:2],2*steps,duration=-1)
    det=history[:,:,2]*history[:,:,5]-history[:,:,3]*history[:,:,4]; expected=np.exp(history[:,:,6])
    diag={'steps':2*steps,'refinement_max_position':float(np.max(np.linalg.norm(coarse[:,:2]-fine[:,:2],axis=1))),
          'inverse_max_position':float(np.max(np.linalg.norm(back[:,:2]-x,axis=1))),
          'minimum_sampled_det':float(np.min(det)),
          'jacobian_identity_relative_error':float(np.max(np.abs(det-expected)/np.maximum(expected,1e-12))),
          'scope':'All displayed grid/curve samples and 65 cached times; no global numerical injectivity certificate.'}
    return {'metric':'sqrt(mean(sum((source-target)^2, axis=1)))','unit':meta['unit'],'paired_RMS':rms(x,y),
            'flow_endpoint_RMS':rms(fine[:len(x),:2],y),'interpolation_residual':field.residual,
            'condition_inf':field.condition,'lipschitz_bound':field.lipschitz_bound,'diagnostics':diag,
            'attribution':'Wendland (1995) compact-support kernel; smooth-flow concept: Beg et al. (2005). Original finite teaching implementation; no geodesic or elastic optimization.'}


def run():
    data=load_dataset()['curves']
    return experiment(resample(data['lobed']['points'],16),resample(data['bean']['points'],16),{})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out');parser.add_argument('--experiment',help='JSON experiment downloaded from the laboratory');args=parser.parse_args()
    if args.experiment:
        d=json.loads(Path(args.experiment).read_text());report=experiment(d['raw_source_mm'],d['raw_target_mm'],d['controls'])
    else: report=run()
    if args.out: Path(args.out).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
