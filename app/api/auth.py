# se importan las herramientas necesarias de las diferentes librerias.
from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from sqlalchemy import or_
from app import db, bcrypt, limiter
from app.models.user import User
from app.schemas.user import UserCreateSchema, UserLoginSchema, UserResponseSchema
from app.services.blacklist import BLACKLIST
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

# se crea un 'blueprint', que es una forma de organizar un grupo de rutas relacionadas.
# en este caso, todas las rutas de autenticacion.
auth_bp = Blueprint('auth', __name__)

# se define la ruta '/register' que solo acepta peticiones de tipo 'post'.
@auth_bp.route('/register', methods=['POST'])
def register():
    # se obtienen los datos enviados en la peticion en formato json.
    json_data = request.get_json()
    if not json_data:
        # si no se envian datos, se devuelve un error.
        return jsonify({"msg": "No se recibió ningún dato"}), 400

    try:
        # se validan los datos recibidos usando el esquema 'usercreateschema'.
        user_data = UserCreateSchema(**json_data)
    except ValidationError as e:
        # si los datos no son validos, se devuelven los errores de validacion.
        return jsonify(e.errors()), 400

    # se comprueba si ya existe un usuario con ese email o nombre de usuario.
    if User.query.filter((User.email == user_data.email) | (User.username == user_data.username)).first():
        return jsonify({"msg": "El email o nombre de usuario ya existe"}), 409

    # se encripta la contraseña antes de guardarla en la base de datos.
    hashed_password = bcrypt.generate_password_hash(user_data.password).decode('utf-8')
    
    # se crea un nuevo objeto 'user' con los datos validados.
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        is_confirmed=False 
    )
    
    # se añade el nuevo usuario a la sesion de la base de datos y se guardan los cambios.
    db.session.add(new_user)
    db.session.commit()
    
    # se devuelve una respuesta de exito.
    return jsonify({"msg": "Usuario registrado exitosamente. Se requiere confirmación (simulada)."}), 201

# se define la ruta '/login' que solo acepta peticiones de tipo 'post'.
@auth_bp.route('/login', methods=['POST'])
# esta linea comentada se usaria para limitar el numero de intentos de login.
# @limiter.limit("5 per 15 minute", error_message="Demasiados intentos de inicio de sesión. Inténtalo más tarde.")
def login():
    # se obtienen los datos json de la peticion.
    json_data = request.get_json()
    if not json_data:
        return jsonify({"msg": "Faltan datos JSON"}), 400

    try:
        # se validan los datos de inicio de sesion.
        login_data = UserLoginSchema(**json_data)
    except ValidationError as e:
        return jsonify(e.errors()), 400

    # se busca al usuario en la base de datos por su nombre de usuario o email.
    user = User.query.filter(
        or_(User.username == login_data.identifier, User.email == login_data.identifier)
    ).first()

    # se comprueba si el usuario existe y si la contraseña es correcta.
    if user and bcrypt.check_password_hash(user.hashed_password, login_data.password):
        # estas lineas comentadas se usarian para verificar si la cuenta ha sido confirmada.
        # if not user.is_confirmed:
        #    return jsonify({"msg": "La cuenta no ha sido confirmada"}), 403

        # si las credenciales son correctas, se crea un token de acceso jwt con la id del usuario.
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token), 200

    # si las credenciales son incorrectas, se devuelve un error.
    return jsonify({"msg": "Credenciales inválidas"}), 401

# se define la ruta '/profile' que solo acepta peticiones 'get'.
# el decorador '@jwt_required' asegura que solo se puede acceder a esta ruta con un token jwt valido.
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        # se obtiene la identidad (la id del usuario) del token jwt.
        current_user_id = int(get_jwt_identity())
    except (ValueError, TypeError):
        return jsonify({"msg": "Token inválido"}), 422
    
    # se busca al usuario en la base de datos usando la id obtenida.
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    # se convierten los datos del usuario al formato de respuesta definido en el esquema.
    user_data = UserResponseSchema.from_orm(user).dict()
    # se devuelve la informacion del perfil del usuario.
    return jsonify(user_data), 200

# se define la ruta '/logout' que acepta peticiones 'post'.
# tambien requiere un token jwt valido.
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # se obtiene el identificador unico del token (jti).
    jti = get_jwt()["jti"]
    # se añade el jti a una lista negra para invalidar el token y que no se pueda volver a usar.
    BLACKLIST.add(jti)
    return jsonify({"msg": "Sesión cerrada exitosamente"}), 200