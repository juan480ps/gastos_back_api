from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from sqlalchemy import or_
from app import db, bcrypt, limiter
from app.models.user import User
from app.schemas.user import UserCreateSchema, UserLoginSchema, UserResponseSchema
from app.services.blacklist import BLACKLIST
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"msg": "No se recibió ningún dato"}), 400

    try:
        user_data = UserCreateSchema(**json_data)
    except ValidationError as e:
        return jsonify(e.errors()), 400

    if User.query.filter((User.email == user_data.email) | (User.username == user_data.username)).first():
        return jsonify({"msg": "El email o nombre de usuario ya existe"}), 409

    hashed_password = bcrypt.generate_password_hash(user_data.password).decode('utf-8')
    
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        is_confirmed=False 
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"msg": "Usuario registrado exitosamente. Se requiere confirmación (simulada)."}), 201

@auth_bp.route('/login', methods=['POST'])
# @limiter.limit("5 per 15 minute", error_message="Demasiados intentos de inicio de sesión. Inténtalo más tarde.")
def login():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"msg": "Faltan datos JSON"}), 400

    try:
        login_data = UserLoginSchema(**json_data)
    except ValidationError as e:
        return jsonify(e.errors()), 400

    user = User.query.filter(
        or_(User.username == login_data.identifier, User.email == login_data.identifier)
    ).first()

    if user and bcrypt.check_password_hash(user.hashed_password, login_data.password):
        # if not user.is_confirmed:
        #    return jsonify({"msg": "La cuenta no ha sido confirmada"}), 403

        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Credenciales inválidas"}), 401

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        current_user_id = int(get_jwt_identity())
    except (ValueError, TypeError):
        return jsonify({"msg": "Token inválido"}), 422
    
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    user_data = UserResponseSchema.from_orm(user).dict()
    return jsonify(user_data), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    BLACKLIST.add(jti)
    return jsonify({"msg": "Sesión cerrada exitosamente"}), 200