"""Original neutral two-allele teaching model; synthetic, nonoverlapping generations.
Diploid population size N is fixed. Each generation samples 2N allele copies
independently from the preceding frequency. No selection, mutation or migration.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def probability(p):
    p=float(p)
    if not np.isfinite(p) or not 0 <= p <= 1:raise ValueError('Allele frequency must be finite and between zero and one')
    return p


def integer(value,name,minimum=1):
    if isinstance(value,(bool,np.bool_)) or not np.isscalar(value):raise ValueError(name+' must be an integer')
    try:valid=np.isfinite(value) and float(value).is_integer() and value>=minimum
    except (TypeError,ValueError,OverflowError):valid=False
    if not valid:raise ValueError(name+' must be an integer at least '+str(minimum))
    return int(value)


def genotype_frequencies(p):
    p=probability(p);q=1-p
    return np.array([p*p,2*p*q,q*q])


def allele_frequency(aa,ab,bb):
    counts=np.array([integer(aa,'AA count',0),integer(ab,'AB count',0),integer(bb,'BB count',0)],dtype=float)
    total=counts.sum()
    if not np.isfinite(total) or total<=0:raise ValueError('Positive finite population required')
    return float((counts[0]+.5*counts[1])/total)


def drift(initial_copies=15,population=25,generations=60,replicates=8,seed=73):
    n=integer(population,'Population');g=integer(generations,'Generations',0);r=integer(replicates,'Replicates');k=integer(initial_copies,'Initial allele copies',0)
    if n>10_000_000 or k>2*n:raise ValueError('Population limit is 10 million; copies must lie between 0 and 2N')
    if (g+1)*r>2_000_000:raise ValueError('Trajectory exceeds classroom computation limit')
    rng=np.random.default_rng(seed);counts=np.empty((g+1,r),dtype=np.int64);counts[0]=k
    for j in range(g):counts[j+1]=rng.binomial(2*n,counts[j]/(2*n))
    return np.arange(g+1),counts/(2*n)


def save(fig,out,name,title,description):
    fig.savefig(out/(name+'.svg'),bbox_inches='tight');fig.savefig(out/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
    path=out/(name+'.svg');tree=ET.parse(path);node=tree.getroot();ns='{http://www.w3.org/2000/svg}'
    node.set('role','img');node.set('aria-labelledby','figure-title figure-description')
    for tag,ident,text in [('title','figure-title',title),('desc','figure-description',description)]:
        el=ET.Element(ns+tag,id=ident);el.text=text;node.insert(0,el)
    tree.write(path,encoding='utf-8',xml_declaration=True)


def run(output_dir=None):
    out=Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent;out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':18,'axes.titlesize':18,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    p=.3;expected=genotype_frequencies(p)
    fig,ax=plt.subplots(figsize=(8.7,4.8));bars=ax.bar(['AA','AB','BB'],expected,color=['#176c7b','#b26738','#647b53'],width=.62)
    ax.set(ylabel='Offspring probability',ylim=(0,.65),title='Independent gametes with A frequency 0.30')
    for bar,value in zip(bars,expected):ax.text(bar.get_x()+bar.get_width()/2,value+.02,f'{value:.2f}',ha='center',va='bottom',fontsize=20)
    ax.text(.98,.96,'Alleles: A = 0.30, B = 0.70',transform=ax.transAxes,ha='right',va='top',fontsize=18)
    fig.tight_layout();save(fig,out,'genotype-probabilities','Genotype probabilities for independent gametes','For A probability 0.30 and B probability 0.70, AA probability 0.09, AB 0.42 and BB 0.49. These are probabilities at random mating before any viability selection, not an exact finite-population count.')
    fig,axs=plt.subplots(1,2,figsize=(11,4.8),sharey=True);summary={}
    for ax,n in zip(axs,[25,250]):
        t,paths=drift(initial_copies=int(.3*2*n),population=n)
        ax.plot(t,paths,lw=1.65,alpha=.82);ax.axhline(.3,color='black',ls='--',lw=1.5)
        ax.set(xlabel='Generation',ylabel='A allele frequency' if n==25 else '',ylim=(-.03,1.03),title=f'N = {n} diploid individuals')
        ax.set_yticks([0,.25,.5,.75,1]);summary[str(n)]={'final_frequencies':paths[-1].tolist(),'one_step_variance_at_p0':p*(1-p)/(2*n)}
    fig.suptitle('Eight neutral trajectories; dashed line = expected frequency',fontsize=18,y=1.04)
    fig.tight_layout();save(fig,out,'neutral-drift','Neutral drift in two finite populations','Eight fixed-seed neutral Wright-Fisher trajectories for N = 25 and N = 250, starting at A frequency 0.30. Each transition samples 2N allele copies independently. Dashed line shows ensemble expectation 0.30, not the mean of the displayed eight paths. No selection, mutation or migration; population size is fixed.')
    assert np.allclose(expected,[.09,.42,.49]) and np.isclose(expected.sum(),1)
    assert allele_frequency(4,10,6)==.45
    for endpoint in [0,50]:
        _,values=drift(endpoint,25);assert np.all(values==endpoint/50)
    assert np.array_equal(drift()[1],drift()[1])
    _,paths=drift();assert np.all((paths>=0)&(paths<=1)) and np.allclose(50*paths,np.round(50*paths))
    # A large independent one-generation ensemble checks the conditional mean and variance.
    draws=np.random.default_rng(812).binomial(50,.3,size=100_000);expected_mean=15.;expected_var=10.5
    assert abs(draws.mean()-expected_mean)<6*np.sqrt(expected_var/len(draws))
    assert abs(draws.var()-expected_var)<.03*expected_var
    rejected=0
    for fn in [lambda:genotype_frequencies(-.1),lambda:genotype_frequencies(np.nan),lambda:allele_frequency(0,0,0),lambda:drift(population=2.5),lambda:drift(initial_copies=51),lambda:drift(generations=-1),lambda:drift(replicates=0),lambda:drift(generations=2_000_001)]:
        try:fn()
        except ValueError:rejected+=1
        else:raise AssertionError('Invalid input accepted')
    report={'model':'neutral diploid Wright-Fisher sampling; synthetic demonstration','p0':p,'genotype_probabilities':expected.tolist(),'counting_example_frequency':allele_frequency(4,10,6),'trajectories':summary,'one_generation_ensemble':{'replicates':len(draws),'mean_copies':float(draws.mean()),'variance_copies':float(draws.var()),'expected_mean':expected_mean,'expected_variance':expected_var},'checks':{'probabilities_sum_to_one':True,'absent_allele_cannot_appear':True,'fixation_absorbing':True,'seed_reproducible':True,'copy_grid_and_bounds':True,'conditional_moments':True,'invalid_inputs_rejected':rejected},'limitations':['one locus and two alleles','fixed diploid population','independent sampling and nonoverlapping generations','no selection mutation or migration','no prediction for an actual species or population']}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(run(),indent=2))
