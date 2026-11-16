"""Original tiny attention calculation for a proposed 2027 Python lesson.
Hand-set embeddings and projections: no training, language generation or API.
Formula reference: Vaswani et al., Attention Is All You Need, section 3.2.1.
"""
from pathlib import Path
import json,html
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def stable_softmax(scores,allowed=None):
    scores=np.asarray(scores,dtype=float)
    if scores.ndim!=2 or min(scores.shape)==0 or scores.size>1_000_000 or not np.isfinite(scores).all():
        raise ValueError('Use a finite nonempty score matrix with at most one million entries.')
    if allowed is None:allowed=np.ones(scores.shape,dtype=bool)
    allowed=np.asarray(allowed)
    if allowed.dtype!=np.bool_ or allowed.shape!=scores.shape or not allowed.any(axis=1).all():
        raise ValueError('The Boolean mask must match scores and allow at least one key per query.')
    masked=np.where(allowed,scores,-np.inf)
    # Large finite negative differences may underflow harmlessly to zero weight.
    with np.errstate(over='ignore',under='ignore'):
        shifted=masked-masked.max(axis=1,keepdims=True)
        weights=np.exp(shifted)
    return weights/weights.sum(axis=1,keepdims=True)


def attention(query,key,value,allowed=None):
    q,k,v=[np.asarray(x,dtype=float) for x in (query,key,value)]
    if any(x.ndim!=2 or min(x.shape)==0 or not np.isfinite(x).all() for x in (q,k,v)):
        raise ValueError('Queries, keys and values must be finite nonempty matrices.')
    if q.shape[1]!=k.shape[1] or k.shape[0]!=v.shape[0]:
        raise ValueError('Query/key feature widths and key/value row counts must match.')
    if max(q.shape+k.shape+v.shape)>1024 or q.shape[0]*k.shape[0]>1_000_000:
        raise ValueError('This classroom calculation limits dimensions and score-matrix size.')
    with np.errstate(over='ignore',invalid='ignore'):
        scores=(q@k.T)/np.sqrt(q.shape[1])
    if not np.isfinite(scores).all():raise ValueError('Dot products overflowed; use smaller input magnitudes.')
    weights=stable_softmax(scores,allowed)
    with np.errstate(over='ignore',invalid='ignore'):
        output=weights@v
    if not np.isfinite(output).all():raise ValueError('Weighted values overflowed; use smaller magnitudes.')
    return output,weights,scores


def toy_state():
    tokens=('red','cell','moves','slowly')
    embedding=np.array([[1,0,0],[0,1,0],[0,0,1],[1,1,0]],float)
    wq=np.array([[1,0],[0,1],[1,-1]],float)
    wk=np.array([[1,1],[1,-1],[0,1]],float)
    wv=np.array([[2,0],[0,4],[1,1]],float)
    return tokens,embedding,wq,wk,wv


def save(fig,out,stem,title,description):
    for ext in ('svg','pdf'):fig.savefig(out/f'{stem}.{ext}',bbox_inches='tight')
    p=out/f'{stem}.svg';s=p.read_text();i=s.index('>',s.index('<svg'))+1
    p.write_text(s[:i]+'<title>'+html.escape(title)+'</title><desc>'+html.escape(description)+'</desc>'+s[i:]);plt.close(fig)


def run(output_dir=None):
    out=Path(output_dir or Path(__file__).parent);out.mkdir(parents=True,exist_ok=True)
    tokens,x,wq,wk,wv=toy_state();q=x@wq;k=x@wk;v=x@wv
    causal=np.tril(np.ones((4,4),bool));z,a,s=attention(q,k,v);zc,ac,_=attention(q,k,v,causal)
    plt.rcParams.update({'font.size':20,'axes.titlesize':20,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(11,5.5),constrained_layout=True)
    for ax,arr,title in zip(axes,[a,ac],['All keys allowed','Causal mask']):
        ax.imshow(arr,vmin=0,vmax=1,cmap='Blues');ax.set(title=title,xlabel='Key position',ylabel='Query position',xticks=range(4),yticks=range(4),xticklabels=range(1,5),yticklabels=range(1,5))
        for i in range(4):
            for j in range(4):ax.text(j,i,f'{arr[i,j]:.2f}',ha='center',va='center',fontsize=20,color='white' if arr[i,j]>.55 else '#122334')
    save(fig,out,'attention-weights','Allowed positions change the normalized weights','Two four-by-four attention matrices use the same hand-set embeddings and projections. Each row sums to one. The causal mask sets future-key weights exactly to zero and renormalizes permitted weights. Positions are numbered one to four; displayed decimals are rounded.')
    hand_q=np.array([[1.,0.]]);hand_k=np.eye(2);hand_v=np.array([[2.,0.],[0.,4.]])
    hand_z,hand_a,hand_s=attention(hand_q,hand_k,hand_v)
    contributions=hand_a[0,:,None]*hand_v
    fig,ax=plt.subplots(figsize=(8.4,5.1),constrained_layout=True)
    ax.bar([0,1],contributions[0],color='#087e8b',label='Key 1 contribution')
    ax.bar([0,1],contributions[1],bottom=contributions[0],color='#c07828',label='Key 2 contribution')
    for i,total in enumerate(hand_z[0]):ax.text(i,total+.06,f'{total:.3f}',ha='center',fontsize=20)
    ax.set(xticks=[0,1],xticklabels=['Component 1','Component 2'],ylabel='Output coordinate',ylim=(0,2.2),title='One query mixes two value vectors');ax.legend(loc='upper center');ax.grid(axis='y',alpha=.15)
    save(fig,out,'weighted-values','Weights mix coordinates rather than certify facts','A hand-calculated query [1,0], identity keys and value rows [2,0] and [0,4] produce weights about 0.670 and 0.330. Multiplying each value row by its weight and adding gives output [1.340,1.321]. These synthetic coordinates are neither token probabilities nor truth scores.')
    assert np.allclose(a.sum(axis=1),1) and np.allclose(ac.sum(axis=1),1)
    assert np.all(ac[~causal]==0)
    uniform=attention(np.zeros((1,2)),hand_k,hand_v)[0];assert np.allclose(uniform,[[1,2]])
    constant=attention(q,k,np.full((4,3),7.))[0];assert np.allclose(constant,7)
    assert np.allclose(stable_softmax([[1000,1001]]),stable_softmax([[0,1]]))
    permutation=np.array([2,0,3,1]);permuted=attention(q[permutation],k[permutation],v[permutation])[0]
    assert np.allclose(permuted,z[permutation])
    changed=x.copy();changed[-1]=[9,-3,2]
    future_z=attention(changed@wq,changed@wk,changed@wv,causal)[0]
    assert np.allclose(future_z[:3],zc[:3])
    unmasked_changed=attention(changed@wq,changed@wk,changed@wv)[0]
    effect=float(np.max(abs(unmasked_changed[:3]-z[:3])));assert effect>1
    bad=[lambda:stable_softmax([[0,1]],[[False,False]]),lambda:stable_softmax([[0,1]],[[1,1]]),lambda:stable_softmax([[np.nan,1]]),lambda:attention([[1,2]],[[1]],[[1]]),lambda:attention([[1]],[[1],[2]],[[1]]),lambda:attention([],[],[]),lambda:attention([[1e308]],[[1e308]],[[1]])]
    for f in bad:
        try:f()
        except ValueError:pass
        else:raise AssertionError('Invalid request accepted')
    results={'tokens':tokens,'embedding_shape':list(x.shape),'projection_shape':list(wq.shape),'score_shape':list(s.shape),'value_shape':list(v.shape),'output_shape':list(z.shape),'hand_scores':hand_s.tolist(),'hand_weights':hand_a.tolist(),'hand_output':hand_z.tolist(),'maximum_row_sum_error':float(max(abs(a.sum(axis=1)-1).max(),abs(ac.sum(axis=1)-1).max())),'causal_future_change_error':float(abs(future_z[:3]-zc[:3]).max()),'unmasked_future_change_effect':effect,'permutation_equivariance_error':float(abs(permuted-z[permutation]).max()),'invalid_requests_rejected':len(bad),'training_performed':False}
    (out/'results.json').write_text(json.dumps(results,indent=2)+'\n');return results

if __name__=='__main__':print(json.dumps(run(),indent=2))
