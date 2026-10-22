%Matriz de rotacion alrrededor del eje Y
%angulo en grados

function T=Roty(a)

if isa(a, 'sym')
        ca = cos(a);
sa = sin(a);
else
    ca = cosd(a);
sa = sind(a);
    end

T = [ ca 0 sa  0;
      0  1  0  0;
      -sa 0    ca  0;
      0  0    0  1];

