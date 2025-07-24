import os
from dotenv import load_dotenv

# aca se carga la funcion que lee las variables de un archivo '.env' y las hace accesibles para el programa.
# es util para no poner informacion sensible como contraseñas directamente en el codigo.
load_dotenv()

# aca se define una clase base que contiene las configuraciones comunes para todos los entornos.
class Config:
    """configuracion base."""
    # se obtiene una clave secreta desde las variables de entorno, usada por flask para seguridad.
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # se desactiva una funcion de sqlalchemy que consume muchos recursos y no se esta usando.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # se obtiene la clave secreta para firmar los tokens jwt.
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    # se define donde se guardara la informacion del limite de peticiones. por defecto, en memoria.
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')
    # se establece la estrategia que se usara para contar las peticiones (en este caso, 'ventana fija').
    RATELIMIT_STRATEGY = 'fixed-window'


# aca se define una clase para la configuracion de desarrollo. hereda las configuraciones de la clase base 'config'.
class DevelopmentConfig(Config):
    """configuracion de desarrollo."""
    # se activa el modo de depuracion, que muestra errores detallados.
    DEBUG = True
    # se obtiene la direccion de la base de datos de desarrollo desde las variables de entorno.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    

# aca se define una clase para la configuracion de produccion, cuando la aplicacion este en linea.
class ProductionConfig(Config):
    """configuracion de produccion."""
    # se desactiva el modo de depuracion por seguridad.
    DEBUG = False
    # se obtiene la direccion de la base de datos de produccion.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # esta linea comentada se usaria en produccion para guardar los datos del limite de peticiones en redis,
    # que es mas robusto que guardarlos en memoria.
    # RATELIMIT_STORAGE_URI = "redis://localhost:6379"

# aca se crea un diccionario que permite seleccionar la clase de configuracion correcta
# usando una cadena de texto como 'development' o 'production'.
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}