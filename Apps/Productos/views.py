from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.core.mail import EmailMessage

from Apps.Usuarios.models import Usuarios

from .serializer import ProductosSerializers
from .models import Productos
from .models import RegistroPedidos

from Apps.Clientes.models import Clientes
from Apps.Usuarios.token import AutenticacionJWTPerzonalizada   #Llama a la clase con la autenticación personalizada del token jwt

from dotenv import load_dotenv
from io import BytesIO

import requests
#pip install requests
import pandas as pd
#pip install pandas
#pip install openpyxl
from datetime import datetime
import os
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



load_dotenv()
@api_view(['POST'])
@permission_classes([AutenticacionJWTPerzonalizada])   #Permite el acceso sin restricciones a la vista, cualquiera puede acceder a ella
def Hacer_Pedido(request):
    try:
        datos = request.data
        lista_productos:list = datos['carrito']
        clienteId:str = datos['clienteId']
        comentario:str = datos['comentario']
        usuario_nombre:str = getattr(request, 'usuario_nombre')
        usuario_id:str = getattr(request, 'usuario_id')

        cliente_base_datos = Clientes.objects.get(cliente_codigo = clienteId)  #Obtener datos del cliente de la base de datos

        registro_pedidos = RegistroPedidos(pedido_vendedor_id = usuario_id, pedido_vendedor_nombre = usuario_nombre, pedido_cliente_id = clienteId, pedido_cliente_nombre = cliente_base_datos.cliente_nombre)

        registro_pedidos.save()

        datos_excel = pd.DataFrame([["Nombre",cliente_base_datos.cliente_nombre],
        [],   # Línea vacía para separación
        ["Localidad",cliente_base_datos.cliente_localidad],
        [],
        ["Vendedor",usuario_nombre],
        [],
        ["Npedido",registro_pedidos.id],
        [],
        ["Fecha",datetime.now().strftime("%d-%m-%Y %H:%M:%S")],
        [],
        ["Comentario",comentario if comentario != '' else 'No hay comentario'],
        []])

        datos_productos = pd.DataFrame(lista_productos)

        datos_productos = datos_productos.rename(columns={
            'producto_codigo':'CProducto',
            'producto_nombre':'NProducto'
        })

        excel_en_memoria = BytesIO()   # Guardar Excel en memoria (en lugar de escribir en disco)

        # Guardar en el mismo archivo de Excel en la misma hoja
        with pd.ExcelWriter(excel_en_memoria) as escritor:
            datos_excel.to_excel(escritor, index=False, header=False, startrow=0)
            datos_productos.to_excel(escritor, index=False, startrow=len(datos_excel))

        excel_en_memoria.seek(0)  # Ir al inicio del archivo

        enviar_email = EmailMessage(   #Preparar el email
            subject= (f'Pedido de {usuario_nombre} del cliente {cliente_base_datos.cliente_nombre}'),
            body= (f'El cliente es {clienteId}'),
            from_email= (os.getenv('EMAIL_EMISOR')),
            to= [os.getenv('EMAIL_RECEPTOR')]
        )

        enviar_email.attach('pedido.xlsx', excel_en_memoria.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')   # Adjuntar el archivo Excel
        enviar_email.send()   # Enviar el email

        token_acceso_permanente = os.getenv('TOKEN_PERMANENTE_WHATSAPP')
        numero_emisor = os.getenv('NUMERO_EMISOR_WHATSAPP')
        version = os.getenv('VERSION')  # Asegurate de usar la última versión de la API
        numero_receptor = os.getenv('NUMERO_RECEPTOR_WHATSAPP')  # Número destino con código de país

        link_subir_excel = f"https://graph.facebook.com/{version}/{numero_emisor}/media"

        cabecera_subir_excel = {
            "Authorization": f"Bearer {token_acceso_permanente}"
        }

        excel_whatsapp = {
            "file": ("datos.xlsx",excel_en_memoria,  # Ruta del archivo Excel
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        }

        data_subir_excel = {
            "messaging_product": "whatsapp"
        }

        respuesta_subir_excel = requests.post(link_subir_excel, headers=cabecera_subir_excel, files=excel_whatsapp, data=data_subir_excel)

        id_excel_subido = respuesta_subir_excel.json().get("id")

        link_mensaje_whatsapp = f"https://graph.facebook.com/{version}/{numero_emisor}/messages"

        cabecera_mensaje_whatsapp = {
            "Authorization": f"Bearer {token_acceso_permanente}",
            "Content-Type": "application/json"
        }

        data = {
            "messaging_product": "whatsapp",
            "to": numero_receptor,
            "type": "template",
            "template": {
                "name": "plantilla_prueba1",  # Nombre exacto de la plantilla
                "language": {
                    "code": "es_AR"  # Idioma correcto
                },
                "components": [
                    {
                        "type": "header",
                        "parameters": [
                            {
                                "type": "document",
                                "document": {
                                    "id": id_excel_subido,
                                    "filename": f"Pedido Nº.xlsx"
                                }
                            }
                        ]
                    },
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": usuario_nombre},        # {{1}} = Vendedor
                            {"type": "text", "text": cliente_base_datos.cliente_nombre},     # {{2}} = Cliente
                            {"type": "text", "text": datetime.now().strftime("%H:%M")}         # {{3}} = Hora
                        ]
                    }
                ]
            }
        }

        respuesta_subir_excel_whatsapp = requests.post(link_mensaje_whatsapp, json=data, headers=cabecera_mensaje_whatsapp)

        return Response({'Hecho' : 'Se recibió el carrito'}, status=status.HTTP_200_OK)

    except KeyError as e:return Response({'Error':f'Datos no enviados en {e}'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        error_trace = traceback.format_exc()  # Obtener el detalle del error
        print(error_trace)  # Mostrar el error en consola (logs)
        return Response({'Error': str(e), 'Detalle': error_trace}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except:return Response({'Error':"Algo salió mal"}, status=status.HTTP_400_BAD_REQUEST)