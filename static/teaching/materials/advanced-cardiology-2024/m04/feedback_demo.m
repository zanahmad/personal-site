function out = feedback_demo(overrides)
% New six-compartment teaching implementation; not an archived source file.
% Methodological credit: Hoppensteadt/Peskin ch.1 and Ahmad/Peskin feedback paper.
% The public paper has TWO storage compartments; this code has SIX.
% MATLAB/Octave execution must be verified on an available engine before release.
% Example: r = feedback_demo(struct('gain',0));
p = struct('rs_rest',17.86,'resistance_factor',.5,'rp',1.79, ...
 'valve_resistance',.01,'f0',80,'gain',10,'pressure_target',90, ...
 'target_factor',1,'tau_filter_s',3,'fmin',30,'fmax',240, ...
 'start_s',30,'stop_s',60,'duration_s',90,'dt_s',.00046875, ...
 'resistance_recovery_delay_s',0,'target_recovery_delay_s',0, ...
 'filter_method','euler');
if nargin>0
 names=fieldnames(overrides);
 for j=1:numel(names)
  assert(isfield(p,names{j}),'Unknown parameter field.');
  p.(names{j})=overrides.(names{j});
 end
end
names=fieldnames(p);
for j=1:numel(names)
 if ~strcmp(names{j},'filter_method')
  assert(isscalar(p.(names{j})) && isfinite(p.(names{j})),'Parameters must be finite scalars.');
 end
end
assert(min([p.rs_rest,p.resistance_factor,p.rp,p.valve_resistance,p.f0,p.pressure_target,p.target_factor,p.tau_filter_s,p.fmin,p.fmax,p.duration_s,p.dt_s])>0);
assert(p.gain>=0 && p.fmin<=p.f0 && p.f0<=p.fmax);
assert(0<=p.start_s && p.start_s<p.stop_s && p.stop_s<p.duration_s);
assert(min([p.resistance_recovery_delay_s,p.target_recovery_delay_s])>=0);
assert(p.stop_s+max(p.resistance_recovery_delay_s,p.target_recovery_delay_s)<p.duration_s);
assert(p.dt_s<=p.tau_filter_s,'Euler filter requires dt <= tau for a non-overshooting update.');
assert(any(strcmp(p.filter_method,{'euler','held-input'})),'Unknown filter method.');
assert(ceil(p.duration_s/p.dt_s)<=2000000,'CPU teaching limit exceeded.');
edges=[6,1;1,2;3,4;4,5;2,3;5,6];
vd=[.027;.825;0;.027;.0382;0];
pressure=[5;80;2;2;8;5];phase=0;C=comply(phase);pf=p.pressure_target;
volume0=sum(vd+C.*pressure);valves=false(4,1);t=0;
events=unique([0,p.start_s,p.stop_s,p.stop_s+p.resistance_recovery_delay_s,p.stop_s+p.target_recovery_delay_s,p.duration_s]);
% Integer-indexed event intervals avoid roundoff-sized terminal steps.
time_grid=0;time_tolerance=64*eps*max(1,p.duration_s);
for segment=1:numel(events)-1
 left=events(segment);right=events(segment+1);
 count=floor((right-left)/p.dt_s);points=left+(1:count)'*p.dt_s;
 points=points(points<right-time_tolerance);
 time_grid=[time_grid;points;right];
end
z=zeros(numel(time_grid),19);k=1;
[rs,target]=inputs(t,p);q=flows(pressure,rs,p,edges);
z(k,:)=[t,phase,pf,p.f0,rs,target,p.f0,pressure',q'];
maxres=0;maxdrift=0;maxsolves=0;
for time_index=2:numel(time_grid)
 tnew=time_grid(time_index);hs=tnew-t;h=hs/60;
 [rs,target]=inputs(t,p);
 if strcmp(p.filter_method,'euler'),w=hs/p.tau_filter_s;else,w=-expm1(-hs/p.tau_filter_s);end
 pfnew=pf+w*(pressure(2)-pf);
 command=p.f0*(1+p.gain*(target-pfnew)/target);
 rate=min(p.fmax,max(p.fmin,command));phase_new=phase+h*rate;
 Cnew=comply(phase_new);
 [pressure,valves,q,res,solves]=hydraulic(pressure,C,Cnew,h,rs,p,valves,edges);
 phase=phase_new;C=Cnew;pf=pfnew;t=tnew;
 maxres=max(maxres,max(abs(res)));maxdrift=max(maxdrift,abs(sum(vd+C.*pressure)-volume0));maxsolves=max(maxsolves,solves);
 k=k+1;z(k,:)=[t,phase,pf,rate,rs,target,command,pressure',q'];
end
z=z(1:k,:);
out=struct('time_s',z(:,1),'phase',z(:,2),'filtered_pressure',z(:,3), ...
 'rate_bpm',z(:,4),'resistance',z(:,5),'target',z(:,6),'unbounded_command',z(:,7), ...
 'pressure',z(:,8:13),'flows',z(:,14:19),'parameters',p, ...
 'max_volume_drift_L',maxdrift,'max_balance_residual_L_min',maxres, ...
 'max_linear_solves_per_step',maxsolves,'initial_total_volume_L',volume0);
end

function C=comply(phase)
theta=mod(phase,1);
if theta<.4
 e=-expm1(-theta/.2)/-expm1(-.4/.2);
 lv=.0146*(.00003/.0146)^e;rv=.0365*(.0002/.0365)^e;
else
 e=-expm1(-(theta-.4)/.6)/-expm1(-.6/.6);
 lv=.00003*(.0146/.00003)^e;rv=.0002*(.0365/.0002)^e;
end
C=[lv;.00175;1.75;rv;.00412;.08];
end

function [rs,target]=inputs(t,p)
rs=p.rs_rest;target=p.pressure_target;
if p.start_s<=t && t<p.stop_s+p.resistance_recovery_delay_s,rs=rs*p.resistance_factor;end
if p.start_s<=t && t<p.stop_s+p.target_recovery_delay_s,target=target*p.target_factor;end
end

function q=flows(P,rs,p,edges)
d=P(edges(:,1))-P(edges(:,2));
q=d./[repmat(p.valve_resistance,4,1);rs;p.rp];
q(1:4)=max(q(1:4),0);
end

function [P,valves,q,res,solves]=hydraulic(Pold,Cold,C,h,rs,p,valves,edges)
conductance=1./[repmat(p.valve_resistance,4,1);rs;p.rp];rhs=Cold.*Pold;
seen=false(16,1);ok=false;solves=0;
for iteration=1:16
 code=1+sum(double(valves(:)').*[8,4,2,1]);
 if seen(code),break;end
 seen(code)=true;solves=solves+1;
 [P,d,ok]=candidate(C,h,conductance,rhs,valves,edges);
 if ok,break;end
 valves=d>0;
end
if ~ok
 for code=0:15
  valves=logical(bitget(code,4:-1:1)');solves=solves+1;
  [P,~,ok]=candidate(C,h,conductance,rhs,valves,edges);
  if ok,break;end
 end
end
assert(ok,'No consistent valve configuration; time step rejected.');
assert(all(isfinite(P)) && min(P)>=-1e-10,'Invalid pressure after implicit solve.');
q=flows(P,rs,p,edges);net=zeros(6,1);
for j=1:6
 net(edges(j,1))=net(edges(j,1))-q(j);net(edges(j,2))=net(edges(j,2))+q(j);
end
res=(C.*P-Cold.*Pold)/h-net;
scale=1+max([max(abs(net)),max(abs((C.*P-Cold.*Pold)/h))]);
assert(max(abs(res))<=1e-8*scale,'Compartment balance failed; time step rejected.');
end

function [P,d,ok]=candidate(C,h,conductance,rhs,valves,edges)
active=[double(valves(:));1;1].*conductance;A=diag(C);
for j=1:6
 i=edges(j,1);k=edges(j,2);w=h*active(j);
 A(i,i)=A(i,i)+w;A(k,k)=A(k,k)+w;A(i,k)=A(i,k)-w;A(k,i)=A(k,i)-w;
end
P=A\rhs;d=P(edges(1:4,1))-P(edges(1:4,2));
ok=all((valves(:) & d>=-1e-10) | (~valves(:) & d<=1e-10));
end
