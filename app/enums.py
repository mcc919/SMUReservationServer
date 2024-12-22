from enum import Enum

class UserRole(Enum):
    ADMIN = 'admin'
    USER =  'user'

class UserStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    BANNED = 'banned'