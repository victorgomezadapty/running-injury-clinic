function [y, idx] = nanmin(x, unused, dim)
  if nargin < 3
    dim = find(size(x) != 1, 1);
    if isempty(dim); dim = 1; endif
  endif
  missing = isnan(x);
  x(missing) = Inf;
  [y, idx] = min(x, [], dim);
  mask = all(missing, dim);
  y(mask) = NaN;
  idx(mask) = 1;
endfunction
