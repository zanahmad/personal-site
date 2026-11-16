"""Original synthetic calibration and classification workshop; no patient data."""
from pathlib import Path
import json,html
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def fit_conductance(pressure_drop,flow):
    x=np.asarray(pressure_drop,float);y=np.asarray(flow,float)
    if x.ndim!=1 or y.shape!=x.shape or len(x)<2 or not np.isfinite(x).all() or not np.isfinite(y).all():raise ValueError('Use matching finite vectors with at least two observations.')
    if np.any(x<0) or np.any(y<0) or np.max(x)<=0:raise ValueError('Use nonnegative observations with at least one positive pressure difference.')
    g=float(np.linalg.lstsq(x[:,None],y,rcond=None)[0][0])
    if not np.isfinite(g) or g<=0:raise ValueError('A positive conductance cannot be identified from these observations.')
    return g


def fit_centroids(features,labels):
    x=np.asarray(features,float);y=np.asarray(labels)
    if x.ndim!=2 or x.shape[1]!=2 or y.shape!=(len(x),) or not np.isfinite(x).all() or set(y.tolist())!={0,1}:raise ValueError('Use finite two-feature rows with both class labels0 and1.')
    mean=x.mean(axis=0);scale=x.std(axis=0)
    if np.any(scale<=1e-12):raise ValueError('Both training features must vary.')
    z=(x-mean)/scale;centers=np.array([z[y==k].mean(axis=0) for k in (0,1)])
    return {'mean':mean,'scale':scale,'centers':centers}


def predict_centroids(model,features):
    x=np.asarray(features,float)
    if x.ndim!=2 or x.shape[1]!=2 or not np.isfinite(x).all():raise ValueError('Use finite two-feature rows.')
    z=(x-model['mean'])/model['scale'];d=((z[:,None,:]-model['centers'][None,:,:])**2).sum(axis=2)
    return np.argmin(d,axis=1)


def cases(seed=8):
    rng=np.random.default_rng(seed)
    x=np.vstack([rng.normal([70,22],[9,14],size=(40,2)),rng.normal([90,48],[9,14],size=(40,2))]);y=np.repeat([0,1],40)
    x=np.maximum(x,[1.,1.])  # Positive rate and interval-variation features; synthetic floor.
    # Split case IDs before fitting or scaling; each generated case has one row.
    train=np.r_[np.arange(24),np.arange(40,64)];test=np.r_[np.arange(24,40),np.arange(64,80)]
    return x,y,train,test


def save(fig,out,stem,title,desc):
    for ext in ('svg','pdf'):fig.savefig(out/f'{stem}.{ext}',bbox_inches='tight',metadata={'Date':None} if ext=='svg' else {'CreationDate':None})
    p=out/f'{stem}.svg';s=p.read_text();i=s.index('>',s.index('<svg'))+1;p.write_text(s[:i]+'<title>'+html.escape(title)+'</title><desc>'+html.escape(desc)+'</desc>'+s[i:]);plt.close(fig)


def run(output_dir=None):
    out=Path(output_dir or Path(__file__).parent);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':20,'axes.titlesize':20,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    train_x=np.array([20.,40.,60.,80.]);train_y=np.array([1.1,1.9,3.1,3.9]);test_x=np.array([30.,70.,90.]);test_y=np.array([1.4,3.6,4.4]);g=fit_conductance(train_x,train_y)
    pred=g*test_x;mae=float(np.mean(abs(pred-test_y)))
    fig,ax=plt.subplots(figsize=(8.2,4.9),constrained_layout=True);xx=np.linspace(0,100,101)
    ax.plot(xx,g*xx,color='#087e8b',label='Fit using training data');ax.scatter(train_x,train_y,s=85,label='Training',color='#18384a');ax.scatter(test_x,test_y,marker='^',s=105,label='Held out',color='#b16a20')
    ax.set(xlabel='Pressure difference (mmHg)',ylabel='Flow (L/min)',title='Calibrate one passive flow law');ax.legend(loc='upper left',fontsize=18);ax.grid(alpha=.15)
    save(fig,out,'calibration','Calibrate conductance from synthetic measurements','Four training observations determine a through-origin pressure-flow law. Three held-out observations assess prediction error. All observations are synthetic.')
    x,y,train,test=cases();model=fit_centroids(x[train],y[train]);guess=predict_centroids(model,x[test]);cm=np.array([[np.sum((y[test]==a)&(guess==b)) for b in (0,1)] for a in (0,1)])
    fig,ax=plt.subplots(figsize=(8.4,5.0),constrained_layout=True);z=(x-model['mean'])/model['scale']
    for k,col in [(0,'#087e8b'),(1,'#b16a20')]:
        a=train[y[train]==k];b=test[y[test]==k];ax.scatter(z[a,0],z[a,1],c=col,s=60,label=f'Train regime {k}');ax.scatter(z[b,0],z[b,1],c=col,s=90,marker='^',edgecolors='black',linewidths=.6,label=f'Test regime {k}')
    ax.scatter(model['centers'][:,0],model['centers'][:,1],c='black',s=160,marker='X',label='Training centers')
    ax.set(xlabel='Rate feature (training SD units)',ylabel='Interval-variation feature\n(training SD units)',title='Two synthetic regimes; no diagnosis');ax.legend(fontsize=18,loc='upper left',bbox_to_anchor=(1.01,1));ax.grid(alpha=.15)
    save(fig,out,'classification','Compare synthetic feature regimes','Training means and scales define two standardized coordinates. Class centroids use only training data. Triangles are held-out cases; labels describe synthetic regimes, not medical diagnoses.')
    assert set(train).isdisjoint(test);assert cm.sum()==32
    assert abs(fit_conductance([20,40],[1,2])-.05)<1e-12
    assert abs(fit_conductance([40,80],[1,2])-.025)<1e-12
    assert np.array_equal(predict_centroids(model,x[test]),guess)
    invalid=0
    for a,b in [([0,0],[0,0]),([1,2],[0,0]),([1,float('nan')],[1,2]),([-1,2],[1,2])]:
        try:fit_conductance(a,b)
        except ValueError:invalid+=1
        else:raise AssertionError('Invalid calibration accepted')
    report={'conductance_L_min_mmHg':g,'resistance_mmHg_min_L':1/g,'held_out_flow_mae_L_min':mae,'classification_confusion_true_rows_predicted_columns':cm.tolist(),'classification_test_accuracy':float(np.mean(guess==y[test])),'training_cases':len(train),'test_cases':len(test),'checks':{'disjoint_case_ids':True,'exact_line_recovered':True,'unit_rescaling':True,'invalid_calibrations_rejected':invalid}}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(run(),indent=2))
