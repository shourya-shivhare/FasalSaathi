import enum

class Language(str, enum.Enum):
    ENGLISH = "ENGLISH"
    HINDI = "HINDI"

class PreferredLanguage(str, enum.Enum):
    ENGLISH = "ENGLISH"
    HINDI = "HINDI"

class Gender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class SoilType(str, enum.Enum):
    CLAY = "CLAY"
    LOAMY = "LOAMY"
    SANDY = "SANDY"
    BLACK = "BLACK"
    RED = "RED"
    SILT = "SILT"

class IrrigationSource(str, enum.Enum):
    RAINFED = "RAINFED"
    BOREWELL = "BOREWELL"
    CANAL = "CANAL"
    DRIP = "DRIP"
    SPRINKLER = "SPRINKLER"

class AccountStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    BLOCKED = "BLOCKED"
    DELETED = "DELETED"

class UserRole(str, enum.Enum):
    FARMER = "FARMER"
    ADMIN = "ADMIN"

class VerificationChannel(str, enum.Enum):
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"

class CropSeason(str, enum.Enum):
    KHARIF = "KHARIF"
    RABI = "RABI"
    ZAID = "ZAID"

class CropStage(str, enum.Enum):
    SEEDING = "SEEDING"
    GERMINATION = "GERMINATION"
    VEGETATIVE = "VEGETATIVE"
    FLOWERING = "FLOWERING"
    FRUITING = "FRUITING"
    MATURITY = "MATURITY"
    HARVEST_READY = "HARVEST_READY"

class CropCycleStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"

class JournalEntryType(str, enum.Enum):
    SOWING = "SOWING"
    IRRIGATION = "IRRIGATION"
    FERTILIZER = "FERTILIZER"
    PESTICIDE = "PESTICIDE"
    OBSERVATION = "OBSERVATION"
    HARVEST = "HARVEST"

class PestDetectionSource(str, enum.Enum):
    YOLO = "YOLO"
    MANUAL = "MANUAL"
    CHATBOT = "CHATBOT"

