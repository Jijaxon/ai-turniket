# 🚪 AI Turniket System — Face Recognition Access Control

A production-ready full-stack system that uses **AI-powered face recognition** to
grant or deny physical access in real time.

---

## 🏗 Architecture

```
┌─────────────────────┐       REST/JSON        ┌──────────────────────┐
│   React Frontend    │ ◄──────────────────────► │  FastAPI Backend     │
│   (Vite + Redux)    │                          │  (Python 3.11)       │
└─────────────────────┘                          └──────────┬───────────┘
                                                            │
                                               ┌────────────▼────────────┐
                                               │  face_recognition lib   │
                                               │  (dlib / OpenCV)        │
                                               └────────────┬────────────┘
                                                            │
                                               ┌────────────▼────────────┐
                                               │   SQLite / PostgreSQL   │
                                               └─────────────────────────┘
```

---

## 📋 Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| Node.js | 18+ |
| CMake | Any (for dlib) |
| C++ build tools | gcc / MSVC |

### macOS
```bash
brew install cmake
```

### Ubuntu / Debian
```bash
sudo apt-get install -y build-essential cmake libopenblas-dev liblapack-dev
```

### Windows
Install Visual Studio Build Tools with C++ workload.

---

## 🚀 Quick Start

### 1. Clone & setup backend

```bash
cd backend

# Copy env file
cp .env.example .env

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies (dlib compiles from source – may take 5 min)
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --port 8000
```

The API will be available at **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

### 2. Setup frontend

```bash
cd frontend

# Copy env file
cp .env.example .env

npm install
npm run dev
```

The dashboard will be at **http://localhost:5173**

### 3. Login

Default credentials:
- **Username:** `admin`
- **Password:** `admin123`

> ⚠️ Change the password in `.env` before deploying to production.

---

## 📡 API Reference

### Authentication

```
POST /auth/login
Content-Type: application/json

{ "username": "admin", "password": "admin123" }

→ { "access_token": "eyJ...", "token_type": "bearer", "expires_in": 86400 }
```

### Register a user

```
POST /users/add
Authorization: Bearer <token>

{
  "name": "John Doe",
  "email": "john@example.com",
  "department": "Engineering",
  "face_image": "data:image/jpeg;base64,/9j/4AAQ..."
}
```

### Face recognition

```
POST /recognize-face
Content-Type: application/json

{ "image": "data:image/jpeg;base64,...", "device_id": "gate-1" }

# Allowed response:
{
  "status": "allowed",
  "user_id": 1,
  "name": "John Doe",
  "confidence": 0.92,
  "reason": null,
  "timestamp": "2024-01-15T10:30:00"
}

# Denied response:
{
  "status": "denied",
  "user_id": null,
  "name": null,
  "confidence": 0.31,
  "reason": "Unknown person – face not recognised",
  "timestamp": "2024-01-15T10:30:01"
}
```

### Access logs

```
GET /logs/               # All logs (paginated)
GET /logs/today          # Today's logs
GET /logs/stats          # Dashboard statistics
GET /logs/daily-report   # 7-day breakdown
GET /logs/export/csv     # CSV export
```

---

## 🧠 Face Recognition Details

| Parameter | Value | Notes |
|-----------|-------|-------|
| Library | `face_recognition` (dlib) | 128-d face encodings |
| Detection model | HOG | Fast CPU inference |
| Distance threshold | 0.55 | Lower = stricter |
| Cache | In-memory dict | Auto-reloaded on user changes |
| Max image size | 5 MB | Configurable |
| Typical latency | < 500 ms | On modern CPU |

The pipeline:
1. Decode base64 image → OpenCV BGR array
2. Resize to max 640px width (speed optimisation)
3. Convert BGR → RGB (required by `face_recognition`)
4. Detect face locations (HOG model)
5. Extract 128-d encoding
6. Compare against cached encodings using Euclidean distance
7. Return best match if distance ≤ threshold

---

## 🗄 Database Schema

```sql
-- Registered users
CREATE TABLE users (
    id            INTEGER PRIMARY KEY,
    name          VARCHAR(100),
    email         VARCHAR(200) UNIQUE,
    department    VARCHAR(100),
    is_active     BOOLEAN DEFAULT TRUE,
    face_encoding TEXT,          -- JSON array of 128 floats
    created_at    DATETIME
);

-- Every recognition attempt
CREATE TABLE access_logs (
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id),
    timestamp   DATETIME,
    status      ENUM('allowed','denied'),
    confidence  FLOAT,
    reason      VARCHAR(200),
    ip_address  VARCHAR(50),
    device_id   VARCHAR(100)
);

-- Admin accounts
CREATE TABLE admin_users (
    id              INTEGER PRIMARY KEY,
    username        VARCHAR(50) UNIQUE,
    hashed_password VARCHAR(200),
    is_active       BOOLEAN
);
```

---

## 🐘 Switch to PostgreSQL

1. Install PostgreSQL and create a database:

```sql
CREATE USER turniket_user WITH PASSWORD 'strongpassword';
CREATE DATABASE turniket_db OWNER turniket_user;
```

2. Update `.env`:

```
DATABASE_URL=postgresql://turniket_user:strongpassword@localhost:5432/turniket_db
```

3. Restart the backend.

---

## 🔐 Security Notes

- JWT tokens expire after 24h by default
- Passwords are hashed with bcrypt
- Image size is limited to prevent DoS
- CORS is restricted to the frontend origin
- Recognition endpoint is intentionally public (kiosk/hardware use)
- Admin endpoints require a valid JWT

---

## 📦 Project Structure

```
turniket/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app factory
│   │   ├── config.py                  # Settings (pydantic-settings)
│   │   ├── database/
│   │   │   ├── db.py                  # Engine & session
│   │   │   └── models.py              # ORM models
│   │   ├── schemas/
│   │   │   ├── user.py                # Pydantic user schemas
│   │   │   └── log.py                 # Pydantic log/auth schemas
│   │   ├── services/
│   │   │   ├── face_recognition_service.py  # AI core
│   │   │   └── auth_service.py        # JWT + admin auth
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── recognition.py
│   │   │   └── logs.py
│   │   ├── utils/
│   │   │   └── image_processing.py    # OpenCV helpers
│   │   └── core/
│   │       └── security.py            # JWT utilities
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── pages/                     # LoginPage, Dashboard, Recognition, Users, Logs
    │   ├── components/                # Layout, sidebar
    │   ├── store/slices/              # Redux slices
    │   └── utils/api.js               # Axios instance
    ├── vite.config.js
    └── package.json
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request

---

## 📄 License

MIT License — feel free to use for educational and commercial projects.
