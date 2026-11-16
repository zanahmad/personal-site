"""Fixed image filters plus a trained centroid classifier; NOT a trained CNN.
Synthetic ellipse-orientation labels have no clinical meaning.
"""
from pathlib import Path
import json,html
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def filter_map(image,kernel):
    a=np.asarray(image,float);k=np.asarray(kernel,float)
    if a.ndim!=2 or k.shape!=(3,3) or min(a.shape)<3 or not np.isfinite(a).all() or not np.isfinite(k).all():raise ValueError('Use a finite2D image at least3 by3 and a finite3 by3 kernel.')
    return np.einsum('ijab,ab->ij',sliding_window_view(a,(3,3)),k)


def features(images):
    a=np.asarray(images,float)
    if a.ndim!=3 or len(a)==0 or min(a.shape[1:])<3 or not np.isfinite(a).all():raise ValueError('Use a nonempty finite image batch.')
    kx=np.array([[-1,0,1],[-1,0,1],[-1,0,1]],float)/3;ky=kx.T
    return np.array([[np.maximum(filter_map(im,k),0).mean() for k in (kx,ky)] for im in a])


def make_images(n=80,seed=10,contrast=1.):
    if isinstance(n,bool) or not isinstance(n,(int,np.integer)) or n<4 or n%2 or n>2000:raise ValueError('Use an even image count from4 through2000.')
    if not np.isfinite(contrast) or not 0<=contrast<=1:raise ValueError('Contrast must be finite and between0 and1.')
    rng=np.random.default_rng(seed);y=np.repeat([0,1],n//2);xx,yy=np.meshgrid(np.linspace(-1,1,16),np.linspace(-1,1,16));images=[]
    for label in y:
        major=rng.uniform(.56,.76);minor=rng.uniform(.22,.36);cx,cy=rng.uniform(-.1,.1,2);a,b=(major,minor) if label==0 else (minor,major)
        mask=((xx-cx)/a)**2+((yy-cy)/b)**2<=1
        images.append(np.clip(.15+contrast*.7*mask+.05*rng.normal(size=(16,16)),0,1))
    return np.array(images),y


def fit_centers(x,y):
    x=np.asarray(x,float);y=np.asarray(y)
    if x.ndim!=2 or x.shape[1]!=2 or y.shape!=(len(x),) or not np.isfinite(x).all() or set(y.tolist())!={0,1}:raise ValueError('Use finite two-feature rows with both labels.')
    return np.array([x[y==k].mean(axis=0) for k in (0,1)])


def predict(x,centers):
    x=np.asarray(x,float);c=np.asarray(centers,float)
    if x.ndim!=2 or x.shape[1]!=2 or c.shape!=(2,2) or not np.isfinite(x).all() or not np.isfinite(c).all():raise ValueError('Use finite two-feature rows and two centers.')
    return np.argmin(((x[:,None]-c[None])**2).sum(axis=2),axis=1)


def save(fig,out,stem,title,desc):
    for ext in ('svg','pdf'):fig.savefig(out/f'{stem}.{ext}',bbox_inches='tight',metadata={'Date':None} if ext=='svg' else {'CreationDate':None})
    p=out/f'{stem}.svg';s=p.read_text();i=s.index('>',s.index('<svg'))+1;p.write_text(s[:i]+'<title>'+html.escape(title)+'</title><desc>'+html.escape(desc)+'</desc>'+s[i:]);plt.close(fig)


def run(output_dir=None):
    out=Path(output_dir or Path(__file__).parent);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':20,'axes.titlesize':20,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    train,ytrain=make_images(80,10);test,ytest=make_images(40,11);ftrain=features(train);ftest=features(test);centers=fit_centers(ftrain,ytrain);pred=predict(ftest,centers)
    kx=np.array([[-1,0,1],[-1,0,1],[-1,0,1]],float)/3;im=test[0];maps=[im,np.maximum(filter_map(im,kx),0),np.maximum(filter_map(im,kx.T),0)]
    fig,axs=plt.subplots(1,3,figsize=(10.5,3.9),constrained_layout=True)
    for ax,a,title in zip(axs,maps,['Synthetic image','x-response + ReLU','y-response + ReLU']):ax.imshow(a,cmap='viridis',vmin=0,vmax=1);ax.set_title(title);ax.set(xticks=[],yticks=[])
    fig.suptitle('Fixed filters: no filter weights were learned',fontsize=20)
    save(fig,out,'image-filters','Two original local image filters','A synthetic horizontally elongated ellipse image and two nonnegative directional response maps. A 3 by 3 fixed kernel is reused at every valid location, shrinking 16 by 16 to 14 by 14. Color scale 0 to 1 is shared.')
    contrasts=[1.,.5,0.];accuracies=[]
    for contrast in contrasts:
        shifted,ys=make_images(40,11,contrast);accuracies.append(float(np.mean(predict(features(shifted),centers)==ys)))
    cm=np.array([[np.sum((ytest==i)&(pred==j)) for j in (0,1)] for i in (0,1)])
    fig,axs=plt.subplots(1,2,figsize=(10.2,4.7),constrained_layout=True)
    axs[0].imshow(cm,cmap='Blues',vmin=0,vmax=20)
    for i in (0,1):
        for j in (0,1):axs[0].text(j,i,str(cm[i,j]),ha='center',va='center',color='white' if cm[i,j]>10 else '#18384a',fontsize=22)
    axs[0].set(xticks=[0,1],xticklabels=['Wide','Tall'],yticks=[0,1],yticklabels=['Wide','Tall'],xlabel='Predicted shape',ylabel='True generator label',title='Held-out images')
    axs[1].bar(['1.0','0.5','0.0'],accuracies,color=['#087e8b','#b16a20','#697b86']);axs[1].set(ylim=(0,1.08),xlabel='Test-image contrast',ylabel='Accuracy (fraction)',title='Frozen model stress test');axs[1].axhline(.5,color='#18384a',ls='--',lw=1.5)
    save(fig,out,'image-evaluation','Evaluate both ordinary and shifted synthetic images','Confusion counts on 40 independent synthetic test images and fixed-model accuracy as the same test masks lose contrast. The dashed line is 0.5 for balanced labels, not a clinical reference. The weights and class centers are never refit to these tests.')
    constant=filter_map(np.ones((5,5)),kx);assert np.max(abs(constant))<1e-12
    assert filter_map(np.arange(25).reshape(5,5),kx).shape==(3,3)
    assert np.all(features(test)>=0)
    np.testing.assert_allclose(features(test.transpose(0,2,1)),ftest[:,::-1],atol=1e-14)
    assert cm.sum()==40 and np.isfinite(accuracies).all()
    report={'architecture':'fixed3x3filters -> ReLU -> global mean pooling -> trained nearest centroid classifier','trained_CNN':False,'train_images':80,'test_images':40,'test_confusion_true_rows_predicted_columns':cm.tolist(),'contrasts':contrasts,'test_accuracies':accuracies,'checks':{'constant_image_zero_directional_response':True,'valid_output_shape':True,'transpose_swaps_features':True,'finite_nonnegative_pooled_features':True}}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(run(),indent=2))
