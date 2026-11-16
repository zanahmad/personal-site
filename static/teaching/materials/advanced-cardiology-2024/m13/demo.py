"""Original synthetic closed-curve alignment lab. Units: mm; no patient data.
Run python demo.py. The companion is standalone; it requires NumPy/Matplotlib.
"""
from pathlib import Path
import json
from html import escape
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter


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


def sampling_comparison(counts=(16, 32, 64, 128)):
    output=[]
    for n in counts:
        n=count(n, 4, 1024); s=np.arange(n)/n
        uniform=curve(2*np.pi*s)
        uneven=curve(2*np.pi*(s+.12*np.sin(2*np.pi*s)))
        output.append([n, align_rigid(uniform, uneven)['rms_mm'],
                       align_rigid(resample_closed(uniform,128), resample_closed(uneven,128))['rms_mm']])
    return np.array(output)


def save(fig, stem, title, description):
    fig.savefig(stem+'.pdf', bbox_inches='tight', metadata={'Title':title,'Author':'Zan Ahmad'})
    fig.savefig(stem+'.svg', bbox_inches='tight')
    path=Path(stem+'.svg'); svg=path.read_text(); start=svg.index('<svg'); end=svg.index('>',start)
    svg=svg[:end]+' role="img" aria-labelledby="figure-title figure-desc"'+svg[end:end+1]+f'<title id="figure-title">{escape(title)}</title><desc id="figure-desc">{escape(description)}</desc>'+svg[end+1:]
    path.write_text(svg); plt.close(fig)


def run():
    plt.rcParams.update({'font.size':22,'axes.labelsize':22,'axes.titlesize':22,'xtick.labelsize':20,'ytick.labelsize':20,'legend.fontsize':20,'svg.fonttype':'none'})
    p=curve(np.arange(64)*2*np.pi/64); q=p@rotation(.65)+[10,-4]; result=align_rigid(p,q)
    fig, axes=plt.subplots(1,2,figsize=(11.4,4.6),layout='constrained')
    for ax, candidate, title in zip(axes,[q,result['aligned']],['Before alignment','Proper rigid alignment']):
        for v,label,style,color in [(p,'Reference','-','#116b8a'),(candidate,'Moving','--','#b55020')]:
            closed=np.vstack([v,v[0]]);ax.plot(*closed.T,style,color=color,lw=2.7,label=label)
        ax.set(xlabel='x (mm)',ylabel='y (mm)',title=title,xlim=(-18,28),ylim=(-20,16));ax.set_aspect('equal');ax.grid(alpha=.2)
    axes[0].legend(loc='upper left',ncol=2,bbox_to_anchor=(-.05,1.27),frameon=False)
    save(fig,'pose-alignment','Pose versus fixed-correspondence shape','A synthetic planar contour in millimetres and its rotated, translated copy. Equal axis limits and aspect ratios. Dashed moving curve overlays the solid reference after proper rigid alignment; size and reflections are not removed.')
    values=sampling_comparison(); n=32; s=np.arange(n)/n; a=curve(2*np.pi*s); b=curve(2*np.pi*(s+.12*np.sin(2*np.pi*s)))
    fig, axes=plt.subplots(1,2,figsize=(11.4,4.5),layout='constrained')
    for v,label,marker,color in [(a,'Uniform angle','o','#116b8a'),(b,'Uneven angle','^','#b55020')]:
        closed=np.vstack([v,v[0]]); axes[0].plot(*closed.T,lw=1,color=color);axes[0].plot(*v.T,marker,ms=5,color=color,label=label)
    axes[0].set(xlabel='x (mm)',ylabel='y (mm)',title='Same analytic contour');axes[0].set_aspect('equal');fig.legend(*axes[0].get_legend_handles_labels(),loc='upper left',bbox_to_anchor=(.10,1.13),ncol=2,frameon=False)
    axes[1].loglog(values[:,0],values[:,1],'o-',label='Index match',color='#b55020',lw=2.5)
    axes[1].loglog(values[:,0],values[:,2],'^--',label='Arclength match',color='#116b8a',lw=2.5)
    axes[1].set(xlabel='Input vertices',ylabel='Aligned RMS (mm)',title='Sampling artifact');axes[1].set_xticks(values[:,0],values[:,0].astype(int));axes[1].set_yticks([.01,.1,1],['0.01','0.1','1']);axes[1].yaxis.set_minor_formatter(NullFormatter());axes[1].xaxis.set_minor_formatter(NullFormatter());axes[1].legend(frameon=False,loc='upper right');axes[1].grid(alpha=.2)
    save(fig,'sampling-artifact','Sampling changes a correspondence-based distance','Both samplings evaluate the same analytic contour with the same starting point and direction. Direct equal-index matching remains mismatched under refinement. Uniform polygonal arclength resampling to 128 points reduces the error as the input polygons improve. The residual is not exactly zero at finite resolution.')
    assert result['rms_mm'] < 1e-12 and abs(result['determinant']-1)<1e-12
    assert values[-1,2] < values[0,2]/10
    out={'pose_before_mm':rms(p,q),'pose_after_mm':result['rms_mm'],'rotation_determinant':result['determinant'],'sampling_columns':['input_vertices','index_match_RMS_mm','arclength_match_RMS_mm'],'sampling':values.tolist(),'scope':'Synthetic fixed correspondence; no scale normalization, reflection, clinical data or full registration.'}
    Path('results.json').write_text(json.dumps(out,indent=2)+'\n');return out

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
