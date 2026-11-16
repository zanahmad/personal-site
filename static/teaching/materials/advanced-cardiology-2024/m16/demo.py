"""Original group-safe multimodal and calibration experiment.
Features A/B and outcomes are synthetic; they have no clinical interpretation.
"""
from pathlib import Path
import json,html
import numpy as np
from scipy.special import expit
from scipy.optimize import minimize, minimize_scalar
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def make_data(seed=161):
    rng=np.random.default_rng(seed);latent=rng.normal(size=(360,2));prob=expit(1.1*latent[:,0]+1.6*latent[:,1]-.2);gy=rng.binomial(1,prob)
    group=np.repeat(np.arange(360),2);x=latent[group]+rng.normal(size=(720,2))*[.65,.45];missing=rng.random(360)<.2;x[missing[group],1]=np.nan
    order=rng.permutation(360);splits={'train':order[:180],'validation':order[180:260],'test':order[260:]}
    return x,gy[group],group,splits


def prepare(x,mode,fit=None):
    a=np.asarray(x,float)
    if a.ndim!=2 or a.shape[1]!=2 or not len(a) or not np.isfinite(a[:,0]).all() or np.isinf(a[:,1]).any() or mode not in ('A','AB'):raise ValueError('Use nonempty A/B rows with finite A; only B may be NaN, and mode A or AB.')
    missing=np.isnan(a[:,1])
    if fit is None:
        if mode=='AB' and missing.all():raise ValueError('At least one observed training B value is required for the AB model.')
        median=float(np.nanmedian(a[:,1])) if mode=='AB' else 0.
        raw=a[:,:1] if mode=='A' else np.column_stack((a[:,0],np.where(missing,median,a[:,1]),missing.astype(float)))
        mean=raw.mean(0);sd=raw.std(0);sd=np.where(sd>0,sd,1.)
        fit={'mode':mode,'B_median':median,'mean':mean.tolist(),'sd':sd.tolist()}
    else:
        if fit.get('mode')!=mode:raise ValueError('Use the training transform for the same modality mode.')
        raw=a[:,:1] if mode=='A' else np.column_stack((a[:,0],np.where(missing,fit['B_median'],a[:,1]),missing.astype(float)))
        mean=np.asarray(fit['mean'],float);sd=np.asarray(fit['sd'],float)
        if mean.shape!=(raw.shape[1],) or sd.shape!=mean.shape or not np.isfinite(mean).all() or not np.isfinite(sd).all() or np.any(sd<=0) or not np.isfinite(fit['B_median']):raise ValueError('Invalid saved preprocessing parameters.')
    return (raw-mean)/sd,fit


def fit_logistic(x,y,l2=.01):
    a=np.asarray(x,float);y=np.asarray(y,float)
    if a.ndim!=2 or not len(a) or a.shape[1]==0 or y.shape!=(len(a),) or not np.isfinite(a).all() or not np.isfinite(y).all() or set(y.tolist())!={0.,1.} or not np.isfinite(l2) or l2<=0:raise ValueError('Use finite feature rows, both binary classes and positive L2.')
    def f(t):
        z=a@t[:-1]+t[-1];r=expit(z)-y
        return float(np.mean(np.logaddexp(0,z)-y*z)+l2*(t[:-1]@t[:-1])/2),np.r_[a.T@r/len(y)+l2*t[:-1],r.mean()]
    fit=minimize(f,np.zeros(a.shape[1]+1),jac=True,method='L-BFGS-B',options={'gtol':1e-9,'ftol':1e-12})
    if not fit.success:raise RuntimeError(fit.message)
    return fit.x


def group_scores(logits,y,groups):
    z=np.asarray(logits,float);y=np.asarray(y);g=np.asarray(groups)
    if z.ndim!=1 or z.size==0 or y.shape!=z.shape or g.shape!=z.shape or not np.isfinite(z).all() or not np.isin(y,[0,1]).all():raise ValueError('Use finite logit, binary label and group vectors of equal nonzero length.')
    ids=np.unique(g);scores=[];targets=[]
    for group in ids:
        take=g==group
        if len(np.unique(y[take]))!=1:raise ValueError('This lesson requires one stable outcome per group.')
        scores.append(float(z[take].mean()));targets.append(int(y[take][0]))
    return np.array(scores),np.array(targets),ids


def temperature_scale(logits,temperature=1.):
    z=np.asarray(logits,float)
    if z.ndim!=1 or not len(z) or not np.isfinite(z).all() or not np.isfinite(temperature) or temperature<=0:raise ValueError('Use finite logits and a finite positive temperature.')
    return expit(z/temperature)


def fit_temperature(logits,y):
    z=np.asarray(logits,float);y=np.asarray(y,float)
    if z.ndim!=1 or len(z)<2 or y.shape!=z.shape or not np.isfinite(z).all() or set(y.tolist())!={0.,1.}:raise ValueError('Use finite calibration logits with both binary classes.')
    if np.max(np.abs(z))<1e-14:raise ValueError('Temperature is unidentifiable when every logit is zero.')
    def loss(log_t):
        adjusted=z/np.exp(log_t);return float(np.mean(np.logaddexp(0,adjusted)-y*adjusted))
    fit=minimize_scalar(loss,bounds=(np.log(.2),np.log(5.)),method='bounded',options={'xatol':1e-10})
    if not fit.success:raise RuntimeError('Temperature optimization failed.')
    return float(np.exp(fit.x))


def evaluate_probabilities(y,p):
    y=np.asarray(y);p=np.asarray(p,float)
    if y.ndim!=1 or not len(y) or p.shape!=y.shape or not np.isin(y,[0,1]).all() or not np.isfinite(p).all() or np.any((p<0)|(p>1)):raise ValueError('Use equal nonempty binary-label and probability vectors.')
    pos=p[y==1];neg=p[y==0]
    auc=None if not len(pos) or not len(neg) else float(np.mean((pos[:,None]>neg[None,:])+.5*(pos[:,None]==neg[None,:])))
    safe=np.clip(p,1e-15,1-1e-15)
    bins=np.minimum((p*5).astype(int),4);curve=[]
    for b in range(5):
        take=bins==b;count=int(take.sum());curve.append({'bin':[b/5,(b+1)/5],'count':count,'mean_probability':None if not count else float(p[take].mean()),'event_fraction':None if not count else float(y[take].mean())})
    return {'groups':len(y),'events':int(y.sum()),'Brier':float(np.mean((p-y)**2)),'log_loss_clipped_1e_15':float(-np.mean(y*np.log(safe)+(1-y)*np.log1p(-safe))),'AUC':auc,'accuracy_at_0_5':float(np.mean((p>=.5)==y)),'reliability_bins':curve}


def save(fig,out,stem,title,desc):
    for ext in ('svg','pdf'):fig.savefig(out/f'{stem}.{ext}',bbox_inches='tight',metadata={'Date':None} if ext=='svg' else {'CreationDate':None})
    p=out/f'{stem}.svg';s=p.read_text();i=s.index('>',s.index('<svg'))+1;p.write_text(s[:i]+f'<title>{html.escape(title)}</title><desc>{html.escape(desc)}</desc>'+s[i:]);plt.close(fig)


def run(output_dir=None):
    out=Path(output_dir or Path(__file__).parent);out.mkdir(parents=True,exist_ok=True);plt.rcParams.update({'font.size':20,'axes.titlesize':21,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    x,y,g,s=make_data();masks={k:np.isin(g,ids) for k,ids in s.items()};models={};results={};test_predictions={};confidence_factor=2.5
    for mode in ('A','AB'):
        tr,prep=prepare(x[masks['train']],mode);theta=fit_logistic(tr,y[masks['train']]);va,_=prepare(x[masks['validation']],mode,prep)
        vz,vy,vg=group_scores(confidence_factor*(va@theta[:-1]+theta[-1]),y[masks['validation']],g[masks['validation']]);temperature=fit_temperature(vz,vy)
        te,_=prepare(x[masks['test']],mode,prep);tz,ty,tg=group_scores(confidence_factor*(te@theta[:-1]+theta[-1]),y[masks['test']],g[masks['test']]);raw=temperature_scale(tz);cal=temperature_scale(tz,temperature)
        models[mode]={'preprocessing':prep,'theta':theta.tolist(),'temperature':temperature};results[mode]={'before':evaluate_probabilities(ty,raw),'after':evaluate_probabilities(ty,cal)};test_predictions[mode]=cal
        np.testing.assert_allclose(results[mode]['before']['AUC'],results[mode]['after']['AUC'],atol=1e-12)
        assert results[mode]['before']['accuracy_at_0_5']==results[mode]['after']['accuracy_at_0_5']
    fig,axs=plt.subplots(1,2,figsize=(10.2,4.8),constrained_layout=True)
    for ax,key,title in zip(axs,['before','after'],['Sharpened AB scores','Validation-calibrated AB']):
        curve=results['AB'][key]['reliability_bins'];used=[b for b in curve if b['count']]
        ax.plot([0,1],[0,1],ls='--',color='#84939a');ax.plot([b['mean_probability'] for b in used],[b['event_fraction'] for b in used],'o-',color='#087e8b',lw=2.5)
        ax.set(xlim=(-.03,1.03),ylim=(-.03,1.03),xlabel='Mean predicted probability',ylabel='Observed event fraction',title=title,xticks=[0,.5,1],yticks=[0,.5,1]);ax.set_aspect('equal')
    save(fig,out,'calibration','Reliability before and after independent calibration','Reliability diagrams on the same 100 synthetic test groups. Five fixed probability bins are used; per-bin counts are preserved in results.json. The raw fitted group logits were deliberately multiplied by 2.5 for this teaching experiment. Temperature was fit on 80 separate validation groups, never these test labels. A connected line is descriptive, not proof of calibration between points.')
    rng=np.random.default_rng(162);drop_draw=rng.random(len(tg));stress=[]
    for fraction in (0.,.5,1.):
        shifted=x[masks['test']].copy();rowgroups=g[masks['test']];drop_groups=tg[drop_draw<fraction];shifted[np.isin(rowgroups,drop_groups),1]=np.nan
        arr,_=prepare(shifted,'AB',models['AB']['preprocessing']);theta=np.array(models['AB']['theta']);z,targets,ids=group_scores(confidence_factor*(arr@theta[:-1]+theta[-1]),y[masks['test']],rowgroups)
        p=temperature_scale(z,models['AB']['temperature']);missing_groups=sum(np.isnan(shifted[rowgroups==gid,1]).all() for gid in ids)
        stress.append({'additional_drop_fraction':fraction,'groups_without_B':int(missing_groups),'metrics':evaluate_probabilities(targets,p)})
    fig,ax=plt.subplots(figsize=(9.2,4.7),constrained_layout=True);positions=np.arange(3);values=[r['metrics']['Brier'] for r in stress];bars=ax.bar(positions,values,color=['#087e8b','#a47a39','#7b8992'],width=.6)
    ax.bar_label(bars,labels=[f'{v:.3f}' for v in values],padding=-26,fontsize=20,color='white');ax.axhline(results['A']['after']['Brier'],color='#8f3e54',ls='--',lw=2.5,label='Calibrated A only')
    ax.set(xticks=positions,xticklabels=[str(r['groups_without_B']) for r in stress],xlabel='Test groups without B (of 100)',ylabel='Brier score (lower is better)',ylim=(0,.32));ax.legend(fontsize=20,loc='upper left');ax.grid(axis='y',alpha=.15)
    save(fig,out,'missing-modality','Stress-test the frozen two-modality model','Test-group membership and labels are unchanged. Additional B measurements are removed in nested sets using a separate fixed seed. The training imputer, scale, model and calibration remain frozen. All cases remain in evaluation; the single-modality A model is unchanged. This probes only the specified missingness intervention.')
    assert not(set(s['train'])&set(s['validation']) or set(s['train'])&set(s['test']) or set(s['validation'])&set(s['test']))
    assert len(tg)==100 and stress[-1]['groups_without_B']==100
    assert evaluate_probabilities([0,1],[.5,.5])['AUC']==.5
    assert evaluate_probabilities([0,1],[0,1])['Brier']==0
    np.testing.assert_allclose(temperature_scale([-2,0,2],1),expit([-2,0,2]))
    report={'definition':'360 original synthetic groups, two rows each; one stable outcome per group. A/B are dimensionless noisy latent measurements.','split_group_counts':{k:len(v) for k,v in s.items()},'aggregation':'Mean logit across two rows per group; one outcome and one evaluated probability per group.','deliberate_teaching_confidence_multiplier':confidence_factor,'models':models,'test_metrics':results,'missingness_stress':stress,'checks':{'group_disjoint_splits':True,'positive_temperature_preserves_AUC_and_0_5_decisions':True,'all_missing_test_B_supported_with_frozen_imputer':True,'perfect_forecasts_Brier_zero':True,'tied_scores_AUC_half':True,'unit_temperature_identity':True}}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');np.savez(out/'multimodal-data.npz',x=x,y=y,groups=g,train_groups=s['train'],validation_groups=s['validation'],test_groups=s['test'],test_group_order=tg,A_predictions=test_predictions['A'],AB_predictions=test_predictions['AB']);return report

if __name__=='__main__':
    r=run();print(json.dumps({'temperatures':{k:v['temperature'] for k,v in r['models'].items()},'metrics':{m:{phase:{k:v for k,v in met.items() if k!='reliability_bins'} for phase,met in val.items()} for m,val in r['test_metrics'].items()},'missingness':[(z['groups_without_B'],z['metrics']['Brier']) for z in r['missingness_stress']]},indent=2))
