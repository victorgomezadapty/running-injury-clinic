function y = nanmedian(x, varargin)
  y = median(x, varargin{:}, 'omitnan');
endfunction
