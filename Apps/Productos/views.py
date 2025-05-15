from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse

from Apps.Usuarios.models import Usuarios

from .serializer import ProductosSerializers, RegistroPedidosSerializers
from .models import Productos, RegistroPedidos

from .enviar_gmail import enviar_email
from .enviar_whatsapp import enviar_whatsapp
from .plantilla_pedido_excel import plantilla_pedido_excel

from Apps.Clientes.models import Clientes
from Apps.Usuarios.token import AutenticacionJWTPerzonalizada   #Llama a la clase con la autenticación personalizada del token jwt


from pytz import timezone
#pip install requests
#pip install pandas
#pip install openpyxl
import traceback   #Para extraer el error en específico
import openpyxl


@api_view(['POST'])
@permission_classes([AutenticacionJWTPerzonalizada])
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
@permission_classes([AutenticacionJWTPerzonalizada])
def Obtener_Productos(request):
    try:
        datos = Productos.objects.all()
        producto = ProductosSerializers(datos, many=True)
        return Response(producto.data, status=status.HTTP_200_OK)

    except ValueError:return Response({'Error':'No se ha podido obtener los productos'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AutenticacionJWTPerzonalizada])
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

        excel_en_memoria = plantilla_pedido_excel(
            cliente_base_datos = cliente_base_datos,
            registro_pedidos = registro_pedidos,
            comentario = comentario,
            lista_productos = lista_productos,
            lista_cables = lista_cables
        )
    
        #email_enviado = enviar_email(usuario_nombre=usuario_nombre, cliente_nombre=cliente_base_datos.cliente_nombre, clienteId=clienteId, excel_en_memoria=excel_en_memoria.getvalue())

        # Zona horaria de Argentina
        argentina_tz = timezone('America/Argentina/Buenos_Aires')

        # Convertir la hora UTC a hora argentina
        hora_arg = registro_pedidos.pedido_hora.astimezone(argentina_tz)

        whatsapp_enviado = enviar_whatsapp(
            excel_en_memoria=excel_en_memoria,
            usuario_nombre=usuario_nombre,
            cliente_nombre=cliente_base_datos.cliente_nombre,
            hora=hora_arg.strftime("%d-%m-%Y %H:%M:%S"),
            tipo=tipo)

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



#Acceso para admin
@api_view(['GET'])
@permission_classes([AutenticacionJWTPerzonalizada])
def Obtener_Registro_Pedidos(request):
    try:
        admin_id:str = getattr(request, 'usuario_id')

        if Usuarios.objects.get(id = admin_id).usuario_rol == 'admin':
            datos = RegistroPedidos.objects.all()
            producto = RegistroPedidosSerializers(datos, many=True)
            return Response(producto.data, status=status.HTTP_200_OK)
        
        else:return Response({'Error':'El usuario no es un administrador'}, status=status.HTTP_401_UNAUTHORIZED)

    except ValueError:return Response({'Error':'No se ha podido obtener el registro'}, status=status.HTTP_400_BAD_REQUEST)



#Acceso para admin
@api_view(['GET'])
@permission_classes([AutenticacionJWTPerzonalizada])
def Descargar_Registro_Pedidos(request):
    try:
        admin_id:str = getattr(request, 'usuario_id')
        if Usuarios.objects.get(id = admin_id).usuario_rol != 'admin':
            return Response({'Error':'El usuario no es un administrador'}, status=status.HTTP_401_UNAUTHORIZED)

        if RegistroPedidos.objects.count() < 1:
            return Response('No hay registros para descargar', status=status.HTTP_204_NO_CONTENT)
        
        wb = openpyxl.Workbook()   #crea un nuevo libro de Excel
        ws = wb.active   #obtiene la hoja por defecto
        ws.title = 'Página1'   #cambia el nombre de la pestaña

        ws.append(['ID', 'Id del Vendedor', 'Nombre del Vendedor', 'Id del Cliente', 'Nombre del Cliente', 'Hora del pedido'])

        for registro in RegistroPedidos.objects.all():
            ws.append([
                registro.pedido_numero,
                registro.pedido_vendedor_id,
                registro.pedido_vendedor_nombre,
                registro.pedido_cliente_id,
                registro.pedido_cliente_nombre,
                registro.pedido_hora.strftime('%Y-%m-%d %H:%M') if registro.pedido_hora else ''
            ])
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=Resgitro Pedidos.xlsx'

        wb.save(response)
        return response
    
    except Exception as e:
        error_trace = traceback.format_exc()  # Obtener el detalle del error
        print(error_trace)  # Mostrar el error en consola (logs)
        return Response({'Error': str(e), 'Detalle': error_trace}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except:return Response({'Error':"Algo salió mal"}, status=status.HTTP_400_BAD_REQUEST)



#Acceso para admin y usuario
@api_view(['GET'])
@permission_classes([AutenticacionJWTPerzonalizada])
def Obtener_Pedido(request, pedido_numero:str):
    try:
        usuario_id:str = getattr(request, 'usuario_id')

        if Usuarios.objects.get(id = usuario_id).usuario_rol != 'admin':

            if usuario_id != RegistroPedidos.objects.get(pedido_numero = pedido_numero).pedido_vendedor_id:
                return Response({'Error':'El pedido solicitado no es suyo'}, status=status.HTTP_401_UNAUTHORIZED)
        
        pedido_bd = RegistroPedidos.objects.get(pedido_numero = pedido_numero)
        pedido = RegistroPedidosSerializers(pedido_bd)
        return Response(pedido.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        error_trace = traceback.format_exc()  # Obtener el detalle del error
        print(error_trace)  # Mostrar el error en consola (logs)
        return Response({'Error': str(e), 'Detalle': error_trace}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except:return Response({'Error':"Algo salió mal"}, status=status.HTTP_400_BAD_REQUEST)



#Acceso para admin y usuario
@api_view(['GET'])
@permission_classes([AutenticacionJWTPerzonalizada])
def Descargar_Pedido(request, pedido_numero:str):
    try:
        usuario_id:str = getattr(request, 'usuario_id')
        
        if Usuarios.objects.get(id = usuario_id).usuario_rol != 'admin':

            if usuario_id != RegistroPedidos.objects.get(pedido_numero = pedido_numero).pedido_vendedor_id:
                return Response({'Error':'El pedido solicitado no es suyo'}, status=status.HTTP_401_UNAUTHORIZED)
            
            #return Response({'Error':'El usuario no es un administrador'}, status=status.HTTP_401_UNAUTHORIZED)
        
        pedido_bd = RegistroPedidos.objects.get(pedido_numero = pedido_numero)

        cliente_base_datos = Clientes.objects.get(cliente_codigo = pedido_bd.pedido_cliente_id)  #Obtener datos del cliente de la base de datos
        
        excel_en_memoria = plantilla_pedido_excel(
            cliente_base_datos = cliente_base_datos,
            registro_pedidos = pedido_bd,
            comentario = [],
            lista_productos = pedido_bd.pedido_productos_json if pedido_bd.pedido_productos_json else [],
            lista_cables = pedido_bd.pedido_cables_json if pedido_bd.pedido_cables_json else []
        )

        response = HttpResponse(
            excel_en_memoria.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=Resgitro Pedidos.xlsx'

        return response
        
    except Exception as e:
        error_trace = traceback.format_exc()  # Obtener el detalle del error
        print(error_trace)  # Mostrar el error en consola (logs)
        return Response({'Error': str(e), 'Detalle': error_trace}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except:return Response({'Error':"Algo salió mal"}, status=status.HTTP_400_BAD_REQUEST)



#Acceso para usuario
@api_view(['GET'])
@permission_classes([AutenticacionJWTPerzonalizada])
def Obtener_Mi_Registro_Pedidos(request):
    try:
        usuario_id:str = getattr(request, 'usuario_id')

        datos = RegistroPedidos.objects.filter(pedido_vendedor_id = usuario_id)
        producto = RegistroPedidosSerializers(datos, many=True)
        return Response(producto.data, status=status.HTTP_200_OK)

    except ValueError:return Response({'Error':'No se ha podido obtener el registro'}, status=status.HTTP_400_BAD_REQUEST)



#Acceso para admin
@api_view(['GET'])
@permission_classes([AutenticacionJWTPerzonalizada])
def Descargar_Mi_Registro_Pedidos(request):
    try:
        usuario_id:str = getattr(request, 'usuario_id')

        if RegistroPedidos.objects.filter(pedido_vendedor_id = usuario_id).count() < 1:
            return Response('No hay registros para descargar', status=status.HTTP_204_NO_CONTENT)
        
        wb = openpyxl.Workbook()   #crea un nuevo libro de Excel
        ws = wb.active   #obtiene la hoja por defecto
        ws.title = 'Página1'   #cambia el nombre de la pestaña

        ws.append(['ID', 'Id del Vendedor', 'Nombre del Vendedor', 'Id del Cliente', 'Nombre del Cliente', 'Hora del pedido'])

        for registro in RegistroPedidos.objects.filter(pedido_vendedor_id = usuario_id):
            ws.append([
                registro.pedido_numero,
                registro.pedido_vendedor_id,
                registro.pedido_vendedor_nombre,
                registro.pedido_cliente_id,
                registro.pedido_cliente_nombre,
                registro.pedido_hora.strftime('%Y-%m-%d %H:%M') if registro.pedido_hora else ''
            ])
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=Resgitro Pedidos.xlsx'

        wb.save(response)
        return response
    
    except Exception as e:
        error_trace = traceback.format_exc()  # Obtener el detalle del error
        print(error_trace)  # Mostrar el error en consola (logs)
        return Response({'Error': str(e), 'Detalle': error_trace}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except:return Response({'Error':"Algo salió mal"}, status=status.HTTP_400_BAD_REQUEST)