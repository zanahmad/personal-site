"""Train one shared 3x3 convolution + sigmoid on original synthetic images.
A ten-parameter segmentation scaffold, not U-Net or a validated cardiac model.
"""
from pathlib import Path
import html, json
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from scipy.ndimage import gaussian_filter, binary_erosion, distance_transform_edt, label
from scipy.special import expit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def make_images(n,seed):
    if isinstance(n,bool) or not isinstance(n,(int,np.integer)) or not 1<=n<=128:raise ValueError('Use an integer image count from 1 to 128.')
    rng=np.random.default_rng(seed);rr,cc=np.indices((24,24));images=[];masks=[]
    for _ in range(n):
        cx,cy=rng.uniform(10,14,2);a,b=rng.uniform(5,8,2)
        mask=((cc-cx)/a)**2+((rr-cy)/b)**2<=1
        image=np.clip(.22+.56*gaussian_filter(mask.astype(float),.7)+rng.normal(0,.14,mask.shape),0,1)
        images.append(image);masks.append(mask)
    return np.array(images),np.array(masks)


def patches(images):
    x=np.asarray(images,float)
    if x.ndim!=3 or len(x)==0 or min(x.shape[1:])<3 or not np.isfinite(x).all() or np.any((x<0)|(x>1)):raise ValueError('Use a finite nonempty batch of images in [0,1], at least 3 by 3.')
    # Reflect padding maintains image size; no labels are used in this transform.
    padded=np.pad(x-.5,((0,0),(1,1),(1,1)),mode='reflect')
    return sliding_window_view(padded,(3,3),axis=(1,2)).reshape(-1,9)


def objective(theta,x,y,l2=.001):
    t=np.asarray(theta,float);x=np.asarray(x,float);y=np.asarray(y,float)
    if t.shape!=(10,) or x.ndim!=2 or x.shape[1]!=9 or len(x)==0 or y.shape!=(len(x),) or not np.isfinite(t).all() or not np.isfinite(x).all() or not np.isfinite(y).all() or np.any((y!=0)&(y!=1)) or not np.isfinite(l2) or l2<0:raise ValueError('Use finite ten parameters, nine-feature rows, binary targets and nonnegative L2.')
    z=x@t[:9]+t[9];p=expit(z)
    loss=float(np.mean(np.logaddexp(0,z)-y*z)+.5*l2*(t[:9]@t[:9]))
    residual=(p-y)/len(y)
    grad=np.r_[x.T@residual+l2*t[:9],residual.sum()]
    return loss,grad


def train(train_images,train_masks,val_images,val_masks,steps=250,rate=1.):
    if isinstance(steps,bool) or not isinstance(steps,(int,np.integer)) or not 1<=steps<=2000 or not np.isfinite(rate) or not 0<rate<=2:raise ValueError('Use 1–2000 steps and a finite learning rate in (0,2].')
    x=patches(train_images);vx=patches(val_images);y=np.asarray(train_masks);vy=np.asarray(val_masks)
    if y.shape!=np.asarray(train_images).shape or vy.shape!=np.asarray(val_images).shape or y.dtype!=bool or vy.dtype!=bool:raise ValueError('Boolean reference masks must match the corresponding image batch.')
    y=y.ravel();vy=vy.ravel();t=np.zeros(10);best=t.copy();best_loss=objective(t,vx,vy,0)[0];best_step=0;history=[]
    for step in range(steps+1):
        loss,grad=objective(t,x,y)
        if step%10==0 or step==steps:
            vl=objective(t,vx,vy,0)[0];history.append({'step':step,'training_objective':loss,'validation_BCE':vl})
            if vl<best_loss:best_loss=vl;best=t.copy();best_step=step
        if step<steps:t-=rate*grad
    return best,{'selected_step':best_step,'validation_BCE':best_loss,'history':history}


def probabilities(images,theta):
    x=patches(images);t=np.asarray(theta,float)
    if t.shape!=(10,) or not np.isfinite(t).all():raise ValueError('Use ten finite trained parameters.')
    return expit(x@t[:9]+t[9]).reshape(np.asarray(images).shape)


def metrics(prediction,reference,spacing_yx=(1.2,.8)):
    p=np.asarray(prediction);r=np.asarray(reference);s=np.asarray(spacing_yx,float)
    if p.ndim!=2 or p.shape!=r.shape or p.size==0 or p.dtype!=bool or r.dtype!=bool or s.shape!=(2,) or not np.isfinite(s).all() or np.any(s<=0):raise ValueError('Use equal-shape nonempty 2D boolean masks and positive row/column spacing.')
    total=int(p.sum()+r.sum());dice=1. if total==0 else float(2*np.sum(p&r)/total)
    err=None if r.sum()==0 else float(100*(int(p.sum())-int(r.sum()))/r.sum())
    # Four-neighbor foreground boundaries at pixel centers; not subpixel surfaces.
    bp=p&~binary_erosion(p,border_value=0);br=r&~binary_erosion(r,border_value=0)
    if not bp.any() and not br.any():msd=hd=0.
    elif not bp.any() or not br.any():msd=hd=None
    else:
        dp=distance_transform_edt(~br,sampling=s)[bp];dr=distance_transform_edt(~bp,sampling=s)[br]
        msd=float((dp.mean()+dr.mean())/2);hd=float(max(dp.max(),dr.max()))
    return {'dice':dice,'signed_area_error_percent':err,'mean_symmetric_boundary_distance_mm':msd,'hausdorff_boundary_distance_mm':hd,'foreground_components_4_connected':int(label(p)[1])}


def bridge_example():
    reference=np.zeros((40,64),bool);reference[10:30,6:26]=True;reference[10:30,38:58]=True;reference[19:21,26:38]=True
    cut=reference.copy();cut[19:21,31:33]=False
    return reference,cut


def save(fig,out,stem,title,desc):
    for ext in ('svg','pdf'):fig.savefig(out/f'{stem}.{ext}',bbox_inches='tight',metadata={'Date':None} if ext=='svg' else {'CreationDate':None})
    p=out/f'{stem}.svg';s=p.read_text();i=s.index('>',s.index('<svg'))+1;p.write_text(s[:i]+f'<title>{html.escape(title)}</title><desc>{html.escape(desc)}</desc>'+s[i:]);plt.close(fig)


def run(output_dir=None):
    out=Path(output_dir or Path(__file__).parent);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':22,'axes.titlesize':22,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    tr,yr=make_images(24,1201);va,yv=make_images(8,1202);te,yt=make_images(12,1203)
    theta,training=train(tr,yr,va,yv);pred=probabilities(te,theta)>=.5;base=te>=.5
    rows=[{'case_id':f'test-{i:02d}','baseline':metrics(base[i],yt[i]),'convolution':metrics(pred[i],yt[i])} for i in range(len(te))]
    aggregate={model:{key:float(np.mean([row[model][key] for row in rows])) for key in ('dice','signed_area_error_percent','mean_symmetric_boundary_distance_mm','hausdorff_boundary_distance_mm')} for model in ('baseline','convolution')}
    fig,axs=plt.subplots(2,2,figsize=(8.7,7.3),constrained_layout=True)
    for ax,a,title in zip(axs.ravel(),[te[0],yt[0],base[0],pred[0]],['Synthetic test image','Generator reference','Fixed threshold 0.5','Learned 3×3 + sigmoid']):
        ax.imshow(a,origin='lower',cmap='gray',vmin=0,vmax=1,extent=(-.4,18.8,-.6,28.2),aspect='equal');ax.set(xticks=[0,10],yticks=[0,15],xlabel='x (mm)',ylabel='y (mm)',title=title)
    save(fig,out,'segmentation-comparison','Held-out synthetic segmentation comparison','One predeclared test case from twelve, shown with equal physical scaling, 0.8 mm column spacing and 1.2 mm row spacing. A fixed intensity threshold is compared with an actually trained ten-parameter shared 3 by 3 convolution plus sigmoid. Complete images are split before training. Grayscale is 0 to 1; mask white means foreground. This is not U-Net and uses no patient data.')
    ref,cut=bridge_example();bridge=metrics(cut,ref)
    fig,axs=plt.subplots(1,2,figsize=(10.3,4.8),constrained_layout=True)
    for ax,a,title in zip(axs,[ref,cut],['Reference: 1 component','Four missing pixels: 2 components']):
        ax.imshow(a,origin='lower',cmap='gray',vmin=0,vmax=1,extent=(-.4,50.8,-.6,47.4));ax.set(xlabel='x (mm)',ylabel='y (mm)',title=title,xticks=[0,25,50],yticks=[0,20,40])
    fig.suptitle(f'Dice = {bridge["dice"]:.4f}; area change = {bridge["signed_area_error_percent"]:.2f}%',fontsize=22)
    save(fig,out,'connectivity-failure','High overlap can conceal a broken connection','Original two-reservoir binary geometry connected by a two-row bridge. Removing four pixels cuts the connection while Dice remains above 0.99 and area loss is below one percent. Component count uses four-neighbor connectivity. These masks are a topology example, not a solved cardiac-flow model.')
    x=patches(tr[:1]);y=yr[:1].ravel();t=np.linspace(-.2,.2,10);_,analytic=objective(t,x,y);eps=1e-6;numeric=[]
    for j in range(10):
        e=np.zeros(10);e[j]=eps;numeric.append((objective(t+e,x,y)[0]-objective(t-e,x,y)[0])/(2*eps))
    grad_error=float(np.max(np.abs(analytic-numeric)));assert grad_error<1e-8
    z=np.zeros((5,5),bool);assert metrics(z,z)['dice']==1 and metrics(z,z)['hausdorff_boundary_distance_mm']==0
    one=z.copy();one[2,2]=True;assert metrics(one,z)['dice']==0 and metrics(one,z)['hausdorff_boundary_distance_mm'] is None
    assert metrics(ref,ref)['dice']==1 and metrics(ref,ref)['hausdorff_boundary_distance_mm']==0
    scaled=metrics(cut,ref,(2.4,1.6));np.testing.assert_allclose(scaled['hausdorff_boundary_distance_mm'],2*bridge['hausdorff_boundary_distance_mm'])
    assert training['validation_BCE']<np.log(2) and pred.shape==yt.shape and bridge['foreground_components_4_connected']==2
    report={'model':'one trained 3x3 cross-correlation + shared bias + sigmoid; ten parameters','train_images':24,'validation_images':8,'test_images':12,'split_seeds':[1201,1202,1203],'spacing_yx_mm':[1.2,.8],'probability_threshold':.5,'training':training,'weights_3x3':theta[:9].reshape(3,3).tolist(),'bias':float(theta[9]),'test_case_metrics':rows,'test_mean_per_image_metrics':aggregate,'bridge_counterexample':bridge,'checks':{'central_difference_gradient_max_abs_error':grad_error,'identical_masks':True,'empty_mask_conventions':True,'boundary_distance_scales_with_spacing':True,'held_out_complete_images':True,'prediction_shape_preserved':True}}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');np.savez(out/'segmentation-data.npz',train_images=tr,train_masks=yr,validation_images=va,validation_masks=yv,test_images=te,test_masks=yt,theta=theta,test_predictions=pred)
    return report

if __name__=='__main__':
    result=run();print(json.dumps({k:v for k,v in result.items() if k not in ('training','test_case_metrics')},indent=2))
