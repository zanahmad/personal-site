"""Original grouped-data counterexample. Same test cases and training row count.
Leaky means invalid for the stated target of previously unseen groups.
"""
from pathlib import Path
import json,html
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def make_data(seed=151):
    rng=np.random.default_rng(seed);group_y=rng.permutation(np.repeat([0,1],60));signal=.7*(2*group_y-1)+rng.normal(0,1.1,120);fingerprints=rng.normal(size=(120,8))
    stable=np.column_stack((signal,fingerprints));groups=np.repeat(np.arange(120),4);visits=np.tile(np.arange(4),120)
    x=stable[groups]+rng.normal(0,.04,(480,9));y=group_y[groups]
    # Split by group, stratified only to make the 40-case teaching comparison balanced.
    test_groups=np.r_[np.flatnonzero(group_y==0)[:20],np.flatnonzero(group_y==1)[:20]]
    proper_groups=np.setdiff1d(np.arange(120),test_groups)
    remaining_half=np.r_[proper_groups[group_y[proper_groups]==0][:20],proper_groups[group_y[proper_groups]==1][:20]]
    leaky_groups=np.r_[remaining_half,test_groups]
    test=np.flatnonzero(np.isin(groups,test_groups)&(visits==3))
    proper=np.flatnonzero(np.isin(groups,proper_groups)&(visits<3));leaky=np.flatnonzero(np.isin(groups,leaky_groups)&(visits<3))
    return x,y,groups,{'proper':proper,'leaky':leaky,'test':test}


def audit_split(groups,train,test,require_disjoint=True):
    g=np.asarray(groups);tr=np.asarray(train);te=np.asarray(test)
    if g.ndim!=1 or tr.ndim!=1 or te.ndim!=1 or not len(tr) or not len(te) or not np.issubdtype(tr.dtype,np.integer) or not np.issubdtype(te.dtype,np.integer) or min(tr.min(),te.min())<0 or max(tr.max(),te.max())>=len(g):raise ValueError('Use nonempty valid integer row-index vectors and one group per row.')
    if len(np.unique(tr))!=len(tr) or len(np.unique(te))!=len(te) or np.intersect1d(tr,te).size:raise ValueError('Rows must be unique and train/test row indices disjoint.')
    overlap=np.intersect1d(g[tr],g[te])
    if require_disjoint and len(overlap):raise ValueError('Group overlap violates the unseen-group target.')
    return {'training_rows':len(tr),'test_rows':len(te),'training_groups':len(np.unique(g[tr])),'test_groups':len(np.unique(g[te])),'overlap_groups':len(overlap)}


def fit_scale(x):
    x=np.asarray(x,float)
    if x.ndim!=2 or len(x)<2 or x.shape[1]==0 or not np.isfinite(x).all():raise ValueError('Use finite training feature rows.')
    mean=x.mean(0);sd=x.std(0);return mean,np.where(sd>0,sd,1.)


def fit_logistic(x,y,l2=.01):
    x=np.asarray(x,float);y=np.asarray(y,float)
    if x.ndim!=2 or len(x)<2 or x.shape[1]==0 or y.shape!=(len(x),) or not np.isfinite(x).all() or not np.isfinite(y).all() or set(y.tolist())!={0.,1.} or not np.isfinite(l2) or l2<=0:raise ValueError('Use finite training rows, both binary labels and positive L2.')
    def loss(t):
        z=x@t[:-1]+t[-1];res=expit(z)-y
        return np.mean(np.logaddexp(0,z)-y*z)+l2*(t[:-1]@t[:-1])/2,np.r_[x.T@res/len(y)+l2*t[:-1],res.mean()]
    fitted=minimize(loss,np.zeros(x.shape[1]+1),jac=True,method='L-BFGS-B',options={'gtol':1e-9,'ftol':1e-12})
    if not fitted.success:raise RuntimeError(fitted.message)
    return fitted.x


def nearest_labels(train_x,train_y,test_x):
    a=np.asarray(train_x,float);b=np.asarray(test_x,float);y=np.asarray(train_y)
    if a.ndim!=2 or b.ndim!=2 or not len(a) or not len(b) or a.shape[1]!=b.shape[1] or y.shape!=(len(a),) or not np.isfinite(a).all() or not np.isfinite(b).all() or not np.isin(y,[0,1]).all():raise ValueError('Use compatible finite feature rows and binary training labels.')
    distances=((b[:,None,:]-a[None,:,:])**2).sum(2);return y[np.argmin(distances,axis=1)]


def confusion(y,pred):
    y=np.asarray(y);p=np.asarray(pred)
    if y.ndim!=1 or y.size==0 or p.shape!=y.shape or not np.isin(y,[0,1]).all() or not np.isin(p,[0,1]).all():raise ValueError('Use nonempty equal-size binary vectors.')
    cm=np.array([[np.sum((y==i)&(p==j)) for j in (0,1)] for i in (0,1)])
    recall=[None if cm[i].sum()==0 else float(cm[i,i]/cm[i].sum()) for i in (0,1)]
    return {'confusion_true_rows_predicted_columns':cm.tolist(),'accuracy':float(np.mean(y==p)),'recall_class0':recall[0],'recall_class1':recall[1],'balanced_accuracy':None if any(v is None for v in recall) else float(np.mean(recall))}


def evaluate(x,y,groups,splits):
    test=splits['test'];report={}
    for name in ('proper','leaky'):
        tr=splits[name];audit=audit_split(groups,tr,test,require_disjoint=name=='proper');mean,sd=fit_scale(x[tr]);tx=(x[tr]-mean)/sd;vx=(x[test]-mean)/sd
        theta=fit_logistic(tx[:,:1],y[tr]);log_pred=expit(vx[:,:1]@theta[:-1]+theta[-1])>=.5
        prior=np.mean(y[tr]);dummy=np.repeat(int(prior>.5),len(test)) # class0 on a tie
        preds={'constant':dummy,'signal_logistic':log_pred,'all_feature_1nn':nearest_labels(tx,y[tr],vx)}
        report[name]={'audit':audit,'scaler_mean':mean.tolist(),'scaler_sd':sd.tolist(),'training_prior':float(prior),'models':{key:confusion(y[test],pred) for key,pred in preds.items()}}
    return report


def save(fig,out,stem,title,desc):
    for ext in ('svg','pdf'):fig.savefig(out/f'{stem}.{ext}',bbox_inches='tight',metadata={'Date':None} if ext=='svg' else {'CreationDate':None})
    p=out/f'{stem}.svg';s=p.read_text();i=s.index('>',s.index('<svg'))+1;p.write_text(s[:i]+f'<title>{html.escape(title)}</title><desc>{html.escape(desc)}</desc>'+s[i:]);plt.close(fig)


def run(output_dir=None):
    out=Path(output_dir or Path(__file__).parent);out.mkdir(parents=True,exist_ok=True);plt.rcParams.update({'font.size':20,'axes.titlesize':22,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    x,y,g,s=make_data();report=evaluate(x,y,g,s)
    fig,axs=plt.subplots(1,2,figsize=(10.4,4.9),constrained_layout=True)
    for ax,name,title in zip(axs,['proper','leaky'],['Unseen-group protocol','Seen-group contamination']):
        ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off');ax.set_title(title)
        labels=['TRAIN: 80 groups\n3 visits each','TEST: 40 groups\n1 visit each']
        for yy,lab,color in zip([.58,.12],labels,['#e0f2f1','#edf0f4']):
            ax.add_patch(FancyBboxPatch((.04,yy),.92,.27,boxstyle='round,pad=.015',facecolor=color,edgecolor='#264653',lw=1.5));ax.text(.5,yy+.135,lab,ha='center',va='center',fontsize=20)
        ax.text(.5,.455,f'{report[name]["audit"]["overlap_groups"]} group IDs overlap',ha='center',va='center',fontsize=20,color='#9a4d15' if name=='leaky' else '#087e8b')
    save(fig,out,'group-protocol','A group audit with matched row counts','Both training sets have 240 rows from 80 groups; the identical 40 final-visit test rows represent 40 groups. The proper training set has no test-group overlap. The deliberately contaminated set replaces 40 proper training groups with the 40 test groups and uses only their other visits. Test row IDs remain disjoint in both cases.')
    fig,ax=plt.subplots(figsize=(9.3,4.8),constrained_layout=True);labels=['Constant\nclass 0','Signal-only\nlogistic','All-feature\n1-neighbor'];positions=np.arange(3)
    for offset,name,color,label in [(-.18,'proper','#087e8b','Unseen groups'),(.18,'leaky','#b56d23','Contaminated')]:
        vals=[report[name]['models'][key]['accuracy'] for key in ('constant','signal_logistic','all_feature_1nn')];bars=ax.bar(positions+offset,vals,width=.34,color=color,label=label)
        ax.bar_label(bars,labels=[f'{v:.3f}' for v in vals],padding=3,fontsize=20)
    ax.set(xticks=positions,xticklabels=labels,ylabel='Accuracy on same 40 cases',ylim=(0,1.25));ax.set_yticks([0,.25,.5,.75,1]);ax.legend(ncol=2,fontsize=20,loc='upper left');ax.grid(axis='y',alpha=.15)
    save(fig,out,'baseline-comparison','The apparent benefit of recognizing already-seen groups','Accuracy of three transparent baselines under matched 240-row training sets and identical 40-case balanced test data. Eight stable synthetic fingerprint features contain no population outcome signal but identify groups when another visit is present. Bars are one deterministic teaching realization, not confidence intervals or clinical evidence.')
    assert report['proper']['audit']['overlap_groups']==0 and report['leaky']['audit']['overlap_groups']==40
    assert report['proper']['audit']['training_rows']==report['leaky']['audit']['training_rows']==240
    try:audit_split(g,s['leaky'],s['test'])
    except ValueError:pass
    else:raise AssertionError('Leaky split was accepted')
    # Test-only perturbation must not change fit-time statistics.
    altered=x.copy();altered[s['test']]+=1000;m2,sd2=fit_scale(altered[s['proper']]);np.testing.assert_allclose(m2,report['proper']['scaler_mean']);np.testing.assert_allclose(sd2,report['proper']['scaler_sd'])
    np.testing.assert_array_equal(nearest_labels([[0],[2]],[0,1],[[.1],[1.9]]),[0,1])
    report['checks']={'matched_training_rows':True,'identical_test_cases':True,'disjoint_test_row_ids_both_protocols':True,'proper_group_disjointness':True,'leaky_split_rejected_when_guard_enabled':True,'test_perturbation_does_not_change_scaler':True,'nearest_neighbor_known_case':True}
    report['data_definition']='120 synthetic groups; four repeated rows each; stable binary group outcome; one weak signal and eight independent group fingerprint features; no clinical meanings.'
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');np.savez(out/'grouped-data.npz',x=x,y=y,group=g,proper_train=s['proper'],leaky_train=s['leaky'],test=s['test']);return report

if __name__=='__main__':
    r=run();print(json.dumps({k:{'audit':r[k]['audit'],'models':r[k]['models']} for k in ('proper','leaky')},indent=2))
