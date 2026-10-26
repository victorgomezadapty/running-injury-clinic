function validate_official_events(projectRoot, outputDir)
% Re-run the supplied RIC MATLAB workflow for the fixed 30-file pilot.
% Requires MATLAB with Statistics and Machine Learning Toolbox plus Signal
% Processing Toolbox. gaitClass.mat is a MATLAB classifier object. The runner
% never modifies raw JSONs.
%
% Run from MATLAB with:
%   validate_official_events('C:\path\to\Running_Injury_Clinic')

if nargin < 1 || strlength(string(projectRoot)) == 0
    projectRoot = fileparts(fileparts(mfilename('fullpath')));
end
if nargin < 2 || strlength(string(outputDir)) == 0
    outputDir = fullfile(projectRoot, 'reports', 'official_reprocessing');
end
projectRoot = char(projectRoot);
outputDir = char(outputDir);

manifestPath = fullfile(projectRoot, 'data', 'interim', 'provenance', ...
    'pilot_manifests', ...
    '0ebffe1704471632f2f2a947194d813af9a857da175422fe237b88c390035ed4.csv');
codeDir = fullfile(projectRoot, 'data', 'raw', 'official_code', ...
    'Supplemental_materials', 'Code');
registryPath = fullfile(projectRoot, 'reports', 'tables', ...
    'pilot_feature_registry.csv');
if ~isfile(manifestPath) || ~isfolder(codeDir) || ~isfile(registryPath)
    error('Pilot manifest, official source code, or feature registry is missing.');
end

manifest = readtable(manifestPath, 'TextType', 'string');
registry = readtable(registryPath, 'TextType', 'string');
if height(manifest) ~= 30 || numel(unique(manifest.participant_id)) ~= 30
    error('The pinned pilot manifest must contain 30 unique participants.');
end

if ~isfolder(outputDir), mkdir(outputDir); end
eventsPath = fullfile(outputDir, 'official_events.csv');
summaryPath = fullfile(outputDir, 'official_trial_summary.csv');
comparisonPath = fullfile(outputDir, 'official_dv_comparison.csv');
resultsPath = fullfile(outputDir, 'official_reprocessing_results.mat');

oldFolder = pwd;
folderCleanup = onCleanup(@() cd(oldFolder));
addpath(codeDir);
cd(codeDir); % PCA functions load event_data_*.mat and gaitClass.mat by name.

eventRows = table(zeros(0,1), strings(0,1), strings(0,1), zeros(0,1), ...
    NaN(0,1), NaN(0,1), NaN(0,1), NaN(0,1), NaN(0,1), NaN(0,1), ...
    NaN(0,1), NaN(0,1), 'VariableNames', {'trial_index','participant_id', ...
    'filename','cycle_index','left_td_frame','left_to_frame', ...
    'right_td_frame','right_to_frame','left_td_pca_used','left_to_pca_used', ...
    'right_td_pca_used','right_to_pca_used'});
summaryRows = table(zeros(0,1), strings(0,1), strings(0,1), strings(0,1), ...
    NaN(0,1), NaN(0,1), NaN(0,1), NaN(0,1), NaN(0,1), NaN(0,1), ...
    NaN(0,1), ...
    'VariableNames', {'trial_index','participant_id','filename', ...
    'official_gait_label','sampling_hz','retained_event_rows','event_rows', ...
    'official_speed_m_s','normalized_left_hip_cycles', ...
    'normalized_right_hip_cycles','fraction_events_using_pca'});
comparisonRows = table(zeros(0,1), strings(0,1), strings(0,1), strings(0,1), ...
    strings(0,1), NaN(0,1), NaN(0,1), NaN(0,1), NaN(0,1), ...
    'VariableNames', {'trial_index','participant_id','filename','side', ...
    'feature','stored_json_value','official_rerun_value','signed_difference', ...
    'absolute_difference'});
cycleRows = table(zeros(0,1), strings(0,1), strings(0,1), strings(0,1), ...
    strings(0,1), NaN(0,1), NaN(0,1), NaN(0,1), NaN(0,1), ...
    'VariableNames', {'trial_index','participant_id','filename','side', ...
    'segment','normalized_angle_cycles','normalized_velocity_cycles', ...
    'normalized_points','coordinate_axes'});
results = repmat(struct('participant_id', '', 'filename', '', ...
    'source_sha256', '', 'status', '', 'error', '', 'label', '', ...
    'sampling_hz', NaN, 'events', [], 'eventsflag', [], 'event', [], ...
    'discrete_variables', [], 'norm_ang', [], 'norm_vel', []), ...
    height(manifest), 1);

for k = 1:height(manifest)
    pid = string(manifest.participant_id(k));
    filename = string(manifest.filename(k));
    rel = fullfile('reformat_data', char(pid), char(filename));
    jsonPath = fullfile(projectRoot, 'data', 'raw', 'pilot', rel);
    if ~isfile(jsonPath)
        jsonPath = fullfile(projectRoot, 'data', 'raw', 'sample', rel);
    end
    results(k).participant_id = char(pid);
    results(k).filename = char(filename);
    try
        if ~isfile(jsonPath), error('Pilot JSON not found: %s', jsonPath); end
        results(k).source_sha256 = sha256_file(jsonPath);
        out = jsondecode(fileread(jsonPath));

        % The official tutorial explicitly transposes these JSON-decoded
        % static arrays before passing them to gait_kinematics/gait_steps.
        names = fieldnames(out.joints);
        for j = 1:numel(names)
            out.joints.(names{j}) = transpose(out.joints.(names{j}));
        end
        names = fieldnames(out.neutral);
        for j = 1:numel(names)
            out.neutral.(names{j}) = transpose(out.neutral.(names{j}));
        end
        if ~isfield(out, 'running') || isempty(out.running) || ...
                ~isfield(out, 'hz_r') || isempty(out.hz_r)
            error('Running trajectories or sampling rate are absent.');
        end

        plots = 0;
        [angles, velocities] = gait_kinematics(out.joints, out.neutral, ...
            out.running, out.hz_r, plots);
        [normAng, normVel, events, event, discrete, speedOutput, eventsflag, label] = ...
            gait_steps(out.neutral, out.running, angles, velocities, ...
            out.hz_r, plots);

        results(k).status = 'ok';
        results(k).label = char(label);
        results(k).sampling_hz = double(out.hz_r);
        results(k).events = events;
        results(k).eventsflag = eventsflag;
        results(k).event = event;
        results(k).discrete_variables = discrete;
        results(k).norm_ang = normAng;
        results(k).norm_vel = normVel;

        n = size(events, 1);
        if n > 0
            ids = repmat(k, n, 1);
            eventRows = [eventRows; table(ids, repmat(pid,n,1), ...
                repmat(filename,n,1), (1:n)', events(:,1), events(:,2), ...
                events(:,3), events(:,4), eventsflag(:,1), eventsflag(:,2), ...
                eventsflag(:,3), eventsflag(:,4), ...
                'VariableNames', {'trial_index','participant_id','filename', ...
                'cycle_index','left_td_frame','left_to_frame','right_td_frame', ...
                'right_to_frame','left_td_pca_used','left_to_pca_used', ...
                'right_td_pca_used','right_to_pca_used'})]; %#ok<AGROW>
        end

        summaryRows = [summaryRows; table(k, pid, filename, string(label), ...
            double(out.hz_r), n, size(event,1), speedOutput, ...
            cycle_count(normAng, 'L_hip'), cycle_count(normAng, 'R_hip'), ...
            mean(eventsflag(:) == 1), 'VariableNames', {'trial_index', ...
            'participant_id','filename','official_gait_label','sampling_hz', ...
            'retained_event_rows','event_rows','official_speed_m_s', ...
            'normalized_left_hip_cycles','normalized_right_hip_cycles', ...
            'fraction_events_using_pca'})]; %#ok<AGROW>

        % gait_steps may remove curves after event pairing. Count returned
        % normalized cycles separately by side and segment.
        segmentNames = {'ankle','knee','hip','foot','pelvis'};
        sideNames = {'L','R'};
        for si = 1:numel(sideNames)
            sidePrefix = sideNames{si};
            sideLabel = 'left';
            if strcmp(sidePrefix, 'R'), sideLabel = 'right'; end
            for gi = 1:numel(segmentNames)
                segment = segmentNames{gi};
                fieldName = [sidePrefix '_' segment];
                a = normAng.(fieldName);
                angleN = size(a, 2);
                velocityN = NaN;
                if isfield(normVel, fieldName)
                    velocityN = size(normVel.(fieldName), 2);
                end
                cycleRows = [cycleRows; table(k, pid, filename, ...
                    string(sideLabel), string(segment), angleN, velocityN, ...
                    size(a,1), size(a,3), 'VariableNames', {'trial_index', ...
                    'participant_id','filename','side','segment', ...
                    'normalized_angle_cycles','normalized_velocity_cycles', ...
                    'normalized_points','coordinate_axes'})]; %#ok<AGROW>
            end
        end

        for q = 1:height(registry)
            feature = char(registry.feature(q));
            for sideColumn = 2:3
                if sideColumn == 2, side = 'left'; else, side = 'right'; end
                stored = NaN;
                try
                    stored = double(out.dv_r.(side).(feature));
                catch
                    % Absent/non-scalar source values remain NaN and are visible.
                end
                rerun = double(discrete(double(registry.source_matrix_row(q)), sideColumn));
                difference = rerun - stored;
                comparisonRows = [comparisonRows; table(k, pid, filename, ...
                    string(side), string(feature), stored, rerun, difference, ...
                    abs(difference), ...
                    'VariableNames', {'trial_index','participant_id','filename', ...
                    'side','feature','stored_json_value','official_rerun_value', ...
                    'signed_difference','absolute_difference'})]; %#ok<AGROW>
            end
        end
        fprintf('Official reprocessing complete: %s / %s (%d cycles)\n', ...
            pid, filename, n);
    catch ME
        results(k).status = 'error';
        results(k).error = getReport(ME, 'basic', 'hyperlinks', 'off');
        summaryRows = [summaryRows; table(k, pid, filename, string("error"), ...
            NaN, 0, 0, NaN, NaN, NaN, NaN, ...
            'VariableNames', {'trial_index', ...
            'participant_id','filename','official_gait_label','sampling_hz', ...
            'retained_event_rows','event_rows','official_speed_m_s', ...
            'normalized_left_hip_cycles','normalized_right_hip_cycles', ...
            'fraction_events_using_pca'})]; %#ok<AGROW>
        fprintf(2, 'Official reprocessing failed: %s / %s: %s\n', ...
            pid, filename, ME.message);
    end
end

writetable(eventRows, eventsPath);
writetable(summaryRows, summaryPath);
writetable(comparisonRows, comparisonPath);
writetable(cycleRows, fullfile(outputDir, 'official_cycle_counts.csv'));
save(resultsPath, 'results', 'manifestPath', 'registryPath', '-v7.3');
fprintf('Saved event/cycle indices: %s\n', eventsPath);
fprintf('Saved normalized cycle counts: %s\n', ...
    fullfile(outputDir, 'official_cycle_counts.csv'));
fprintf('Saved rerun comparisons: %s\n', comparisonPath);
fprintf('Successful trials: %d/%d\n', sum(strcmp({results.status}, 'ok')), ...
    numel(results));
end

function n = cycle_count(curves, fieldName)
n = NaN;
if isfield(curves, fieldName)
    n = size(curves.(fieldName), 2);
end
end

function value = sha256_file(path)
fid = fopen(path, 'rb');
if fid < 0, error('Cannot open source JSON for hashing: %s', path); end
cleanup = onCleanup(@() fclose(fid));
bytes = fread(fid, Inf, '*uint8');
engine = java.security.MessageDigest.getInstance('SHA-256');
engine.update(bytes);
hashBytes = typecast(engine.digest(), 'uint8');
value = lower(reshape(dec2hex(hashBytes, 2).', 1, []));
end
