% Traslacion segun un vector [dx,dy,dz]
%si especifica escalar es x, si es de 2 dimensiones es x e y

function T=Traslacion(vec)

switch length(vec)
    case 1 
        vec=[vec 0 0];
     case 2 
         vec=[vec 0];  
    case 3 
      vec=vec ;  
    otherwise
            print('Dimension no valida')
            return
end

T = [1  0  0  vec(1);
     0  1  0  vec(2);
     0  0  1  vec(3);
     0  0  0  1];
end     
