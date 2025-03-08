from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .serializer import ClientesSerializers
from .models import Clientes

from Apps.Usuarios.token import AutenticacionJWTPerzonalizada   #Llama a la clase con la autenticación personalizada del token jwt
from Apps.Usuarios.models import Usuarios



@api_view(['POST'])
@permission_classes([AutenticacionJWTPerzonalizada])   #Protege la ruta, es necesario un token jwt
def Crear_Cliente(request):
    try:
        datos = request.data
        cliente_codigo:str = datos['cliente_codigo']
        admin_nombre:str = getattr(request, 'usuario_nombre')

        if Usuarios.objects.get(usuario_nombre = admin_nombre).usuario_rol == 'admin':

            if Clientes.objects.filter(cliente_codigo = cliente_codigo).exists() is False:
                cliente_nombre:str = datos['cliente_nombre']
                cliente_localidad:str = datos['cliente_localidad']
            
                ingresar_cliente = Clientes(cliente_codigo = cliente_codigo, cliente_nombre = cliente_nombre, cliente_localidad = cliente_localidad)
                
                ingresar_cliente.save()

                return Response({'Completado':'El cliente fue ingresado'}, status=status.HTTP_201_CREATED)

            else:return Response({'Inválido':'El cliente ya existe'}, status=status.HTTP_302_FOUND)
        
        else:return Response({'Error':'El usuario no es un administrador'}, status=status.HTTP_401_UNAUTHORIZED)

    except KeyError as e:return Response({'Error':f'Datos no enviados en {e}'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([AutenticacionJWTPerzonalizada])   #Protege la ruta, es necesario un token jwt
def Obtener_Clientes(request):
    try:
        datos = Clientes.objects.all()
        cliente = ClientesSerializers(datos, many=True)
        return Response(cliente.data, status=status.HTTP_200_OK)

    except ValueError:return Response({'Error':'No se ha podido obtener los clientes'}, status=status.HTTP_400_BAD_REQUEST)