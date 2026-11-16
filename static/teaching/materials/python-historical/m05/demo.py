"""Original synthetic specimen example: regression, PCA and two-center clustering.
Fit only on training rows. Raw mixed-unit metrics are deliberate counterexamples.
No external data, internet, or machine-learning framework is needed.
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


def make_data():
    rng=np.random.default_rng(5701);n=120
    length=20+3*rng.normal(size=n)
    mixture=np.repeat([-1.,1.],n//2)
    mass=4+2*mixture+.4*rng.normal(size=n)
    response=5+1.5*length+1.5*rng.normal(size=n)
    x=np.column_stack([length,mass]);order=rng.permutation(n)
    return x,response,order[:90],order[90:]


def fit_line(length,response):
    x=np.asarray(length,dtype=float);y=np.asarray(response,dtype=float)
    if x.ndim!=1 or len(x)<2 or y.shape!=x.shape or not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError('Use matching finite one-dimensional observations.')
    design=np.column_stack([np.ones(len(x)),x])
    coef,_,rank,_=np.linalg.lstsq(design,y,rcond=None)
    if rank!=2:raise ValueError('A unique intercept and slope need variation in length.')
    return coef


def rmse(observed,predicted):
    a=np.asarray(observed,dtype=float);b=np.asarray(predicted,dtype=float)
    if a.ndim!=1 or not len(a) or a.shape!=b.shape or not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        raise ValueError('RMSE needs matching nonempty finite vectors.')
    return float(np.sqrt(np.mean((a-b)**2)))


def fit_standardizer(x):
    x=matrix(x);mean=x.mean(axis=0);scale=x.std(axis=0,ddof=0)
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


def run(output_dir=None):
    out=Path(output_dir) if output_dir else Path(__file__).resolve().parent;out.mkdir(parents=True,exist_ok=True)
    x,y,train,test=make_data();xt=x[train];yt=y[train]
    assert not set(train)&set(test) and len(set(train)|set(test))==len(x)
    coef=fit_line(xt[:,0],yt);pred=coef[0]+coef[1]*x[:,0];baseline=np.full(len(test),yt.mean())
    mean,scale=fit_standardizer(xt);z=(xt-mean)/scale;zt=(x[test]-mean)/scale
    pca=fit_pca(z);scores=(z-pca['center'])@pca['components'].T
    full=scores@pca['components']+pca['center'];assert np.allclose(full,z)
    assert np.allclose(pca['components']@pca['components'].T,np.eye(2))
    converted=xt*np.array([1.,1000.]);cm,cs=fit_standardizer(converted)
    assert np.allclose((converted-cm)/cs,z)
    clusters=fit_two_centers(z);converted_clusters=fit_two_centers((converted-cm)/cs)
    assert np.array_equal(clusters['labels'][:,None]==clusters['labels'][None,:],converted_clusters['labels'][:,None]==converted_clusters['labels'][None,:])
    raw=fit_two_centers(xt);mg=fit_two_centers(converted)
    changed=int(np.count_nonzero(np.triu((raw['labels'][:,None]==raw['labels'][None,:])!=(mg['labels'][:,None]==mg['labels'][None,:]),1)))
    assert np.allclose(fit_line([0,1,2],[3,5,7]),[3,2])
    rejected=0
    for fn in [lambda:fit_line([1,1],[2,3]),lambda:fit_standardizer([[1,2],[1,3]]),lambda:fit_pca([[1,2],[1,2]]),lambda:fit_two_centers([[1,2],[1,2]])]:
        try:fn()
        except ValueError:rejected+=1
    assert rejected==4
    plt.rcParams.update({'font.size':20,'axes.titlesize':20,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(1,2,figsize=(10.5,5.5));axs[0].scatter(xt[:,0],yt,s=22,color='#176c7b',label='Training (90)');axs[0].scatter(x[test,0],y[test],s=34,facecolors='none',edgecolors='#b46d27',marker='^',label='Test (30)')
    grid=np.linspace(x[:,0].min(),x[:,0].max(),100);axs[0].plot(grid,coef[0]+coef[1]*grid,color='#303c44',label='Training-fitted line');axs[0].set(xlabel='Specimen length (mm)',ylabel='Synthetic response (mV)',title='Training fit');fig.legend(*axs[0].get_legend_handles_labels(),fontsize=20,frameon=False,loc='lower center',ncol=3)
    axs[1].scatter(pred[test],y[test]-pred[test],color='#b46d27');axs[1].axhline(0,color='#555',lw=.8);axs[1].set(xlabel='Test prediction (mV)',ylabel='Test residual (mV)',title='Held-out residuals')
    for ax in axs:ax.grid(alpha=.2)
    fig.tight_layout(rect=(0,.13,1,1));save(fig,out,'regression-and-residuals','Training fit and held-out regression residuals','The line is fitted using ninety training specimens. Thirty open test points are evaluated without refitting. Residuals have response units, millivolts. Synthetic association is not a causal law.')
    fig,axs=plt.subplots(1,3,figsize=(11.5,5.5),sharex=True,sharey=True)
    settings=[(xt,np.ones(2),np.zeros(2),raw,'Raw metric\nmm and g'),(converted,np.array([1.,.001]),np.zeros(2),mg,'Raw metric\nmm and mg'),(z,scale,mean,clusters,'Standardized\nmetric')]
    ratios=[]
    for ax,(metric,back_scale,offset,km,title) in zip(axs,settings):
        pc=fit_pca(metric);ratios.append(float(pc['variance_ratio'][0]));centers=km['centers']*back_scale+offset
        # Color numbering is chosen by center mass only for side-by-side display.
        low=np.argmin(centers[:,1]);colors=np.where(km['labels']==low,'#176c7b','#b46d27')
        
        for membership,marker,color in [(km['labels']==low,'o','#176c7b'),(km['labels']!=low,'^','#b46d27')]:
            ax.scatter(xt[membership,0],xt[membership,1],color=color,marker=marker,s=30)
        ax.scatter(centers[:,0],centers[:,1],marker='X',s=95,c='#222',edgecolors='white',zorder=4)
        direction=pc['components'][0]*back_scale;direction=direction/np.linalg.norm(direction/scale)*1.7
        middle=pc['center']*back_scale+offset
        ax.plot([middle[0]-direction[0],middle[0]+direction[0]],[middle[1]-direction[1],middle[1]+direction[1]],'k--',lw=1.6,label='PC1 direction')
        ax.set(xlabel='Length (mm)',title=title);ax.grid(alpha=.2)
    axs[0].set_ylabel('Mass (g)')
    from matplotlib.lines import Line2D
    handles=[Line2D([],[],marker='o',ls='',color='#176c7b',label='Lower-center group'),Line2D([],[],marker='^',ls='',color='#b46d27',label='Higher-center group'),Line2D([],[],ls='--',color='black',label='PC1')]
    fig.legend(handles=handles,loc='lower center',ncol=3,fontsize=20,frameon=False)
    fig.suptitle('Same data, different distance metrics',fontsize=20)
    fig.tight_layout(rect=(0,.14,1,.92));save(fig,out,'scale-projection-groups','PCA directions and cluster groups depend on feature metric','All panels display the identical training specimens in millimeters and grams. Colors and circle/triangle markers redundantly indicate two-center memberships ordered by center mass, X marks centers, and dashed lines show first principal directions. The middle computation converts grams to milligrams before using raw Euclidean distances. The right computation standardizes using training means and scales, which removes this arbitrary unit-conversion effect. Cluster numbers are not known scientific classes.')
    report={'split':{'train':len(train),'test':len(test),'disjoint':True},'regression':{'intercept_mV':float(coef[0]),'slope_mV_per_mm':float(coef[1]),'train_RMSE_mV':rmse(yt,pred[train]),'test_RMSE_mV':rmse(y[test],pred[test]),'training_mean_baseline_test_RMSE_mV':rmse(y[test],baseline)},'PCA_first_variance_ratio':{'raw_mm_g':ratios[0],'raw_mm_mg':ratios[1],'standardized':ratios[2]},'standardized_test_scores_shape':list(((zt-pca['center'])@pca['components'].T).shape),'raw_unit_conversion_changed_coassigned_pairs':changed,'standardized_clustering_inertia':clusters['inertia'],'checks':{'exact_line_recovery':True,'full_PCA_reconstruction':True,'orthonormal_components':True,'standardized_unit_conversion_invariant':True,'cluster_label_permutation_handled':True,'nonincreasing_Lloyd_objective':True,'invalid_inputs_rejected':rejected}}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(run(),indent=2))
