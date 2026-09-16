from fastapi import APIRouter, Depends, HTTPException, status, Response
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import List, Any

from ..database import get_db
from ..models import ParkingSlot
from ..schemas import ParkingSlotCreate, ParkingSlotResponse

router = APIRouter(prefix="/api/v1/slots", tags=["slots"])

@router.get("/", response_model=List[ParkingSlotResponse])
def get_all_slots(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> Any:
    slots = db.query(ParkingSlot).offset(skip).limit(limit).all()
    return slots

@router.get("/available", response_model=List[ParkingSlotResponse])
def get_available_slots(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> Any:
    slots = db.query(ParkingSlot).filter(ParkingSlot.is_available == True, ParkingSlot.is_active == True).offset(skip).limit(limit).all()
    return slots

@router.get("/{slot_id}", response_model=ParkingSlotResponse)
def get_slot(slot_id: int, db: Session = Depends(get_db)) -> Any:
    slot = db.query(ParkingSlot).filter(ParkingSlot.slot_id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    return slot

@router.post("/", response_model=ParkingSlotResponse)
def create_slot(slot_in: ParkingSlotCreate, db: Session = Depends(get_db)) -> Any:
    # Check if slot number already exists
    existing_slot = db.query(ParkingSlot).filter(ParkingSlot.slot_number == slot_in.slot_number).first()
    if existing_slot:
        raise HTTPException(status_code=400, detail="Slot number already exists")
    
    slot_obj = ParkingSlot(
        slot_number=slot_in.slot_number,
        floor_number=slot_in.floor_number,
        location=slot_in.location,
        slot_type=slot_in.slot_type,
        slot_length=slot_in.slot_length,
        hourly_rate=slot_in.hourly_rate,
        daily_rate=slot_in.daily_rate
    )
    db.add(slot_obj)
    db.commit()
    db.refresh(slot_obj)
    return slot_obj

@router.put("/{slot_id}", response_model=ParkingSlotResponse)
def update_slot(slot_id: int, slot_in: ParkingSlotCreate, db: Session = Depends(get_db)) -> Any:
    slot_obj = db.query(ParkingSlot).filter(ParkingSlot.slot_id == slot_id).first()
    if not slot_obj:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    # Check if new slot number conflicts
    if slot_in.slot_number != slot_obj.slot_number:
        existing_slot = db.query(ParkingSlot).filter(ParkingSlot.slot_number == slot_in.slot_number).first()
        if existing_slot:
            raise HTTPException(status_code=400, detail="Slot number already exists")

    slot_obj.slot_number = slot_in.slot_number
    slot_obj.floor_number = slot_in.floor_number
    slot_obj.location = slot_in.location
    slot_obj.slot_type = slot_in.slot_type
    slot_obj.slot_length = slot_in.slot_length
    slot_obj.hourly_rate = slot_in.hourly_rate
    slot_obj.daily_rate = slot_in.daily_rate

    db.commit()
    db.refresh(slot_obj)
    return slot_obj

@router.delete("/{slot_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_slot(slot_id: int, db: Session = Depends(get_db)) -> None:
    slot_obj = db.query(ParkingSlot).filter(ParkingSlot.slot_id == slot_id).first()
    if not slot_obj:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    # Cannot delete if a vehicle is parked there
    if not slot_obj.is_available:
        raise HTTPException(status_code=400, detail="Cannot delete an occupied slot")

    db.delete(slot_obj)
    db.commit()
    return None
