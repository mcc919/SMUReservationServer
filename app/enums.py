from enum import Enum

class UserRole(Enum):
    ADMIN = 'admin'             # 관리자
    USER =  'user'              # 일반 사용자

class UserStatus(Enum):
    UNAPPROVED = 'unapproved'   # 승인되지 않음 (최초 상태)
    ACTIVE = 'active'           # 활성화
    INACTIVE = 'inactive'       # 비활성화
    BANNED = 'banned'           # 사용 정지
    DELETED = 'deleted'         # 삭제됨

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
    SUBMITTED = 'submitted'         # 제출됨
    
    UNDER_REVIEW = 'under_review'   # 검토중
    REJECTED = 'rejected'           # 거절됨
    NEED_REVISION = 'need_revision' # 보완필요

    APPROVED = 'approved'           # 승인됨
    IN_PROGRESS = 'in_progress'     # 처리중

    COMPLETED = 'completed'         # 완료됨
    CANCELLED = 'cancelled'         # 취소됨
    HOLD_ON = 'hold_on'             # 보류중
    