function dibujarSistemasDeEjesCoordenadosDeRobot(titulo, varargin)
% Dibuja los sistemas de ejes coordenados del robot en 3D
% Cada argumento debe ser una matriz de transformación homogénea 4x4
% RELATIVA entre eslabones consecutivos: A01, A12, A23, ...
% La función acumula internamente para obtener T0i = A01*A12*...*A(i-1)i
% y dibuja los sistemas S0 (base), S1, S2, ..., Sn.
% Las flechas se dibujan con largo fijo de 100 mm para que sean visibles
% en escenas de robots cuyas dimensiones son del orden de cientos de mm.

    L = 100;   % [mm] largo de las flechas

    figure;   % siempre una figura nueva en cada llamada
    set(gca,'FontSize',12); hold on; grid on
    xlabel('x'); ylabel('y'); zlabel('z');
    title(titulo)

    n = length(varargin);

    % Acumular: T{1}=I (S0 base), T{i+1}=T{i}*A_{i-1,i}
    T = cell(1, n+1);
    T{1} = eye(4);
    for i = 1:n
        A = varargin{i};
        if ~isequal(size(A), [4 4])
            error('Cada argumento debe ser una matriz 4x4 (A01, A12, ...)');
        end
        T{i+1} = T{i} * A;
    end

    for i = 1:(n+1)
        % Extraer rotación y posición del sistema i-1 (índice MATLAB i)
        R = T{i}(1:3,1:3);
        p = T{i}(1:3,4);

        % Dibujar ejes del sistema (flechas de largo L)
        arrow(p, p + L*R(:,1), 'linewidth', 2, 'color', 'r');
        arrow(p, p + L*R(:,2), 'linewidth', 2, 'color', 'g');
        arrow(p, p + L*R(:,3), 'linewidth', 2, 'color', 'b');

        % Etiquetas: S0, S1, ..., Sn
        text(p(1), p(2), p(3), sprintf('S%d', i-1), 'FontSize', 12, 'FontWeight', 'bold');

        % Dibujar línea al sistema anterior
        if i > 1
            pprev = T{i-1}(1:3,4);
            line([pprev(1), p(1)], [pprev(2), p(2)], [pprev(3), p(3)], ...
                'Color', 'k', 'LineWidth', 2, 'LineStyle', '-.');
        end
    end

    view(30,30)
    axis equal
end


function arrow(position, target, varargin)
    % Argumentos por defecto
    linewidth = 1;
    color = 'b';

    % Procesar argumentos opcionales
    for i = 1:2:numel(varargin)
        if strcmp(varargin{i}, 'linewidth')
            linewidth = varargin{i + 1};
        elseif strcmp(varargin{i}, 'color')
            color = varargin{i + 1};
        end
    end

    % Dibujar la flecha
    quiver3(position(1), position(2), position(3), ...
        target(1) - position(1), target(2) - position(2), target(3) - position(3), ...
        'LineWidth', linewidth, ...
        'Color', color, ...
        'MaxHeadSize', 1);
end
