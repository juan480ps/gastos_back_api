import os
from app import create_app

# aca se busca una variable de entorno llamada 'flask_env' para saber en que modo (desarrollo, produccion, etc.) debe ejecutarse la aplicacion.
# si no se encuentra, se usa 'development' (desarrollo) por defecto.
config_name = os.getenv('FLASK_ENV', 'development')
# se crea la aplicacion llamando a la funcion 'create_app' y se le pasa el nombre de la configuracion que se obtuvo antes.
app = create_app(config_name)

# esta linea comprueba si el archivo se esta ejecutando directamente.
# es una forma estandar en python de asegurarse que el codigo de adentro solo corra cuando se inicia este archivo especifico.
if __name__ == '__main__':
    # si la condicion anterior es verdadera, se inicia el servidor de la aplicacion para que pueda recibir peticiones.
    app.run()