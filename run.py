import os
import sys
from app import create_app, db
from app.seed import seed_data
from app.models import User, Room
from datetime import datetime, date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from app.enums import ReservationStatus
from app.models import Reservation

relative_path = 'custom_library'
package_path = os.path.join(os.getcwd(), relative_path)
sys.path.append(package_path)

app = create_app()

def initialize_db(app):
    with app.app_context():
        db.create_all() # Create tables for our models
        print("Database initialized!")

        # Seed initial data
        if not Room.query.first():
            seed_data()
            print("Initial data has been seeded.")

def update_reservation_state():
    with app.app_context():
        now = datetime.now()

        # 오늘 날짜에 완료된 예약 상태를 업데이트
        reservations_to_update = Reservation.query.filter(
            Reservation.status == ReservationStatus.RESERVED,
            Reservation.end_time <= now
        ).all()

        if not reservations_to_update:
            print(f"[{now}] 업데이트할 예약 없음")
            return
        
        for reservation in reservations_to_update:
            reservation.status = ReservationStatus.COMPLETED
            print(f"Reservation ID {reservation.id} 상태를 'completed'로 변경")

        # 변경 사항 커밋
        db.session.commit()
        print(f"[{now}] 완료된 예약 상태 업데이트 완료!")

def reset_today_reserved_time():
    with app.app_context():
        users = User.query.all()

        for user in users:
            user.today_reserved_time = 0
        
        db.session.commit()
        print("유저 하루 예약 시간 초기화 완료")

if __name__ == "__main__":
    initialize_db(app)
    update_reservation_state()
    
    # 스케줄러 초기화
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_reservation_state, 'cron', minute='0, 15, 30, 45')  # 매 00, 15, 30, 45분에 실행
    scheduler.add_job(reset_today_reserved_time, 'cron', hour='22')
    scheduler.start()

    print("스케줄러 시작!")
    try:
        # Flask 앱 실행
        app.run(host='0.0.0.0', port=5000)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()  # 스케줄러 종료
        print("스케줄러 종료!")