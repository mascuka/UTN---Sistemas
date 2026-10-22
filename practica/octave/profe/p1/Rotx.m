%Matriz de rotacion alrrededor del eje X
%angulo en grados
function T = Rotx(a)

if isa(a, 'sym')
        ca = cos(a);
sa = sin(a);
else
    ca = cosd(a);
sa = sind(a);
    end

T = [1  0  0  0;
     0 ca -sa 0;
     0 sa ca  0;
     0 0   0  1
     ];
