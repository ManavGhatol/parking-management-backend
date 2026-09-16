import sys
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import ParkingSlot, SlotType

# Create tables
Base.metadata.create_all(bind=engine)

def seed_slots():
    db = SessionLocal()
    
    # Check current slot count
    current_count = db.query(ParkingSlot).count()
    if current_count >= 14:
        print(f"Slots already seeded. Total: {current_count}")
        return

    # Delete existing slots if they are fewer than 14 just for a clean re-seed (optional) or just add what's missing.
    # It's easier to just add new slots. Let's seed exactly 14 slots.
    slots_to_add = [
        ParkingSlot(slot_number="A1", floor_number=1, location="Zone A", slot_type=SlotType.regular, slot_length=5.0, hourly_rate=5.0, daily_rate=40.0),
        ParkingSlot(slot_number="A2", floor_number=1, location="Zone A", slot_type=SlotType.regular, slot_length=5.0, hourly_rate=5.0, daily_rate=40.0),
        ParkingSlot(slot_number="A3", floor_number=1, location="Zone A", slot_type=SlotType.regular, slot_length=5.0, hourly_rate=5.0, daily_rate=40.0),
        ParkingSlot(slot_number="A4", floor_number=1, location="Zone A", slot_type=SlotType.regular, slot_length=5.0, hourly_rate=5.0, daily_rate=40.0),
        ParkingSlot(slot_number="A5", floor_number=1, location="Zone A", slot_type=SlotType.regular, slot_length=5.0, hourly_rate=5.0, daily_rate=40.0),
        ParkingSlot(slot_number="B1", floor_number=1, location="Zone B", slot_type=SlotType.compact, slot_length=4.0, hourly_rate=4.0, daily_rate=30.0),
        ParkingSlot(slot_number="B2", floor_number=1, location="Zone B", slot_type=SlotType.compact, slot_length=4.0, hourly_rate=4.0, daily_rate=30.0),
        ParkingSlot(slot_number="B3", floor_number=1, location="Zone B", slot_type=SlotType.compact, slot_length=4.0, hourly_rate=4.0, daily_rate=30.0),
        ParkingSlot(slot_number="B4", floor_number=1, location="Zone B", slot_type=SlotType.compact, slot_length=4.0, hourly_rate=4.0, daily_rate=30.0),
        ParkingSlot(slot_number="B5", floor_number=1, location="Zone B", slot_type=SlotType.compact, slot_length=4.0, hourly_rate=4.0, daily_rate=30.0),
        ParkingSlot(slot_number="C1", floor_number=2, location="Zone C", slot_type=SlotType.handicapped, slot_length=6.0, hourly_rate=5.0, daily_rate=40.0),
        ParkingSlot(slot_number="C2", floor_number=2, location="Zone C", slot_type=SlotType.handicapped, slot_length=6.0, hourly_rate=5.0, daily_rate=40.0),
        ParkingSlot(slot_number="C3", floor_number=2, location="Zone C", slot_type=SlotType.handicapped, slot_length=6.0, hourly_rate=5.0, daily_rate=40.0),
        ParkingSlot(slot_number="C4", floor_number=2, location="Zone C", slot_type=SlotType.handicapped, slot_length=6.0, hourly_rate=5.0, daily_rate=40.0),
    ]
    
    # We will just iterate and add if not exists
    added = 0
    for slot in slots_to_add:
        if not db.query(ParkingSlot).filter_by(slot_number=slot.slot_number).first():
            db.add(slot)
            added += 1
            
    db.commit()
    print("Successfully seeded parking slots.")

if __name__ == "__main__":
    seed_slots()
