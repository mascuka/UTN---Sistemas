function A = matrizDenavitHartenberg(q, d, a, alfa, unidad)
% MATRIZDENAVITHARTENBERG  Matriz de transformacion DH estandar.
%
%   A = matrizDenavitHartenberg(q, d, a, alfa)            % por defecto grados (deg)
%   A = matrizDenavitHartenberg(q, d, a, alfa, 'rad')     % q y alfa en radianes
%
% unidad = 'deg' (default) -> q y alfa en grados sexagesimales (cosd/sind).
% unidad = 'rad'           -> q y alfa en radianes (cos/sin).

    if nargin < 5
        unidad = 'deg';
    end

    if strcmpi(unidad, 'deg')
        A = [ cosd(q) -sind(q)*cosd(alfa)  sind(q)*sind(alfa)  a*cosd(q);
              sind(q)  cosd(q)*cosd(alfa) -cosd(q)*sind(alfa)  a*sind(q);
              0        sind(alfa)          cosd(alfa)           d;
              0        0                   0                    1 ];
    else
        A = [ cos(q)  -sin(q)*cos(alfa)   sin(q)*sin(alfa)   a*cos(q);
              sin(q)   cos(q)*cos(alfa)  -cos(q)*sin(alfa)   a*sin(q);
              0        sin(alfa)          cos(alfa)           d;
              0        0                  0                   1 ];
    end
end