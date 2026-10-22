function animar_trayectoria(t, q, dh_params, joint_types)
%% ANIMAR_TRAYECTORIA Visualiza el robot en 3D mediante matrices DH sin toolboxes.
% Entradas:
%   t           : Vector de tiempos (Npts x 1)
%   q           : Matriz de valores articulares (Npts x dof) [Rad/m o Deg/m]
%   dh_params   : Matriz DH constante (dof x 3) -> [a, alpha, d_o_theta_fijo]
%   joint_types : (Opcional) String o Cell array indicando el tipo de articulación:
%                 'R' o 0 para Rotacional (varía theta)
%                 'P' o 1 para Prismática (varía d)
%                 Ejemplo: ['R', 'P', 'R'] o {'R', 'P', 'R'}

    [Npts, dof] = size(q);

    % Configurar tipos de articulación por defecto si no se especifican (todas Rotacionales)
    if nargin < 4 || isempty(joint_types)
        joint_types = repmat('R', 1, dof);
    end

    % Convertir joint_types a formato de caracteres estandarizado
    if isnumeric(joint_types)
        % Convertir 0/1 a 'R'/'P'
        types_char = repmat('R', 1, dof);
        types_char(joint_types == 1) = 'P';
        joint_types = types_char;
    end

    % Convertir a radianes SOLO las articulaciones que sean Rotacionales
    q_rad = q;
    for j = 1:dof
        if upper(joint_types(j)) == 'R' && max(abs(q(:, j))) > 2*pi
            q_rad(:, j) = deg2rad(q(:, j));
        end
    end

    % --- ANIMACIÓN 3D ---
    if nargin >= 3 && ~isempty(dh_params)
        fig = figure('Name', 'Animación 3D Robot (Rotacional + Prismático)', 'NumberTitle', 'off');
        grid on; hold on; axis equal; view(3);
        xlabel('X [m]'); ylabel('Y [m]'); zlabel('Z [m]');
        %rotate3d on; set(gca, 'GraphicsSmoothing', 'on');

        h_brazo = plot3(0, 0, 0, '-o', 'LineWidth', 3, 'MarkerSize', 6, ...
                        'MarkerFaceColor', 'r', 'Color', [0.2 0.2 0.8]);
        h_traza = plot3(0, 0, 0, 'r--', 'LineWidth', 1.2);
        
        traza_punta = zeros(Npts, 3);

        % Ajuste dinámico de límites considerando desplazamientos prismáticos máximos
%         alcanzo_max = sum(abs(dh_params(:,1)) + abs(dh_params(:,3))) + max(abs(q(:)));
%         if alcanzo_max == 0, alcanzo_max = 1; end
%         xlim([-alcanzo_max, alcanzo_max]);
%         ylim([-alcanzo_max, alcanzo_max]);
%         zlim([-alcanzo_max*0.2, alcanzo_max*1.2]);

        for i = 1:Npts
            if ~ishandle(h_brazo), break; end
            
            % Se pasa el tipo de articulación a la cinemática directa
            P = calcular_puntos_dh(q_rad(i, :), dh_params, joint_types);
            traza_punta(i, :) = P(end, :);

            set(h_brazo, 'XData', P(:,1), 'YData', P(:,2), 'ZData', P(:,3));
            set(h_traza, 'XData', traza_punta(1:i,1), ...
                         'YData', traza_punta(1:i,2), ...
                         'ZData', traza_punta(1:i,3));
            
            title(sprintf('Tiempo: %.2f s / %.2f s', t(i), t(end)));
            drawnow ;

            if i < Npts
                dt = t(i+1) - t(i);
                if dt > 0, pause(dt); end
            end
        end
   
    axis equal
    end
end
function P = calcular_puntos_dh(q, dh, joint_types)
    dof = length(q);
    P = zeros(dof + 1, 3);
    T_acum = eye(4);

    for i = 1:dof
        a     = dh(i, 1);
        alpha = dh(i, 2);

        % Lógica de asignación según tipo de articulación
        if upper(joint_types(i)) == 'P'
            theta = dh(i, 3); % theta es constante (definido en dh_params)
            d     = q(i);     % d es la variable articular (distancia en metros)
        else
            theta = q(i);     % theta es la variable articular (ángulo en rad)
            d     = dh(i, 3); % d es constante (definido en dh_params)
        end

        % Matriz de Transformación Homogénea (Estándar Denavit-Hartenberg)
        A = [cos(theta), -sin(theta)*cos(alpha),  sin(theta)*sin(alpha), a*cos(theta);
             sin(theta),  cos(theta)*cos(alpha), -cos(theta)*sin(alpha), a*sin(theta);
             0,           sin(alpha),             cos(alpha),            d;
             0,           0,                      0,                     1];

        T_acum = T_acum * A;
        P(i+1, :) = T_acum(1:3, 4).';
    end
end