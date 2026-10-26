function run_reference(root, jobs_file, adapted_folder)
  pkg load signal;
  addpath(adapted_folder, '-begin');
  cd(adapted_folder);
  set(0, 'defaultfigurevisible', 'off');
  jobs = jsondecode(fileread(jobs_file));
  for index = 1:numel(jobs)
    job = jobs(index);
    if exist(job.output_path, 'file')
      fprintf('REFERENCE cached %s\n', job.participant_id); fflush(stdout); continue;
    endif
    fprintf('REFERENCE start %s\n', job.participant_id); fflush(stdout);
    try
      raw = jsondecode(fileread(job.raw_path));
      names = fieldnames(raw.joints);
      for k = 1:numel(names); raw.joints.(names{k}) = raw.joints.(names{k})(:)'; endfor
      names = fieldnames(raw.neutral);
      for k = 1:numel(names); raw.neutral.(names{k}) = raw.neutral.(names{k})(:)'; endfor
      hz = raw.hz_r;
      nframes = rows(raw.running.pelvis_1);
      [angles, velocities] = gait_kinematics(raw.joints,raw.neutral,raw.running,hz,0);
      pca = struct(); pca_error = '';
      try
        [pca.L_TD,pca.R_TD] = pca_td(angles,hz,'run');
        [pca.L_TO,pca.R_TO] = pca_to(angles,hz,'run');
      catch err
        pca_error = err.message;
      end_try_catch
      [norm_ang, ~, events, event, discrete, speed, eventsflag, label] = gait_steps(raw.neutral,raw.running,angles,velocities,hz,0);
      participant_id = job.participant_id;
      filename = job.filename;
      engine = version;
      save('-mat7-binary',job.output_path,'participant_id','filename','engine','hz','nframes','angles','pca','pca_error','norm_ang','events','event','eventsflag','discrete','speed','label');
      fprintf('REFERENCE complete %s events=%d\n',job.participant_id,rows(events)); fflush(stdout);
    catch err
      failed = struct('participant_id',job.participant_id,'filename',job.filename,'error',err.message,'stack',err.stack);
      handle = fopen([job.output_path '.error.json'],'w'); fputs(handle,jsonencode(failed)); fclose(handle);
      fprintf('REFERENCE FAILED %s: %s\n',job.participant_id,err.message); fflush(stdout);
    end_try_catch
    clear raw angles velocities norm_ang events event discrete pca;
  endfor
endfunction
