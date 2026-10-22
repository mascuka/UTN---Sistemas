function [q, Dq, t] = generacion_de_trayectorias(qi, qf, wmax, h)
%% Generador de trayectorias punto a punto - Movimiento SIMULTANEO sincronizado.
% Todas las articulaciones arrancan y llegan juntas (velocidades ecualizadas).
%
% Entradas (vectores fila 1xN):
%   qi    : configuracion inicial          [q1i q2i ...]
%   qf    : configuracion final            [q1f q2f ...]
%   wmax  : velocidad maxima por eje (>0)  [w1  w2  ...]
%   h     : paso de muestreo deseado [s]   (escalar > 0)
% Salidas:
%   q  : matriz de posiciones  (Npts x dof)
%   Dq : matriz de velocidades (Npts x dof)
%   t  : vector de tiempos     (Npts x 1)

    qi = qi(:).';  qf = qf(:).';  wmax = wmax(:).';   % forzar fila
    dof =  max(size(qf));    % Grados de libertad

    % Tiempo total = el de la articulacion mas lenta. Marca el ritmo de todas.
    T = max( abs(qf - qi) ./ wmax );

    % Caso degenerado: no hay movimiento.
    if T == 0
        t  = [0; h];
        q  = [qi; qf];
        Dq = zeros(2, dof);
        
        return
    end

    % Velocidades ecualizadas: cada eje recorre su delta en el MISMO T.
    wT = (qf - qi) / T;                     % |wT(k)| <= wmax(k) por construccion

    % Grilla temporal robusta: siempre incluye 0 y T, y nunca menos de 2 puntos.
    % Paso efectivo <= h (cierra exacto en qf aunque T no sea multiplo de h).
    n = max(2, ceil(T / h) + 1);
    t = linspace(0, T, n).';                % columna Npts x 1

    % Trayectoria: posicion lineal en el tiempo, velocidad constante.
    q = repmat(qi, n, 1) + t * wT;                  % (Npts x 1)*(1 x dof) -> Npts x dof
    Dq = repmat(wT, n, 1);

    
end
