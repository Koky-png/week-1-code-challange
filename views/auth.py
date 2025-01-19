from flask import jsonify, request, Blueprint
from model import User, db, TokenBlocklist
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta, timezone


auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data ["email"]
    password = data["password"]

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200

    else:
        return jsonify({"error": "Either Email or Password is Incorrect"}), 404
    
@auth_bp.route("/current_user", methods=["GET"])
@jwt_required()
def current_user():
    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)
    user_data = {
            'id':user.id,
            'username':user.username,
            'email':user.email
        }
    return jsonify(user_data), 200

@auth_bp.route("/user/update", methods=["PATCH"])
@jwt_required()
def update_info():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if user:
        data = request.get_json()
        username = data.get("username", user.username)
        email = data.get("email", user.email)

        check_username = User.query.filter_by(username=username and id!=user.id).first()
        check_email = User.query.filter_by(email=email and id!=user.id).first()

        if check_username:
            return jsonify({"error":"First name not changed"}),406

        
        if check_email:
            return jsonify({"error":"Email not changed"}),406
        
        else:
            user.username=username
            user.email=email

            db.session.commit()
            return jsonify({"success":"Updated successfully"}), 200
        
    else:
        return jsonify({"error":"User is not Logged in "}),406    


@auth_bp.route("/user/updatepassword", methods=["PATCH"])
@jwt_required()
def update_password():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if user:
        data = request.get_json()
        new_password = data.get("password")

        if check_password_hash(user.password, new_password):
            return jsonify({"error": "Password not changed"}), 406
         
        else:
            user.password= generate_password_hash(new_password)

            db.session.commit()
            return jsonify({"success":"Password Updated successfully"}), 200
        
    else:
        return jsonify({"error":"User is not Logged in "}),406       

@auth_bp.route("/user/delete_account", methods=["DELETE"])
@jwt_required()
def delete_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"success":" User Deleted successfully"}), 200

    else:
        return jsonify({"error":"User is not Logged in "}),406

@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return jsonify({"success": "Logged Out successfully"}), 200

