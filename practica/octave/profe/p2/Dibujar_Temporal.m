function Dibujar_Temporal( T_total,Q_total,DQ_total )
% Dibuja Posiciones y velocidades en el tiempo en 2 graficos por figura
%   Parametros 
% T_total Vector de tiempos
% Q_total Matriz de Posiciones
% DQ_total Matriz  de Velocidades
figure
subplot(2,1,1)
plot(T_total,Q_total,'Linewidth',2)
xlabel('tiempo')
title('Posiciones')
grid on
subplot(2,1,2)
plot(T_total,DQ_total,'Linewidth',2)
xlabel('tiempo')

title('Velocidades')
grid on


end

