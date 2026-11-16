function run_matlab_checks()
% Must actually run on MATLAB or compatible Octave before cross-language claims.
% Generate Python references first with: python demo.py
names={'fixed','feedback'};gains=[0,10];summary=zeros(2,4);
columns={'phase','filtered_pressure','rate_bpm','P_LV','P_sa','P_sv','P_RV','P_pa','P_pv','Q_mi','Q_ao','Q_tr','Q_pu','Q_s','Q_p'};
fprintf('Engine: %s\n',version);
for k=1:2
 r=feedback_demo(struct('gain',gains(k)));
 ref=dlmread(['cross-language-',names{k},'.csv'],',',1,0);
 computed=[r.phase,r.filtered_pressure,r.rate_bpm,r.pressure,r.flows];
 at_ref=interp1(r.time_s,computed,ref(:,1),'linear');
 [difference,where]=max(abs(at_ref-ref(:,2:end)),[],1);
 [worst,j]=max(difference);
 fprintf('%s: largest difference %.16g in %s at %.16g s\n',names{k},worst,columns{j},ref(where(j),1));
 assert(all(isfinite(at_ref(:))),'Nonfinite cross-language interpolation.');
 assert(worst<1e-4,'Python/companion discrepancy above declared tolerance; see named column/time above.');
 assert(r.max_volume_drift_L<1e-8 && r.max_balance_residual_L_min<1e-7);
 assert(all(diff(r.phase)>0) && min(r.rate_bpm)>=30 && max(r.rate_bpm)<=240);
 summary(k,:)=[max(difference),r.max_volume_drift_L,r.max_balance_residual_L_min,r.max_linear_solves_per_step];
end
fid=fopen('matlab-check-results.csv','w');
assert(fid>0,'Could not create MATLAB test receipt.');
fprintf(fid,'max_cross_language_error,max_volume_drift_L,max_balance_residual_L_min,max_linear_solves\n');
fprintf(fid,'%.16g,%.16g,%.16g,%.16g\n',summary');fclose(fid);
disp('Companion checks executed and passed on the engine reported above; receipt: matlab-check-results.csv');
end
