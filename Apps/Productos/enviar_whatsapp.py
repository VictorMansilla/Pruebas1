import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def enviar_whatsapp(excel_en_memoria, usuario_nombre, cliente_nombre, hora, tipo):
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
            "name": "pedido",  # Nombre exacto de la plantilla
            "language": {
                "code": "en"  # Idioma correcto
            },
            "components": [
                {
                    "type": "header",
                    "parameters": [
                        {
                            "type": "document",
                            "document": {
                                "id": id_excel_subido,
                                "filename": f"{str(tipo).capitalize()}-{hora}.xlsx"
                            }
                        }
                    ]
                },
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": usuario_nombre},        # {{1}} = Vendedor
                        {"type": "text", "text": cliente_nombre},     # {{2}} = Cliente
                        {"type": "text", "text": hora}         # {{3}} = Hora
                    ]
                }
            ]
        }
    }

    respuesta_subir_excel_whatsapp = requests.post(link_mensaje_whatsapp, json=data, headers=cabecera_mensaje_whatsapp)

    return respuesta_subir_excel_whatsapp