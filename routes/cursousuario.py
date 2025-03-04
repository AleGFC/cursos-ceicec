from ..modelo import db, cursousuario,cursosusuarios_schema,CursoUsuarioSchema,cursousuario_schema,usuario_schema
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint

routa=Blueprint('cursousuario_blueprint',__name__)

@routa.route('/ruta_protegida', methods=['GET'])
@jwt_required()
def ruta_protegida():
    cedula = get_jwt_identity()
    return jsonify({'cedula': cedula})

@routa.route('/pago', methods=['POST'])
@jwt_required()
def pago_curso():
    try:
        cedula = get_jwt_identity()
        data = request.get_json()
        print("Data recibida:", data)
        
        # Procesar múltiples cursos
        cursos_ids = data.get('cursos', [])
        metodo_pago = data.get('metodo_pago', '')
        referencia = data.get('referencia', '')

        for curso_id in cursos_ids:
            pago = cursousuario(cedula=cedula, curso_id=curso_id, metodo_pago=metodo_pago, referencia=referencia)
            db.session.add(pago)
        
        db.session.commit()
        return jsonify({'mensaje': 'Pago realizado con éxito'}), 201
    except Exception as e:
        db.session.rollback()
        print("Error en el backend:", str(e))
        return jsonify({'error': str(e)}), 400
    
    
@routa.route('/lista_pago', methods=['GET'])
def lista_pago():
    listado= cursousuario.query.all()
    resultado=cursosusuarios_schema.dump(listado)
    return jsonify(resultado)
@routa.route('/actualizar_pago/<cedula>', methods=['PUT'])
def actualizar_curso(cedula):
    act_pago = cursousuario.query.get_or_404(cedula)  # Manejo de usuario no encontrado#
    try:
        data = request.get_json()  # Obtén los datos JSON del request
        pago_data = cursousuario_schema.load(data, partial=True)  # Deserializa y valida, partial=True
        
        # Actualiza los atributos del usuario existente
        for key, value in pago_data.items():
            setattr(act_pago, key, value)#
        db.session.commit()#
        result = cursousuario_schema.dump(act_pago)
        return jsonify(result), 200  # 200 OK#

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
@routa.route('/eliminar_curso/<cedula>', methods=['DELETE'])
def eliminar_curso(cedula):
    try:
        pagounico= cursousuario.query.get_or_404(cedula) 
    
        db.session.delete(pagounico)
        db.session.commit()
        return jsonify({'mensaje': 'Curso eliminado correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
