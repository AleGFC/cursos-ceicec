from ..modelo import usuario, usuario_schema, db, usuarios_schema, Rol  
from flask import request, jsonify
import bcrypt
from flask import Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload


ruta=Blueprint('modelo_blueprint',__name__) 

from flask import Blueprint, request, jsonify
from ..modelo import usuario, usuario_schema, db
import bcrypt

ruta = Blueprint('modelo_blueprint', __name__)

@ruta.route('/usuario', methods=['POST'])
def agregar_usuario():
    try:
        data = request.get_json()  # Obtén los datos JSON del request
        usuario_data = usuario_schema.load(data)  # Deserializa y valida los datos

        # ¡CIFRADO DE CONTRASEÑA (MUY IMPORTANTE)!
        contrasena_cifrada = bcrypt.hashpw(usuario_data['contrasena'].encode('utf-8'), bcrypt.gensalt())
        usuario_data['contrasena'] = contrasena_cifrada.decode('utf-8')  # Guarda la versión cifrada

        nuevo_usuario = usuario(**usuario_data)  # Crea el nuevo usuario
        db.session.add(nuevo_usuario)
        db.session.commit()

        # Serializa el nuevo usuario usando el esquema antes de enviarlo en la respuesta
        result = usuario_schema.dump(nuevo_usuario)  # Serializa el objeto usuario
        return jsonify(result), 201  # 201 Created y JSON serializado

    except Exception as e:
        db.session.rollback()  # Revierte los cambios en la base de datos
        return jsonify({'error': str(e)}), 400 

@ruta.route('/usuarios', methods=['GET'])
def lista_usuarios():
    print("Se ha recibido una petición a /usuarios")  # Mensaje de depuración
    try:
        # Cargar usuarios junto con sus roles
        listado = usuario.query.options(joinedload(usuario.rol)).all()
        resultado = usuarios_schema.dump(listado)
        
        # Mensaje de depuración
        print("Usuarios obtenidos:", resultado)  
        return jsonify(resultado)
    except Exception as e:
        print(f"Error en /usuarios: {e}")  # Mensaje de depuración
        return jsonify({'error': str(e)}), 500

@ruta.route('/usuarios/por-rol', methods=['GET'])
def obtener_usuarios_por_rol():
    try:
        # Obtener el nombre del rol desde los parámetros de la URL
        nombre_rol = request.args.get('rol', '')

        if not nombre_rol:
            return jsonify({'error': 'El parámetro "rol" es requerido'}), 400

        # Buscar el rol en la base de datos
        rol = Rol.query.filter_by(rol_nombre=nombre_rol).first()

        if not rol:
            return jsonify({'error': f'No se encontró el rol "{nombre_rol}"'}), 404

        # Filtrar usuarios por el rol_id
        usuarios = usuario.query.filter_by(rol_id=rol.rol_id).options(joinedload(usuario.rol)).all()

        if not usuarios:
            return jsonify({'mensaje': f'No hay usuarios asociados al rol "{nombre_rol}"'}), 200

        # Serializar los resultados
        resultado = usuarios_schema.dump(usuarios)
        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#@ruta.route('/usuarios/<cedula>', methods=['GET'])
#def seleccionar_usuario(cedula):
#    usuariounico= usuario.query.get(cedula)
#    return usuario_schema.jsonify(usuariounico)
#
#@ruta.route('/actualizar/<cedula>', methods=['PUT'])
#def actualizar_usuario(cedula):
#    act_usuario = usuario.query.get_or_404(cedula)  # Manejo de usuario no encontrado
#
#    try:
#        data = request.get_json()  # Obtén los datos JSON del request
#        usuario_data = usuario_schema.load(data, partial=True)  # Deserializa y valida, partial=True
#
#        # ¡CIFRADO DE CONTRASEÑA (si se proporciona)!
#        if 'contrasena' in usuario_data:  # Solo cifrar si se proporciona la contraseña
#            contrasena_cifrada = bcrypt.hashpw(usuario_data['contrasena'].encode('utf-8'), bcrypt.gensalt())
#            usuario_data['contrasena'] = contrasena_cifrada.decode('utf-8')
#
#        # Actualiza los atributos del usuario existente
#        for key, value in usuario_data.items():
#            setattr(act_usuario, key, value)
#
#        db.session.commit()
#
#        result = usuario_schema.dump(act_usuario)
#        return jsonify(result), 200  # 200 OK
#
#    except Exception as e:
#        db.session.rollback()
#        return jsonify({'error': str(e)}), 400
#    

@ruta.route('/usuarios/<int:cedula>', methods=['GET'])  # <int:cedula> is crucial
def seleccionar_usuario(cedula):
    usuariounico = usuario.query.get_or_404(cedula)
    return usuario_schema.jsonify(usuariounico)

@ruta.route('/actualizar/<int:cedula>', methods=['PUT'])  # <int:cedula> is crucial
def actualizar_usuario(cedula):
    act_usuario = usuario.query.get_or_404(cedula)
    try:
        data = request.get_json()
        usuario_data = usuario_schema.load(data, partial=True)

        if 'contrasena' in usuario_data:
            contrasena_cifrada = bcrypt.hashpw(usuario_data['contrasena'].encode('utf-8'), bcrypt.gensalt())
            usuario_data['contrasena'] = contrasena_cifrada.decode('utf-8')

        for key, value in usuario_data.items():
            setattr(act_usuario, key, value)

        db.session.commit()
        result = usuario_schema.dump(act_usuario)
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@ruta.route('/eliminar/<cedula>', methods=['DELETE'])
def eliminar_usuario(cedula):
    try:
        cedula= usuario.query.get_or_404(cedula) 
    
        db.session.delete(cedula)
        db.session.commit()
        return jsonify({'mensaje': 'Usuario eliminado correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    
@ruta.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        cedula = data.get('cedula')
        contrasena = data.get('contrasena')

        if not cedula or not contrasena:
            return jsonify({'error': 'Cédula y contraseña son requeridas'}), 400

        # Buscar el usuario por cédula
        user = usuario.query.filter_by(cedula=cedula).first()

        if user and bcrypt.checkpw(contrasena.encode('utf-8'), user.contrasena.encode('utf-8')):
            # Verificar que el usuario tenga un rol_id válido
            if not user.rol_id:
                return jsonify({'error': 'El usuario no tiene un rol asignado'}), 400

            # Crear el token de acceso
            access_token = create_access_token(identity=cedula)

            # Devolver el token y la información del usuario, incluyendo el rol
            return jsonify({
                'access_token': access_token,
                'usuario': {
                    'cedula': user.cedula,
                    'usuario_telegram': user.usuario_telegram,
                    'nombre': user.nombre,
                    'apellido': user.apellido,
                    'correo': user.correo,
                    'rol_id': user.rol_id,  
                    'rol_nombre': user.rol.rol_nombre if user.rol else None,  
                    'created_at': user.created_at,
                }
            }), 200
        else:
            return jsonify({'error': 'Credenciales inválidas'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Error interno del servidor