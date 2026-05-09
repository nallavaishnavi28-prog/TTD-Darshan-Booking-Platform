import os
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/ttd")
client = MongoClient(MONGO_URI)
db = client.get_database()

def seed_db():
    print("Seeding database...")
    
    # 1. Darshan Types
    darshan_types = [
        {"darshan_type_id": "sarva", "darshan_name": "Sarva Darshan", "price": 0, "description": "Free Darshan"},
        {"darshan_type_id": "special", "darshan_name": "Special Entry Darshan", "price": 300, "description": "Rs. 300 Darshan"},
        {"darshan_type_id": "vip", "darshan_name": "VIP Break Darshan", "price": 10000, "description": "Exclusive Access"}
    ]
    
    if db.darshan_types.count_documents({}) == 0:
        db.darshan_types.insert_many(darshan_types)
        print("Inserted darshan types.")
        
    # 2. Timeslots (Create for next 7 days)
    if db.timeslots.count_documents({}) == 0:
        slots = []
        slot_id = 1
        today = datetime.date.today()
        
        for i in range(7):
            d = today + datetime.timedelta(days=i)
            d_str = d.strftime("%Y-%m-%d")
            
            # Sarva
            slots.append({"time_slot_id": slot_id, "darshan_type_id": "sarva", "darshan_date": d_str, "start_time": "08:00:00", "end_time": "12:00:00", "max_capacity": 500, "available_seats": 500, "booked_count": 0, "slot_type": "indian"})
            slot_id += 1
            slots.append({"time_slot_id": slot_id, "darshan_type_id": "sarva", "darshan_date": d_str, "start_time": "14:00:00", "end_time": "18:00:00", "max_capacity": 500, "available_seats": 500, "booked_count": 0, "slot_type": "indian"})
            slot_id += 1
            
            # Special
            slots.append({"time_slot_id": slot_id, "darshan_type_id": "special", "darshan_date": d_str, "start_time": "09:00:00", "end_time": "11:00:00", "max_capacity": 200, "available_seats": 200, "booked_count": 0, "slot_type": "indian"})
            slot_id += 1
            slots.append({"time_slot_id": slot_id, "darshan_type_id": "special", "darshan_date": d_str, "start_time": "13:00:00", "end_time": "15:00:00", "max_capacity": 200, "available_seats": 200, "booked_count": 0, "slot_type": "nri"})
            slot_id += 1
            
            # VIP
            slots.append({"time_slot_id": slot_id, "darshan_type_id": "vip", "darshan_date": d_str, "start_time": "06:00:00", "end_time": "07:30:00", "max_capacity": 50, "available_seats": 50, "booked_count": 0, "slot_type": "indian"})
            slot_id += 1
            
        db.timeslots.insert_many(slots)
        print("Inserted timeslots.")
        
    # 3. Rooms
    rooms = [
        {"room_id": "std_1", "room_type": "Standard Room", "capacity": 2, "price_per_day": 500, "is_available": True},
        {"room_id": "dlx_1", "room_type": "Deluxe Room", "capacity": 3, "price_per_day": 1500, "is_available": True},
        {"room_id": "sui_1", "room_type": "Suite Room", "capacity": 4, "price_per_day": 3000, "is_available": True}
    ]
    
    if db.rooms.count_documents({}) == 0:
        db.rooms.insert_many(rooms)
        print("Inserted rooms.")
        
    print("Database seeding completed.")

if __name__ == '__main__':
    seed_db()
