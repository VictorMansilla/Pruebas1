import os
import datetime
import jwt

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import APIException

#Generar una clave secreta para los tokens
#import secrets
#secret = secrets.token_hex(32)
#print(secret)

segundos_exp = int(os.getenv('segundos_exp'))
clave_secreta = os.getenv('clave_secreta')   #secrets.token_hex(32)
algoritmo:list = [os.getenv('algoritmo')]

def Generar_Token(usuario_nombre_token, usuario_id_token):
    payload = {
        'Id_usuario' : usuario_id_token,
        'nombre_usuario' : usuario_nombre_token,
        'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=segundos_exp)}
    token = jwt.encode(payload, clave_secreta, algorithm=os.getenv('algoritmo'))
    return token


class TokenNoProporcionadoException(APIException):
    status_code = 402
    default_detail = "Token no proporcionado."
    default_code = "token_missing"

class TokenExpiradoException(APIException):
    status_code = 401
    default_detail = "El token ha expirado."
    default_code = "token_expired"

class TokenInvalidoException(APIException):
    status_code = 403
    default_detail = "Token inválido."
    default_code = "token_invalid"

class TokenErrorException(APIException):
    status_code = 500
    default_detail = "Error en la validación del token."
    default_code = "token_error"



class AutenticacionJWTPerzonalizada(BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise TokenNoProporcionadoException()

        try:
            token:str = auth_header.split(' ')[1]
            token_payload:str = jwt.decode(token, os.getenv('clave_secreta'), os.getenv('algoritmo'))
            request.usuario_id = token_payload['Id_usuario']
            request.usuario_nombre = token_payload['nombre_usuario']
            return True
            
        #except jwt.DecodeError: raise jwt.DecodeError('Error al decodificar el token')
        except jwt.DecodeError: raise TokenInvalidoException()

        #except jwt.ExpiredSignatureError: raise jwt.ExpiredSignatureError('El token a expirado')
        except jwt.ExpiredSignatureError: raise TokenExpiradoException()

        #except jwt.InvalidTokenError: raise jwt.InvalidTokenError('Error en la validación del token')
        except jwt.InvalidTokenError: raise TokenErrorException()