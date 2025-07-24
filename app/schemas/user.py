from datetime import datetime  
import re
from pydantic import BaseModel, EmailStr, validator, Field

# aca se define una funcion que se usara como validador personalizado para las contraseñas.
def strong_password(password: str) -> str:
    """validador de contraseña fuerte."""
    # se comprueba la longitud de la contraseña.
    if len(password) < 8:
        raise ValueError('La contraseña debe tener al menos 8 caracteres')
    # se comprueba si contiene al menos una letra minuscula.
    if not re.search("[a-z]", password):
        raise ValueError('La contraseña debe contener al menos una letra minúscula')
    # se comprueba si contiene al menos una letra mayuscula.
    if not re.search("[A-Z]", password):
        raise ValueError('La contraseña debe contener al menos una letra mayúscula')
    # se comprueba si contiene al menos un numero.
    if not re.search("[0-9]", password):
        raise ValueError('La contraseña debe contener al menos un número')
    # si todas las validaciones pasan, se devuelve la contraseña.
    return password

# aca se define el esquema de datos para la creacion de un usuario.
# hereda de 'basemodel' de pydantic, lo que permite validaciones automaticas.
class UserCreateSchema(BaseModel):
    # se define el campo 'full_name', debe tener al menos 3 caracteres.
    full_name: str = Field(..., min_length=3)
    # se define el campo 'email', se valida automaticamente que sea un email valido.
    email: EmailStr
    # se define el campo 'username', debe tener al menos 3 caracteres.
    username: str = Field(..., min_length=3)
    # se define el campo 'password'.
    password: str

    # aca se registra la funcion 'strong_password' como un validador para el campo 'password'.
    _validate_password = validator('password', allow_reuse=True)(strong_password)

# aca se define el esquema de datos para el inicio de sesion.
class UserLoginSchema(BaseModel):
    # 'identifier' puede ser el email o el nombre de usuario.
    identifier: str  
    password: str

# aca se define el esquema de datos para la respuesta que se envia con la informacion del perfil del usuario.
class UserResponseSchema(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    username: str
    created_at: datetime 
    is_confirmed: bool

    # la clase 'config' se usa para configurar el comportamiento del modelo de pydantic.
    class Config:
        # 'from_attributes = true' permite que el modelo se cree a partir de un objeto de sqlalchemy
        # (como el objeto 'user') leyendo sus atributos directamente.
        from_attributes = True