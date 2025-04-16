import pandas as pd
from io import BytesIO
from pytz import timezone



def plantilla_pedido_excel(cliente_base_datos, registro_pedidos, comentario, lista_productos, lista_cables):
    # Zona horaria de Argentina
    argentina_tz = timezone('America/Argentina/Buenos_Aires')

    # Convertir la hora UTC a hora argentina
    hora_arg = registro_pedidos.pedido_hora.astimezone(argentina_tz)

    datos_excel = pd.DataFrame([["Nombre",cliente_base_datos.cliente_nombre],
    [],   # Línea vacía para separación
    ["Localidad",cliente_base_datos.cliente_localidad],
    [],
    ["Ccliente",registro_pedidos.pedido_cliente_id],
    [],
    ["Vendedor",registro_pedidos.pedido_vendedor_nombre],
    [],
    ["Npedido",registro_pedidos.id],
    [],
    # Formatear la hora
    ["Fecha",hora_arg.strftime("%d-%m-%Y %H:%M:%S")],
    [],
    ["Comentario",comentario if comentario != '' else 'No hay comentario'],
    []
    ])

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

    return excel_en_memoria