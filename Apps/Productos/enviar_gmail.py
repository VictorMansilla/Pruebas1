from django.core.mail import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()

def enviar_email(usuario_nombre, cliente_nombre, clienteId, excel_en_memoria):
    enviar_email = EmailMessage(   #Preparar el email
        subject= (f'Pedido de {usuario_nombre} del cliente {cliente_nombre}'),
        body= (f'El cliente es {clienteId}'),
        from_email= (os.getenv('EMAIL_EMISOR')),
        to= [os.getenv('EMAIL_RECEPTOR')]
    )

    enviar_email.attach('pedido.xlsx', excel_en_memoria, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')   # Adjuntar el archivo Excel
    
    email_enviado = enviar_email.send()   # Enviar el email

    return email_enviado