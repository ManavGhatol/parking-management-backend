# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Enum, Date, Text
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
# pyrefly: ignore [missing-import]
from sqlalchemy.sql import func
import enum
from .database import Base

class UserType(str, enum.Enum):
    customer = "customer"
    attendant = "attendant"
    admin = "admin"
    superadmin = "superadmin"

class SlotType(str, enum.Enum):
    regular = "regular"
    handicapped = "handicapped"
    compact = "compact"
    reserved = "reserved"

class VehicleType(str, enum.Enum):
    car = "car"
    bike = "bike"
    truck = "truck"
    van = "van"

class PaymentStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"

class PaymentMethod(str, enum.Enum):
    card = "card"
    wallet = "wallet"
    cash = "cash"
    qrcode = "qrcode"

class BookingStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    phone_number = Column(String(15))
    user_type = Column(Enum(UserType), default=UserType.customer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))

    vehicles = relationship("Vehicle", back_populates="owner")
    bookings = relationship("Booking", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")


class ParkingSlot(Base):
    __tablename__ = "parking_slots"

    slot_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    slot_number = Column(String(20), unique=True, index=True, nullable=False)
    floor_number = Column(Integer)
    location = Column(String(100))
    slot_type = Column(Enum(SlotType), default=SlotType.regular)
    is_available = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    slot_length = Column(Float)
    hourly_rate = Column(Float)
    daily_rate = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vehicles = relationship("Vehicle", back_populates="slot")
    bookings = relationship("Booking", back_populates="slot")


class Vehicle(Base):
    __tablename__ = "vehicles"

    vehicle_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    registration_number = Column(String(20), index=True, nullable=False)
    vehicle_type = Column(Enum(VehicleType))
    vehicle_color = Column(String(20))
    entry_time = Column(DateTime(timezone=True), nullable=False)
    exit_time = Column(DateTime(timezone=True), nullable=True)
    slot_id = Column(Integer, ForeignKey("parking_slots.slot_id"), nullable=True)
    duration_minutes = Column(Integer)
    amount_paid = Column(Float)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    ticket_id = Column(String(20), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="vehicles")
    slot = relationship("ParkingSlot", back_populates="vehicles")
    payments = relationship("Payment", back_populates="vehicle")
    feedbacks = relationship("Feedback", back_populates="vehicle")


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.vehicle_id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(Enum(PaymentMethod))
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    transaction_id = Column(String(100), unique=True, index=True)
    reference_number = Column(String(50))
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    receipt_url = Column(String(255))

    vehicle = relationship("Vehicle", back_populates="payments")


class Rate(Base):
    __tablename__ = "rates"

    rate_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vehicle_type = Column(String(20), index=True)
    hourly_rate = Column(Float)
    daily_rate = Column(Float)
    monthly_rate = Column(Float)
    effective_date = Column(Date, index=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("parking_slots.slot_id"), nullable=False)
    booking_date = Column(Date, index=True, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    vehicle_type = Column(String(20))
    status = Column(Enum(BookingStatus), default=BookingStatus.pending)
    booking_confirmation = Column(String(50), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="bookings")
    slot = relationship("ParkingSlot", back_populates="bookings")


class Feedback(Base):
    __tablename__ = "feedback"

    feedback_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.vehicle_id"), nullable=True)
    rating = Column(Integer)  # Should add constraint 1-5 later
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="feedbacks")
    vehicle = relationship("Vehicle", back_populates="feedbacks")
