from app import db
from app.models import User, Room, Board, RoomStatus, UserStatus, Reservation, ReservationStatus, UserRole
from pytz import timezone
from datetime import datetime

def seed_data():
    rooms = [
        Room(number='UB301', name='레슨실17', location='UB', floor=3, status=RoomStatus.AVAILABLE),
        Room(number='UB302', name='레슨실16', location='UB', floor=3, status=RoomStatus.AVAILABLE),
        Room(number='UB303', name='레슨실15', location='UB', floor=3, status=RoomStatus.AVAILABLE),
        Room(number='UB304', name='레슨실14', location='UB', floor=3, status=RoomStatus.AVAILABLE),
        Room(number='UB305', name='레슨실13', location='UB', floor=3, status=RoomStatus.AVAILABLE),
        Room(number='UB306', name='레슨실12', location='UB', floor=3, status=RoomStatus.AVAILABLE),
        Room(number='UB307', name='레슨실11', location='UB', floor=3, status=RoomStatus.AVAILABLE),
        Room(number='UB308', name='레슨실10', location='UB', floor=3, status=RoomStatus.AVAILABLE),
        Room(number='UB309', name='레슨실9', location='UB', floor=3, status=RoomStatus.AVAILABLE),
        Room(number='UB310', name='레슨실8', location='UB', floor=3, status=RoomStatus.AVAILABLE),
    ]

    db.session.bulk_save_objects(rooms)

    # reservations = [
    #     Reservation(user_id='202010832', room_id=1, start_time=datetime(2024, 12, 30, 9, 0), end_time=datetime(2024, 12, 30, 11, 0)),
    #     Reservation(user_id='202010832', room_id=1, start_time=datetime(2024, 12, 30, 11, 0), end_time=datetime(2024, 12, 30, 12, 0)),
    #     Reservation(user_id='202010832', room_id=1, start_time=datetime(2024, 12, 30, 13, 0), end_time=datetime(2024, 12, 30, 14, 30)),
    #     Reservation(user_id='202010832', room_id=1, start_time=datetime(2024, 12, 30, 15, 0), end_time=datetime(2024, 12, 30, 16, 0)),
    #     Reservation(user_id='202010832', room_id=1, start_time=datetime(2024, 12, 30, 17, 0), end_time=datetime(2024, 12, 30, 20, 30)),
    # ]
    #db.session.bulk_save_objects(reservations)

    # DUMMY DATA
    created_at = datetime.now(timezone('Asia/Seoul')).replace(microsecond=0)
    users = [
        User(status=UserStatus.ACTIVE, role=UserRole.ADMIN, user_id='202010832', department='휴먼지능정보공학전공', email='mcc919@naver.com', nationality='대한민국', username_kor='한호택', username_eng='Han Hotaek', grade=3, enrollment_status='재학', created_at=created_at),
        User(user_id='202011111', department='음악학부', email='chelsoo91@naver.com', nationality='대한민국', username_kor='김철수', username_eng='Kim Chelsoo', grade=3, enrollment_status='재학', created_at=created_at),
        User(status=UserStatus.BANNED, user_id='202022222', department='음악학부', email='younghee0201@gmail.com', nationality='대한민국', username_kor='박영희', username_eng='Park Younghee', grade=3, enrollment_status='재학', created_at=created_at),
        User(status=UserStatus.ACTIVE, user_id='202411111', department='음악학부', email='minsu23@naver.com', nationality='대한민국', username_kor='이민수', username_eng='Lee Minsu', grade=1, enrollment_status='재학', created_at=created_at),
        User(user_id='202422222', department='음악학부', email='sangmyung@naver.com', nationality='대한민국', username_kor='조상명', username_eng='Jo Sangmyung', grade=1, enrollment_status='재학', created_at=created_at),
    ]
    db.session.bulk_save_objects(users)

    boards = [
        Board(user_id='202022222', room_id=1, title='조율 부탁드립니다.', content='2옥타브 라의 음이 맞지 않습니다. 조율 부탁드립니다!', created_at=created_at, edited_at=created_at, status_updated_at=created_at),
        Board(user_id='202422222', room_id=3, title='현이 끊어져 있습니다.', content='3옥타브 파의 현이 끊어져있습니다! 제가 그런건 아니구요...발견만 제가했습니다. 수리 부탁드립니다!', created_at=created_at, edited_at=created_at, status_updated_at=created_at)
    ]
    db.session.bulk_save_objects(boards)
    
    db.session.commit()

if __name__ == '__main__':
    seed_data()
    print("Initial data has been seeded.")