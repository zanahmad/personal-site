"""Original synthetic cohort and fixed-displacement cost lab. Units: mm; no patient data.
Run python demo.py. The companion is standalone; it requires NumPy/Matplotlib.
"""
from pathlib import Path
import json
from html import escape
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def points(value):
    a = np.asarray(value, dtype=float)
    if a.ndim != 2 or a.shape[1] != 2 or not 3 <= len(a) <= 4096:
        raise ValueError('Expected 3..4096 two-dimensional points.')
    if not np.all(np.isfinite(a)) or np.max(np.abs(a)) > 1e6:
        raise ValueError('Coordinates must be finite and at most 1e6 mm in magnitude.')
    return a


def count(value, lo=4, hi=4096):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or not lo <= value <= hi:
        raise ValueError(f'Count must be an integer in [{lo}, {hi}].')
    return int(value)


def rotation(angle):
    if not np.isscalar(angle) or not np.isfinite(angle) or abs(angle) > 1e6:
        raise ValueError('Angle must be finite with magnitude at most 1e6 radians.')
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, -s], [s, c]])


def curve(theta):
    t = np.asarray(theta, dtype=float)
    if t.ndim != 1 or not 3 <= len(t) <= 4096 or not np.all(np.isfinite(t)) or np.max(abs(t)) > 1e6:
        raise ValueError('Supply 3..4096 finite angles with magnitude at most 1e6 radians.')
    radius = 12 * (1 + .16 * np.cos(3*t) + .07 * np.sin(2*t))
    return np.column_stack([radius*np.cos(t), .7*radius*np.sin(t)])


def rms(reference, moving):
    x, y = points(reference), points(moving)
    if x.shape != y.shape:
        raise ValueError('Corresponding arrays must have equal shape.')
    return float(np.sqrt(np.mean(np.sum((x-y)**2, axis=1))))


def resample_closed(vertices, n=64):
    """Uniform polygonal arclength; no duplicated endpoint. Keeps start/direction."""
    p = points(vertices); n = count(n)
    edge = np.roll(p, -1, axis=0)-p
    lengths = np.linalg.norm(edge, axis=1)
    if np.any(lengths <= 1e-12):
        raise ValueError('Adjacent vertices, including closing pair, must differ.')
    cumulative = np.r_[0., np.cumsum(lengths)]
    targets = np.arange(n)*cumulative[-1]/n
    j = np.searchsorted(cumulative, targets, side='right')-1
    fraction = (targets-cumulative[j])/lengths[j]
    return p[j]+fraction[:, None]*edge[j]


def align_rigid(reference, moving):
    """Minimize fixed-correspondence RMS using translation and proper rotation.
    Points are ROW vectors, aligned = moving @ R + translation. No scale/reflection.
    A nonunique optimum is allowed for symmetric/degenerate data, but not zero spread.
    """
    x, y = points(reference), points(moving)
    if x.shape != y.shape:
        raise ValueError('Correspondence requires arrays of the same shape.')
    xm, ym = x.mean(0), y.mean(0); xc, yc = x-xm, y-ym
    if np.linalg.norm(xc) <= 1e-12 or np.linalg.norm(yc) <= 1e-12:
        raise ValueError('Both point sets need nonzero spread.')
    u, _, vt = np.linalg.svd(yc.T@xc)
    d = np.diag([1., 1. if np.linalg.det(u@vt) >= 0 else -1.])
    r = u@d@vt; shift = xm-ym@r; aligned = y@r+shift
    return {'aligned': aligned, 'rotation': r, 'translation': shift,
            'rms_mm': rms(x, aligned), 'determinant': float(np.linalg.det(r))}


def save(fig, stem, title, description):
    fig.savefig(stem+'.pdf', bbox_inches='tight', metadata={'Title':title,'Author':'Zan Ahmad'})
    fig.savefig(stem+'.svg', bbox_inches='tight')
    path=Path(stem+'.svg'); svg=path.read_text(); start=svg.index('<svg'); end=svg.index('>',start)
    svg=svg[:end]+' role="img" aria-labelledby="figure-title figure-desc"'+svg[end:end+1]+f'<title id="figure-title">{escape(title)}</title><desc id="figure-desc">{escape(description)}</desc>'+svg[end+1:]
    path.write_text(svg); plt.close(fig)


def aligned_distance(reference, moving):
    """Proper rigid alignment over all cyclic starts; direction/size are preserved."""
    x,y=points(reference),points(moving)
    if x.shape != y.shape or len(x)>256:
        raise ValueError('Use equal 3..256 point arrays for bounded cyclic enumeration.')
    best=None
    for k in range(len(y)):
        candidate=align_rigid(x,np.roll(y,k,axis=0))
        if best is None or candidate['rms_mm']<best['rms_mm']:
            best=candidate|{'cyclic_shift':k}
    return best


def cohort(n=64):
    n=count(n, 16, 128);t=np.arange(n)*2*np.pi/n;p=resample_closed(curve(np.arange(512)*2*np.pi/512),n)
    bulge=p.copy();weight=np.exp(-((np.angle(np.exp(1j*(t-.8))))/.35)**2);bulge[:,0]+=3*weight
    return {'A':p,'B':p@rotation(.65)+[10,-4],'C':1.15*p,'D':bulge,'E':np.roll(p,9,axis=0)}


def pairwise(shapes, aligned=False):
    if not isinstance(aligned,(bool,np.bool_)) or not 2<=len(shapes)<=10:
        raise ValueError('Use 2..10 shapes and a Boolean alignment flag.')
    names=list(shapes);p=[points(shapes[k]) for k in names];out=np.zeros((len(p),len(p)))
    for i in range(len(p)):
        for j in range(i):
            d=aligned_distance(p[i],p[j])['rms_mm'] if aligned else rms(p[i],p[j]);out[i,j]=out[j,i]=d
    return names,out


def displacement_cost(displacements, weight=1.):
    """Finite fixed-grid teaching score in mm^2, not physical or elastic energy."""
    u=points(displacements)
    if not np.isscalar(weight) or not np.isfinite(weight) or not 0<=weight<=1e6:
        raise ValueError('Weight must be finite in [0,1e6].')
    amplitude=float(np.mean(np.sum(u*u,axis=1)))
    roughness=float(np.mean(np.sum((np.roll(u,-1,axis=0)-u)**2,axis=1)))
    return {'amplitude_mm2':amplitude,'roughness_mm2':roughness,'score_mm2':amplitude+weight*roughness}


def displacement_fields(n=64):
    n=count(n,32,256);t=np.arange(n)*2*np.pi/n;radial=np.column_stack([np.cos(t),np.sin(t)])
    fields=[]
    for frequency in [2,10]:
        u=np.cos(frequency*t)[:,None]*radial
        fields.append(u/np.sqrt(np.mean(np.sum(u*u,axis=1))))
    return t,fields


def run():
    plt.rcParams.update({'font.size':22,'axes.labelsize':22,'axes.titlesize':22,'xtick.labelsize':20,'ytick.labelsize':20,'legend.fontsize':20,'svg.fonttype':'none'})
    shapes=cohort();names,raw=pairwise(shapes);_,aligned=pairwise(shapes,True)
    fig,axes=plt.subplots(1,2,figsize=(11.6,4.8),layout='constrained')
    for ax,matrix,title in zip(axes,[raw,aligned],['Raw index RMS','Rigid + cyclic RMS']):
        image=ax.imshow(matrix,cmap='Blues',vmin=0,vmax=max(matrix.max(),1e-12))
        ax.set_xticks(range(5),names);ax.set_yticks(range(5),names);ax.set_title(title);ax.set_xlabel('Contour');ax.set_ylabel('Contour')
        for i in range(5):
            for j in range(5):
                v=matrix[i,j];ax.text(j,i,f'{v:.1f}',ha='center',va='center',fontsize=20,color='white' if v>.55*matrix.max() else '#111111')
        bar=fig.colorbar(image,ax=ax,shrink=.8);bar.set_label('RMS (mm)')
    save(fig,'cohort-distances','Synthetic cohort distances under two declared comparison rules','A is the reference. B is a posed copy, C is 15 percent larger, D has a local bulge, and E has a changed cyclic starting index. Left: raw index RMS. Right: minimum RMS over proper rigid motions and cyclic shifts. Each panel uses its own labeled color scale in millimetres; compare numeric values, not shades across panels. Size differences remain.')
    t,fields=displacement_fields();weights=np.linspace(0,8,81)
    fig,axes=plt.subplots(1,2,figsize=(11.4,4.7),layout='constrained')
    for u,label,style,color in zip(fields,['Smooth','Oscillatory'],['-','--'],['#116b8a','#b55020']):
        radial=np.column_stack([np.cos(t),np.sin(t)]);profile=np.sum(u*radial,axis=1)
        axes[0].plot(np.arange(len(t)),profile,style,color=color,label=label,lw=2.7)
        scores=[displacement_cost(u,w)['score_mm2'] for w in weights];axes[1].plot(weights,scores,style,color=color,label=label,lw=2.7)
    axes[0].set(xlabel='Fixed cyclic index',ylabel='Radial displacement (mm)',title='Both RMS = 1 mm')
    axes[1].set(xlabel='Roughness weight (unitless)',ylabel='Finite score (mm²)',title='Same size, different roughness');axes[1].legend(frameon=False)
    for ax in axes:ax.grid(alpha=.2)
    save(fig,'displacement-cost','A finite fixed-correspondence cost illustrates weighting','Two zero-mean radial displacement fields on a fixed 64-point ring have equal root-mean-square amplitude, 1 millimetre. Solid smooth and dashed oscillatory fields receive different scores when nonnegative neighbor-difference weight increases. This grid-dependent quadratic score is not a path energy, elastic geodesic, physical strain, varifold distance or clinical result.')
    assert aligned[0,1]<1e-12 and aligned[0,4]<1e-12 and aligned[0,2]>.1
    diagnostics=[displacement_cost(u) for u in fields];assert all(abs(v['amplitude_mm2']-1)<1e-12 for v in diagnostics)
    out={'names':names,'raw_RMS_mm':raw.tolist(),'rigid_cyclic_RMS_mm':aligned.tolist(),'costs_at_weight_one':diagnostics,'scope':'Proper rigid plus finite cyclic comparison; finite fixed-grid displacement cost only. No elastic path optimization or varifold implementation.'}
    Path('results.json').write_text(json.dumps(out,indent=2)+'\n');return out

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
