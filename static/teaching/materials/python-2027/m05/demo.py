"""Original CPU lesson: synthetic stripe classification, MLP and fixed filters.

Run: python demo.py
Requires numpy and matplotlib only. All images are generated locally. A small
fully connected neural network is trained; the separate convolutional feature
stage uses fixed filters and is explicitly NOT a trained CNN. Test images are
used once after training; learning rate/epochs are fixed in this script.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def make_images(n, seed):
    if not isinstance(n,int) or n < 2 or n % 2:
        raise ValueError('n must be an even integer at least 2')
    rng=np.random.default_rng(seed)
    labels=np.arange(n)%2
    rng.shuffle(labels)
    images=np.zeros((n,8,8,1),dtype=float)
    for i,label in enumerate(labels):
        center=int(rng.integers(1,7))
        intensity=float(rng.uniform(.7,1.0))
        if label==0: images[i,:,center,0]=intensity
        else: images[i,center,:,0]=intensity
    images += rng.normal(0,.035,images.shape)
    return np.clip(images,0,1),labels.astype(float)


def sigmoid(z):
    e=np.exp(-np.abs(z))
    return np.where(z>=0,1/(1+e),e/(1+e))


def initialize(n_features,hidden,seed=24):
    rng=np.random.default_rng(seed)
    return {'W1':rng.normal(0,1/np.sqrt(n_features),(n_features,hidden)),
            'b1':np.zeros(hidden), 'W2':rng.normal(0,1/np.sqrt(hidden),hidden), 'b2':np.array(0.)}


def forward(x,p):
    h=np.tanh(x@p['W1']+p['b1'])
    logits=h@p['W2']+p['b2']
    return h,logits,sigmoid(logits)


def loss_and_gradients(x,y,p):
    h,z,prob=forward(x,p)
    loss=float(np.mean(np.logaddexp(0,z)-y*z))
    dz=(prob-y)/len(y)
    dh=dz[:,None]*p['W2'][None,:]*(1-h*h)
    return loss,{'W1':x.T@dh,'b1':dh.sum(axis=0),'W2':h.T@dz,'b2':np.array(dz.sum())}


def train(x,y,epochs=160,learning_rate=.08,batch_size=32):
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float)
    if x.ndim!=2 or y.shape!=(len(x),) or not len(x) or not np.all(np.isfinite(x)):
        raise ValueError('finite feature rows and one label per row are required')
    if not np.all(np.isin(y,[0.,1.])):raise ValueError('labels must be 0 or 1')
    if not isinstance(epochs,int) or epochs<1 or not isinstance(batch_size,int) or batch_size<1:
        raise ValueError('epochs and batch_size must be positive integers')
    if not np.isfinite(learning_rate) or learning_rate<=0:raise ValueError('learning_rate must be finite and positive')
    # Store training-only preprocessing. Never fit mean/scale on the test data.
    mean=x.mean(axis=0);scale=x.std(axis=0);scale=np.where(scale<1e-8,1,scale)
    xn=(x-mean)/scale
    p=initialize(x.shape[1],8)
    rng=np.random.default_rng(77)
    history=[loss_and_gradients(xn,y,p)[0]]
    for _ in range(epochs):
        order=rng.permutation(len(xn))
        for start in range(0,len(xn),batch_size):
            ids=order[start:start+batch_size]
            _,g=loss_and_gradients(xn[ids],y[ids],p)
            for key in p:p[key]-=learning_rate*g[key]
        history.append(loss_and_gradients(xn,y,p)[0])
    return p,mean,scale,np.array(history)


def predict(x,p,mean,scale):
    x=np.asarray(x,dtype=float)
    if x.ndim!=2 or x.shape[1]!=len(mean) or not np.all(np.isfinite(x)):
        raise ValueError('prediction requires finite rows with training feature count')
    return forward((x-mean)/scale,p)[2]


def kernels():
    vertical=np.array([[-1,0,1],[-1,0,1],[-1,0,1]],dtype=float)/3
    return np.stack([vertical,vertical.T],axis=-1)[:,:,None,:]


def correlate_valid(images,filters):
    """NHWC input and (height,width,input_channel,output_channel) filters.

    Unit stride, no padding, one input channel. Cross-correlation (no kernel
    reversal), conventionally called convolution in neural-network libraries.
    """
    x=np.asarray(images,dtype=float);k=np.asarray(filters,dtype=float)
    if x.ndim!=4 or k.ndim!=4 or x.shape[-1]!=1 or k.shape[2]!=1:
        raise ValueError('expected NHW1 images and hw1F filters')
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(k)):
        raise ValueError('images and filters must be finite')
    if min(k.shape[:2])<1 or x.shape[1]<k.shape[0] or x.shape[2]<k.shape[1]:
        raise ValueError('filter must fit inside image')
    windows=np.lib.stride_tricks.sliding_window_view(x[...,0],k.shape[:2],axis=(1,2))
    return np.einsum('nxyij,ijf->nxyf',windows,k[:,:,0,:])


def filter_features(images):
    return np.mean(np.abs(correlate_valid(images,kernels())),axis=(1,2))


def gradient_check():
    x=np.array([[.2,-.3],[.7,.1],[-.4,.5]])
    y=np.array([0.,1.,0.]);p=initialize(2,3)
    _,g=loss_and_gradients(x,y,p)
    errors=[]
    for key,index in [('W1',(0,1)),('b1',(2,)),('W2',(1,)),('b2',())]:
        old=p[key][index].copy();eps=1e-5
        p[key][index]=old+eps;plus=loss_and_gradients(x,y,p)[0]
        p[key][index]=old-eps;minus=loss_and_gradients(x,y,p)[0]
        p[key][index]=old
        errors.append(abs((plus-minus)/(2*eps)-g[key][index]))
    return max(errors)


def save(fig,out,stem,title,description):
    fig.savefig(out/(stem+'.svg'),bbox_inches='tight');fig.savefig(out/(stem+'.pdf'),bbox_inches='tight');plt.close(fig)
    tree=ET.parse(out/(stem+'.svg'));node=tree.getroot();ns='{http://www.w3.org/2000/svg}'
    node.set('role','img');node.set('aria-labelledby','figure-title figure-description')
    t=ET.Element(ns+'title',id='figure-title');t.text=title
    d=ET.Element(ns+'desc',id='figure-description');d.text=description
    node.insert(0,d);node.insert(0,t);tree.write(out/(stem+'.svg'),encoding='utf-8',xml_declaration=True)


def run(output_dir=None):
    out=Path(output_dir) if output_dir else Path(__file__).resolve().parent;out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'font.family':'DejaVu Sans','svg.fonttype':'none',
                         'axes.spines.top':False,'axes.spines.right':False})
    train_images,train_y=make_images(192,42)
    test_images,test_y=make_images(96,142)
    xtrain=train_images.reshape(192,-1);xtest=test_images.reshape(96,-1)
    p,mean,scale,history=train(xtrain,train_y)
    # This is the first use of test images by the trained pipeline.
    test_prob=predict(xtest,p,mean,scale);pred=(test_prob>=.5).astype(int)
    features=filter_features(test_images);filter_pred=(features[:,1]>features[:,0]).astype(int)
    constant_label=int(train_y.mean()>.5);constant_pred=np.full(96,constant_label)
    scores={'Constant training-majority baseline':float(np.mean(constant_pred==test_y)),
            'Fixed filters + pooling':float(np.mean(filter_pred==test_y)),
            'Small trained MLP':float(np.mean(pred==test_y))}
    conf=np.array([[np.sum((test_y==i)&(pred==j)) for j in range(2)] for i in range(2)])
    grad_error=gradient_check()
    response=correlate_valid(test_images[:2],kernels())
    assert response.shape==(2,6,6,2)
    assert np.allclose(correlate_valid(np.ones((1,8,8,1)),kernels()),0)
    assert grad_error<1e-8
    assert np.all(np.isfinite(history)) and history[-1]<history[0]/5
    assert np.all((test_prob>=0)&(test_prob<=1))
    assert np.array_equal(predict(xtest,p,mean,scale),test_prob)
    assert np.allclose(mean,xtrain.mean(axis=0))
    rejected=0
    for call in [lambda:make_images(3,1),lambda:train(xtrain,train_y,learning_rate=-.1),
                 lambda:correlate_valid(np.ones((8,8)),kernels()),lambda:predict(np.full((1,64),np.nan),p,mean,scale)]:
        try:call()
        except ValueError:rejected+=1
        else:raise AssertionError('invalid input was not rejected')
    # A separate idealized display pair keeps both edges inside the valid window.
    # These images do not select, fit, or contribute to the held-out benchmark.
    examples=np.zeros((2,8,8,1),dtype=float)
    examples[0,:,3,0]=.9
    examples[1,3,:,0]=.9
    maps=correlate_valid(examples,kernels())
    assert maps[0,:,:,0].min()<0<maps[0,:,:,0].max()
    assert maps[1,:,:,1].min()<0<maps[1,:,:,1].max()
    fig,axs=plt.subplots(2,3,figsize=(9.4,5.6),constrained_layout=True)
    for row,name in enumerate(['Vertical stripe (class 0)','Horizontal stripe (class 1)']):
        im=axs[row,0].imshow(examples[row,:,:,0],vmin=0,vmax=1,cmap='gray')
        axs[row,0].set_title(name)
        for col,title in [(1,'Change across columns'),(2,'Change across rows')]:
            mp=axs[row,col].imshow(maps[row,:,:,col-1],vmin=-1,vmax=1,cmap='RdBu_r')
            axs[row,col].set_title(title)
        for ax in axs[row]:ax.set_xlabel('Column (pixels)');ax.set_ylabel('Row (pixels)')
    fig.colorbar(im,ax=axs[:,0],shrink=.7,label='Normalized intensity')
    fig.colorbar(mp,ax=axs[:,1:].ravel().tolist(),shrink=.7,label='Signed filter response')
    save(fig,out,'filters','Original synthetic images and two fixed filter responses',
         'Two separate idealized display images show interior vertical and horizontal synthetic stripes; they are not benchmark samples. Both edges remain inside the valid filter window. The input image has eight by eight pixels; each valid three by three filter produces six by six responses. Left-right and up-down derivative filters respond differently to orientation; blue and red denote opposite signs.')
    fig,axs=plt.subplots(1,2,figsize=(9.8,3.8),gridspec_kw={'width_ratios':[1.1,1]})
    axs[0].plot(np.arange(len(history)),history,color='#294e70',lw=2)
    axs[0].set_xlabel('Epoch (full passes through training rows)');axs[0].set_ylabel('Mean training binary cross-entropy')
    axs[0].set_title('Training loss only; fixed 160 epochs')
    vals=list(scores.values());axs[1].bar(range(3),vals,color=['#9ca9b3','#66816f','#294e70'])
    axs[1].set_xticks(range(3),['Constant','Fixed filters','MLP']);axs[1].set_ylim(0,1.14)
    axs[1].set_ylabel('Test accuracy (96 independent synthetic images)');axs[1].set_title('One test evaluation after training')
    for i,val in enumerate(vals):axs[1].text(i,val+.025,f'{100*val:.1f}%',ha='center')
    fig.tight_layout()
    save(fig,out,'learning-and-baselines','Training curve and held-out synthetic benchmark',
         'Left: mean training cross-entropy decreases over 160 epochs. Right: held-out accuracy of a constant baseline, a fixed-filter rule and the trained MLP. The simple fixed-filter rule can solve this controlled problem without learned image filters; no clinical or general image-recognition claim is implied.')
    report={'task':'original synthetic 8x8 vertical/horizontal stripes; no patient or external data',
            'training_examples':192,'test_examples':96,'seeds':{'train_images':42,'test_images':142,'weights':24,'batches':77},
            'architecture':[64,8,1],'batch_size':32,'epochs':160,'learning_rate':.08,
            'initial_training_loss':float(history[0]),'final_training_loss':float(history[-1]),
            'test_scores':scores,'MLP_confusion_rows_true_columns_predicted':conf.tolist(),
            'maximum_checked_gradient_error':grad_error,
            'checks':{'fixed_filters_zero_on_constant_image':True,'output_shape':[2,6,6,2],
                      'probability_bounds':True,'training_only_preprocessing':True,'deterministic_inference':True,
                      'invalid_inputs_rejected':rejected},
            'limits':['fixed filters are not learned CNN filters','independent images from same synthetic generator do not test distribution shift','test set is not used in fitting or parameter selection']}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
