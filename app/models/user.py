from datetime import datetime
from app import db

# aca se define la clase 'user' que representa la tabla de usuarios en la base de datos.
# hereda de 'db.model', lo que le da las funcionalidades de un modelo de sqlalchemy.
class User(db.Model):
    # se especifica el nombre de la tabla en la base de datos.
    __tablename__ = 'users'

    # aca se definen las columnas de la tabla.
    # 'id' es la llave primaria, un numero entero.
    id = db.Column(db.Integer, primary_key=True)
    # 'full_name' guarda el nombre completo, no puede ser nulo.
    full_name = db.Column(db.String(100), nullable=False)
    # 'email' guarda el correo, debe ser unico y no puede ser nulo.
    email = db.Column(db.String(120), unique=True, nullable=False)
    # 'username' guarda el nombre de usuario, debe ser unico y no puede ser nulo.
    username = db.Column(db.String(80), unique=True, nullable=False)
    # 'hashed_password' guarda la contraseña encriptada, no puede ser nula.
    hashed_password = db.Column(db.String(255), nullable=False)
    # 'created_at' guarda la fecha de creacion, por defecto es la fecha y hora actual.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # 'is_confirmed' indica si el usuario ha confirmado su cuenta, por defecto es falso.
    is_confirmed = db.Column(db.Boolean, default=False, nullable=False)

    # esta funcion define como se representara el objeto 'user' cuando se imprima.
    # es util para depuracion.
    def __repr__(self):
        return f'<User {self.username}>'