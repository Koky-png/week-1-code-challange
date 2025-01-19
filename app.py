from flask import Flask
from flask_migrate import Migrate
from model import  db 
from flask_jwt_extended import JWTManager
from datetime import timedelta


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///petstore.db'
migrate = Migrate(app, db)
db.init_app(app)

app.config["JWT_SECRET_KEY"] = "snow"  
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=35)

jwt = JWTManager(app)
jwt.init_app(app)


from views import *

app.register_blueprint(user_bp)
app.register_blueprint(pet_bp)
app.register_blueprint(auth_bp)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None