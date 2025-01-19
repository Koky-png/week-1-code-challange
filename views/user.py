
from flask import jsonify, request, Blueprint
from model import User, db
from werkzeug.security import generate_password_hash

user_bp = Blueprint("user_bp", __name__)

# ADD A USER
@user_bp.route("/user", methods=["POST"])
def add_user():
    data = request.get_json()
    username = data["username"]
    email = data["email"]
    password = data["password"]

    check_email = User.query.filter_by(email=email).first()
    print("email", check_email)
    if check_email:
        return jsonify({"error": "Email exists"}), 404
    
    else:
        new_user = User(username=username,email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"Success": " User Added Successfully"}), 200