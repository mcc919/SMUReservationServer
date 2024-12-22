# app/models.py
from app import db  # app/__init__.py에서 선언한 db 객체 가져오기
from sqlalchemy import Enum as dbEnum
from app.enums import UserRole, UserStatus
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

    time = datetime.now(timezone('Asia/Seoul'))
    created_at = db.Column(db.DateTime, nullable=False, default=time)

    def __repr__(self):
        return f'<User {self.user_id}>'
    
    def to_dict(self):
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
            'created_at': self.created_at
        }
