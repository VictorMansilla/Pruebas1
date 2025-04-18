from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from django.contrib.auth.hashers import make_password, check_password

from .token import Generar_Token
from .models import Usuarios

from Apps.Usuarios.token import AutenticacionJWTPerzonalizada   #Llama a la clase con la autenticación personalizada del token jwt



@api_view(['POST'])
@permission_classes([AutenticacionJWTPerzonalizada])   #Protege la ruta, es necesario un token jwt
def Crear_Usuario(request):
    try:
        datos = request.data
        usuario_nombre:str = datos['usuario_nombre']
        admin_id:str = getattr(request, 'usuario_id')

        if Usuarios.objects.get(id = admin_id).usuario_rol == 'admin':
            
            if Usuarios.objects.filter(usuario_nombre = usuario_nombre).exists() is False:
                usuario_contrasegna:str = datos['usuario_contrasegna']
                usuario_rol:str = datos.get('usuario_rol', 'normal')

                if usuario_rol not in dict(Usuarios.Roles.choices):
                    usuario_rol = 'normal'

                usuario_contrasegna_hasheada = make_password(usuario_contrasegna)

                ingresar_usuario = Usuarios(
                    usuario_nombre = usuario_nombre,
                    usuario_contrasegna = usuario_contrasegna_hasheada,
                    usuario_rol = usuario_rol)
                
                ingresar_usuario.save()

                return Response({'Completado':'El usuario fue ingresado'}, status=status.HTTP_201_CREATED)

            else:return Response({'Inválido':'El usuario ya existe'}, status=status.HTTP_302_FOUND)
        
        else:return Response({'Error':'El usuario no es un administrador'}, status=status.HTTP_401_UNAUTHORIZED)
        
    except KeyError as e:return Response({'Error':f'Datos no enviados en {e}'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AllowAny])   #Permite el acceso sin restricciones a la vista, cualquiera puede acceder a ella
def Validar_Usuario(request):
    try:
        datos = request.data
        usuario_nombre:str = datos['usuario_nombre']

        if Usuarios.objects.filter(usuario_nombre = usuario_nombre).exists():
            usuario_contrasegna:str = datos['usuario_contrasegna']
            datos_usuario = Usuarios.objects.get(usuario_nombre = usuario_nombre)

            if check_password(usuario_contrasegna, datos_usuario.usuario_contrasegna):
                token:str = Generar_Token(datos_usuario.usuario_nombre, datos_usuario.id)
                return Response({'token': f'{token}'}, status=status.HTTP_200_OK)

            else:return Response({'Error':'Contraseña inválida'}, status=status.HTTP_401_UNAUTHORIZED)
        
        else:return Response({'Error':'El usuario no existe'}, status=status.HTTP_404_NOT_FOUND)

    except KeyError as e:return Response({'Error':f'Datos no enviados en {e}'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AutenticacionJWTPerzonalizada])   #Protege la ruta, es necesario un token jwt
def Validar_Admin(request):
    try:
        admin_id:str = getattr(request, 'usuario_id')

        if Usuarios.objects.get(id = admin_id).usuario_rol == 'admin':

            return Response(True, status=status.HTTP_200_OK)

        else:return Response(False, status=status.HTTP_401_UNAUTHORIZED)

    except KeyError as e:return Response({'Error':f'Datos no enviados en {e}'}, status=status.HTTP_400_BAD_REQUEST)