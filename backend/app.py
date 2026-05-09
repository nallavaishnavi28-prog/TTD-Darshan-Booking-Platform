import os
import datetime
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
import jwt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({
        "success": True, 
        "message": "TTD Backend API is running! Please open the frontend HTML files in your browser to use the application."
    })

# Config
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/ttd")
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-change-me-in-prod")

client = MongoClient(MONGO_URI)
db = client.get_database()

# Collections
users_col = db.users
darshan_types_col = db.darshan_types
timeslots_col = db.timeslots
darshan_bookings_col = db.darshan_bookings
rooms_col = db.rooms
room_bookings_col = db.room_bookings
payments_col = db.payments
donations_col = db.donations

# --- JWT Decorator ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            current_user = users_col.find_one({'_id': ObjectId(data['user_id'])})
            if not current_user:
                raise Exception("User not found")
        except Exception as e:
            return jsonify({'success': False, 'message': 'Token is invalid or expired'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

# --- Auth Routes ---
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    required_fields = ['name', 'email', 'phone_number', 'password']
    if not all(k in data for k in required_fields):
        return jsonify({'success': False, 'message': 'Missing fields'}), 400
        
    if users_col.find_one({'email': data['email']}):
        return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
    hashed_pw = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    
    user_doc = {
        'name': data['name'],
        'email': data['email'],
        'phone_number': data['phone_number'],
        'country': data.get('country', 'India'),
        'password': hashed_pw.decode('utf-8'),
        'aadhar_number': data.get('aadhar_number'),
        'passport_number': data.get('passport_number'),
        'user_status': 'active',
        'created_at': datetime.datetime.utcnow().isoformat()
    }
    
    users_col.insert_one(user_doc)
    return jsonify({'success': True, 'message': 'User registered successfully'}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    if not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Email and password required'}), 400
        
    user = users_col.find_one({'email': data['email']})
    if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
    token = jwt.encode({
        'user_id': str(user['_id']),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, JWT_SECRET, algorithm="HS256")
    
    return jsonify({
        'success': True,
        'token': token,
        'user': {
            'name': user['name'],
            'email': user['email']
        }
    }), 200

@app.route('/auth/profile', methods=['GET'])
@token_required
def profile(current_user):
    user_data = {k: v for k, v in current_user.items() if k not in ['password', '_id']}
    return jsonify({'success': True, 'user': user_data}), 200

# --- Darshan Routes ---
@app.route('/darshan-types', methods=['GET'])
def get_darshan_types():
    types = list(darshan_types_col.find({}, {'_id': 0}))
    return jsonify({'success': True, 'types': types}), 200

@app.route('/timeslots', methods=['GET'])
def get_timeslots():
    date = request.args.get('date')
    darshan_type_id = request.args.get('darshan_type_id')
    slot_type = request.args.get('slot_type')
    
    query = {}
    if date: query['darshan_date'] = date
    if darshan_type_id: query['darshan_type_id'] = darshan_type_id
    if slot_type: query['slot_type'] = slot_type
    
    slots = list(timeslots_col.find(query, {'_id': 0}))
    
    # Add darshan name and price from darshan_types
    for slot in slots:
        dt = darshan_types_col.find_one({'darshan_type_id': slot['darshan_type_id']})
        if dt:
            slot['darshan_name'] = dt['darshan_name']
            slot['price'] = dt['price']
            
    return jsonify({'success': True, 'slots': slots}), 200

@app.route('/bookings/darshan', methods=['POST'])
@token_required
def book_darshan(current_user):
    data = request.json
    slot_id = data.get('time_slot_id')
    num_persons = data.get('number_of_persons', 1)
    
    slot = timeslots_col.find_one({'time_slot_id': slot_id})
    if not slot:
        return jsonify({'success': False, 'message': 'Slot not found'}), 404
        
    if slot['available_seats'] < num_persons:
        return jsonify({'success': False, 'message': 'Not enough seats available'}), 400
        
    dt = darshan_types_col.find_one({'darshan_type_id': slot['darshan_type_id']})
    total_amount = dt['price'] * num_persons
    
    booking_ref = f"DAR{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    booking_id = int(datetime.datetime.now().timestamp())
    
    booking = {
        'booking_id': booking_id,
        'user_id': str(current_user['_id']),
        'time_slot_id': slot_id,
        'number_of_persons': num_persons,
        'booking_type': data.get('booking_type', 'indian'),
        'total_amount': total_amount,
        'booking_status': 'pending',
        'booking_reference': booking_ref,
        'pilgrims': data.get('pilgrims', []),
        'created_at': datetime.datetime.utcnow().isoformat()
    }
    
    darshan_bookings_col.insert_one(booking)
    
    # Deduct seats
    timeslots_col.update_one(
        {'time_slot_id': slot_id},
        {'$inc': {'available_seats': -num_persons, 'booked_count': num_persons}}
    )
    
    return jsonify({
        'success': True,
        'booking_id': booking_id,
        'booking_reference': booking_ref,
        'total_amount': total_amount
    }), 201

@app.route('/bookings/darshan', methods=['GET'])
@token_required
def get_user_darshan_bookings(current_user):
    bookings = list(darshan_bookings_col.find({'user_id': str(current_user['_id'])}, {'_id': 0}))
    
    # Enrich data
    for b in bookings:
        slot = timeslots_col.find_one({'time_slot_id': b['time_slot_id']})
        if slot:
            b['darshan_date'] = slot['darshan_date']
            b['start_time'] = slot['start_time']
            b['end_time'] = slot['end_time']
            dt = darshan_types_col.find_one({'darshan_type_id': slot['darshan_type_id']})
            if dt: b['darshan_name'] = dt['darshan_name']
            
    # Sort descending by created_at
    bookings.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify({'success': True, 'bookings': bookings}), 200

@app.route('/bookings/darshan/<int:booking_id>/cancel', methods=['PUT'])
@token_required
def cancel_darshan(current_user, booking_id):
    booking = darshan_bookings_col.find_one({'booking_id': booking_id, 'user_id': str(current_user['_id'])})
    if not booking:
        return jsonify({'success': False, 'message': 'Booking not found'}), 404
        
    if booking['booking_status'] == 'cancelled':
        return jsonify({'success': False, 'message': 'Already cancelled'}), 400
        
    darshan_bookings_col.update_one(
        {'booking_id': booking_id},
        {'$set': {'booking_status': 'cancelled'}}
    )
    
    # Restore seats
    timeslots_col.update_one(
        {'time_slot_id': booking['time_slot_id']},
        {'$inc': {'available_seats': booking['number_of_persons'], 'booked_count': -booking['number_of_persons']}}
    )
    
    return jsonify({'success': True, 'message': 'Booking cancelled'}), 200

# --- Accommodation Routes ---
@app.route('/accommodation', methods=['GET'])
def get_rooms():
    # In a real app, check date availability in room_bookings. 
    # For now, just return all active rooms.
    rooms = list(rooms_col.find({}, {'_id': 0}))
    return jsonify({'success': True, 'rooms': rooms}), 200

@app.route('/bookings/room', methods=['POST'])
@token_required
def book_room(current_user):
    data = request.json
    room_id = data.get('room_id')
    cin = data.get('check_in_date')
    cout = data.get('check_out_date')
    
    if not all([room_id, cin, cout]):
        return jsonify({'success': False, 'message': 'Missing data'}), 400
        
    room = rooms_col.find_one({'room_id': room_id})
    if not room:
        return jsonify({'success': False, 'message': 'Room not found'}), 404
        
    cin_d = datetime.datetime.strptime(cin, "%Y-%m-%d")
    cout_d = datetime.datetime.strptime(cout, "%Y-%m-%d")
    nights = (cout_d - cin_d).days
    if nights <= 0:
        return jsonify({'success': False, 'message': 'Invalid dates'}), 400
        
    total_amount = room['price_per_day'] * nights
    room_booking_id = int(datetime.datetime.now().timestamp())
    
    booking = {
        'room_booking_id': room_booking_id,
        'user_id': str(current_user['_id']),
        'room_id': room_id,
        'booking_id': data.get('booking_id'), # Linked darshan
        'check_in_date': cin,
        'check_out_date': cout,
        'nights': nights,
        'total_amount': total_amount,
        'booking_status': 'pending',
        'created_at': datetime.datetime.utcnow().isoformat()
    }
    
    room_bookings_col.insert_one(booking)
    
    return jsonify({
        'success': True,
        'room_booking_id': room_booking_id,
        'total_amount': total_amount,
        'nights': nights
    }), 201

@app.route('/bookings/room', methods=['GET'])
@token_required
def get_user_room_bookings(current_user):
    bookings = list(room_bookings_col.find({'user_id': str(current_user['_id'])}, {'_id': 0}))
    
    for b in bookings:
        room = rooms_col.find_one({'room_id': b['room_id']})
        if room:
            b['room_type'] = room['room_type']
            
    bookings.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify({'success': True, 'bookings': bookings}), 200

@app.route('/bookings/room/<int:booking_id>/cancel', methods=['PUT'])
@token_required
def cancel_room(current_user, booking_id):
    booking = room_bookings_col.find_one({'room_booking_id': booking_id, 'user_id': str(current_user['_id'])})
    if not booking:
        return jsonify({'success': False, 'message': 'Booking not found'}), 404
        
    if booking['booking_status'] == 'cancelled':
        return jsonify({'success': False, 'message': 'Already cancelled'}), 400
        
    room_bookings_col.update_one(
        {'room_booking_id': booking_id},
        {'$set': {'booking_status': 'cancelled'}}
    )
    return jsonify({'success': True, 'message': 'Booking cancelled'}), 200

# --- Payment & Donations ---
@app.route('/payment', methods=['POST'])
@token_required
def process_payment(current_user):
    data = request.json
    amount = data.get('amount')
    method = data.get('payment_method')
    
    if not method or amount is None:
        return jsonify({'success': False, 'message': 'Invalid payment data'}), 400
        
    txn_id = f"TXN{int(datetime.datetime.now().timestamp())}"
    
    payment = {
        'transaction_id': txn_id,
        'user_id': str(current_user['_id']),
        'booking_id': data.get('booking_id'),
        'room_booking_id': data.get('room_booking_id'),
        'amount': amount,
        'payment_method': method,
        'payment_status': 'success',
        'payment_date': datetime.datetime.utcnow().isoformat()
    }
    
    payments_col.insert_one(payment)
    
    # Update status
    if data.get('booking_id'):
        darshan_bookings_col.update_one(
            {'booking_id': data.get('booking_id')},
            {'$set': {'booking_status': 'confirmed'}}
        )
    if data.get('room_booking_id'):
        room_bookings_col.update_one(
            {'room_booking_id': data.get('room_booking_id')},
            {'$set': {'booking_status': 'confirmed'}}
        )
        
    return jsonify({'success': True, 'transaction_id': txn_id}), 201

@app.route('/payment', methods=['GET'])
@token_required
def get_payments(current_user):
    payments = list(payments_col.find({'user_id': str(current_user['_id'])}, {'_id': 0}))
    
    for p in payments:
        if p.get('booking_id'):
            b = darshan_bookings_col.find_one({'booking_id': p['booking_id']})
            if b:
                s = timeslots_col.find_one({'time_slot_id': b['time_slot_id']})
                if s: p['darshan_date'] = s['darshan_date']
                dt = darshan_types_col.find_one({'darshan_type_id': s['darshan_type_id'] if s else None})
                if dt: p['darshan_name'] = dt['darshan_name']
        if p.get('room_booking_id'):
            rb = room_bookings_col.find_one({'room_booking_id': p['room_booking_id']})
            if rb:
                p['check_in_date'] = rb['check_in_date']
                r = rooms_col.find_one({'room_id': rb['room_id']})
                if r: p['room_type'] = r['room_type']
                
    payments.sort(key=lambda x: x.get('payment_date', ''), reverse=True)
    return jsonify({'success': True, 'payments': payments}), 200

@app.route('/donation', methods=['POST'])
@token_required
def make_donation(current_user):
    data = request.json
    amount = data.get('amount')
    dtype = data.get('donation_type')
    
    if not amount or not dtype:
        return jsonify({'success': False, 'message': 'Amount and type required'}), 400
        
    donation_id = int(datetime.datetime.now().timestamp())
    
    donation = {
        'donation_id': donation_id,
        'user_id': str(current_user['_id']),
        'donation_type': dtype,
        'amount': amount,
        'remarks': data.get('remarks'),
        'donation_date': datetime.datetime.utcnow().isoformat()
    }
    
    donations_col.insert_one(donation)
    
    # Record payment for donation
    txn_id = f"TXN{int(datetime.datetime.now().timestamp())}"
    payments_col.insert_one({
        'transaction_id': txn_id,
        'user_id': str(current_user['_id']),
        'donation_id': donation_id,
        'amount': amount,
        'payment_method': data.get('payment_method', 'upi'),
        'payment_status': 'success',
        'payment_date': datetime.datetime.utcnow().isoformat()
    })
    
    return jsonify({'success': True, 'donation_id': donation_id, 'transaction_id': txn_id}), 201

@app.route('/donation', methods=['GET'])
@token_required
def get_donations(current_user):
    donations = list(donations_col.find({'user_id': str(current_user['_id'])}, {'_id': 0}))
    donations.sort(key=lambda x: x.get('donation_date', ''), reverse=True)
    return jsonify({'success': True, 'donations': donations}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
