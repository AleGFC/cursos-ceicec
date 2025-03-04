from flask import Flask
from flask_cors import CORS
from .routes import roles, usuario, modalidad, curso, cursousuario
from flask_jwt_extended import JWTManager
from .extensiones import db, ma

def page_not_found(error):
    return '<h1>Not found page </h1>',404

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://Lilian:lilian@localhost:5432/proyecto3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['JWT_SECRET_KEY'] = 'lili' #Change this to a random secret key
jwt = JWTManager(app)
app.register_blueprint(roles.main)
app.register_blueprint(usuario.ruta)
app.register_blueprint(modalidad.rout)
app.register_blueprint(curso.rut)
app.register_blueprint(cursousuario.routa)
app.register_error_handler(404,page_not_found)
CORS(app)
db.init_app(app)
ma.init_app(app)


if __name__ == '__main__':  # Importante para scripts
    with app.app_context():  # ¡Contexto de aplicación!
        try:
            db.create_all()
            print("Tablas creadas.")
        except Exception as e:
            print(f"Error: {e}")
    app.run(debug=True)


