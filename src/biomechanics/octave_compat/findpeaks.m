function [peaks, locations] = findpeaks(x, varargin)
% Restricted MATLAB-style adapter for the parameters used by the RIC source.
% Handles signed signals and greedy height-based minimum peak distance.
  x = x(:);
  distance = 1; height = -Inf;
  for k = 1:2:numel(varargin)
    switch lower(varargin{k})
      case 'minpeakdistance'; distance = varargin{k+1};
      case 'minpeakheight'; height = varargin{k+1};
      otherwise; error('Unsupported findpeaks parameter in reference adapter');
    endswitch
  endfor
  candidate = [];
  k = 2;
  while k < numel(x)
    if isfinite(x(k)) && x(k) > x(k-1)
      last = k;
      while last < numel(x) && x(last+1) == x(k); last = last+1; endwhile
      if last < numel(x) && x(k) > x(last+1) && x(k) > height
        candidate(end+1,1) = k;
      endif
      k = last+1;
    else
      k = k+1;
    endif
  endwhile
  if isempty(candidate); peaks = []; locations = []; return; endif
  [~, order] = sortrows([-x(candidate), candidate], [1 2]);
  kept = [];
  for j = order(:)'
    position = candidate(j);
    if isempty(kept) || all(abs(kept-position) >= distance)
      kept(end+1,1) = position;
    endif
  endfor
  locations = sort(kept);
  peaks = x(locations);
endfunction
