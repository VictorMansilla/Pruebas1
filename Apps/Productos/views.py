from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from Apps.Usuarios.token import AutenticacionJWTPerzonalizada   #Llama a la clase con la autenticación personalizada del token jwt
from rest_framework.permissions import AllowAny

from .serializer import ProductosSerializers
from .models import Productos



@api_view(['POST'])
@permission_classes([AutenticacionJWTPerzonalizada])   #Permite el acceso sin restricciones a la vista, cualquiera puede acceder a ella
def Crear_Producto(request):
    try:
        datos = request.data
        producto_codigo:str = datos['producto_codigo']

        if Productos.objects.filter(producto_codigo = producto_codigo).exists() is False:
            producto_nombre:str = datos['producto_nombre']
        
            ingresar_producto = Productos(producto_codigo = producto_codigo, producto_nombre = producto_nombre)
            
            ingresar_producto.save()

            return Response({'Completado':'El producto fue ingresado'}, status=status.HTTP_201_CREATED)

        else:return Response({'Inválido':'El producto ya existe'}, status=status.HTTP_302_FOUND)
        
    except KeyError as e:return Response({'Error':f'Datos no enviados en {e}'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([AutenticacionJWTPerzonalizada])   #Permite el acceso sin restricciones a la vista, cualquiera puede acceder a ella
def Obtener_Productos(request):
    try:
        datos = Productos.objects.all()
        producto = ProductosSerializers(datos, many=True)
        return Response(producto.data, status=status.HTTP_200_OK)

    except ValueError:return Response({'Error':'No se ha podido obtener los productos'}, status=status.HTTP_400_BAD_REQUEST)



#Endpoint para hacer busquedas personalizadas en la base de datos
""" from django.db.models import Q

@api_view(['GET'])
@permission_classes([AutenticacionJWTPerzonalizada])   #Protege la ruta, es necesario un token jwt
def Buscar_Productos(request):
    try:
        datos = request.data
        query = datos['query']

        if datos:
            productos = Productos.objects.filter(Q(producto_nombre__icontains = query))
            resultado_productos = ProductosSerializers(productos, many=True)
            return Response(resultado_productos.data, status=status.HTTP_200_OK)
            
        else:return Response({'Error':'No se enviaron datos a buscar'}, status=status.HTTP_400_BAD_REQUEST)

    except KeyError as e:return Response({'Error':f'Datos no enviados en {e}'}, status=status.HTTP_400_BAD_REQUEST)

    except ValueError:return Response({'Error':'Ocurrió un error'}, status=status.HTTP_400_BAD_REQUEST) """



from django.core.mail import send_mail
import os
from dotenv import load_dotenv
load_dotenv()
@api_view(['POST'])
@permission_classes([AutenticacionJWTPerzonalizada])   #Permite el acceso sin restricciones a la vista, cualquiera puede acceder a ella
def Hacer_Pedido(request):
    try:
        datos = request.data
        lista_productos:str = datos['carrito']
        clienteId:str = datos['clienteId']
        print(clienteId)
        print(lista_productos)

        send_mail(
            'Título',
            f'El cliente es {clienteId} El carrito es {lista_productos}',
            os.getenv('EMAIL_EMISOR'),
            [os.getenv('EMAIL_RECEPTOR')],
            fail_silently=False
        )
        return Response({'Hecho' : 'Se recibió el carrito'}, status=status.HTTP_200_OK)

        """         if Productos.objects.filter(producto_codigo = producto_codigo).exists() is False:
            producto_nombre:str = datos['producto_nombre']
        
            ingresar_producto = Productos(producto_codigo = producto_codigo, producto_nombre = producto_nombre)
            
            ingresar_producto.save()

            return Response({'Completado':'El producto fue ingresado'}, status=status.HTTP_201_CREATED)

        else:return Response({'Inválido':'El producto ya existe'}, status=status.HTTP_302_FOUND)
         """
    except KeyError as e:return Response({'Error':f'Datos no enviados en {e}'}, status=status.HTTP_400_BAD_REQUEST)

    except:return Response({'Error':"Algo salió mal"}, status=status.HTTP_400_BAD_REQUEST)