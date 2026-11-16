"""Original small NumPy classification comparison; no deep-learning dependency.
Two synthetic rings, frozen balanced split, training-only scaling, linear logistic
baseline and trained 2 -> 8 tanh -> 1 sigmoid network. Not historical NN evidence.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def matrix(x):
    x=np.asarray(x,dtype=float)
    if x.ndim!=2 or x.shape[1]!=2 or len(x)<1 or not np.all(np.isfinite(x)):
        raise ValueError('Use finite rows with exactly two features.')
    return x


def labels(y,n):
    y=np.asarray(y)
    if y.shape!=(n,) or not np.all(np.isin(y,[0,1])):raise ValueError('Use one binary label per row.')
    return y.astype(float)


def make_data():
    rng=np.random.default_rng(6601);x=[];y=[];train=[];test=[]
    for cls,radius in [(0,.65),(1,1.45)]:
        angle=rng.uniform(0,2*np.pi,120);r=radius+.12*rng.normal(size=120)
        x.append(np.column_stack([r*np.cos(angle),r*np.sin(angle)]));y.extend([cls]*120)
        order=rng.permutation(120)+cls*120;train.extend(order[:80]);test.extend(order[80:])
    return np.vstack(x),np.array(y),np.array(train),np.array(test)


def standardize_fit(x):
    x=matrix(x);mean=x.mean(axis=0);scale=x.std(axis=0)
    if np.any(scale<=1e-12):raise ValueError('Both training features must vary.')
    return mean,scale


def sigmoid(a):
    a=np.asarray(a,dtype=float)
    return np.exp(-np.logaddexp(0,-a))


def init_network(seed=73,hidden=8):
    if not isinstance(hidden,int) or not 1<=hidden<=32:raise ValueError('Use 1 to 32 hidden units.')
    rng=np.random.default_rng(seed)
    return {'W1':rng.normal(0,.45,(2,hidden)),'b1':np.zeros(hidden),'W2':rng.normal(0,.45,hidden),'b2':np.array(0.)}


def forward(x,p):
    x=matrix(x);h=np.tanh(x@p['W1']+p['b1']);a=h@p['W2']+p['b2']
    return h,a


def network_loss_gradient(x,y,p,penalty=.001):
    x=matrix(x);y=labels(y,len(x))
    if not np.isfinite(penalty) or penalty<0:raise ValueError('Penalty must be finite and nonnegative.')
    h,a=forward(x,p);loss=np.mean(np.logaddexp(0,a)-y*a)+penalty/2*(np.sum(p['W1']**2)+np.sum(p['W2']**2))
    d=(sigmoid(a)-y)/len(x)
    hidden_derivative=d[:,None]*p['W2'][None,:]*(1-h*h)
    gradients={'W2':h.T@d+penalty*p['W2'],'b2':np.array(d.sum()),'W1':x.T@hidden_derivative+penalty*p['W1'],'b1':hidden_derivative.sum(axis=0)}
    return float(loss),gradients


def settings(steps,rate):
    if not isinstance(steps,int) or not 1<=steps<=10000:raise ValueError('Use 1 to 10000 training steps.')
    if not np.isfinite(rate) or not 0<rate<=1:raise ValueError('Learning rate must be finite in (0, 1].')


def fit_network(x,y,steps=2500,rate=.08,penalty=.001):
    settings(steps,rate);x=matrix(x);y=labels(y,len(x));p=init_network();history=[]
    for step in range(steps+1):
        loss,g=network_loss_gradient(x,y,p,penalty)
        if not np.isfinite(loss):raise RuntimeError('Training produced nonfinite loss.')
        if step%50==0 or step==steps:history.append((step,loss))
        if step<steps:
            for key in p:p[key]-=rate*g[key]
    return p,np.array(history)


def fit_logistic(x,y,steps=2500,rate=.08,penalty=.001):
    settings(steps,rate);x=matrix(x);y=labels(y,len(x))
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


def gradient_check():
    # Independent central finite differences of the scalar loss for every parameter.
    x=np.array([[-.7,.3],[.2,-.4],[1.,.5],[-.1,.8]]);y=np.array([0,1,1,0]);p=init_network(hidden=3)
    _,analytic=network_loss_gradient(x,y,p);maximum=0.;eps=1e-6
    for key in p:
        for idx in np.ndindex(p[key].shape):
            old=float(p[key][idx]);p[key][idx]=old+eps;plus=network_loss_gradient(x,y,p)[0]
            p[key][idx]=old-eps;minus=network_loss_gradient(x,y,p)[0];p[key][idx]=old
            maximum=max(maximum,abs((plus-minus)/(2*eps)-analytic[key][idx]))
    assert maximum<1e-7
    return maximum


def save(fig,out,stem,title,description):
    for ext in ('svg','pdf'):fig.savefig(out/(stem+'.'+ext),bbox_inches='tight')
    plt.close(fig);ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns)
    tree=ET.parse(out/(stem+'.svg'));r=tree.getroot();r.set('role','img');r.set('aria-labelledby',stem+'-title '+stem+'-desc')
    for tag,text in [('title',title),('desc',description)]:
        node=ET.Element('{'+ns+'}'+tag,id=stem+'-'+tag);node.text=text;r.insert(0,node)
    tree.write(out/(stem+'.svg'),encoding='utf-8',xml_declaration=True)


def run(output_dir=None):
    out=Path(output_dir) if output_dir else Path(__file__).resolve().parent;out.mkdir(parents=True,exist_ok=True)
    x,y,train,test=make_data();assert not set(train)&set(test) and len(set(train)|set(test))==len(x)
    mean,scale=standardize_fit(x[train]);z=(x-mean)/scale
    linear,lh=fit_logistic(z[train],y[train]);network,nh=fit_network(z[train],y[train]);w,b=linear
    # Evaluate the frozen models once on test rows; do not select settings with these values.
    lp=sigmoid(z[test]@w+b);npred=sigmoid(forward(z[test],network)[1]);lm=metrics(y[test],lp);nm=metrics(y[test],npred)
    # Transparent comparisons: a tied training majority chooses class 0.
    constant=metrics(y[test],np.zeros(len(test)))
    radii=np.linalg.norm(x,axis=1)
    radial_threshold=.5*(radii[train][y[train]==0].mean()+radii[train][y[train]==1].mean())
    radial=metrics(y[test],(radii[test]>=radial_threshold).astype(float))
    assert nh[-1,1]<nh[0,1] and lh[-1,1]<=lh[0,1]
    assert sum(sum(row) for row in nm['confusion_rows_actual_cols_predicted'])==len(test)
    assert metrics([0,1],[0,0])['precision_class1'] is None
    assert metrics([0,0],[.2,.3])['recall_class1'] is None
    assert metrics([1],[.5])['confusion_rows_actual_cols_predicted']==[[0,0],[0,1]]
    # Changing held-out rows cannot affect training-only normalization.
    changed=x.copy();changed[test]+=1000
    cm,cs=standardize_fit(changed[train]);assert np.array_equal(cm,mean) and np.array_equal(cs,scale)
    grad_error=gradient_check();rejected=0
    for fn in [lambda:metrics([0,1],[.2,np.nan]),lambda:metrics([0,1],[.2,.3],1.1),lambda:fit_network(z[train],y[train],steps=0),lambda:standardize_fit([[1,2],[1,3]])]:
        try:fn()
        except ValueError:rejected+=1
    assert rejected==4
    plt.rcParams.update({'font.size':20,'axes.titlesize':20,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    axis=np.linspace(-2,2,120);gx,gy=np.meshgrid(axis,axis);points=np.column_stack([gx.ravel(),gy.ravel()]);zg=(points-mean)/scale
    grid_scores=[sigmoid(zg@w+b),sigmoid(forward(zg,network)[1])]
    fig,axs=plt.subplots(1,2,figsize=(10.5,6.0),sharex=True,sharey=True,layout='constrained')
    for ax,score,title in zip(axs,grid_scores,['Linear logistic','2 → 8 → 1 network']):
        contour=ax.contourf(gx,gy,score.reshape(gx.shape),levels=np.linspace(0,1,11),cmap='RdBu_r',alpha=.65)
        ax.contour(gx,gy,score.reshape(gx.shape),levels=[.5],colors='#333',linewidths=1.2)
        for cls,marker in [(0,'o'),(1,'^')]:
            selected=test[y[test]==cls]
            ax.scatter(x[selected,0],x[selected,1],color=plt.get_cmap('RdBu_r')(float(cls)),marker=marker,edgecolors='#222',s=40,label=f'True class {cls}')
        ax.set(xlabel='Sensor 1 (unitless)',title=title,aspect='equal')
    axs[0].set_ylabel('Sensor 2 (unitless)');fig.colorbar(contour,ax=axs,label='Class-1 score',shrink=.8)
    fig.legend(*axs[0].get_legend_handles_labels(),loc='outside lower center',ncol=2,fontsize=20,frameon=False)
    save(fig,out,'decision-comparison','Linear and neural decision functions on held-out synthetic rings','Both models use the same training rows, scaling and frozen settings. Background color is a class-one score, dark contours mark threshold one-half, and points are eighty held-out observations with circle and triangle shapes as well as color indicating the true classes in the separate key. A curved boundary can represent the ring relation; the score map does not establish probability calibration or real-world performance.')
    fig,axs=plt.subplots(1,3,figsize=(11.5,4.8),gridspec_kw={'width_ratios':[1.3,1,1]},layout='constrained')
    axs[0].plot(lh[:,0],lh[:,1],label='Linear',color='#176c7b');axs[0].plot(nh[:,0],nh[:,1],label='Network',color='#b46d27');axs[0].set(xlabel='Training step',ylabel='BCE + penalty',title='Training objective');axs[0].legend(frameon=False,fontsize=20);axs[0].grid(alpha=.2)
    for ax,report,title in zip(axs[1:],[lm,nm],['Linear test','Network test']):
        counts=np.array(report['confusion_rows_actual_cols_predicted']);ax.imshow(counts,cmap='Blues',vmin=0,vmax=40)
        for i in range(2):
            for j in range(2):ax.text(j,i,str(counts[i,j]),ha='center',va='center',color='white' if counts[i,j]>24 else '#111',fontsize=24)
        ax.set(xticks=[0,1],yticks=[0,1],xlabel='Predicted',ylabel='Actual',title=title)
    save(fig,out,'loss-and-confusion','Training objectives and held-out confusion counts','Training curves use no test labels. Each confusion matrix has actual classes as rows and predicted classes as columns, with forty test examples of each class. Training loss and held-out error are distinct evidence. Fixed architecture and settings were not selected by the test score.')
    report={'data':{'train':len(train),'test':len(test),'train_class_counts':np.bincount(y[train]).tolist(),'test_class_counts':np.bincount(y[test]).tolist(),'scaling_fit':'training rows only'},'settings':{'steps':2500,'learning_rate':.08,'weight_penalty':.001,'hidden_units':8,'network_parameters':sum(v.size for v in network.values())},'linear_test':lm,'network_test':nm,'constant_class0_test':constant,'optional_radius_rule':{'threshold_dimensionless':float(radial_threshold),'test':radial,'meaning':'A supplied scientific feature can replace a learned representation; this rule is fitted only using training labels.'},'training_objective':{'linear_initial':float(lh[0,1]),'linear_final':float(lh[-1,1]),'network_initial':float(nh[0,1]),'network_final':float(nh[-1,1])},'checks':{'disjoint_split':True,'test_mutation_does_not_change_training_scaler':True,'finite_difference_max_gradient_error':grad_error,'undefined_precision_and_recall_explicit':True,'threshold_equality_is_positive':True,'invalid_inputs_rejected':rejected}}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(run(),indent=2))
