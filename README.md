# 🛕 TTD Darshan Booking Platform

A comprehensive, full-stack booking system for Tirumala Tirupati Devasthanams (TTD) services. This platform allows pilgrims to book Darshan slots, reserve guest house accommodation, and make e-Hundi donations through a secure and modern interface.

## 🚀 Live Demo
- **Frontend:** [https://ttd-darshan-booking-platform-4.onrender.com](https://ttd-darshan-booking-platform-4.onrender.com)
- **Backend API:** [https://ttd-darshan-booking-platform-3.onrender.com](https://ttd-darshan-booking-platform-3.onrender.com)

## ✨ Features
- **Secure Authentication:** JWT-based login and registration system with Aadhar/Passport validation.
- **Darshan Booking:** Real-time slot selection and pilgrim detail management for various darshan types (Sarva, Special, VIP).
- **Accommodation:** Browse and book guest house rooms with automated check-in/check-out tracking.
- **Donations (e-Hundi):** Support for multiple TTD trusts including Annaprasadam and Go Samrakshana.
- **Dynamic Dashboard:** Personalized user overview for tracking bookings, payments, and profile details.
- **Cloud Database:** Integrated with MongoDB Atlas for scalable and reliable data storage.

## 🛠️ Tech Stack
- **Frontend:** HTML5, CSS3 (Vanilla), JavaScript (ES6+), Google Fonts (Poppins, Cinzel)
- **Backend:** Python, Flask, PyMongo, BCrypt (Hashing), PyJWT
- **Database:** MongoDB Atlas (Cloud)
- **Deployment:** Render (Web Service & Static Site)

## 📂 Project Structure
```text
Darshan Booking System/
├── backend/
│   ├── app.py             # Flask API Server
│   ├── init_db.py         # Database Seeding Script
│   └── requirements.txt   # Python Dependencies
├── frontend/
│   ├── index.html         # Landing Page
│   ├── login.html         # User Authentication
│   ├── dashboard.html     # User Profile & History
│   ├── darshan.html       # Ticket Booking Flow
│   ├── accommodation.html # Room Reservation Flow
│   ├── donation.html      # e-Hundi Donations
│   ├── css/style.css      # Core Design System
│   └── js/                # Frontend Logic (API calls, Nav)
└── render.yaml            # Render Deployment Blueprint
```

## ⚙️ Local Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/nallavaishnavi28-prog/TTD-Darshan-Booking-Platform.git
   ```
2. **Install Dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. **Configure Environment:**
   Create a `.env` file in the `backend/` folder with your `MONGO_URI` and `JWT_SECRET`.
4. **Seed Database:**
   ```bash
   python init_db.py
   ```
5. **Run Application:**
   ```bash
   python app.py
   ```

---
*ॐ नमो वेङ्कटेशाय 🙏*
