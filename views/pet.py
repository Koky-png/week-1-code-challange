from flask import jsonify, request, Blueprint
from model import Pet, User, db
from flask_jwt_extended import  jwt_required, get_jwt_identity


pet_bp = Blueprint("pet_bp", __name__)

@pet_bp.route("/pet", methods=["POST"])
def add_pet():
    data = request.get_json()

    name= data['name']
    species = data['species']
    age= data['age']
    user_id = data['user_id']

    chech_user_id = User.query.get(user_id)

    if not chech_user_id:
        return jsonify({"error":"User doesn't exists"}),406
    
    else:
        new_pet = Pet(name=name, species=species, age=age,user_id=user_id)
        
        db.session.add(new_pet)
        db.session.commit()
        return jsonify({"success":"Pet added successfully"}), 201


@pet_bp.route("/pets", methods=["GET"])
@jwt_required()
def fetch_pets():
    current_user_id = get_jwt_identity()
    pets = Pet.query.filter_by(user_id=current_user_id)
    pet_list = []

    for pet in pets:
        pet_list.append({
            "id": pet.id,
            "name": pet.name,
            "species": pet.species,
            "age": pet.age,
            "user_id": {"id": pet.user.id, "username": pet.user.username, "Email": pet.user.email}
        })

    return jsonify(pet_list)

@pet_bp.route("/pet/<int:pet_id>", methods=["GET"])
@jwt_required()
def fetch_pet(pet_id):
    current_user_id = get_jwt_identity()
    pet = Pet.query.filter_by(id=pet_id, user_id=current_user_id).first()

    if pet:
        pet_data = {
            "id": pet.id,
            "name": pet.name,
            "species": pet.species,
            "age": pet.age,
            "user_id": {"id": pet.user.id, "username": pet.user.username, "Email": pet.user.email}
        }

        return jsonify(pet_data)
    
    return jsonify({"error": "Pet doesn't exist!"}), 406


@pet_bp.route("/pet/<int:pet_id>", methods=["PATCH"])
def update_pet(pet_id):
    pet = Pet.query.get(pet_id)

    if pet:
        data = request.get_json()
        name = data.get('name', pet.name)
        species = data.get('species', pet.species)
        age = data.get('age', pet.age)
        user_id = data.get('user_id', pet.user_id)

        check_user_id = User.query.get(user_id)
        if  not check_user_id:
            return jsonify({"error": "User doesn't exist"}), 406
        
        pet.name = name
        pet.species = species
        pet.age = age
        pet.user_id = user_id

        db.session.commit()
        return jsonify({"success": "pet Updated successfully"}), 200
    
    return jsonify({"error": "pet doesn't exist!"}), 406


@pet_bp.route("/pet/<int:pet_id>", methods=["DELETE"])
def delete_todos(pet_id):
    pet = Pet.query.get(pet_id)

    if pet:
        db.session.delete(pet)
        db.session.commit()
        return jsonify({"success":"pet Deleted successfully"}), 200

    else:
        return jsonify({"error":"pet your are trying to delete doesn't exist!"}),406

