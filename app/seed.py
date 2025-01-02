from app import db
from app.models import Room, RoomStatus, Reservation, ReservationStatus
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

    reservations = [
        Reservation(user_id='202010832', room_id=1, start_time=datetime(2024, 12, 30, 9, 0), end_time=datetime(2024, 12, 30, 11, 0)),
        Reservation(user_id='202010832', room_id=1, start_time=datetime(2024, 12, 30, 11, 0), end_time=datetime(2024, 12, 30, 12, 0)),
        Reservation(user_id='202010832', room_id=1, start_time=datetime(2024, 12, 30, 13, 0), end_time=datetime(2024, 12, 30, 14, 30)),
        Reservation(user_id='202010832', room_id=1, start_time=datetime(2024, 12, 30, 15, 0), end_time=datetime(2024, 12, 30, 16, 0)),
        Reservation(user_id='202010832', room_id=1, start_time=datetime(2024, 12, 30, 17, 0), end_time=datetime(2024, 12, 30, 20, 30)),
    ]
    db.session.bulk_save_objects(reservations)

    db.session.commit()

if __name__ == '__main__':
    seed_data()
    print("Initial data has been seeded.")