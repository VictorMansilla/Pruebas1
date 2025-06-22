from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.http import FileResponse, HttpResponse, JsonResponse
from django.utils.dateparse import parse_datetime

from Apps.Usuarios.models import Usuarios

from .plantilla_hacer_comprobante import hashear_comprobante, hacer_comprobante

from .models import ReciboPago, ImagenReciboPago
from .serializer import ComprobantesSerializers

from Apps.Clientes.models import Clientes
from Apps.Usuarios.token import AutenticacionJWTPerzonalizada   #Llama a la clase con la autenticación personalizada del token jwt

from cloudinary.uploader import upload
from cloudinary.exceptions import Error

import traceback   #Para extraer el error en específico
import json

from datetime import datetime



def imprimir_error_especifico(e):
    error_trace = traceback.format_exc()  # Obtener el detalle del error
    print(error_trace)  # Mostrar el error en consola (logs)
    return Response({'Error': str(e), 'Detalle': error_trace}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
@permission_classes([AutenticacionJWTPerzonalizada])
def Hacer_Comprobante(request):
    datos = request.data
    campos_requeridos = ['cliente', 'facturaRelacionada', 'fechafactura', 'metodoPago', 'montoRecibido']
    
    for campo in campos_requeridos:
        if campo not in datos:
            return Response({'Error':f'Datos no enviados en {campo}'}, status=status.HTTP_400_BAD_REQUEST)

    cliente_str:str = datos['cliente']
    facturaRelacionada:str = datos['facturaRelacionada'].strip()
    fechafactura:str = datos['fechafactura'].strip()
    id_vendedor:str = getattr(request, 'usuario_id')
    metodoPago:str = datos['metodoPago'].strip()
    montoRecibido:str = datos['montoRecibido'].strip()

    transferidoA:str = datos['transferidoA'].strip() if datos['transferidoA'] != '' else None or None
    fechaTransferencia:str = datos['fechaTransferencia'].strip() if datos['fechaTransferencia'] != '' else None or None

    #Convertir el str del cliente y hacerlo dict
    try:
        cliente = json.loads(cliente_str)  # Ahora cliente es un dict
    except json.JSONDecodeError:
        return Response({'Error': 'El cliente enviado no es un JSON válido'}, status=status.HTTP_400_BAD_REQUEST)
    
    #Validaciones
    if cliente == '' or facturaRelacionada == '' or fechafactura == '' or metodoPago == '' or montoRecibido == '':
        return Response({'Error' : 'Todos los campos deben ser completados'}, status=status.HTTP_400_BAD_REQUEST)

    if int(fechafactura[0:3]) > 2025:
        return Response({'Error' : f'Le fecha {fechafactura} es una fecha futura'}, status=status.HTTP_400_BAD_REQUEST)
    
    fecha_factura = datetime.strptime(fechafactura, "%Y-%m-%d").date()  # si es DateField

    try:
        cliente_bd = Clientes.objects.get(cliente_codigo = cliente['cliente_codigo'])
    except Clientes.DoesNotExist:
        return Response({'Error': 'Cliente no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    try:
        vendedor_bd = Usuarios.objects.get(id = id_vendedor)
    except Usuarios.DoesNotExist:
        return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

    comprobante_hasheado = hashear_comprobante(cliente=cliente_bd.cliente_nombre,
                                               facturaRelacionada=facturaRelacionada,
                                               fechafactura=f"{fecha_factura}",
                                               vendedor=vendedor_bd.usuario_nombre,
                                               metodoPago=metodoPago,
                                               montoRecibido=montoRecibido,
                                               transferidoA=transferidoA,
                                               fechaTransferencia=fechaTransferencia)

    recibo_pago_db = ReciboPago(cliente = cliente_bd,
                                vendedor = vendedor_bd,
                                factura_relacionada = facturaRelacionada,
                                fecha_factura = fecha_factura,
                                monto_recibido = montoRecibido,
                                medio_de_pago = metodoPago,
                                transferido_a = transferidoA,
                                fecha_transferencia = fechaTransferencia,
                                recibo_hasheado = comprobante_hasheado)
    
    recibo_pago_db.save()

    try:
        comprobante = hacer_comprobante(recibo_pago_db=recibo_pago_db)

    except Exception as e:
        return imprimir_error_especifico(e=e)

    except:return Response({'Error':"Algo salió mal"}, status=status.HTTP_400_BAD_REQUEST)

    #subir las imágenes a cloudinary
    if metodoPago == "TRANSFERENCIA":
        imagenes = request.FILES.getlist('files')

        if imagenes:
            for imagen in imagenes:
                try:
                    resultado = upload(imagen)
                    ImagenReciboPago.objects.create(recibo=recibo_pago_db,
                                                    url=resultado['secure_url'])
                except Error as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
    response = HttpResponse(comprobante, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="comprobante.pdf"'
    return response



#Acceso para admin
@api_view(['GET'])
@permission_classes([AutenticacionJWTPerzonalizada])
def Obtener_Registro_Comprobantes(request):
    try:
        admin_id:str = getattr(request, 'usuario_id')

        if Usuarios.objects.get(id = admin_id).usuario_rol == 'admin':
            datos = ReciboPago.objects.all()
            comprobantes = ComprobantesSerializers(datos, many=True)
            return Response(comprobantes.data, status=status.HTTP_200_OK)
        
        else:return Response({'Error':'El usuario no es un administrador'}, status=status.HTTP_401_UNAUTHORIZED)

    except ValueError:return Response({'Error':'No se ha podido obtener los comprobantes'}, status=status.HTTP_400_BAD_REQUEST)



#Acceso para admin y usuario
@api_view(['GET'])
@permission_classes([AutenticacionJWTPerzonalizada])
def Obtener_Comprobante(request, comprobante_numero:str):
    usuario_id:str = getattr(request, 'usuario_id')

    try:
        usuario = Usuarios.objects.get(id=usuario_id)

    except Usuarios.DoesNotExist:
        return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        comprobante_bd = ReciboPago.objects.get(recibo_pago_numero=comprobante_numero)

    except ReciboPago.DoesNotExist:
        return Response({'Error': 'No existe el comprobante'}, status=status.HTTP_404_NOT_FOUND)

    if usuario.usuario_rol != 'admin' and comprobante_bd.vendedor.id != usuario_id:
        return Response({'Error': 'El comprobante solicitado no es suyo'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        comprobante = ComprobantesSerializers(comprobante_bd)
        return Response(comprobante.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return imprimir_error_especifico(e=e)

    except:return Response({'Error':"Algo salió mal"}, status=status.HTTP_400_BAD_REQUEST)



#Acceso para admin y usuario
@api_view(['GET'])
@permission_classes([AutenticacionJWTPerzonalizada])
def Descargar_Comprobante(request, comprobante_numero:str):
    usuario_id:str = getattr(request, 'usuario_id')
    
    try:
        usuario = Usuarios.objects.get(id=usuario_id)

    except Usuarios.DoesNotExist:
        return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        comprobante_bd = ReciboPago.objects.get(recibo_pago_numero=comprobante_numero)

    except ReciboPago.DoesNotExist:
        return Response({'Error': 'No existe el comprobante'}, status=status.HTTP_404_NOT_FOUND)

    if usuario.usuario_rol != 'admin' and comprobante_bd.vendedor.id != usuario_id:
        return Response({'Error': 'El comprobante solicitado no es suyo'}, status=status.HTTP_403_FORBIDDEN)

    try:
        comprobante = hacer_comprobante(recibo_pago_db=comprobante_bd)
        
    except Exception as e:
        return imprimir_error_especifico(e=e)

    except:return Response({'Error':"Algo salió mal"}, status=status.HTTP_400_BAD_REQUEST)

    response = HttpResponse(comprobante, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="comprobante.pdf"'
    return response