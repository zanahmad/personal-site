"""Synthetic image-to-model workflow and a well-mixed washout surrogate, NOT CFD."""
from pathlib import Path
import json,html
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter


def remaining_fraction(time_s,flow_ml_s=50.,volume_ml=100.):
    t=np.asarray(time_s,float)
    if not np.isfinite(t).all() or np.any(t<0) or not np.isfinite([flow_ml_s,volume_ml]).all() or flow_ml_s<0 or volume_ml<=0:raise ValueError('Use finite nonnegative time/flow and positive volume.')
    return np.exp(-flow_ml_s*t/volume_ml)


def synthetic_image(n=64):
    if isinstance(n,bool) or not isinstance(n,(int,np.integer)) or n<16 or n>256:raise ValueError('Use an integer grid size from16 through256.')
    axis=np.linspace(-1,1,n);x,y=np.meshgrid(axis,axis)
    chamber=(x/.64)**2+(y/.70)**2<1
    appendage=((x-.57)/.30)**2+((y-.25)/.23)**2<1
    inlet=(abs(x+.20)<.12)&(y>.55)&(y<.96)
    outlet=(abs(x-.12)<.16)&(y<-.55)&(y>-.96)
    truth=chamber|appendage|inlet|outlet
    image=.15+.7*gaussian_filter(truth.astype(float),1.1)+.035*np.random.default_rng(9).normal(size=(n,n))
    return np.clip(image,0,1),truth


def segment(image,threshold=.5):
    a=np.asarray(image,float)
    if a.ndim!=2 or not np.isfinite(a).all() or not np.isfinite(threshold) or not 0<threshold<1:raise ValueError('Use a finite2D image and threshold strictly between0 and1.')
    return a>=threshold


def save(fig,out,stem,title,desc):
    for ext in ('svg','pdf'):fig.savefig(out/f'{stem}.{ext}',bbox_inches='tight',metadata={'Date':None} if ext=='svg' else {'CreationDate':None})
    p=out/f'{stem}.svg';s=p.read_text();i=s.index('>',s.index('<svg'))+1;p.write_text(s[:i]+'<title>'+html.escape(title)+'</title><desc>'+html.escape(desc)+'</desc>'+s[i:]);plt.close(fig)


def run(output_dir=None):
    out=Path(output_dir or Path(__file__).parent);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':20,'axes.titlesize':20,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    image,truth=synthetic_image();mask=segment(image)
    fig,axs=plt.subplots(1,3,figsize=(11.5,4.5),constrained_layout=True)
    for ax in axs:ax.set(xticks=[],yticks=[],aspect='equal')
    axs[0].imshow(image,cmap='gray',vmin=0,vmax=1,origin='lower');axs[0].set_title('Synthetic image')
    axs[1].imshow(mask,cmap='Blues',vmin=0,vmax=1,origin='lower');axs[1].set_title('Threshold mask')
    axs[2].imshow(mask,cmap='Blues',vmin=0,vmax=1,origin='lower',alpha=.35)
    for i in range(0,64,4):
        for j in range(0,64,4):
            if mask[i:i+4,j:j+4].all():axs[2].add_patch(plt.Rectangle((j-.5,i-.5),4,4,fill=False,ec='#18384a',lw=.8))
    axs[2].set_title('Grid sketch only');axs[2].annotate('Inlet',xy=(25,60),xytext=(42,53),ha='left',va='center',fontsize=20,arrowprops={'arrowstyle':'->','lw':1.5});axs[2].annotate('Outlet',xy=(35,3),xytext=(7,8),ha='left',va='center',fontsize=20,arrowprops={'arrowstyle':'->','lw':1.5})
    fig.suptitle('Geometry is one input; this grid is not a CFD mesh',fontsize=20)
    save(fig,out,'image-pipeline','Separate image, mask and spatial representation','Original synthetic chamber-shaped image, threshold mask, and interior square-grid sketch. Inlet and outlet labels identify artificial boundaries. This is not a patient image, anatomical segmentation, or a solver-ready CFD mesh.')
    t=np.linspace(0,8,161);fig,ax=plt.subplots(figsize=(8.2,4.9),constrained_layout=True)
    for q,col in [(25.,'#b16a20'),(50.,'#087e8b'),(100.,'#18384a')]:ax.plot(t,remaining_fraction(t,q,100),lw=2.4,color=col,label=f'Q = {q:g} mL/s')
    ax.set(xlabel='Time since tracer-free inflow (s)',ylabel='Fraction of tracer remaining',title='One well-mixed 100 mL compartment',ylim=(0,1.05));ax.legend(fontsize=20);ax.grid(alpha=.15)
    save(fig,out,'washout','A prescribed flow changes a well-mixed washout curve','Original exact exponential washout curves for a constant 100 mL compartment with balanced inflow/outflow at 25, 50, and 100 mL/s. Spatial velocity, clots, and stroke risk are not predicted.')
    assert remaining_fraction(0,50,100)==1
    assert np.all(remaining_fraction(t,0,100)==1)
    assert np.all(np.diff(remaining_fraction(t))<=0)
    np.testing.assert_allclose(remaining_fraction(t,100,200),remaining_fraction(t,50,100),atol=0,rtol=0)
    assert segment(image,.6).sum()<=segment(image,.5).sum()<=segment(image,.4).sum()
    assert remaining_fraction(2,100,100)<remaining_fraction(2,50,100)
    invalid=0
    for args in [([-1],50,100),([1],-1,100),([1],50,0),([float('nan')],50,100)]:
        try:remaining_fraction(*args)
        except ValueError:invalid+=1
        else:raise AssertionError('Invalid washout input accepted')
    report={'scope':'well-mixed compartment surrogate, not resolved CFD','volume_ml':100.,'fraction_at2s_Q25_50_100':[float(remaining_fraction(2,q,100)) for q in (25,50,100)],'time_constant_s_Q25_50_100':[4.,2.,1.],'mask_pixel_counts_at_thresholds04_05_06':[int(segment(image,a).sum()) for a in (.4,.5,.6)],'checks':{'initial_fraction_one':True,'no_flow_no_washout':True,'ratio_invariance':True,'threshold_masks_nested':True,'invalid_inputs_rejected':invalid}}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(run(),indent=2))
