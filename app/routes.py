from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from datetime import datetime
from app.models import User, Room, Reservation
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
            print('가입 날짜: ', user.created_at)
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
    #data = request.get_data()
    print(data)

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

@bp.route('/rooms', methods=['GET'])
@jwt_required()
def get_rooms():
    rooms = Room.query.all()
    rooms = [room.to_dict() for room in rooms]
    return jsonify(rooms), 200


@bp.route('/reservations', methods=['POST'])
@jwt_required()
def create_reservation():
    if not request.is_json:
        return jsonify({"message": "올바른 JSON 형식이 아닙니다."}), 400

    data = request.get_json()  # JSON 데이터 받기

    user_id = data.get('userId')
    room_id = data.get('roomId')
    start_time_str = data.get('startTime')
    end_time_str = data.get('endTime')

    if not user_id or not room_id or not start_time_str or not end_time_str:
        return jsonify({"message":"필수 정보 누락"}), 400

    try:
        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.fromisoformat(end_time_str)
        
        new_rev = Reservation(user_id=user_id,
                              room_id=room_id,
                              start_time=start_time,
                              end_time=end_time)
        db.session.add(new_rev)
        db.session.commit()
        return jsonify({"message": "New Reservation created"}), 201
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"message": "Error creating reservation"}), 500



# @bp.route('/reservations', methods=['GET'])
# @jwt_required()
# def get_reservations():
#     pass


@bp.route('/reservations/user/<user_id>', methods=['GET'])
#@jwt_required()
def get_reservations_by_user(user_id):
    reservations = Reservation.query.filter_by(user_id=user_id).all()
    return jsonify([reservation.to_dict() for reservation in reservations]), 200


@bp.route('/reservations/room/<room_id>', methods=['GET'])
#@jwt_required()
def get_reservations_by_room(room_id):
    reservations = Reservation.query.filter_by(id=room_id).all()
    return jsonify([reservation.to_dict() for reservation in reservations]), 200


@bp.route('/reservations/room/<room_id>/date/<date>')
#@jwt_required()
def get_reservations_by_room_and_date(room_id, date):
    try:
        room_id = int(room_id)

        reservation_date = datetime.strptime(date, '%Y-%m-%d')
        print('reservation_date: ',reservation_date)

        start_of_day = reservation_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = reservation_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        print('start_of_day: ',start_of_day)
        print('end_of_day: ',end_of_day)

        reservations = Reservation.query.filter(
            Reservation.room_id == room_id,
            Reservation.start_time >= start_of_day,
            Reservation.start_time <= end_of_day
        ).all()

        for reservation in reservations:        # debug
            print(reservation.to_dict())

        return jsonify([reservation.to_dict() for reservation in reservations]), 200

    except ValueError:
        print('유효한 포멧이 아니거나 예외 발생')   # degub
        return jsonify({"message": "유효한 날짜 포멧이 아닙니다. (YYYY-MM-DD)"}), 400