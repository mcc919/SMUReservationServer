from app import create_app
from app.models import db, User  # User는 예제 모델 이름
from app.seed import seed_data
import os, sys

relative_path = 'custom_library'
package_path = os.path.join(os.getcwd(), relative_path)
sys.path.append(package_path)

# 애플리케이션 및 DB 설정 로드
app = create_app()

with app.app_context():
    # 기존 데이터베이스 파일 삭제 (선택 사항, SQLite에만 적용)
    db_path = os.path.join(os.getcwd(), 'instance', 'app.db')
    if os.path.exists(db_path):
        os.remove(db_path)

    # 테이블 생성
    db.create_all()
    print("db_init: Database initialized! (Tables created)")

    # 초기 데이터 삽입
    seed_data()
    print("db_init: Initial data has been seeded.")