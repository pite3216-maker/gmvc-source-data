% Plot deposited simulation outputs. Core simulation algorithms are not included.
% Tested with MATLAB R2025a. No specialist toolboxes are required.
root = fileparts(fileparts(mfilename('fullpath')));
data = fullfile(root,'data'); out = fullfile(root,'analysis_results');
if ~exist(out,'dir'), mkdir(out); end

D = readtable(fullfile(data,'dual_control.csv'));
fig = figure('Visible','off','Color','w','Position',[50 50 1000 600]);
tiledlayout(2,1);
nexttile; plot(D.step,D.reference,'k--',D.step,D.output,'b-');
xlabel('Control step'); ylabel('Output');
legend('Reference','GMVC output','Location','best'); grid on;
nexttile; plot(D.step,D.error,'b-'); xlabel('Control step');
ylabel('Tracking error'); grid on;
exportgraphics(fig,fullfile(out,'dual_tracking.png'),'Resolution',200); close(fig);

D = readtable(fullfile(data,'dual_fit.csv'));
S = jsondecode(fileread(fullfile(data,'dual_summary.json')));
fig = figure('Visible','off','Color','w','Position',[50 50 1000 400]);
plot(D.sample_index,D.contribution_score,'b-'); hold on;
yline(S.pruning_threshold,'k--');
isPruned = ~logical(D.retained);
scatter(D.sample_index(isPruned),D.contribution_score(isPruned),8,'r','filled');
xlabel('Original sample index'); ylabel('Weighted contribution');
legend('Contribution','Threshold','Pruned samples','Location','best'); grid on;
exportgraphics(fig,fullfile(out,'dual_pruning.png'),'Resolution',200); close(fig);

V = readtable(fullfile(data,'microgrid_validation.csv'));
fig = figure('Visible','off','Color','w','Position',[50 50 1000 800]);
tiledlayout(3,1);
for mode = 1:3
    idx = V.target_mode == mode;
    prediction = V.(sprintf('prediction_%d_V',mode));
    nexttile; plot(V.target_index(idx),V.actual_voltage_V(idx),'k-', ...
                  V.target_index(idx),prediction(idx),'r--');
    xlabel('Target sample index'); ylabel('Bus voltage (V)');
    title(sprintf('Local predictor %d on its corresponding mode',mode));
    legend('Actual','Predicted','Location','best'); grid on;
end
exportgraphics(fig,fullfile(out,'microgrid_validation.png'),'Resolution',200); close(fig);

C = readtable(fullfile(data,'microgrid_control.csv'));
fig = figure('Visible','off','Color','w','Position',[50 50 1000 750]);
tiledlayout(3,1);
nexttile; plot(C.time_s,C.reference_V,'k:',C.time_s,C.gmvc_voltage_V,'b-',C.time_s,C.mv_voltage_V,'r--');
xlabel('Time (s)'); ylabel('Bus voltage (V)');
legend('Reference','GMVC','Classical MV','Location','best'); grid on;
nexttile; plot(C.time_s,C.gmvc_error_V,'b-',C.time_s,C.mv_error_V,'r--');
xlabel('Time (s)'); ylabel('Tracking error (V)'); legend('GMVC','Classical MV','Location','best'); grid on;
nexttile; plot(C.time_s,C.gmvc_input_command_V,'b-',C.time_s,C.mv_input_command_V,'r--');
xlabel('Time (s)'); ylabel('Input command (V)'); legend('GMVC','Classical MV','Location','best'); grid on;
exportgraphics(fig,fullfile(out,'microgrid_control.png'),'Resolution',200); close(fig);

fig = figure('Visible','off','Color','w','Position',[50 50 1000 650]);
tiledlayout(2,1);
nexttile; plot(V.predictor_index,[V.residual_belief_1,V.residual_belief_2,V.residual_belief_3]);
xlabel('Predictor sample index'); ylabel('Weight'); title('Smoothed residual-based weights');
legend('Model 1','Model 2','Model 3','Location','best'); grid on;
nexttile; plot(V.predictor_index,[V.display_belief_1,V.display_belief_2,V.display_belief_3]);
xlabel('Predictor sample index'); ylabel('Weight'); title('Displayed weights: 94% schedule + 6% residual');
legend('Model 1','Model 2','Model 3','Location','best'); grid on;
exportgraphics(fig,fullfile(out,'microgrid_weights.png'),'Resolution',200); close(fig);
fprintf('Deposited data plots written to %s\n',out);
