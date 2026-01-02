from enum import Enum

class Role(Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    MEMBER = "MEMBER"
    TRAINER = "TRAINER"
    ATTENDANT = "ATTENDANT"

class MembershipType(Enum):
    REGULAR = "REGULAR"
    PREMIUM = "PREMIUM"
    TRIAL = "TRIAL"
