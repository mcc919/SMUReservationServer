# app/models.py
from app import db  # app/__init__.py에서 선언한 db 객체 가져오기

class User(db.Model):

    username = db.Column(db.String(80), primary_key=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
    