from fastapi import APIRouter, Depends, HTTPException, status, Response
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from typing import Any, List
from pymongo import MongoClient

from ..database import get_db
from ..models import Vehicle, ParkingSlot, Payment, PaymentStatus
from ..schemas import VehicleEntry, VehicleExit, VehicleResponse, PaymentProcess, VehicleUpdate

router = APIRouter(prefix="/api/v1/vehicles", tags=["vehicles"])

@router.get("/", response_model=List[VehicleResponse])
def get_all_vehicles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> Any:
    vehicles = db.query(Vehicle).order_by(Vehicle.entry_time.desc()).offset(skip).limit(limit).all()
    return vehicles

@router.post("/entry", response_model=VehicleResponse)
def register_vehicle_entry(entry: VehicleEntry, db: Session = Depends(get_db)) -> Any:
    # Find an available slot
    # Basic logic: find first available slot of type 'regular'
    slot = db.query(ParkingSlot).filter(ParkingSlot.is_available == True).first()
    
    if not slot:
        raise HTTPException(status_code=400, detail="No parking slots available")

    # Generate unique ticket ID
    ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"

    vehicle = Vehicle(
        registration_number=entry.registration_number,
        vehicle_type=entry.vehicle_type,
        vehicle_color=entry.vehicle_color,
        user_id=entry.user_id,
        entry_time=datetime.utcnow(),
        slot_id=slot.slot_id,
        ticket_id=ticket_id,
        payment_status=PaymentStatus.pending
    )

    # Mark slot as unavailable
    slot.is_available = False

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    
    # --- MongoDB Audit Log Insertion ---
    try:
        mongo_client = MongoClient("mongodb://localhost:27017/")
        mongo_db = mongo_client["parking_audit_db"]
        mongo_collection = mongo_db["vehicles_test"]
        
        # Use custom frontend time if provided, else fallback to UTC
        mongo_entry_time = entry.entry_time if entry.entry_time else vehicle.entry_time.isoformat()
        
        mongo_collection.insert_one({
            "ticket_id": vehicle.ticket_id,
            "reg_number": vehicle.registration_number,
            "type": vehicle.vehicle_type,
            "entry_time": mongo_entry_time,
            "status": "PENDING"
        })
    except Exception as e:
        print(f"MongoDB save error: {e}")
    # -----------------------------------

    return vehicle

@router.post("/exit", response_model=VehicleResponse)
def register_vehicle_exit(exit_data: VehicleExit, db: Session = Depends(get_db)) -> Any:
    vehicle = db.query(Vehicle).filter(Vehicle.ticket_id == exit_data.ticket_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found or invalid ticket ID")
    
    if vehicle.exit_time:
        raise HTTPException(status_code=400, detail="Vehicle already exited")

    if vehicle.payment_status != PaymentStatus.completed:
        raise HTTPException(status_code=400, detail="Payment pending. Please complete payment before exiting.")

    vehicle.exit_time = datetime.utcnow()
    duration = vehicle.exit_time - vehicle.entry_time
    vehicle.duration_minutes = int(duration.total_seconds() / 60)

    # Free the slot
    slot = db.query(ParkingSlot).filter(ParkingSlot.slot_id == vehicle.slot_id).first()
    if slot:
        slot.is_available = True

    db.commit()
    db.refresh(vehicle)
    return vehicle

@router.post("/payment")
def process_payment(payment_data: PaymentProcess, db: Session = Depends(get_db)) -> Any:
    vehicle = db.query(Vehicle).filter(Vehicle.ticket_id == payment_data.ticket_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Invalid ticket ID")
    
    if vehicle.payment_status == PaymentStatus.completed:
        raise HTTPException(status_code=400, detail="Payment already completed")

    # Mock calculation: 5 units per hour, minimum 10
    now = datetime.utcnow()
    duration = now - vehicle.entry_time
    hours = max(1, int(duration.total_seconds() / 3600))
    amount = max(10.0, float(hours * 5.0))

    payment = Payment(
        vehicle_id=vehicle.vehicle_id,
        amount=amount,
        payment_method=payment_data.payment_method,
        payment_status=PaymentStatus.completed,
        transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}"
    )

    db.add(payment)
    vehicle.payment_status = PaymentStatus.completed
    vehicle.amount_paid = amount
    db.commit()
    
    return {"message": "Payment successful", "amount": amount, "transaction_id": payment.transaction_id}

@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(vehicle_id: int, vehicle_in: VehicleUpdate, db: Session = Depends(get_db)) -> Any:
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    if vehicle_in.registration_number is not None:
        vehicle.registration_number = vehicle_in.registration_number
    if vehicle_in.vehicle_type is not None:
        vehicle.vehicle_type = vehicle_in.vehicle_type
    if vehicle_in.vehicle_color is not None:
        vehicle.vehicle_color = vehicle_in.vehicle_color

    db.commit()
    db.refresh(vehicle)
    return vehicle

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)) -> None:
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # If vehicle hasn't exited, free up the slot
    if vehicle.slot_id and not vehicle.exit_time:
        slot = db.query(ParkingSlot).filter(ParkingSlot.slot_id == vehicle.slot_id).first()
        if slot:
            slot.is_available = True
            
    # Need to clean up related payments first (basic cascade alternative)
    db.query(Payment).filter(Payment.vehicle_id == vehicle_id).delete()
    
    db.delete(vehicle)
    db.commit()
    return None
