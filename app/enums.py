from enum import Enum

class UserRole(Enum):
    ADMIN = 'admin'             # 관리자
    USER =  'user'              # 일반 사용자

class UserStatus(Enum):
    ACTIVE = 'active'           # 활성화
    INACTIVE = 'inactive'       # 비활성화
    BANNED = 'banned'           # 사용 정지

class RoomStatus(Enum):
    AVAILABLE = 'available'     # 사용 가능
    MAINTENANCE = 'maintenance' # 보수 중
    OCCUPIED = 'occupied'       # 레슨실로 사용 중
    CLOSED = 'closed'           # 폐쇄

class RoomLocation(Enum):
    UB = 'UB'                   # 문화예술관 지하 3, 4층
    M = 'M'                     # 월해관 지하 1층

class ReservationStatus(Enum):
    RESERVED = 'reserved'       # 예약됨
    CANCELLED = 'cancelled'     # 취소됨
    COMPLETED = 'completed'     # 완료됨

class BoardStatus(Enum):
    IN_PROGRESS = 'in_progress'     # 처리중
    