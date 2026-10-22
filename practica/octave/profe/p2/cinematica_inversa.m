function [q_sol,theta,d, success, info] = cinematica_inversa(pd, q0, tipo, q_offset, d_offset, a, alpha, unidad, opts)
% CINEMATICA_INVERSA  CI numerica por Damped Least Squares (solo posicion).
% Generica para articulaciones R y P.
%
% Resuelve la postura q tal que la POSICION del TCP coincida con pd.
% Si el robot tiene mas GdL que dimensiones controladas (3, posicion),
% el algoritmo aterriza en una solucion consistente con q0 (continuidad).
%
% Entradas:
%   pd            posicion deseada del TCP, [x y z]  (mm)
%   q0            postura inicial (nx1, en la unidad indicada por 'unidad'
%                 para las R; en mm para las P)
%   tipo          string 1xn con 'R' o 'P'
%   q_offset      offsets de theta del DH (nx1, deg o rad segun unidad)
%   d_offset      offsets de d del DH     (nx1, mm)
%   a, alpha      resto de parametros DH  (nx1)
%   unidad        'deg' (default, sexagesimal) o 'rad'   -> aplica a angulos
%   opts          (opcional) struct con:
%                    max_iter (default 200)
%                    tol_pos  (default 1e-3 mm)
%                    lambda   (default 0.05) factor de amortiguamiento DLS
%                    alpha_step (default 1.0) multiplicador del paso
%                    use_analitico (default true) si false usa el numerico
%                    verbose  (default false)
%                    q_min, q_max  (default []) limites articulares (nx1)
%                                  en la misma unidad que q. Si se pasan,
%                                  se aplican como box constraints durante
%                                  la iteracion.
%
% Salidas:
%   q_sol    postura solucion (nx1)
%   success  true si convergio dentro de tol_pos
%   info     struct: iters, err_pos, lambda, en_q_min, en_q_max
%
% Algoritmo:
%   1) Evalua CD(q) y calcula error  e = pd - p_cur
%   2) Si ||e|| < tol -> listo
%   3) Calcula J con la firma general, toma solo las 3 filas de posicion
%   4) DLS:  dq = J^T (J J^T + lambda^2 I)^-1 e
%   5) q <- q + alpha_step * dq
%   6) vuelve a 1
%
% Notas:
%   - No wrap-eamos angulos dentro del loop (puede romper convergencia
%     cerca de los -180/180). Se envuelve UNA vez al final, ya convergido.
%   - El wrap (opts.wrap, default true) lleva cada eje R al equivalente
%     mod 360 (o 2*pi) mas cercano a la semilla q0. Asi un robot suelto
%     queda en el rango limpio y, encadenando muestras, no hay saltos de
%     360 (se preserva la continuidad). Las P no se tocan.
%   - El damping lambda da robustez frente a singularidades.

    if nargin < 8, unidad = 'deg'; end
    if nargin < 9, opts = struct(); end

    if ~isfield(opts,'max_iter'),     opts.max_iter     = 200;   end
    if ~isfield(opts,'tol_pos'),      opts.tol_pos      = 1e-3;  end
    if ~isfield(opts,'lambda'),       opts.lambda       = 0.05;  end
    if ~isfield(opts,'alpha_step'),   opts.alpha_step   = 1.0;   end
    if ~isfield(opts,'use_analitico'),opts.use_analitico= true;  end
    if ~isfield(opts,'verbose'),      opts.verbose      = false; end
    if ~isfield(opts,'q_min'),        opts.q_min        = [];    end
    if ~isfield(opts,'q_max'),        opts.q_max        = [];    end
    if ~isfield(opts,'wrap'),         opts.wrap         = true;  end

    q  = q0(:);
    pd = pd(:);
    n  = length(q);
    tipo = upper(tipo(:)');
    assert(length(tipo) == n, 'tipo debe tener %d caracteres', n);

    q_offset = q_offset(:);  d_offset = d_offset(:);

    % --- Limites articulares (opcional, box constraint) -----------------
    aplicar_lim = ~isempty(opts.q_min) && ~isempty(opts.q_max);
    if aplicar_lim
        q_min = opts.q_min(:);  q_max = opts.q_max(:);
        assert(length(q_min)==n && length(q_max)==n, ...
            'q_min/q_max deben tener %d elementos', n);
        assert(all(q_max >= q_min), 'q_max debe ser >= q_min componente a componente');
        % Saturamos la postura inicial por si viene afuera
        q = min(max(q, q_min), q_max);
    end

    success = false;
    err_pos = NaN;

    for k = 1:opts.max_iter
        % --- CD respetando R/P ------------------------------------------
        theta = q_offset; d = d_offset;
        for i = 1:n
            if tipo(i)=='R', theta(i) = theta(i) + q(i);
            else,            d(i)     = d(i)     + q(i);
            end
        end
        [T, ~] = cinematica_directa(theta, d, a, alpha, unidad);
        p_cur  = T(1:3, 4);
        e      = pd - p_cur;
        err_pos = norm(e);

        if opts.verbose
            fprintf('  iter %3d  err=%.4e mm  q=[%s]\n', k, err_pos, ...
                sprintf('%6.2f ', q));
        end

        if err_pos < opts.tol_pos
            success = true;
            break;
        end

        % --- Jacobiano con la firma general -----------------------------
        if opts.use_analitico
            J = jacobiano_analitico(q, tipo, q_offset, d_offset, a, alpha, unidad);
        else
            J = jacobiano_numerico (q, tipo, q_offset, d_offset, a, alpha, unidad);
        end
        Jp = J(1:3, :);

        % Damped Least Squares (forma derecha)
        dq = Jp' * ((Jp * Jp' + opts.lambda^2 * eye(3)) \ e);

        step = opts.alpha_step * dq;

        if aplicar_lim
            tol_b = 1e-9;
            % 1) Anular componentes que empujan hacia afuera de un limite ya tocado
            en_min = (q <= q_min + tol_b) & (step < 0);
            en_max = (q >= q_max - tol_b) & (step > 0);
            step(en_min | en_max) = 0;

            % 2) Escalar el paso para no salirse de los limites
            factor = 1;
            for i = 1:n
                if step(i) > 0
                    margen = q_max(i) - q(i);
                    if step(i) > margen,  factor = min(factor, margen/step(i)); end
                elseif step(i) < 0
                    margen = q_min(i) - q(i);    % negativo
                    if step(i) < margen,  factor = min(factor, margen/step(i)); end
                end
            end
            step = max(0, factor) * step;

            q = q + step;
            % Saneo numerico
            q = min(max(q, q_min), q_max);
        else
            q = q + step;
        end
    end

    % --- Wrap final SOLO de las articulaciones de revolucion -----------
    % Despues de converger (nunca dentro del loop). Cada eje R se lleva al
    % equivalente mod 360 / mod 2*pi mas cercano a la semilla q0: mismo TCP,
    % valor limpio y sin romper la continuidad al encadenar muestras.
    % Si hay limites articulares activos no se envuelve (los limites ya
    % definen el rango valido y el wrap podria sacarte de el).
    if opts.wrap && ~aplicar_lim
        if strcmpi(unidad, 'rad'), periodo = 2*pi; else, periodo = 360; end
        q0c = q0(:);
        for i = 1:n
            if tipo(i) == 'R'
                delta = q(i) - q0c(i);
                delta = mod(delta + periodo/2, periodo) - periodo/2;
                q(i)  = q0c(i) + delta;
            end
        end
    end

    q_sol = q;
    info.iters    = k;
    info.err_pos  = err_pos;
    info.lambda   = opts.lambda;
    info.unidad   = unidad;
    if aplicar_lim
        info.en_q_min = (q_sol <= q_min + 1e-6);
        info.en_q_max = (q_sol >= q_max - 1e-6);
    else
        info.en_q_min = false(n,1);
        info.en_q_max = false(n,1);
    end
end
