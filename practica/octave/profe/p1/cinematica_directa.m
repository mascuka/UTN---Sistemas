function [T, origins, Tsist] = cinematica_directa(theta, d, a, alpha, unidad)
% CINEMATICA_DIRECTA  CD del robot a partir de los 4 vectores DH.
%
% Entradas (vectores de igual longitud n):
%   theta   angulo total de cada articulacion       (deg o rad segun unidad)
%   d       desplazamiento sobre z_{i-1}            (m o mm)
%   a       longitud del eslabon sobre x_i          (m o mm)
%   alpha   torsion del eslabon sobre x_i           (deg o rad segun unidad)
%   unidad  'deg' (default, sexagesimal) o 'rad'
%
% Salidas:
%   T        matriz homogenea 4x4 del TCP respecto a la base
%   origins  3x(n+1) con la posicion de cada origen, incluyendo la base
%   Tsist    (opcional) 4x4xn con las matrices RELATIVAS A_{i-1,i} para
%            i=1..n. Es decir Tsist(:,:,1)=A01, Tsist(:,:,2)=A12, ...,
%            Tsist(:,:,n)=A_{n-1,n}. Pensado para alimentar directo a
%            dibujarSistemasDeEjesCoordenadosDeRobot.

    if nargin < 5, unidad = 'deg'; end

    theta = theta(:); d = d(:); a = a(:); alpha = alpha(:);
    n = length(theta);
    assert(all([length(d) length(a) length(alpha)] == n), ...
        'theta, d, a, alpha deben tener la misma longitud');

    T = eye(4);
    origins = zeros(3, n+1);   % col 1 = base
    Tsist = repmat(eye(4), [1 1 n]);

    for i = 1:n
        A = matrizDenavitHartenberg(theta(i), d(i), a(i), alpha(i), unidad);
        Tsist(:,:,i) = A;
        T = T * A;
        origins(:, i+1) = T(1:3, 4);
    end
end