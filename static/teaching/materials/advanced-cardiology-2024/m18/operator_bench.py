"""Original teaching benchmark: sealed 1D heat flow, not G-FuNK.

Space/time/amplitude are nondimensional. Fixed interval [0,L], constant kappa.
Input coefficients are [mean, cosine_mode_1, ...]. Midpoint grids are quadrature
samples of a continuous field. Analytic truth is available; training is an
illustration, not a recommendation to learn this inexpensive known solution.
The optional diagonal spectral fit learns only a stated finite-band, fixed-time,
fixed-diffusivity family. No patient data or external trained model is used.
"""
import numpy as np
from scipy.linalg import solve_banded

def parameters(kappa,T,L):
    if not np.isfinite([kappa,T,L]).all() or not 0<=kappa<=10 or not 0<=T<=100 or not .1<=L<=10:
        raise ValueError('Use finite kappa in[0,10], time in[0,100], and length in[0.1,10].')

def grid(n,L=1.):
    if not isinstance(n,(int,np.integer)) or isinstance(n,bool) or not 8<=n<=2000 or not np.isfinite(L) or not .1<=L<=10:
        raise ValueError('Use8–2000 midpoint cells and a finite length in[0.1,10].')
    return (np.arange(n)+.5)*L/n

def basis(n,k,L=1.):
    x=grid(n,L)
    if not isinstance(k,(int,np.integer)) or isinstance(k,bool) or not 1<=k<n/2:
        raise ValueError('Use at least one mode and fewer than half the grid size.')
    return np.cos(np.pi*x[:,None]*np.arange(1,k+1)[None,:]/L)

def field(coeff,n=64,kappa=.1,T=.1,L=1.):
    parameters(kappa,T,L);coeff=np.asarray(coeff,float)
    if coeff.ndim not in (1,2) or coeff.shape[-1]<2 or not np.isfinite(coeff).all() or np.max(abs(coeff))>100:
        raise ValueError('Finite mean-plus-mode coefficient vectors with magnitude<=100 required.')
    k=coeff.shape[-1]-1;B=basis(n,k,L);gains=np.exp(-kappa*(np.pi*np.arange(1,k+1)/L)**2*T)
    out=coeff[...,0,None]+(coeff[...,1:]*gains)@B.T
    if not np.isfinite(out).all():raise RuntimeError('Nonfinite analytic field.')
    return out

def project(u,k=3,L=1.):
    u=np.asarray(u,float)
    if u.ndim not in (1,2) or not np.isfinite(u).all():raise ValueError('Finite vector or batch of field vectors required.')
    B=basis(u.shape[-1],k,L)
    return np.concatenate([u.mean(axis=-1,keepdims=True),2/u.shape[-1]*(u@B)],axis=-1)

def dataset(count=48,n=64,k=3,seed=1701,kappa=.1,T=.1,L=1.):
    if not isinstance(count,(int,np.integer)) or isinstance(count,bool) or not 4<=count<=10000:raise ValueError('Use4–10000 complete trajectories.')
    basis(n,k,L);parameters(kappa,T,L)
    rng=np.random.default_rng(seed);coeff=np.column_stack([rng.uniform(.8,1.2,count),rng.uniform(-.2,.2,(count,k))])
    return {'coefficients':coeff,'initial':field(coeff,n,kappa,0,L),'final':field(coeff,n,kappa,T,L),'ids':[f'{seed}-{j:04d}' for j in range(count)],'kappa':kappa,'time':T,'length':L}

def fit(initial,final,k=3,L=1.):
    initial=np.asarray(initial,float);final=np.asarray(final,float)
    if initial.ndim!=2 or final.shape!=initial.shape or len(initial)<k+1:raise ValueError('Matched training field matrices with enough cases required.')
    a=project(initial,k,L)[:,1:];b=project(final,k,L)[:,1:];denom=np.sum(a*a,axis=0)
    if np.any(denom<1e-12):raise ValueError('Each retained mode must be excited in training data.')
    gains=np.sum(a*b,axis=0)/denom
    if not np.isfinite(gains).all():raise RuntimeError('Nonfinite fitted gains.')
    return {'gains':gains,'modes':k,'length':L}

def predict(model,initial):
    initial=np.asarray(initial,float);coeff=project(initial,model['modes'],model['length']);g=np.asarray(model['gains'],float)
    if g.shape!=(model['modes'],) or not np.isfinite(g).all():raise ValueError('Finite gain vector matching retained modes required.')
    return coeff[...,0,None]+(coeff[...,1:]*g)@basis(initial.shape[-1],model['modes'],model['length']).T

def reference_fd(initial,kappa=.1,T=.1,L=1.,dt=.001):
    parameters(kappa,T,L);u=np.asarray(initial,float).copy()
    if u.ndim!=1 or not np.isfinite(u).all():raise ValueError('Finite one-dimensional initial field required.')
    grid(len(u),L)
    if not np.isfinite(dt) or dt<=0 or T/dt>20000:raise ValueError('Positive finite step with at most20000 intervals required.')
    if T==0:return u
    count=int(np.ceil(T/dt));h=T/count;dx=L/len(u);r=kappa*h/dx**2
    ab=np.zeros((3,len(u)));ab[0,1:]=-r;ab[1]=1+2*r;ab[1,[0,-1]]=1+r;ab[2,:-1]=-r
    for _ in range(count):u=solve_banded((1,1),ab,u,check_finite=True)
    if not np.isfinite(u).all():raise RuntimeError('Nonfinite reference solve.')
    return u

def metrics(predicted,truth):
    p=np.asarray(predicted,float);y=np.asarray(truth,float)
    if p.shape!=y.shape or p.ndim!=1 or not np.isfinite(p).all() or not np.isfinite(y).all():raise ValueError('Matched finite field vectors required.')
    try:
        with np.errstate(over='raise',invalid='raise',divide='raise'):
            difference=p-y;scale=float(np.max(abs(difference)));yscale=float(np.max(abs(y)))
            rms=0. if scale==0 else scale*float(np.sqrt(np.mean((difference/scale)**2)))
            yrms=0. if yscale==0 else yscale*float(np.sqrt(np.mean((y/yscale)**2)))
            relative=None if yrms==0 else rms/yrms
            mean_error=0. if scale==0 else abs(scale*float(np.mean(difference/scale)))
    except FloatingPointError as error:raise ValueError('Field metric exceeds numerical range.') from error
    if not np.isfinite([rms,scale,mean_error]).all() or (relative is not None and not np.isfinite(relative)):raise ValueError('Nonfinite field metric.')
    return {'rms':rms,'relative_l2':relative,'max_error':scale,'mean_error':mean_error}
