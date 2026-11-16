"""Original synthetic image -> threshold mask -> conforming 2D pixel-cell mesh.
This is geometry verification, not a 3D cardiac model or a CFD solver.
"""
from pathlib import Path
import hashlib, html, json
import numpy as np
import scipy
from scipy.ndimage import gaussian_filter, label
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def geometry(spacing=(1.25, 2.), origin=(-20., -10.), angle_degrees=20.):
    s=np.asarray(spacing,float);o=np.asarray(origin,float)
    if s.shape!=(2,) or o.shape!=(2,) or not np.isfinite(s).all() or not np.isfinite(o).all() or np.any(s<=0) or not np.isfinite(angle_degrees):
        raise ValueError('Use finite positive x/y spacing, finite x/y origin and finite angle.')
    a=np.deg2rad(angle_degrees);d=np.array([[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]])
    return {'spacing_xy_mm':s,'origin_xy_mm':o,'direction':d}


def physical_points(index_xy,meta):
    p=np.asarray(index_xy,float)
    if p.ndim!=2 or p.shape[1]!=2 or not np.isfinite(p).all():raise ValueError('Use finite point rows [column,row].')
    s=np.asarray(meta['spacing_xy_mm'],float);o=np.asarray(meta['origin_xy_mm'],float);d=np.asarray(meta['direction'],float)
    if s.shape!=(2,) or o.shape!=(2,) or d.shape!=(2,2) or not np.isfinite(s).all() or not np.isfinite(o).all() or not np.isfinite(d).all() or np.any(s<=0):raise ValueError('Invalid image metadata.')
    if not np.allclose(d.T@d,np.eye(2),atol=1e-10) or np.linalg.det(d)<=0:raise ValueError('This lesson supports proper orthonormal direction matrices only.')
    return (p*s)@d.T+o


def make_image(seed=111):
    rng=np.random.default_rng(seed);row,col=np.indices((28,36))
    truth=((col-15)/9)**2+((row-14)/9)**2<=1
    truth|=((col-24)/6)**2+((row-10)/4)**2<=1
    image=np.clip(.12+.76*gaussian_filter(truth.astype(float),.85)+rng.normal(0,.012,truth.shape),0,1)
    return image,truth


def segment(image,threshold=.5):
    a=np.asarray(image,float)
    if a.ndim!=2 or a.size==0 or not np.isfinite(a).all() or np.any((a<0)|(a>1)):raise ValueError('Use a nonempty finite 2D image in [0,1].')
    if not np.isfinite(threshold) or not 0<=threshold<=1:raise ValueError('Threshold must be finite in [0,1].')
    return a>=threshold


def mesh_from_mask(mask,meta):
    a=np.asarray(mask)
    if a.ndim!=2 or a.size==0 or a.dtype!=bool or not a.any():raise ValueError('Use a nonempty foreground boolean 2D mask.')
    h,w=a.shape;rr,cc=np.indices((h+1,w+1));points=physical_points(np.column_stack((cc.ravel()-.5,rr.ravel()-.5)),meta)
    r,c=np.nonzero(a);a0=r*(w+1)+c;b=a0+1;d=(r+1)*(w+1)+c;e=d+1
    tris=np.concatenate((np.column_stack((a0,b,e)),np.column_stack((a0,e,d))))
    used,inv=np.unique(tris,return_inverse=True)
    return points[used],inv.reshape(-1,3)


def signed_areas(points,triangles):
    p=np.asarray(points,float);t=np.asarray(triangles)
    if p.ndim!=2 or p.shape[1]!=2 or t.ndim!=2 or t.shape[1]!=3 or not np.issubdtype(t.dtype,np.integer) or t.size==0 or not np.isfinite(p).all() or t.min()<0 or t.max()>=len(p):raise ValueError('Use finite 2D vertices and valid integer triangle indices.')
    u=p[t[:,1]]-p[t[:,0]];v=p[t[:,2]]-p[t[:,0]]
    return .5*(u[:,0]*v[:,1]-u[:,1]*v[:,0])


def save(fig,out,stem,title,desc):
    for ext in ('svg','pdf'):fig.savefig(out/f'{stem}.{ext}',bbox_inches='tight',metadata={'Date':None} if ext=='svg' else {'CreationDate':None})
    p=out/f'{stem}.svg';s=p.read_text();i=s.index('>',s.index('<svg'))+1;p.write_text(s[:i]+f'<title>{html.escape(title)}</title><desc>{html.escape(desc)}</desc>'+s[i:]);plt.close(fig)


def run(output_dir=None):
    out=Path(output_dir or Path(__file__).parent);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':20,'axes.titlesize':21,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    image,truth=make_image();meta=geometry();mask=segment(image);points,triangles=mesh_from_mask(mask,meta);areas=signed_areas(points,triangles)
    pixel_area=float(np.prod(meta['spacing_xy_mm']));area=float(mask.sum()*pixel_area)
    np.testing.assert_allclose(areas.sum(),area,rtol=1e-12);assert np.all(areas>0)
    fig,axs=plt.subplots(1,2,figsize=(10.4,5.5),constrained_layout=True)
    axs[0].imshow(image,origin='lower',vmin=0,vmax=1,cmap='gray');axs[0].contour(mask,levels=[.5],colors=['#e5a741'],linewidths=1.7)
    axs[0].set(xlabel='Column index',ylabel='Row index',title='Image + threshold mask',xticks=[0,10,20,30],yticks=[0,10,20])
    axs[1].triplot(points[:,0],points[:,1],triangles,color='#087e8b',lw=.45);axs[1].set_aspect('equal');axs[1].set(xlabel='Physical x (mm)',ylabel='Physical y (mm)',title='Two triangles per cell');axs[1].locator_params(axis='both',nbins=4)
    save(fig,out,'image-mesh','Image indices and physical triangular mesh','Original 28 by 36 synthetic intensity image with threshold 0.5 contour, beside its actual conforming triangular mesh. Spacing is 1.25 mm per column and 2 mm per row; origin is (-20,-10) mm and orientation is a 20 degree proper rotation. No flow equation is solved.')
    thresholds=np.array([.35,.4,.45,.5,.55,.6,.65]);counts=[];sums=[];components=[]
    for th in thresholds:
        m=segment(image,float(th));p,t=mesh_from_mask(m,meta);counts.append(int(m.sum()));sums.append(float(signed_areas(p,t).sum()));components.append(int(label(m)[1]))
    counts=np.asarray(counts);a=np.asarray(sums);d=2*np.sqrt(a/np.pi)
    fig,axs=plt.subplots(1,2,figsize=(10.4,4.9),constrained_layout=True)
    axs[0].plot(thresholds,a,'o-',lw=2.5,color='#087e8b');axs[0].axhline(truth.sum()*pixel_area,color='#9b6020',ls='--',label='Generator area');axs[0].set(xlabel='Intensity threshold',ylabel='Mask area (mm²)',title='Segmentation sensitivity');axs[0].legend(fontsize=20,loc='best')
    axs[1].plot(thresholds,a/area,'o-',lw=2.5,label='Area ratio',color='#087e8b');axs[1].plot(thresholds,d/(2*np.sqrt(area/np.pi)),'s--',lw=2.5,label='Diameter ratio',color='#9b6020');axs[1].set(xlabel='Intensity threshold',ylabel='Ratio to threshold 0.5',title='Equivalent-circle summary');axs[1].legend(fontsize=20,loc='best')
    for ax in axs:ax.set_xticks([.35,.5,.65]);ax.grid(alpha=.18)
    save(fig,out,'geometry-sensitivity','Threshold sensitivity of physical area and equivalent diameter','The same image and spatial metadata are used for every threshold. The dashed reference in the left panel is the original synthetic generator mask area, not an expert annotation. The diameter is that of a circle with equal area, not a measured anatomical diameter. No probability distribution over thresholds is assumed.')
    rotated=geometry(angle_degrees=83,origin=(100,-50));pr,tr=mesh_from_mask(mask,rotated);np.testing.assert_allclose(signed_areas(pr,tr).sum(),area,rtol=1e-12)
    doubled=geometry(spacing=(2.5,4.));pd,td=mesh_from_mask(mask,doubled);np.testing.assert_allclose(signed_areas(pd,td).sum(),4*area,rtol=1e-12)
    np.testing.assert_allclose(physical_points([[0,0]],meta)[0],meta['origin_xy_mm'])
    assert np.all(np.diff(counts)<=0)
    # Unique shared edges occur once at the boundary or twice in the interior.
    edges=np.sort(np.concatenate((triangles[:,[0,1]],triangles[:,[1,2]],triangles[:,[2,0]])),axis=1);_,freq=np.unique(edges,axis=0,return_counts=True);assert np.isin(freq,[1,2]).all()
    metadata={k:v.tolist() for k,v in meta.items()};metadata.update({'units':'mm','array_order':'row,column','point_order':'x,y = column,row before spatial transform','threshold':.5,'comparison':'>=','synthetic_seed':111,'shape':list(image.shape),'image_sha256':hashlib.sha256(np.ascontiguousarray(image,dtype='<f8').tobytes()).hexdigest(),'hash_encoding':'C order, little-endian float64 bytes','geometry_type':'2D union of foreground pixel cells; two triangles per cell','dependencies':{'numpy':np.__version__,'scipy':scipy.__version__},'generator':'demo.make_image: ellipses, Gaussian blur sigma0.85 pixels, noise sigma0.012','purpose':'Teaching geometry only; no patient data and no fluid simulation'})
    (out/'provenance.json').write_text(json.dumps(metadata,indent=2)+'\n');np.savez(out/'geometry-data.npz',image=image,truth=truth,mask=mask,points_mm=points,triangles=triangles)
    report={'foreground_pixels':int(mask.sum()),'triangles':len(triangles),'vertices':len(points),'area_mm2':area,'minimum_signed_triangle_area_mm2':float(areas.min()),'thresholds':thresholds.tolist(),'counts':counts.tolist(),'areas_mm2':a.tolist(),'equivalent_diameters_mm':d.tolist(),'components_4_connected':components,'generator_area_mm2':float(truth.sum()*pixel_area),'checks':{'mesh_equals_pixel_area':True,'positive_signed_elements':True,'rigid_transform_preserves_area':True,'doubling_both_spacings_quadruples_area':True,'threshold_masks_nested':True,'edge_incidence_one_or_two':True}}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(run(),indent=2))
