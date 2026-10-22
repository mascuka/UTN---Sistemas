function J = jacobiano_analitico(q, tipo, q_offset, d_offset, a, alpha, unidad)
% JACOBIANO_ANALITICO  Jacobiano geometrico del TCP, por columnas. R y P.
%
% Convencion HIBRIDA (coincide con jacobiano_numerico.m):
%   filas 1..3  velocidad lineal del TCP, expresada en frame BASE
%   filas 4..6  velocidad angular del TCP, expresada en frame TCP
%
% Para revoluta i:
%   Jv_i = z_{i-1}  x  (p_n - p_{i-1})
%   Jw_i = R_n' * z_{i-1}
% Para prismatica i:
%   Jv_i = z_{i-1}
%   Jw_i = 0
%
% Entradas:
%   q             coordenadas articulares (nx1, deg/rad para R; mm para P)
%   tipo          string 1xn con 'R' o 'P'
%   q_offset  offsets de theta del DH (nx1)
%   d_offset      offsets de d del DH     (nx1)
%   a, alpha      resto de parametros DH  (nx1)
%   unidad        'deg' (default, sexagesimal) o 'rad'. Aplica a angulos.
%
% Salida:
%   J  6xn. Unidades por columna segun tipo y unidad de q.
%      Revoluta + 'deg' -> se escala por pi/180 (compatible con numerico).

    if nargin < 7, unidad = 'deg'; end
    q = q(:); q_offset = q_offset(:); d_offset = d_offset(:);
    a = a(:); alpha = alpha(:);
    tipo = upper(tipo(:)');
    n = length(q);
    assert(length(tipo) == n, 'tipo debe tener %d caracteres', n);

    % Armado de theta y d finales segun tipo
    theta = q_offset; d = d_offset;
    for i = 1:n
        switch tipo(i)
            case 'R', theta(i) = theta(i) + q(i);
            case 'P', d(i)     = d(i)     + q(i);
            otherwise, error('tipo(%d) invalido: %s', i, tipo(i));
        end
    end

    % Transformaciones acumuladas T_{0,i} para i=0..n
    Tcum = repmat(eye(4), [1 1 n+1]);
    for i = 1:n
        A = matrizDenavitHartenberg(theta(i), d(i), a(i), alpha(i), unidad);
        Tcum(:,:,i+1) = Tcum(:,:,i) * A;
    end

    p_n = Tcum(1:3, 4, n+1);
    R_n = Tcum(1:3, 1:3, n+1);

    J = zeros(6, n);
    for i = 1:n
        z_prev = Tcum(1:3, 3, i);   % z_{i-1} en frame base
        p_prev = Tcum(1:3, 4, i);   % p_{i-1} en frame base

        if tipo(i) == 'R'
            Jv = cross(z_prev, p_n - p_prev);   % base
            Jw = R_n' * z_prev;                 % TCP
        else  % 'P'
            Jv = z_prev;
            Jw = zeros(3,1);
        end

        J(:, i) = [Jv; Jw];
    end

    % Escalado deg->rad solo para revolutas (compatibilidad con numerico)
    if strcmpi(unidad, 'deg')
        k = pi/180;
        for i = 1:n
            if tipo(i) == 'R'
                J(:,i) = J(:,i) * k;
            end
        end
    end
end