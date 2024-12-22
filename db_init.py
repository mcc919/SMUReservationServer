from app import create_app
from app.models import db, User  # User는 예제 모델 이름
import os

# 애플리케이션 및 DB 설정 로드
app = create_app()

with app.app_context():
    # 기존 데이터베이스 파일 삭제 (선택 사항, SQLite에만 적용)
    db_path = os.path.join(os.getcwd(), 'app.db')
    if os.path.exists(db_path):
        os.remove(db_path)

    # 테이블 생성
    db.create_all()

    print("Database initialized!")
