"""Proposed 2027 synthetic experiment workflow: prediction, projection, grouping.
Self-contained NumPy implementation. Frozen train/test split; all fitted transforms
use training rows. Measurement yield is the outcome, never an input feature.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def matrix(values,minimum_rows=2):
    x=np.asarray(values,dtype=float)
    if x.ndim!=2 or len(x)<minimum_rows or x.shape[1]<1 or not np.all(np.isfinite(x)):
        raise ValueError('Use a finite two-dimensional sample-by-feature array.')
    return x


def rmse(observed,predicted):
    a=np.asarray(observed,dtype=float);b=np.asarray(predicted,dtype=float)
    if a.ndim!=1 or not len(a) or a.shape!=b.shape or not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        raise ValueError('RMSE needs matching nonempty finite vectors.')
    with np.errstate(over='ignore',invalid='ignore'):
        result=float(np.sqrt(np.mean((a-b)**2)))
    if not np.isfinite(result):raise ValueError('RMSE arithmetic exceeds finite range.')
    return result


def fit_standardizer(x):
    x=matrix(x)
    with np.errstate(over='ignore',invalid='ignore'):
        mean=x.mean(axis=0);scale=x.std(axis=0,ddof=0)
    if not np.all(np.isfinite(mean)) or not np.all(np.isfinite(scale)):
        raise ValueError('Feature means or scales exceed finite arithmetic range.')
    if np.any(scale<=1e-12):raise ValueError('Constant features require an explicit handling choice.')
    return mean,scale


def fit_pca(x):
    x=matrix(x);center=x.mean(axis=0);z=x-center
    _,s,vt=np.linalg.svd(z,full_matrices=False)
    if np.sum(s*s)<=1e-24:raise ValueError('PCA needs nonzero total variation.')
    # Sign is arbitrary; choose one convention solely for reproducible display.
    for row in vt:
        if row[np.argmax(abs(row))]<0:row*=-1
    return {'center':center,'components':vt,'variance_ratio':s*s/np.sum(s*s)}


def assign(x,centers):
    x=matrix(x,1);centers=matrix(centers,1)
    if x.shape[1]!=centers.shape[1]:raise ValueError('Feature dimensions must agree.')
    return np.argmin(np.sum((x[:,None,:]-centers[None,:,:])**2,axis=2),axis=1)


def fit_two_centers(x,seed=19,starts=20):
    x=matrix(x)
    if len(np.unique(x,axis=0))<2:raise ValueError('Two centers need at least two distinct samples.')
    if not isinstance(starts,int) or not 1<=starts<=100:raise ValueError('Use 1 to 100 starts.')
    rng=np.random.default_rng(seed);best=None
    for _ in range(starts):
        centers=x[rng.choice(len(x),2,replace=False)].copy();history=[]
        for iteration in range(100):
            labels=assign(x,centers)
            if len(np.unique(labels))!=2:break  # reject an empty-cluster start
            updated=np.array([x[labels==j].mean(axis=0) for j in range(2)])
            inertia=float(np.sum((x-updated[labels])**2));history.append(inertia)
            stable=np.array_equal(assign(x,updated),labels);centers=updated
            if stable:
                candidate={'centers':centers,'labels':labels,'inertia':inertia,'history':history,'iterations':iteration+1}
                if best is None or inertia<best['inertia']:best=candidate
                break
    if best is None:raise RuntimeError('No nonempty stable clustering found; inspect initialization.')
    assert np.all(np.diff(best['history'])<=1e-9)
    return best


def save(fig,out,stem,title,description):
    for ext in ('svg','pdf'):fig.savefig(out/(stem+'.'+ext),bbox_inches='tight')
    plt.close(fig);ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns)
    tree=ET.parse(out/(stem+'.svg'));r=tree.getroot();r.set('role','img');r.set('aria-labelledby',stem+'-title '+stem+'-desc')
    for tag,text in [('title',title),('desc',description)]:
        node=ET.Element('{'+ns+'}'+tag,id=stem+'-'+tag);node.text=text;r.insert(0,node)
    tree.write(out/(stem+'.svg'),encoding='utf-8',xml_declaration=True)


def labels(y,n):
    y=np.asarray(y)
    if y.shape!=(n,) or not np.all(np.isin(y,[0,1])):raise ValueError('Use one binary label per row.')
    return y.astype(float)


def sigmoid(a):
    a=np.asarray(a,dtype=float)
    return np.exp(-np.logaddexp(0,-a))


def settings(steps,rate):
    if not isinstance(steps,int) or not 1<=steps<=10000:raise ValueError('Use 1 to 10000 training steps.')
    if not np.isfinite(rate) or not 0<rate<=1:raise ValueError('Learning rate must be finite in (0, 1].')


def fit_logistic(x,y,steps=2500,rate=.08,penalty=.001):
    settings(steps,rate);x=matrix(x);y=labels(y,len(x))
    if x.shape[1]!=2:raise ValueError('This teaching classifier expects exactly two features.')
    if not np.isfinite(penalty) or penalty<0:raise ValueError('Penalty must be finite and nonnegative.')
    w=np.zeros(2);b=0.;history=[]
    for step in range(steps+1):
        a=x@w+b;loss=float(np.mean(np.logaddexp(0,a)-y*a)+penalty/2*np.sum(w*w));d=(sigmoid(a)-y)/len(x)
        if not np.isfinite(loss):raise RuntimeError('Training produced nonfinite loss.')
        if step%50==0 or step==steps:history.append((step,loss))
        if step<steps:w-=rate*(x.T@d+penalty*w);b-=rate*d.sum()
    return (w,b),np.array(history)


def metrics(y,probability,threshold=.5):
    p=np.asarray(probability,dtype=float)
    if p.ndim!=1 or len(p)<1 or not np.all(np.isfinite(p)) or np.any((p<0)|(p>1)):
        raise ValueError('Use a finite nonempty vector of scores between zero and one.')
    y=labels(y,len(p)).astype(int)
    if not np.isfinite(threshold) or not 0<=threshold<=1:raise ValueError('Threshold must be in [0, 1].')
    predicted=(p>=threshold).astype(int);cm=np.zeros((2,2),dtype=int)
    for actual,guess in zip(y,predicted):cm[actual,guess]+=1
    tn,fp,fn,tp=cm.ravel();precision=float(tp/(tp+fp)) if tp+fp else None;recall=float(tp/(tp+fn)) if tp+fn else None
    return {'threshold':float(threshold),'confusion_rows_actual_cols_predicted':cm.tolist(),'accuracy':float((tp+tn)/len(y)),'precision_class1':precision,'recall_class1':recall,'sample_count':len(y)}


def make_data():
    rng=np.random.default_rng(2704);n=150
    temperature=np.repeat([40.,70.],n//2)+rng.normal(0,5,n)
    dwell=rng.uniform(1,5,n)
    x=np.column_stack([temperature,dwell])
    measured=2+.04*temperature+1.2*dwell+.7*rng.normal(size=n)
    success=(measured>=8.).astype(int)
    order=rng.permutation(n)
    return x,measured,success,order[:100],order[100:]


def fit_regression(x,y):
    x=matrix(x,3);y=np.asarray(y,dtype=float)
    if x.shape[1]!=2 or y.shape!=(len(x),) or not np.all(np.isfinite(y)):
        raise ValueError('Use two finite features and one finite response per row.')
    design=np.column_stack([np.ones(len(x)),x]);coef,_,rank,_=np.linalg.lstsq(design,y,rcond=None)
    if rank!=3:raise ValueError('The intercept and two slopes require full column rank.')
    return coef


def run(output_dir=None):
    out=Path(output_dir) if output_dir else Path(__file__).resolve().parent;out.mkdir(parents=True,exist_ok=True)
    x,y,label,train,test=make_data()
    assert not set(train)&set(test) and len(set(train)|set(test))==len(x)
    coef=fit_regression(x[train],y[train]);pred=np.column_stack([np.ones(len(x)),x])@coef
    mean,scale=fit_standardizer(x[train]);z=(x-mean)/scale
    (w,b),history=fit_logistic(z[train],label[train],steps=1800,rate=.1,penalty=.001)
    probability=sigmoid(z[test]@w+b);score=metrics(label[test],probability)
    majority=int(label[train].mean()>.5);constant=metrics(label[test],np.full(len(test),majority))
    pc=fit_pca(z[train]);km=fit_two_centers(z[train]);components=pc['components']
    reconstructed=((z[train]-pc['center'])@components.T)@components+pc['center']
    assert np.allclose(reconstructed,z[train]) and np.allclose(components@components.T,np.eye(2))
    changed=x.copy();changed[test]+=1000
    mm,ss=fit_standardizer(changed[train]);assert np.array_equal(mm,mean) and np.array_equal(ss,scale)
    # Changing units (Celsius -> kelvin, minutes -> seconds) leaves standardized inputs unchanged.
    converted=x*np.array([1.,60.])+np.array([273.15,0.]);cm,cs=fit_standardizer(converted[train])
    assert np.allclose((converted-cm)/cs,z)
    assert metrics([0,1],[0,0])['precision_class1'] is None
    assert metrics([0,0],[.1,.2])['recall_class1'] is None
    assert metrics([1],[.5])['accuracy']==1.
    exact_x=np.array([[0,0],[1,0],[0,1],[1,1.]])
    assert np.allclose(fit_regression(exact_x,2+3*exact_x[:,0]+4*exact_x[:,1]),[2,3,4])
    assert history[-1,1]<history[0,1] and sum(map(sum,score['confusion_rows_actual_cols_predicted']))==len(test)
    rejected=0
    for fn in [lambda:fit_regression([[1,2],[1,3],[1,4]],[1,2,3]),lambda:fit_standardizer([[1,2],[1,3]]),lambda:metrics([0,2],[.1,.8]),lambda:fit_pca([[1,1],[1,1]]),lambda:fit_two_centers([[0,0],[0,0]])]:
        try:fn()
        except ValueError:rejected+=1
    assert rejected==5
    plt.rcParams.update({'font.size':18, 'axes.titlesize':18, 'legend.fontsize':18,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(1,2,figsize=(9.2,4.8),layout='constrained')
    axs[0].scatter(y[test],pred[test],color='#176c7b',s=28)
    low=min(y[test].min(),pred[test].min())-.2;high=max(y[test].max(),pred[test].max())+.2
    axs[0].plot([low,high],[low,high],'--',color='#777');axs[0].set(xlabel='Measured yield (mg)',ylabel='Predicted yield (mg)',title='50 held-out runs',xlim=(low,high),ylim=(low,high),aspect='equal');axs[0].grid(alpha=.2)
    counts=np.array(score['confusion_rows_actual_cols_predicted']);axs[1].imshow(counts,cmap='Blues',vmin=0,vmax=max(counts.max(),1))
    for i in range(2):
        for j in range(2):axs[1].text(j,i,str(counts[i,j]),ha='center',va='center',fontsize=20,color='white' if counts[i,j]>.6*counts.max() else '#222')
    axs[1].set(xticks=[0,1],yticks=[0,1],xlabel='Predicted class\n(score >= 0.5)',ylabel='Actual class\n(yield >= 8 mg)',title='Same test runs')
    save(fig,out,'heldout-predictions','Continuous and binary predictions on fifty held-out experiment runs','The regression scatter compares predicted and measured synthetic yield in milligrams with an identity guide. The confusion matrix reports actual classes as rows and predicted classes as columns. Success means measured yield at least eight milligrams; measured yield is not an input feature. Both models were fitted only on one hundred training runs.')
    fig,axs=plt.subplots(1,2,figsize=(10,6.2),layout='constrained')
    low_center=np.argmin(km['centers'][:,0]);colors=np.where(km['labels']==low_center,'#176c7b','#b46d27')
    for group,marker,color in [(low_center,'o','#176c7b'),(1-low_center,'s','#b46d27')]:
        members=km['labels']==group
        axs[0].scatter(z[train][members,0],z[train][members,1],color=color,marker=marker,s=35,label='Group '+('1' if group==low_center else '2'))
    axs[0].scatter(km['centers'][:,0],km['centers'][:,1],marker='X',s=110,color='#222',edgecolors='white',label='Centers')
    direction=components[0]*1.6;mid=pc['center'];axs[0].plot([mid[0]-direction[0],mid[0]+direction[0]],[mid[1]-direction[1],mid[1]+direction[1]],'k--',label='PC1')
    axs[0].set(title='Training groups + PCA');axs[0].legend(fontsize=18,frameon=False,ncol=2,loc='upper center',bbox_to_anchor=(.5,-.24),columnspacing=.8,handletextpad=.3)
    gx,gy=np.meshgrid(np.linspace(-2.5,2.5,120),np.linspace(-2.5,2.5,120));grid=np.column_stack([gx.ravel(),gy.ravel()]);p=sigmoid(grid@w+b).reshape(gx.shape)
    contour=axs[1].contourf(gx,gy,p,levels=np.linspace(0,1,11),cmap='RdBu_r',alpha=.65);axs[1].contour(gx,gy,p,levels=[.5],colors='#222')
    for actual,marker,color in [(0,'o','#2166ac'),(1,'^','#b2182b')]:
        rows=label[test]==actual
        axs[1].scatter(z[test][rows,0],z[test][rows,1],color=color,marker=marker,edgecolors='#222',s=45,label=f'Class {actual}')
    axs[1].set(title='Actual test classes');axs[1].legend(fontsize=18,frameon=False,ncol=2,loc='upper center',bbox_to_anchor=(.5,-.24),columnspacing=.8,handletextpad=.3)
    for ax in axs:ax.set(xlabel='Temperature (train SD)',ylabel='Dwell time (train SD)',xlim=(-2.5,2.5),ylim=(-2.5,2.5),aspect='equal');ax.grid(alpha=.15)
    fig.colorbar(contour,ax=axs[1],label='Class-1 model score',shrink=.8)
    save(fig,out,'projection-groups-classification','Projection and grouping are different from predicting success','Left: one hundred standardized training inputs colored and marked by two-center membership, with X symbols for centers and a dashed first principal direction. These cluster colors do not encode success labels. Right: fifty test settings colored and marked by actual success, over a logistic model score background fitted on training labels. The horizontal and vertical units are training standard deviations. A grid extending beyond observed settings does not establish extrapolation accuracy.')
    report={'split':{'train':len(train),'test':len(test),'training_class_counts':np.bincount(label[train],minlength=2).tolist(),'test_class_counts':np.bincount(label[test],minlength=2).tolist()},'regression':{'coefficients_intercept_mg_temperature_mg_per_C_dwell_mg_per_min':coef.tolist(),'test_RMSE_mg':rmse(y[test],pred[test]),'training_mean_baseline_test_RMSE_mg':rmse(y[test],np.full(len(test),y[train].mean()))},'classification':score,'constant_training_majority_class':majority,'constant_baseline':constant,'pca_first_variance_fraction':float(pc['variance_ratio'][0]),'training_scaler':{'mean_C_min':mean.tolist(),'scale_C_min':scale.tolist()},'classification_training_loss':{'initial':float(history[0,1]),'final':float(history[-1,1])},'checks':{'disjoint_complete_split':True,'heldout_changes_do_not_change_scaler':True,'unit_conversion_standardization_invariant':True,'exact_plane_recovered':True,'PCA_orthogonality_and_full_reconstruction':True,'undefined_precision_recall_explicit':True,'threshold_equality_positive':True,'cluster_objective_nonincreasing':True,'invalid_inputs_rejected':rejected}}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(run(),indent=2))
