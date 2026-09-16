from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from .models import UserType, SlotType, VehicleType, PaymentStatus, PaymentMethod, BookingStatus

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    user_type: UserType = UserType.customer

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    user_id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class ParkingSlotBase(BaseModel):
    slot_number: str
    floor_number: int
    location: str
    slot_type: SlotType
    slot_length: float
    hourly_rate: float
    daily_rate: float

class ParkingSlotCreate(ParkingSlotBase):
    pass

class ParkingSlotResponse(ParkingSlotBase):
    slot_id: int
    is_available: bool
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AuditLogCreate(BaseModel):
    user_id: Optional[int] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
    status: str = "success"

class VehicleEntry(BaseModel):
    registration_number: str
    vehicle_type: VehicleType
    vehicle_color: Optional[str] = None
    user_id: Optional[int] = None # Optional if guest
    entry_time: Optional[str] = None
    
class VehicleUpdate(BaseModel):
    registration_number: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    vehicle_color: Optional[str] = None

    
class VehicleExit(BaseModel):
    ticket_id: str

class VehicleResponse(BaseModel):
    vehicle_id: int
    registration_number: str
    vehicle_type: VehicleType
    entry_time: datetime
    exit_time: Optional[datetime] = None
    slot_id: Optional[int] = None
    amount_paid: Optional[float] = None
    payment_status: PaymentStatus
    ticket_id: str

    model_config = ConfigDict(from_attributes=True)

class PaymentProcess(BaseModel):
    ticket_id: str
    payment_method: PaymentMethod

