from flask import Blueprint, request, jsonify
from models import User, List, ListParticipant
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import check_password_hash, generate_password_hash
from models import db

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/token', methods=['POST'])
def create_token():
    username = request.json.get('username')
    password = request.json.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password.encode('utf-8')):
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username, fresh=True)

    return jsonify(access_token=access_token, token_type='bearer', expires_in=3600), 200


@api_bp.route('/users', methods=['GET', 'POST'])
@jwt_required()
def users_api():
    if request.method == 'GET':
        # Get all users
        users = User.query.all()
        user_list = []
        for user in users:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
            user_list.append(user_data)
        return jsonify(users=user_list), 200

    elif request.method == 'POST':
        # Create a new user
        username = request.json.get('username')
        email = request.json.get('email')
        password = request.json.get('password')

        if not username or not email or not password:
            return jsonify({"msg": "Username, email, and password are required"}), 400

        existing_user_username = User.query.filter_by(username=username).first()
        if existing_user_username:
            return jsonify({"msg": "Username already exists"}), 400

        existing_user_email = User.query.filter_by(email=email).first()
        if existing_user_email:
            return jsonify({"msg": "Email already registered"}), 400


        hashed_password = generate_password_hash(password.encode('utf-8')).decode('utf-8')
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"msg": "User created successfully", "user_id": new_user.id}), 201


@api_bp.route('/users/<int:id>', methods=['GET', 'DELETE', 'PUT', 'PATCH'])
@jwt_required()
def user_api_by_id(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    if request.method == 'GET':
        # Get specific user by ID
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
        return jsonify(user=user_data), 200

    elif request.method == 'DELETE':
        # Delete user by ID
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "User deleted successfully"}), 200

    elif request.method in ['PUT', 'PATCH']: # PUT for full update, PATCH for partial
        # Update user by ID
        username = request.json.get('username')
        email = request.json.get('email')
        password = request.json.get('password')


        if username:
            existing_user_username = User.query.filter_by(username=username).first()
            if existing_user_username and existing_user_username.id != user.id: # Check if username exists for *another* user
                return jsonify({"msg": "Username already exists"}), 400
            user.username = username

        if email:
            existing_user_email = User.query.filter_by(email=email).first()
            if existing_user_email and existing_user_email.id != user.id: # Check if email exists for *another* user
                return jsonify({"msg": "Email already registered"}), 400
            user.email = email

        if password: # Only update password if a new password is provided
            hashed_password = generate_password_hash(password.encode('utf-8')).decode('utf-8')
            user.password_hash = hashed_password

        db.session.commit()
        return jsonify({"msg": "User updated successfully", "user_id": user.id}), 200


@api_bp.route('/list', methods=['GET'])
@jwt_required()
def get_lists():
    current_user_username = get_jwt_identity()
    user = User.query.filter_by(username=current_user_username).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    created_lists = List.query.filter_by(created_by_id=user.id).all()
    participated_lists = [participant.list for participant in ListParticipant.query.filter_by(user_id=user.id).all()]

    lists_data = []
    for lst in created_lists + participated_lists: # Combine lists
        list_data = {
            'id': lst.id,
            'name': lst.name,
            'created_by': lst.creator.username,
            'created_at': str(lst.created_at),
            'is_creator': lst.created_by_id == user.id # Flag if current user is the creator
        }
        lists_data.append(list_data)

    return jsonify(lists=lists_data)


@api_bp.route('/list/<int:list_id>', methods=['GET'])
@jwt_required()
def get_list_detail(list_id):
    current_user_username = get_jwt_identity()
    user = User.query.filter_by(username=current_user_username).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    lst = List.query.get_or_404(list_id)
    if lst.created_by_id != user.id and not ListParticipant.query.filter_by(list_id=list_id, user_id=user.id).first():
        return jsonify({"msg": "Not authorized to view this list"}), 403

    items_data = []
    for item in lst.items:
        items_data.append({
            'id': item.id,
            'name': item.name,
            'is_ticked': item.is_ticked,
            'added_by': item.added_by_user.username,
            'added_at': str(item.added_at),
            'ticked_by': item.ticked_by_user.username if item.ticked_by_user else None,
            'ticked_at': str(item.ticked_at) if item.ticked_at else None
        })

    list_detail_data = {
        'id': lst.id,
        'name': lst.name,
        'created_by': lst.creator.username,
        'created_at': str(lst.created_at),
        'items': items_data,
        'is_creator': lst.created_by_id == user.id # Flag for creator
    }

    return jsonify(list_detail=list_detail_data)