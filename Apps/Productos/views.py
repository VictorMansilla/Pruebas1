from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from Apps.Usuarios.models import Usuarios

from .serializer import ProductosSerializers, RegistroPedidosSerializers
from .models import Productos, RegistroPedidos

from .enviar_gmail import enviar_email
from .enviar_whatsapp import enviar_whatsapp

from Apps.Clientes.models import Clientes
from Apps.Usuarios.token import AutenticacionJWTPerzonalizada   #Llama a la clase con la autenticación personalizada del token jwt

from io import BytesIO

#pip install requests
import pandas as pd
#pip install pandas
#pip install openpyxl
from pytz import timezone
import traceback   #Para extraer el error en específico


@api_view(['POST'])
@permission_classes([AutenticacionJWTPerzonalizada])   #Permite el acceso sin restricciones a la vista, cualquiera puede acceder a ella
def Crear_Producto(request):
    try:
        datos = request.data
        producto_codigo:str = datos['producto_codigo']
        admin_nombre:str = getattr(request, 'usuario_nombre')

        if Usuarios.objects.get(usuario_nombre = admin_nombre).usuario_rol == 'admin':

            if Productos.objects.filter(producto_codigo = producto_codigo).exists() is False:
                producto_nombre:str = datos['producto_nombre']
            
                ingresar_producto = Productos(producto_codigo = producto_codigo, producto_nombre = producto_nombre)
                
                ingresar_producto.save()

                return Response({'Completado':'El producto fue ingresado'}, status=status.HTTP_201_CREATED)

            else:return Response({'Inválido':'El producto ya existe'}, status=status.HTTP_302_FOUND)
        
        else:return Response({'Error':'El usuario no es un administrador'}, status=status.HTTP_401_UNAUTHORIZED)
        
    except KeyError as e:return Response({'Error':f'Datos no enviados en {e}'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([AutenticacionJWTPerzonalizada])   #Permite el acceso sin restricciones a la vista, cualquiera puede acceder a ella
def Obtener_Productos(request):
    try:
        datos = Productos.objects.all()
        producto = ProductosSerializers(datos, many=True)
        return Response(producto.data, status=status.HTTP_200_OK)

    except ValueError:return Response({'Error':'No se ha podido obtener los productos'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AutenticacionJWTPerzonalizada])   #Permite el acceso sin restricciones a la vista, cualquiera puede acceder a ella
def Hacer_Pedido(request):
    try:
        datos = request.data
        tipo:str = datos['tipo']
        lista_productos:list = datos['carrito']
        lista_cables:list = datos['carritoCables']
        clienteId:str = datos['clienteId']
        comentario:str = datos['comentario']
        usuario_nombre:str = getattr(request, 'usuario_nombre')
        usuario_id:str = getattr(request, 'usuario_id')

        print(tipo)

        cliente_base_datos = Clientes.objects.get(cliente_codigo = clienteId)  #Obtener datos del cliente de la base de datos

        registro_pedidos = RegistroPedidos(
            tipo = tipo,
            pedido_vendedor_id = usuario_id,
            pedido_vendedor_nombre = usuario_nombre,
            pedido_cliente_id = clienteId,
            pedido_cliente_nombre = cliente_base_datos.cliente_nombre,
            pedido_productos_json = lista_productos if lista_productos else None,
            pedido_cables_json = lista_cables if lista_cables else None)

        registro_pedidos.save()

        # Zona horaria de Argentina
        argentina_tz = timezone('America/Argentina/Buenos_Aires')

        # Convertir la hora UTC a hora argentina
        hora_arg = registro_pedidos.pedido_hora.astimezone(argentina_tz)

        datos_excel = pd.DataFrame([["Nombre",cliente_base_datos.cliente_nombre],
        [],   # Línea vacía para separación
        ["Localidad",cliente_base_datos.cliente_localidad],
        [],
        ["Ccliente",cliente_base_datos.cliente_codigo],
        [],
        ["Vendedor",usuario_nombre],
        [],
        ["Npedido",registro_pedidos.id],
        [],
        # Formatear la hora
        ["Fecha",hora_arg.strftime("%d-%m-%Y %H:%M:%S")],
        [],
        ["Comentario",comentario if comentario != '' else 'No hay comentario'],
        []])

        excel_en_memoria = BytesIO()   # Guardar Excel en memoria (en lugar de escribir en disco)

        # Guardar en el mismo archivo de Excel en la misma hoja
        with pd.ExcelWriter(excel_en_memoria) as escritor:
            datos_excel.to_excel(escritor, index=False, header=False, startrow=0)

            datos_productos = pd.DataFrame(lista_productos)

            datos_productos = datos_productos.rename(columns={
                'producto_codigo':'CProducto',
                'producto_nombre':'NProducto'
            })

            datos_productos.to_excel(escritor, index=False, startrow=len(datos_excel))

            if lista_cables != []:
                datos_cables = pd.DataFrame(lista_cables)
                datos_cables.to_excel(escritor, index=False, startrow=((len(datos_productos)+len(datos_excel)+2) if len(datos_productos) > 0 else len(datos_excel)))

        excel_en_memoria.seek(0)  # Ir al inicio del archivo

        #email_enviado = enviar_email(usuario_nombre=usuario_nombre, cliente_nombre=cliente_base_datos.cliente_nombre, clienteId=clienteId, excel_en_memoria=excel_en_memoria.getvalue())

        whatsapp_enviado = enviar_whatsapp(
            excel_en_memoria=excel_en_memoria,
            usuario_nombre=usuario_nombre,
            cliente_nombre=cliente_base_datos.cliente_nombre,
            hora=hora_arg.strftime("%d-%m-%Y %H:%M:%S"),
            tipo=tipo)

        print(whatsapp_enviado.json())
        print(whatsapp_enviado.status_code)

        if whatsapp_enviado.status_code == 200:
            return Response({'Hecho' : f'Se envió el {tipo}'}, status=status.HTTP_200_OK)

            """ elif whatsapp_enviado.status_code == 200 and not email_enviado:
            return Response({'Mensaje': 'Se envió el WhatsApp, pero no el email'}, status=status.HTTP_206_PARTIAL_CONTENT)

        elif whatsapp_enviado.status_code != 200:
            return Response({'Mensaje': 'Se envió el email, pero no el WhatsApp'}, status=status.HTTP_206_PARTIAL_CONTENT) """

        else:
            return Response({'Mensaje': 'No se envió ni el WhatsApp ni el email'}, status=status.HTTP_400_BAD_REQUEST)

    except KeyError as e:return Response({'Error':f'Datos no enviados en {e}'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        error_trace = traceback.format_exc()  # Obtener el detalle del error
        print(error_trace)  # Mostrar el error en consola (logs)
        return Response({'Error': str(e), 'Detalle': error_trace}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except:return Response({'Error':"Algo salió mal"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([AutenticacionJWTPerzonalizada])   #Permite el acceso sin restricciones a la vista, cualquiera puede acceder a ella
def Obtener_Registro_Pedidos(request):
    try:
        admin_id:str = getattr(request, 'usuario_id')

        if Usuarios.objects.get(id = admin_id).usuario_rol == 'admin':
            datos = RegistroPedidos.objects.all()
            producto = RegistroPedidosSerializers(datos, many=True)
            return Response(producto.data, status=status.HTTP_200_OK)

        else:return Response({'Error':'El usuario no es un administrador'}, status=status.HTTP_401_UNAUTHORIZED)

    except ValueError:return Response({'Error':'No se ha podido obtener el registro'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AutenticacionJWTPerzonalizada])
def Cargar_Pago(request):
    pass