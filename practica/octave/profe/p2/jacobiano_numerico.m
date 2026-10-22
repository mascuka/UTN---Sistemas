function J = jacobiano_numerico(q, tipo, q_offset, d_offset, a, alpha, unidad)
% JACOBIANO_NUMERICO  Jacobiano del TCP por diferencias finitas centradas.
% Soporta articulaciones R y P.
%
% Entradas:
%   q             vector 1xn o nx1 de coordenadas articulares
%                 (deg si tipo='R' y unidad='deg', rad si 'rad'; mm si tipo='P')
%   tipo          vector char 1xn con 'R' (rotacional) o 'P' (prismatica)
%   q_offset  offsets de theta del DH (mismo n)
%   d_offset      offsets de d del DH     (mismo n)
%   a, alpha      resto de parametros DH  (vectores n)
%   unidad        'deg' (default, sexagesimal) o 'rad'. Aplica a angulos (theta, alpha).
%
% Salida:
%   J  6 x n :
%        filas 1..3  d(posicion TCP)/d(q_i)         [mm/rad o mm/deg o mm/mm]
%        filas 4..6  d(axis*ang en frame TCP)/d(q_i)

    if nargin < 7, unidad = 'deg'; end
    q = q(:);  q_offset = q_offset(:);  d_offset = d_offset(:);
    tipo = upper(tipo(:)');
    n = length(q);
    assert(length(tipo)==n,'tipo debe tener un caracter por articulacion');

    % Armado de los vectores DH segun tipo
    theta = q_offset; d = d_offset;
    for i = 1:n
        if tipo(i)=='R', theta(i) = theta(i) + q(i);
        else,            d(i)     = d(i)     + q(i);
        end
    end

    % Pose nominal
    [T0, ~] = cinematica_directa(theta, d, a, alpha, unidad);
    R0 = T0(1:3, 1:3);

    % Paso por articulacion (R en unidad angular, P en mm)
    if strcmpi(unidad,'deg'), hR = 1e-3; else, hR = 1e-6; end
    hP = 1e-3;  % mm

    J = zeros(6, n);

    for i = 1:n
        thp = theta; dp = d;
        thm = theta; dm = d;

        if tipo(i)=='R'
            thp(i) = thp(i) + hR;  thm(i) = thm(i) - hR;  h = hR;
        else
            dp(i)  = dp(i)  + hP;  dm(i)  = dm(i)  - hP;  h = hP;
        end

        [Tp, ~] = cinematica_directa(thp, dp, a, alpha, unidad);
        [Tm, ~] = cinematica_directa(thm, dm, a, alpha, unidad);

        % Posicion
        dpos = (Tp(1:3,4) - Tm(1:3,4)) / (2*h);

        % Orientacion en frame TCP (axis-angle de R0' * R_pert)
        Rp = Tp(1:3,1:3);
        Rm = Tm(1:3,1:3);
        dori = ( axisAngle(R0' * Rp) - axisAngle(R0' * Rm) ) / (2*h);

        J(:, i) = [dpos; dori];
    end
end

function v = axisAngle(R)
    c = (trace(R) - 1) / 2;
    c = max(-1, min(1, c));
    ang = acos(c);
    if abs(ang) < 1e-9
        v = zeros(3,1);
    else
        axis = 1/(2*sin(ang)) * [ R(3,2)-R(2,3);
                                  R(1,3)-R(3,1);
                                  R(2,1)-R(1,2) ];
        v = axis * ang;
    end
end
