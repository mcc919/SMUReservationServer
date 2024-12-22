from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from app.models import User
from app import db
from sangmyung_univ_auth import auth_detail, auth

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    return '<p>hello world</p>'

@bp.route('/login', methods=['POST'])
def login():
    user_id = request.form['userId']
    password = request.form['password']

    print('user_id:', user_id)
    result = auth(user_id, password)
    result = result._asdict()  # AuthResponse를 dictionary 형태로 변환
    
    if not result["is_auth"]:
        result['access_token'] = None
        return jsonify(result), 401
    else:
        access_token = create_access_token(identity=user_id)

        user = User.query.filter_by(user_id=user_id).first()

        if user is None:
            return jsonify({"message": "회원가입 필요"}), 404
        else:
            result = {
                "is_auth": result['is_auth'],
                "access_token": access_token,
                "user": user.to_dict(),
            }
            return jsonify(result), 200

@bp.route("/validateToken", methods=["GET"])
@jwt_required()
def validateToken():
    current_user = get_jwt_identity()
    if current_user is None:
        return jsonify({"message": "Invalid token"}), 401
    
    return jsonify(logged_in_as=current_user), 200

@bp.route('/register', methods=['POST'])
def register():
    user_id = request.form['userId']
    password = request.form['password']

    if not user_id or not password:
        return jsonify({"error": "Missing userId or password"}), 400
    
    result = auth_detail(user_id, password)
    result = result._asdict()  # AuthResponse를 dictionary 형태로 변환

    print(result)   # Debugging 
    if not result["is_auth"]:
        return jsonify({"message": "Invalid userId or password"}), 401
    
    user = User.query.filter_by(user_id=user_id).first()

    if user:
        return jsonify({"message": "User already exists"}), 409    

    try:
        data = result['body']
        new_user = User(user_id=user_id,
                        department=data['department'],
                        email=data['email'],
                        nationality=data['nationality'],
                        username_kor=data['name'],
                        username_eng=data['name_eng'],
                        username_cha=data['name_chinese'],
                        grade=data['grade'],
                        enrollment_status=data['enrollment_status'])
                        
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created"}), 201
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"message": "Error creating user"}), 500

@bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify(users.to_dict()), 200

