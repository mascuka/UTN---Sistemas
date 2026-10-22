%Matriz de rotacion alrrededor del eje Z
%angulo en grados

function T=Rotz(a)
if isa(a, 'sym')
        ca = cos(a);
sa = sin(a);
else
    ca = cosd(a);
sa = sind(a);
    end


T = [ ca -sa  0  0;
      sa  ca  0  0;
      0  0    1  0;
      0  0    0  1];
