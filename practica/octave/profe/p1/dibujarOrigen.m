function dibujarOrigen
T=eye(4);
    origen = T(1:3, 4);
x0 = origen(1);
y0 = origen(2);
z0 = origen(3);

% 3. Extraer los vectores de dirección de los nuevos ejes (Columnas de Rotación)
ejeX = T(1:3, 1);
ejeY = T(1:3, 2);
ejeZ = T(1:3, 3);

% Longitud visual de las flechas
L = 3; 

% 4. Graficar
figure;
hold on;

% Dibujar Nuevo Eje X (Rojo)
quiver3(x0, y0, z0, ejeX(1)*L, ejeX(2)*L, ejeX(3)*L, 0, 'LineWidth', 2.5,'LineStyle' ,':', 'Color', 'r', 'MaxHeadSize', 0.5);
text(x0 + ejeX(1)*(L+0.3), y0 + ejeX(2)*(L+0.3), z0 + ejeX(3)*(L+0.3), 'X', 'Color', 'r', 'FontSize', 12, 'FontWeight', 'bold');

% Dibujar Nuevo Eje Y (Verde)
quiver3(x0, y0, z0, ejeY(1)*L, ejeY(2)*L, ejeY(3)*L, 0, 'LineWidth', 2.5, 'Color', 'g','LineStyle' ,':', 'MaxHeadSize', 0.5);
text(x0 + ejeY(1)*(L+0.3), y0 + ejeY(2)*(L+0.3), z0 + ejeY(3)*(L+0.3), 'Y', 'Color', 'g', 'FontSize', 12, 'FontWeight', 'bold');

% Dibujar Nuevo Eje Z (Azul)
quiver3(x0, y0, z0, ejeZ(1)*L, ejeZ(2)*L, ejeZ(3)*L, 0, 'LineWidth', 2.5, 'Color', 'b','LineStyle' ,':', 'MaxHeadSize', 0.5);
text(x0 + ejeZ(1)*(L+0.3), y0 + ejeZ(2)*(L+0.3), z0 + ejeZ(3)*(L+0.3), 'Z', 'Color', 'b', 'FontSize', 12, 'FontWeight', 'bold');


% Configuración del espacio de trabajo
grid on;
axis equal;
xlabel('X Global'); ylabel('Y Global'); zlabel('Z Global');
view(3);
hold off;
