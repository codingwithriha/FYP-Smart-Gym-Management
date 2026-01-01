from enum import Enum

class Role(Enum):
    ADMIN = "ADMIN"
    BRANCH_MANAGER = "BRANCH_MANAGER"
    MEMBER = "MEMBER"

class MembershipType(Enum):
    REGULAR = "REGULAR"
    PREMIUM = "PREMIUM"
    TRIAL = "TRIAL"
