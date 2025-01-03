# app/models.py
from app import db  # app/__init__.py에서 선언한 db 객체 가져오기
from sqlalchemy import Enum as dbEnum
from app.enums import UserRole, UserStatus, RoomStatus, RoomLocation, ReservationStatus
from datetime import datetime
from pytz import timezone

class User(db.Model):

    user_id = db.Column(db.String(20), primary_key=True, nullable=False)
    department = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    nationality = db.Column(db.String(20), nullable=False)
    username_kor = db.Column(db.String(20), nullable=False)
    username_eng = db.Column(db.String(20), nullable=False)
    username_cha = db.Column(db.String(20), nullable=True, default="")

    grade = db.Column(db.Integer, nullable=False)
    enrollment_status = db.Column(db.String(20), nullable=False)

    # Below are initialized with default values
    role = db.Column(dbEnum(UserRole), nullable=False, default=UserRole.USER)
    status = db.Column(dbEnum(UserStatus), nullable=False, default=UserStatus.ACTIVE)

    #time = datetime.now(timezone('Asia/Seoul')).replace(microsecond=0)
    created_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<User {self.user_id}>'
    
    def to_dict(self):
        date = self.created_at
        return {
            'user_id': self.user_id,
            'department': self.department,
            'email': self.email,
            'nationality': self.nationality,
            'username_kor': self.username_kor,
            'username_eng': self.username_eng,
            'username_cha': self.username_cha,
            'grade': self.grade,
            'enrollment_status': self.enrollment_status,
            'role': self.role.value,
            'status': self.status.value,
            'created_at': f'{date.year}-{date.month}-{date.day}-{date.hour}-{date.minute}-{date.second}'
        }

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(30), nullable=False)
    location = db.Column(dbEnum(RoomLocation), nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    status = db.Column(dbEnum(RoomStatus), nullable=False, default=RoomStatus.AVAILABLE)

    def __repr__(self):
        return f'<Room {self.number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'name': self.name,
            'location': self.location.value,
            'floor': self.floor,
            'status': self.status.value
        }

class Reservation(db.Model):
    __table_args__ = ( 
        db.Index('idx_reservation_start_time', 'start_time'),  # start_time 컬럼에 인덱스 추가 -> 검색 속도 향상
    )

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = db.Column(db.String(20), db.ForeignKey('user.user_id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    # reservation time
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(dbEnum(ReservationStatus), nullable=False, default=ReservationStatus.RESERVED)
    #time = datetime.now(timezone('Asia/Seoul')).replace(microsecond=0)
    created_at = db.Column(db.DateTime, nullable=False)

    # Relation setting
    user = db.relationship('User', backref=db.backref('reservation', lazy=True))
    room = db.relationship('Room', backref=db.backref('reservation', lazy=True))

    def __repr__(self):
        return f'<Reservation {self.id}>'
    
    def to_dict(self):
        start = self.start_time
        end = self.end_time
        created = self.created_at

        return {
            'id': self.id,
            'user_id': self.user_id,
            'room_id': self.room_id,
            'start_time': f'{start.year}-{start.month}-{start.day}-{start.hour}-{start.minute}-{start.second}',
            'end_time': f'{end.year}-{end.month}-{end.day}-{end.hour}-{end.minute}-{end.second}',
            'status': self.status.value,
            'created_at': f'{created.year}-{created.month}-{created.day}-{created.hour}-{created.minute}-{created.second}'
        }