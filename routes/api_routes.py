from flask import Blueprint, request, jsonify
from models import User, List, ListParticipant
#from flask_bcrypt import check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import check_password_hash

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/token', methods=['POST'])
def create_token():
    username = request.json.get('username')
    password = request.json.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password.encode('utf-8')): # flask_bcrypt check, encode password
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username, fresh=True)

    return jsonify(access_token=access_token, token_type='bearer', expires_in=3600), 200

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