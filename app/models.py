# app/models.py
from app import db  # app/__init__.py에서 선언한 db 객체 가져오기
from sqlalchemy import Enum as dbEnum
from app.enums import UserRole, UserStatus, RoomStatus, RoomLocation, ReservationStatus, BoardStatus
from constants.settings import Settings
from datetime import datetime
from pytz import timezone
from utils import stringToTime

class User(db.Model):

    user_id = db.Column(db.String(20), primary_key=True, nullable=False)
    department = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    nationality = db.Column(db.String(20), nullable=False)
    username_kor = db.Column(db.String(20), nullable=True, default="")
    username_eng = db.Column(db.String(20), nullable=True, default="")
    username_cha = db.Column(db.String(20), nullable=True, default="")

    grade = db.Column(db.Integer, nullable=False)
    enrollment_status = db.Column(db.String(20), nullable=False)

    # Below are initialized with default values
    role = db.Column(dbEnum(UserRole), nullable=False, default=UserRole.USER)
    status = db.Column(dbEnum(UserStatus), nullable=False, default=UserStatus.UNAPPROVED)

    # Limit is 6 hours in 1 day.
    today_reserved_time = db.Column(db.String(20), nullable=False, default='00:00:00')

    #time = datetime.now(timezone('Asia/Seoul')).replace(microsecond=0)
    created_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<User {self.user_id}>'
    
    def to_dict(self):
        date = self.created_at
        _today_reserved_time = stringToTime(self.today_reserved_time)
        minutes = _today_reserved_time.hour * 60 + _today_reserved_time.minute
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
            'today_reserved_time': minutes,
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
        db.Index('idx_reservation_end_time', 'status', 'end_time')
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

        start = start.strftime("%Y-%m-%d-%H-%M-%S")
        end = end.strftime("%Y-%m-%d-%H-%M-%S")
        created = created.strftime("%Y-%m-%d-%H-%M-%S")

        return {
            'id': self.id,
            'user_id': self.user_id,
            'room_id': self.room_id,
            'start_time': start,
            'end_time': end,
            #'start_time': f'{start.year}-{start.month}-{start.day}-{start.hour}-{start.minute}-{start.second}',
            #'end_time': f'{end.year}-{end.month}-{end.day}-{end.hour}-{end.minute}-{end.second}',
            'status': self.status.value,
            'created_at': created
            #'created_at': f'{created.year}-{created.month}-{created.day}-{created.hour}-{created.minute}-{created.second}'
        }
    
class Board(db.Model):
    __table_args__ = ( 
        db.Index('idx_board_status_updated_at', 'status_updated_at'),
    )

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = db.Column(db.String(20), db.ForeignKey('user.user_id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)

    title = db.Column(db.String(Settings.BOARD_MAX_TITLE_LENGTH), nullable=False)
    content = db.Column(db.String(Settings.BOARD_MAX_CONTENT_LENGTH), nullable=False)
    status = db.Column(dbEnum(BoardStatus), nullable=False, default=BoardStatus.SUBMITTED)

    created_at = db.Column(db.DateTime, nullable=False)
    edited_at = db.Column(db.DateTime)

    status_updated_at = db.Column(db.DateTime, nullable=False)
    

    def __repr__(self):
        return f'<Board {self.id}>'
    
    def to_dict(self):
        created = self.created_at
        edited = self.edited_at
        updated = self.status_updated_at

        created = created.strftime("%Y-%m-%d-%H-%M-%S")
        edited = edited.strftime("%Y-%m-%d-%H-%M-%S")
        updated = updated.strftime("%Y-%m-%d-%H-%M-%S")

        return {
            'id': self.id,
            'user_id': self.user_id,
            'room_id': self.room_id,
            'title': self.title,
            'content': self.content,
            'status': self.status.value,
            'created_at': created,
            'edited_at': edited,
            'status_updated_at': updated
        }

class BoardComment(db.Model):
    __table_args__ = ( 
        db.Index('idx_comment_created_at', 'created_at'),
    )
    
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'), nullable=False, autoincrement=True)
    admin_id = db.Column(db.String(20), db.ForeignKey('user.user_id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)

    status = db.Column(dbEnum(BoardStatus), nullable=False, default=BoardStatus.SUBMITTED)
    comment = db.Column(db.String(300), nullable=False)


    created_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<BoardComment {self.id}>'
    
    def to_dict(self):
        created = self.created_at
        created = created.strftime("%Y-%m-%d-%H-%M-%S")

        return {
            'id': self.id,
            'board_id': self.board_id,
            'admin_id': self.admin_id,
            'room_id': self.room_id,
            'status': self.status.value,
            'comment': self.comment,
            'created_at': created
        }