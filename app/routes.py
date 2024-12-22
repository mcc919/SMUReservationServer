from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from app.models import User
from app import db
from app.auth import auth

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    return '<p>hello world</p>'

@bp.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    print('username:', username)
    result = auth(username, password)
    result = result._asdict()  # AuthResponse를 dictionary 형태로 변환

    if not result["is_auth"]:
        result['access_token'] = None
        return jsonify(result), 401
    
    access_token = create_access_token(identity=username)

    if result["is_auth"]:
        user = User.query.filter_by(username=username).first()

        if user is None:
            return jsonify({"message": "User not found"}), 404
        
        result['access_token'] = access_token
        return jsonify(result), 200

@bp.route("/validateToken", methods=["GET"])
@jwt_required()
def validateToken():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@bp.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    
    result = auth(username, password)
    result = result._asdict()  # AuthResponse를 dictionary 형태로 변환

    if not result["is_auth"]:
        return jsonify({"message": "Invalid username or password"}), 401
    
    user = User.query.filter_by(username=username).first()

    if user:
        return jsonify({"message": "User already exists"}), 409

    new_user = User(username=username)
    

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created"}), 201
    except:
        db.session.rollback()
        return jsonify({"message": "Error creating user"}), 500

@bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.username for user in users]), 200

@bp.route('/users/<username>', methods=['GET'])
def get_user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({"message": "User not found"}), 404
    return jsonify(user.username), 200
