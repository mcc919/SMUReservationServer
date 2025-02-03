from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from datetime import datetime, date, time, timedelta
from app.models import User, Room, Reservation, Board, BoardComment, UserStatusLog
from app.enums import ReservationStatus, UserStatus, BoardStatus, UserRole
from app import db
from sangmyung_univ_auth import auth_detail, auth
from sqlalchemy import desc, case, or_, and_, asc
from pytz import timezone
from constants.settings import Settings
from utils import stringToDatetime, stringToTime

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    print(Settings.BOARD_MAX_TITLE_LENGTH)
    print(Settings.to_dict(self=Settings()))
    return '<p>hello world</p>'

@bp.route('/user/<id>', methods=['GET'])
def get_user_info(id):
    user = User.query.filter_by(user_id=id).first()
    if user is None:
        return jsonify({"message": "유저 정보를 찾을 수 없습니다."}), 404
    
    return jsonify(user.to_dict()), 200

@bp.route('/login', methods=['POST'])
def login():
    user_id = request.form['userId']
    password = request.form['password']

    print('user_id:', user_id)
    if not user_id or not password:
        return jsonify({"error": "Missing userId or password"}), 400
    
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
        
        if user.status == UserStatus.INACTIVE:
            return jsonify({"message": "승인 대기 중인 계정입니다. 관리자에게 문의하세요."}), 403

        else:
            print('가입 날짜: ', user.created_at)
            result = {
                "is_auth": result['is_auth'],
                "access_token": access_token,
                "user": user.to_dict(),
            }
            return jsonify(result), 200

@bp.route("/settings", methods=["GET"])
def get_settings():
    settings = Settings()
    return jsonify(settings.to_dict()), 200


@bp.route("/validateToken", methods=["GET"])
@jwt_required()
def validateToken():
    current_user = get_jwt_identity()
    if current_user is None:
        return jsonify({"message": "Invalid token"}), 401
    
    user = User.query.filter_by(user_id=current_user).first()
    if user is None:
        return jsonify({"message": "유저 정보가 데이터베이스에 존재하지 않습니다."}), 404
    
    return jsonify(user.to_dict()), 200

@bp.route('/register', methods=['POST'])
def register():
    #data = request.get_data()
    #print(data)

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
        created_at = datetime.now(timezone('Asia/Seoul')).replace(microsecond=0)
        new_user = User(user_id=user_id,
                        department=data['department'],
                        email=data['email'],
                        nationality=data['nationality'],
                        username_kor=data['name'],
                        username_eng=data['name_eng'],
                        username_cha=data['name_chinese'],
                        grade=data['grade'],
                        enrollment_status=data['enrollment_status'],
                        created_at=created_at)
                        
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


# get every user list (only for admin)
@bp.route('/user/all/<id>', methods=['GET'])
@jwt_required()
def get_user_all(id):
    try:
        user = User.query.filter_by(user_id=id).first()

        if user is None:
            return jsonify({'message': '회원가입 후 이용해주세요.'}), 404
        
        if user.role == UserRole.USER:
            return jsonify({'message': '접근 권한이 없습니다.'}), 409
        
        profiles = User.query.all()

        return jsonify([profile.to_dict() for profile in profiles]), 200

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"message": e}), 404
    

# get specific user info
@bp.route('/user/<id>', methods=['GET'])
@jwt_required()
def get_user(id):
    print(id)
    user = User.query.filter_by(user_id=id).first()

    if user is None:
        return jsonify({'message': '해당 유저 정보를 찾을 수 없습니다.'}), 404
    
    return jsonify(user.to_dict()), 200



@bp.route('/user/accept', methods=['POST'])
@jwt_required()
def accept_user():
    if not request.is_json:
        return jsonify({"message": "올바른 JSON 형식이 아닙니다."}), 400

    data = request.get_json()  # JSON 데이터 받기

    input_user_id = data.get('userId')
    input_admin_id = data.get('adminId')

    if not input_user_id or not input_admin_id:
        return jsonify({"message":"필수 정보가 누락되었습니다."}), 400

    try:
        admin = User.query.filter_by(user_id=input_admin_id).first()
        if admin is None:
            return jsonify({"message": "사용자님의 회원 정보를 데이터베이스에서 찾을 수 없습니다."}), 403
        
        if admin.role != UserRole.ADMIN:
            return jsonify({"message": "관리자 권한이 없습니다."}), 409

        user = User.query.filter_by(user_id=input_user_id).first()
        if user is None:
            return jsonify({"message": "사용자 정보를 찾을 수 없습니다."}), 404

        if user.status != UserStatus.UNAPPROVED:
            return jsonify({"message": "이미 활성화된 계정입니다."}), 409
        
        changed_at = datetime.now(timezone('Asia/Seoul')).replace(microsecond=0)

        new_log = UserStatusLog(user_id=input_user_id,
                              previous_status=user.status,
                              new_status=UserStatus.ACTIVE,
                              changed_at=changed_at)
        db.session.add(new_log)

        user.status = UserStatus.ACTIVE

        db.session.commit()
        return jsonify({"message": "성공적으로 반영되었습니다."}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": e}), 500


# delete join request
@bp.route('/user/delete', methods=["DELETE"])
@jwt_required()
def delete_user():
    if not request.is_json:
        return jsonify({"message": "올바른 JSON 형식이 아닙니다."}), 400

    data = request.get_json()  # JSON 데이터 받기

    input_user_id = data.get('userId')
    input_admin_id = data.get('adminId')

    if not input_user_id or not input_admin_id:
        return jsonify({"message":"필수 정보가 누락되었습니다."}), 400

    try:
        admin = User.query.filter_by(user_id=input_admin_id).first()
        if admin is None:
            return jsonify({"message": "사용자님의 회원 정보를 데이터베이스에서 찾을 수 없습니다."}), 403
        
        if admin.role != UserRole.ADMIN:
            return jsonify({"message": "관리자 권한이 없습니다."}), 409

        user = User.query.filter_by(user_id=input_user_id).first()
        if user is None:
            return jsonify({"message": "사용자 정보를 찾을 수 없습니다."}), 404

        if user.status != UserStatus.UNAPPROVED:
            return jsonify({"message": "해당 사용자는 삭제 대상이 아닙니다. (가입 요청만 삭제 가능합니다.)"}), 409
       
        changed_at = datetime.now(timezone('Asia/Seoul')).replace(microsecond=0)

        new_log = UserStatusLog(user_id=input_user_id,
                              previous_status=user.status,
                              new_status=UserStatus.DELETED,
                              changed_at=changed_at)
        db.session.add(new_log)

        user.status = UserStatus.DELETED    # 삭제할거라 의미는 없는데 일단
        db.session.delete(user)

        db.session.commit()
        return jsonify({"message": "성공적으로 반영되었습니다."}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": e}), 500



@bp.route('/user/deactivate', methods=["POST"])
@jwt_required()
def deactivate_user():
    pass



@bp.route('/user/promote', methods=["POST"])
@jwt_required()
def promote_user_to_admin():
    pass



@bp.route('/user/demote', methods=["POST"])
@jwt_required()
def demote_admin_to_user():
    pass



@bp.route('/user/ban', methods=["POST"])
@jwt_required()
def ban_user():
    if not request.is_json:
        return jsonify({"message": "올바른 JSON 형식이 아닙니다."}), 400

    data = request.get_json()  # JSON 데이터 받기

    input_user_id = data.get('userId')
    input_admin_id = data.get('adminId')
    input_ban_days = data.get('banDays')
    input_reason = data.get('reason')

    if not input_user_id or not input_admin_id or not input_ban_days or not input_reason:
        return jsonify({"message":"필수 정보가 누락되었습니다."}), 400

    try:
        admin = User.query.filter_by(user_id=input_admin_id).first()
        if admin is None:
            return jsonify({"message": "사용자님의 회원 정보를 데이터베이스에서 찾을 수 없습니다."}), 403
        
        if admin.role != UserRole.ADMIN:
            return jsonify({"message": "관리자 권한이 없습니다."}), 409

        user = User.query.filter_by(user_id=input_user_id).first()
        if user is None:
            return jsonify({"message": "사용자 정보를 찾을 수 없습니다."}), 404

        if user.status != UserStatus.ACTIVE:
            return jsonify({"message": "해당 사용자는 정지 대상이 아닙니다."}), 409
       
        changed_at = datetime.now(timezone('Asia/Seoul')).replace(microsecond=0)

        new_log = UserStatusLog(user_id=input_user_id,
                              previous_status=user.status,
                              new_status=UserStatus.DELETED,
                              changed_at=changed_at)
        db.session.add(new_log)

        user.status = UserStatus.DELETED    # 삭제할거라 의미는 없는데 일단
        db.session.delete(user)

        db.session.commit()
        return jsonify({"message": "성공적으로 반영되었습니다."}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": e}), 500



@bp.route('/user/unban', methods=["POST"])
@jwt_required()
def unban_user():
    pass




@bp.route('/reservations', methods=['POST'])
@jwt_required()
def create_reservation():
    if not request.is_json:
        return jsonify({"message": "올바른 JSON 형식이 아닙니다."}), 400

    data = request.get_json()  # JSON 데이터 받기

    input_user_id = data.get('userId')
    input_room_id = data.get('roomId')
    input_start_time_str = data.get('startTime')
    input_end_time_str = data.get('endTime')
    input_date = data.get('date')

    if not input_user_id or not input_room_id or not input_start_time_str or not input_end_time_str or not input_date:
        return jsonify({"message":"필수 정보가 누락되었습니다."}), 400

    try:
        user = User.query.filter_by(user_id=input_user_id).first()
        if user is None:
            return jsonify({"message": "접근 권한이 없습니다. 회원가입 후 이용해주세요."}), 403 # Forbidden
        
        if user.status == UserStatus.INACTIVE:
            return jsonify({"message": "계정이 아직 승인되지 않았습니다. 관리자에게 문의하세요."}), 403
        
        if user.status == UserStatus.BANNED:
            return jsonify({f"message": "연습실 사용이 금지된 계정입니다. 금지 해제 날짜는 {}입니다."}), 409 # Conflict
        
        if user.enrollment_status != '재학':
            print(user.enrollment_status)
            return jsonify({"message": "재학 중인 학생만 이용할 수 있습니다."}), 422    # Unprocessable Content

        reservation_date = datetime.strptime(input_date, '%Y-%m-%d')
        start_of_day = reservation_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = reservation_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        start_time = datetime.fromisoformat(input_start_time_str)
        end_time = datetime.fromisoformat(input_end_time_str)

    # 유저가 하루 예약 가능 시간을 초과했는지 검사합니다.
    # 18시 이후의 건은 하루 예약 가능 시간에 포함되지 않습니다.
        print('현재 예약 토탈: ', user.today_reserved_time)
        _today_reserved_time = stringToTime(user.today_reserved_time)   # time 객체로 변경
        _time_to_reserve_before18 = timedelta(hours=0, minutes=0, seconds=0)
        _time_to_reserve_after18 = timedelta(hours=0, minutes=0, seconds=0)

        if (end_time.time() <= time(18, 0, 0)):
            print('case1')
            _time_to_reserve_before18 = end_time - start_time   # timedelta
            #_diff = end_time - start_time   # timedelta

        elif (start_time.time() < time(18, 0, 0) and time(18, 0, 0) < end_time.time()):
            print('case2')
            _time_to_reserve_before18 = datetime.combine(date.today(), time(18, 0, 0)) - datetime.combine(date.today(), start_time.time())  # timedelta
            _time_to_reserve_after18 = datetime.combine(date.today(), end_time.time()) - datetime.combine(date.today(), time(18, 0, 0))
            #_diff = datetime.combine(date.today(), time(18, 0, 0)) - datetime.combine(date.today(), start_time.time())  # timedelta
        elif (time(18, 0, 0) <= start_time.time()):
            print('case3')
            _time_to_reserve_after18 = end_time - start_time    # timedelta
            #_diff = timedelta(hours=0, minutes=0, seconds=0)
            pass
        else:
            return jsonify({"message": "예약 조건 확인 중 1번 오류 발생"}), 404

        #new_today_reserved_time = (datetime.combine(date.today(), _today_reserved_time) + _diff).time()
        new_today_reserved_time = (datetime.combine(date.today(), _today_reserved_time) + _time_to_reserve_before18).time()
        if (start_time.time() < time(18, 0, 0) and Settings.RESERVATION_LIMIT_PER_DAY * 60 < new_today_reserved_time.hour * 60 + new_today_reserved_time.minute):
            return jsonify({"message":
f'''하루 최대 예약 가능 시간을 초과하였습니다.
(현재까지 사용된 시간: {user.today_reserved_time})
(추가로 예약하려는 시간: {str(_time_to_reserve_before18)})'''}), 409
    
    # 유저가 같은 시간에 다른 방에 예약한 내역이 있는지 확인합니다. (중복 예약 방지)
        reservation = Reservation.query.\
            filter(
                Reservation.start_time >= start_of_day,
                Reservation.start_time <= end_of_day,
                Reservation.user_id == input_user_id,
                Reservation.status != ReservationStatus.CANCELLED).\
            filter(
                or_(
                    and_(Reservation.start_time < end_time, Reservation.end_time > start_time),
                    and_(Reservation.end_time > start_time, Reservation.start_time < end_time)
                )).first()
        if reservation:
            _info = reservation.to_dict()
            _room_id = _info['room_id']
            print(_info)
            room = Room.query.filter_by(id=_room_id).first()
            
            if room is None:
                return jsonify({"message": "서버에서 오류가 발생하였습니다."}), 500
            
            room = room.to_dict()
            _start_time = stringToDatetime(_info['start_time'])
            _end_time = stringToDatetime(_info['end_time'])
            print(_info['start_time'])
            return jsonify({
                "message":
f'''같은 시간에 중복된 예약이 존재합니다.
취소 후에 다시 시도해주세요.\n
중복된 예약:
{room['number']}
{_start_time.strftime('%Y년 %m월 %d일')}
{_start_time.strftime('%H:%M:%S')}-{_end_time.strftime('%H:%M:%S')}
''',
                }), 409

    # 해당 시간의 다른 유저가 예약했는지 확인합니다.
    # 클라이언트 단에서 예약된 시간은 선택할 수 없도록 해 놓았지만 서버에서 한번 더 확인합니다.
        reservations = Reservation.query.\
            filter(
                Reservation.start_time >= start_of_day,
                Reservation.start_time <= end_of_day,
                Reservation.room_id == input_room_id,
                Reservation.status == ReservationStatus.RESERVED).\
            filter(
                or_(
                    and_(Reservation.start_time < end_time, Reservation.end_time > start_time),
                    and_(Reservation.end_time > start_time, Reservation.start_time < end_time)
                )).all()

        if (reservations):
            return jsonify({"message":"이미 예약된 시간대입니다."}), 409

    # 해당 연습실의 최대 연습 시간을 넘기지 않았는지 확인합니다.
    # 18시 이전 예약의 경우 3시간, 18시를 포함하는 경우 4시간까지 허용됩니다.
        reservations = Reservation.query.\
            filter(
                Reservation.start_time >= start_of_day,
                Reservation.start_time <= end_of_day,
                Reservation.room_id == input_room_id,
                Reservation.user_id == input_user_id,
                Reservation.status == ReservationStatus.RESERVED).all()
        #_reserved_time = time(0, 0, 0)
        _total_reserved_time_after18 = timedelta(hours=0, minutes=0, seconds=0)
        _total_reserved_time_before18 = timedelta(hours=0, minutes=0, seconds=0)

        for reservation in reservations:
            _reservation = reservation.to_dict()
            _start_time = stringToDatetime(_reservation['start_time'])
            _end_time = stringToDatetime(_reservation['end_time'])
            _reserved_time_after18 = timedelta(hours=0, minutes=0, seconds=0)
            _reserved_time_before18 = timedelta(hours=0, minutes=0, seconds=0)

            print('_start_time:', _start_time.time())
            print('_end_time:', _end_time.time())
            if (_end_time.time() <= time(18, 0, 0)):
                _reserved_time_before18 = _end_time - _start_time   # timedelta
            elif (_start_time.time() < time(18, 0, 0) and time(18, 0, 0) < _end_time.time()):
                _reserved_time_before18 = datetime.combine(date.today(), time(18, 0, 0)) - datetime.combine(date.today(), _start_time.time())  # timedelta
                _reserved_time_after18 = datetime.combine(date.today(), _end_time.time()) - datetime.combine(date.today(), time(18, 0, 0))
            elif (time(18, 0, 0) <= _start_time.time()):
                _reserved_time_after18 = end_time - start_time    # timedelta
                pass
            else:
                return jsonify({"message": "예약 조건 확인 중 2번 오류 발생"}), 404
            
            _total_reserved_time_before18 += _reserved_time_before18
            _total_reserved_time_after18 += _reserved_time_after18
            print('현재 _before18:', _total_reserved_time_before18)
            print('현재 _after18:', _total_reserved_time_after18)
            #_diff = _end_time - _start_time
            #_reserved_time = (datetime.combine(date.today(), _reserved_time) + _diff).time()

        total_reserved_time_before18 = _total_reserved_time_before18 + _time_to_reserve_before18
        total_reserved_time_after18 = _total_reserved_time_after18 + _time_to_reserve_after18
        total_reserved_time = total_reserved_time_before18 + total_reserved_time_after18
        print('이 방 18시 이전 총합:', str(total_reserved_time_before18))
        print('이 방 18시 이후 총합:', str(total_reserved_time_after18))
        print('이 방 총 합', str(total_reserved_time))
        if (total_reserved_time_before18 > timedelta(hours=3, minutes=0, seconds=0)):
            return jsonify({'message':
f'''18시 이전 예약의 경우, 한 방에 최대 3시간까지만 예약할 수 있습니다.
현재 이 방에 예약된 시간: {str(total_reserved_time_before18 - _time_to_reserve_before18)}'''}), 409

        #total_reserved_time = (datetime.combine(date.today(), _reserved_time) + (end_time - start_time)).time()
        if (total_reserved_time > timedelta(hours=4, minutes=0, seconds=0)):
            return jsonify({'message':
f'''18시 이후를 포함하는 경우, 한 방에 최대 4시간까지 예약할 수 있습니다.
현재 이 방에 예약된 시간: {str(total_reserved_time - (_time_to_reserve_before18 + _time_to_reserve_after18))}'''}), 409
            


    # 모든 것에 문제가 없으면 예약을 생성합니다.
        created_at = datetime.now(timezone('Asia/Seoul')).replace(microsecond=0)

        new_rev = Reservation(user_id=input_user_id,
                              room_id=input_room_id,
                              start_time=start_time,
                              end_time=end_time,
                              created_at=created_at)
        db.session.add(new_rev)

        user.today_reserved_time = str(new_today_reserved_time)

        db.session.commit()
        return jsonify({"message": "성공적으로 예약되었습니다."}), 201
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"message": "예약 처리 중 서버 오류가 발생하였습니다."}), 500


@bp.route('/reservations/<int:reservation_id>', methods=['PUT'])
@jwt_required()
def delete_reservation(reservation_id):
    reservation = Reservation.query.filter_by(id=reservation_id).first()

    if reservation is None:
        return jsonify({"message": "예약 내역을 찾을 수 없습니다."}), 404
    
    if reservation.status.value != ReservationStatus.RESERVED.value:
        return jsonify({"message": "해당 레코드는 예약 상태가 아닙니다."}), 400

    try:
        reservation.status = ReservationStatus.CANCELLED

        # 유저의 하루 예약 가능 시간을 다시 늘려줘야 합니다.
        _reservation = reservation.to_dict()
        user = User.query.filter_by(user_id=_reservation['user_id']).first()
        _today_reserved_time = stringToTime(user.today_reserved_time)

        start_time = stringToDatetime(_reservation['start_time'])
        end_time = stringToDatetime(_reservation['end_time'])

        if (end_time.time() <= time(18, 0, 0)):
            _diff = end_time - start_time   # timedelta
        elif (start_time.time() < time(18, 0, 0) and time(18, 0, 0) < end_time.time()):
            _diff = datetime.combine(date.today(), time(18, 0, 0)) - datetime.combine(date.today(), start_time.time())  # timedelta
        elif (time(18, 0, 0) <= start_time.time()):
            _diff = timedelta(hours=0, minutes=0, seconds=0)
        else:
            return jsonify({"message": "예약 취소 중 오류가 발생하였습니다."}), 404

        new_today_reserved_time = str((datetime.combine(date.today(), _today_reserved_time) - _diff).time())
        user.today_reserved_time = new_today_reserved_time

        db.session.commit()
        return jsonify({"message":
f'''취소되었습니다.
오늘 18시 이전 사용 시간: {user.today_reserved_time}
(18시 이후는 사용 시간 제한 없음)'''}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


# @bp.route('/reservations', methods=['GET'])
# @jwt_required()
# def get_reservations():
#     pass


@bp.route('/reservations/user/<user_id>', methods=['GET'])
@jwt_required()
def get_reservations_by_user(user_id):
    reservations = Reservation.query.filter_by(user_id=user_id).order_by(
        case(
            (Reservation.status == ReservationStatus.RESERVED, 0),
            else_=1
        ),
        asc(Reservation.start_time)
        ).all()
    for reservation in reservations:
        print(reservation.to_dict())
    return jsonify([reservation.to_dict() for reservation in reservations]), 200


@bp.route('/reservations/room/<room_id>', methods=['GET'])
@jwt_required()
def get_reservations_by_room(room_id):
    room_id = int(room_id)

    reservations = Reservation.query.filter_by(id=room_id).all()
    return jsonify([reservation.to_dict() for reservation in reservations]), 200


@bp.route('/reservations/room/<room_id>/date/<date>')
@jwt_required()
def get_reservations_by_room_and_date(room_id, date):

    room_id = int(room_id)

    reservation_date = datetime.strptime(date, '%Y-%m-%d')
    print('reservation_date: ',reservation_date)

    start_of_day = reservation_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = reservation_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    print('start_of_day: ',start_of_day)
    print('end_of_day: ',end_of_day)

    try:
        reservations = Reservation.query.filter(
            Reservation.room_id == room_id,
            Reservation.start_time >= start_of_day,
            Reservation.start_time <= end_of_day,
            Reservation.status != ReservationStatus.CANCELLED
        ).all()

        for reservation in reservations:        # debug
            print(reservation.to_dict())

        return jsonify([reservation.to_dict() for reservation in reservations]), 200

    except ValueError:
        return jsonify({"message": "데이터베이스 처리 중 오류가 발생하였습니다."}), 500


# 게시물 목록 전체를 불러옵니다.
# 정렬 기준: 상태 최종 업데이트 오름차순
@bp.route('/boards', methods=['GET'])
@jwt_required()
def get_boards():
    try:
        boards = Board.query.order_by(desc(Board.status_updated_at)).all()
        return jsonify([board.to_dict() for board in boards]), 200
    except Exception as e:
        return jsonify({"message":e}), 404


# board_id에 해당하는 특정 게시물 한 개를 불러옵니다.
@bp.route('/board/<int:board_id>', methods=['GET'])
@jwt_required()
def get_board_by_board_id(board_id):
    try:
        board_with_user = db.session.query(Board, User).join(User, Board.user_id==User.user_id).filter(Board.id==board_id).first()
        board, user = board_with_user
        board_dict = board.to_dict()
        board_dict['user'] = user.to_dict()
        print(board_dict)
        return jsonify(board_dict), 200
    except Exception as e:
        db.session.rollback()
        print(e)

@bp.route('/boards', methods=['POST'])
@jwt_required()
def submit_board():
    if not request.is_json:
        return jsonify({"message": "올바른 JSON 형식이 아닙니다."}), 400

    data = request.get_json()  # JSON 데이터 받기
    print(data)

    input_user_id = data.get('userId')
    input_room_id = data.get('roomId')
    input_title = data.get('title')
    input_content = data.get('content')

    if not input_user_id or not input_room_id or not input_title or not input_content:
        return jsonify({"message":"필수 정보가 누락되었습니다."}), 400
    
    try:
        created_at = datetime.now(timezone('Asia/Seoul')).replace(microsecond=0)
    
        new_board = Board(user_id=input_user_id,
                        room_id=input_room_id,
                        title=input_title,
                        content=input_content,
                        created_at=created_at,
                        edited_at=created_at,
                        status_updated_at=created_at)
                        
        db.session.add(new_board)
        db.session.commit()

        return jsonify({"message": "성공적으로 제출되었습니다."}), 201
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"message": "서버 내부 오류로 인해 제출에 실패하였습니다."}), 500


@bp.route('/boardcomments/board/<board_id>', methods=['GET'])
@jwt_required()
def get_boardcomments(board_id):
    try:
        boardcomments = BoardComment.query.filter_by(board_id=board_id).order_by(asc(BoardComment.created_at)).all()
        result = []
        for boardcomment in boardcomments:
            admin = User.query.filter_by(user_id=boardcomment.admin_id).first()
            if admin is None:
                return jsonify({"message":"답변자 정보를 찾을 수 없습니다."}), 404
            
            _data = boardcomment.to_dict()
            _data["writer"] = admin.to_dict()
            result.append(_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"message":e}), 404
    
@bp.route('/boardcomment', methods=['POST'])
@jwt_required()
def create_comment():
    if not request.is_json:
        return jsonify({"message": "올바른 JSON 형식이 아닙니다."}), 400

    data = request.get_json()  # JSON 데이터 받기

    input_user_id = data.get('userId')
    input_room_id = data.get('roomId')
    input_board_id = data.get('boardId')
    input_content = data.get('content')
    input_selected_state = data.get('state')

    if not input_user_id or not input_content or not input_selected_state or not input_board_id or not input_room_id:
        return jsonify({"message":"필수 정보가 누락되었습니다."}), 400

    try:
        board = Board.query.filter_by(id=input_board_id).first()
        if board is None:
            return jsonify({"message": "게시글이 존재하지 않습니다."}), 404
        
        user = User.query.filter_by(user_id=input_user_id).first()
        if user is None:
            return jsonify({"message": "회원가입이 필요한 서비스입니다."}), 403
        print(user.role)
        if user.role == UserRole.USER:
            return jsonify({"message": "답변을 작성할 권한이 없습니다."}), 409

        if (input_selected_state == BoardStatus.UNDER_REVIEW.value):
            _status = BoardStatus.UNDER_REVIEW
        elif (input_selected_state == BoardStatus.REJECTED.value):
            _status = BoardStatus.REJECTED
        elif (input_selected_state == BoardStatus.NEED_REVISION.value):
            _status = BoardStatus.NEED_REVISION
        elif (input_selected_state == BoardStatus.APPROVED.value):
            _status = BoardStatus.APPROVED
        elif (input_selected_state == BoardStatus.IN_PROGRESS.value):
            _status = BoardStatus.IN_PROGRESS
        elif (input_selected_state == BoardStatus.COMPLETED.value):
            _status = BoardStatus.COMPLETED
        elif (input_selected_state == BoardStatus.CANCELLED.value):
            _status = BoardStatus.CANCELLED
        elif (input_selected_state == BoardStatus.HOLD_ON.value):
            _status = BoardStatus.HOLD_ON
        else:
            return jsonify({"message": "지정하신 상태는 올바른 형식이 아닙니다."}), 400
        
        _created_at = datetime.now(timezone('Asia/Seoul')).replace(microsecond=0)

        new_comment = BoardComment(board_id=input_board_id,
                                   admin_id=input_user_id,
                                   room_id=input_room_id,
                                   status=_status,
                                   comment=input_content,
                                   created_at=_created_at)
        db.session.add(new_comment)

        board.status_updated_at = _created_at
        board.status = _status
        
        db.session.commit()


        return jsonify({"message": '답변이 성공적으로 업로드되었습니다!'}), 201
    except Exception as e:
        print('야야야야야에러뜸: :', e)
        db.session.rollback()
        return jsonify({"message":e}), 404