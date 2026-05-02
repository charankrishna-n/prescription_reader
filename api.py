"""
api.py - Complete RxAssist AI Backend
FastAPI backend for prescription extraction using Gemini 2.5 Pro.
"""

import os
import sys
import tempfile
import logging
from typing import Any, Dict
from datetime import datetime, timedelta

from fastapi import FastAPI, File, HTTPException, UploadFile, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
import jwt

from prescription_pipeline import run_pipeline, dosage_to_timing

# Suppress noisy multipart parser warnings
logging.getLogger("multipart.multipart").setLevel(logging.ERROR)
logging.getLogger("python_multipart.multipart").setLevel(logging.ERROR)

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

# Demo users
DEMO_USERS = {
    "test@example.com": "password123"
}

DEMO_DOCTORS = {
    "doctor@example.com": "password123"
}

# In-memory storage (replace with database in production)
calendar_items = {}
tracker_items = {}
notifications_list = {}
prescriptions = {}
calendar_id_counter = 1
tracker_id_counter = 1
prescription_id_counter = 1

# Pydantic Models
class LoginRequest(BaseModel):
    email: str
    password: str

class CalendarRequest(BaseModel):
    medicine_name: str
    dosage: str
    frequency: str
    duration: str
    start_date: str

class TrackerUpdateRequest(BaseModel):
    taken: bool

app = FastAPI(
    title="RxAssist AI - Prescription OCR API",
    description="AI-powered prescription analysis using Gemini 2.5 Pro",
    version="2.0.0",
)

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_token(email: str) -> str:
    """Create JWT token"""
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(authorization: str = Header(None)) -> str:
    """Verify JWT token from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("email")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except:
        raise HTTPException(status_code=401, detail="Invalid authorization header")


# ============================================
# AUTH ENDPOINTS
# ============================================

@app.post("/api/auth/login")
async def login(data: LoginRequest) -> Dict[str, Any]:
    """User login endpoint"""
    email = data.email
    password = data.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    if email in DEMO_USERS and DEMO_USERS[email] == password:
        token = create_token(email)
        return {"status": "success", "token": token, "email": email}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/api/doctor/login")
async def doctor_login(data: LoginRequest) -> Dict[str, Any]:
    """Doctor login endpoint"""
    email = data.email
    password = data.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    if email in DEMO_DOCTORS and DEMO_DOCTORS[email] == password:
        token = create_token(email)
        return {"status": "success", "token": token, "email": email}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")


# ============================================
# PRESCRIPTION ENDPOINTS
# ============================================

@app.post("/predict")
async def predict_prescription(file: UploadFile = File(...), authorization: str = Header(None)) -> Dict[str, Any]:
    """Upload a prescription image and receive structured medicine data."""
    email = verify_token(authorization)

    allowed = {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(allowed)}",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        result = run_pipeline(tmp_path, verbose=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")
    finally:
        os.unlink(tmp_path)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    medicines = []
    for med in result.get("parsed_medicines", []):
        quantity = med.get("quantity") or med.get("strength") or "N/A"
        when_to_take = med.get("when_to_take")
        if not when_to_take or when_to_take == "N/A":
            when_to_take = dosage_to_timing(med.get("dosage") or "")

        medicines.append({
            "name": med.get("medicine", "Unknown"),
            "dosage": quantity,
            "frequency": when_to_take,
            "duration": med.get("duration") or "N/A",
            "dosage_code": med.get("dosage") or "N/A",
            "meal_context": med.get("meal_context") or "N/A",
            "confidence": med.get("confidence", 0),
        })

    return {
        "status": "success",
        "filename": file.filename,
        "medicines": medicines,
        "raw_text": result.get("raw_text", ""),
    }


# ============================================
# CALENDAR ENDPOINTS
# ============================================

@app.post("/api/calendar")
async def add_to_calendar(data: dict, authorization: str = Header(None)) -> Dict[str, Any]:
    """Add medicine to calendar"""
    global calendar_id_counter
    email = verify_token(authorization)

    # Parse duration - handle "N/A" or extract number
    duration_str = data.get("duration", "1 days")
    try:
        if duration_str == "N/A" or not duration_str:
            duration_days = 1
        else:
            duration_days = int(duration_str.split()[0])
    except:
        duration_days = 1

    start_date = datetime.now()
    items = []
    
    for i in range(duration_days):
        date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        item = {
            "id": calendar_id_counter,
            "user_email": email,
            "medicine_name": data.get("medicine_name"),
            "dosage": data.get("dosage"),
            "frequency": data.get("frequency"),
            "date": date,
            "created_at": datetime.utcnow().isoformat(),
        }
        calendar_items[calendar_id_counter] = item
        items.append(item)
        calendar_id_counter += 1

    return {"status": "success", "items": items}


@app.get("/api/calendar")
async def get_calendar(authorization: str = Header(None)) -> Dict[str, Any]:
    """Get calendar items for user"""
    email = verify_token(authorization)
    user_items = [item for item in calendar_items.values() if item["user_email"] == email]
    return {"status": "success", "items": user_items}


@app.delete("/api/calendar/{item_id}")
async def delete_calendar_item(item_id: int, authorization: str = Header(None)) -> Dict[str, Any]:
    """Delete calendar item"""
    email = verify_token(authorization)

    if item_id not in calendar_items:
        raise HTTPException(status_code=404, detail="Item not found")

    item = calendar_items[item_id]
    if item["user_email"] != email:
        raise HTTPException(status_code=403, detail="Unauthorized")

    del calendar_items[item_id]
    return {"status": "success", "message": "Item deleted"}


# ============================================
# TRACKER ENDPOINTS
# ============================================

@app.post("/api/tracker")
async def add_to_tracker(data: dict, authorization: str = Header(None)) -> Dict[str, Any]:
    """Add item to tracker"""
    global tracker_id_counter
    email = verify_token(authorization)

    item = {
        "id": tracker_id_counter,
        "user_email": email,
        "medicine_name": data.get("medicine_name"),
        "dosage": data.get("dosage"),
        "frequency": data.get("frequency"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": data.get("time", ""),
        "taken": False,
        "created_at": datetime.utcnow().isoformat(),
    }
    tracker_items[tracker_id_counter] = item
    tracker_id_counter += 1

    return {"status": "success", "item": item}


@app.get("/api/tracker")
async def get_tracker(authorization: str = Header(None)) -> Dict[str, Any]:
    """Get tracker items for user"""
    email = verify_token(authorization)
    user_items = [item for item in tracker_items.values() if item["user_email"] == email]
    return {"status": "success", "items": user_items}


@app.put("/api/tracker/{item_id}")
async def update_tracker(item_id: int, data: TrackerUpdateRequest, authorization: str = Header(None)) -> Dict[str, Any]:
    """Update tracker item"""
    email = verify_token(authorization)

    if item_id not in tracker_items:
        raise HTTPException(status_code=404, detail="Item not found")

    item = tracker_items[item_id]
    if item["user_email"] != email:
        raise HTTPException(status_code=403, detail="Unauthorized")

    item["taken"] = data.taken
    return {"status": "success", "item": item}


@app.delete("/api/tracker/{item_id}")
async def delete_tracker_item(item_id: int, authorization: str = Header(None)) -> Dict[str, Any]:
    """Delete tracker item"""
    email = verify_token(authorization)

    if item_id not in tracker_items:
        raise HTTPException(status_code=404, detail="Item not found")

    item = tracker_items[item_id]
    if item["user_email"] != email:
        raise HTTPException(status_code=403, detail="Unauthorized")

    del tracker_items[item_id]
    return {"status": "success", "message": "Item deleted"}


# ============================================
# NOTIFICATIONS ENDPOINTS
# ============================================

@app.post("/api/notifications")
async def add_notification(data: dict, authorization: str = Header(None)) -> Dict[str, Any]:
    """Add notification for medicine"""
    email = verify_token(authorization)

    notification = {
        "user_email": email,
        "medicine_name": data.get("name"),
        "dosage": data.get("dosage"),
        "frequency": data.get("frequency"),
        "message": f"Reminder: Take {data.get('name')}",
        "created_at": datetime.utcnow().isoformat(),
    }
    notifications_list[len(notifications_list) + 1] = notification

    return {"status": "success", "notification": notification}


@app.get("/api/notifications")
async def get_notifications(authorization: str = Header(None)) -> Dict[str, Any]:
    """Get notifications for user"""
    email = verify_token(authorization)

    # Generate notifications from tracker items
    notifications = []
    for item in tracker_items.values():
        if item["user_email"] == email:
            if not item["taken"]:
                notifications.append({
                    "id": item["id"],
                    "type": "pending",
                    "medicine_name": item["medicine_name"],
                    "message": f"Time to take {item['medicine_name']}",
                    "time": item["time"] or "Now",
                })

    return {"status": "success", "notifications": notifications}


@app.delete("/api/notifications/{item_id}")
async def delete_notification(item_id: int, authorization: str = Header(None)) -> Dict[str, Any]:
    """Delete notification (by deleting associated tracker item)"""
    email = verify_token(authorization)

    if item_id not in tracker_items:
        raise HTTPException(status_code=404, detail="Item not found")

    item = tracker_items[item_id]
    if item["user_email"] != email:
        raise HTTPException(status_code=403, detail="Unauthorized")

    del tracker_items[item_id]
    return {"status": "success", "message": "Notification deleted"}


# ============================================
# ADHERENCE ENDPOINTS
# ============================================

@app.get("/api/adherence")
async def get_adherence(authorization: str = Header(None)) -> Dict[str, Any]:
    """Get adherence statistics for user"""
    email = verify_token(authorization)

    user_items = [item for item in tracker_items.values() if item["user_email"] == email]
    total = len(user_items)
    taken = len([item for item in user_items if item["taken"]])
    missed = total - taken
    percentage = int((taken / total * 100)) if total > 0 else 0

    return {
        "status": "success",
        "total_medicines": total,
        "taken_medicines": taken,
        "missed_medicines": missed,
        "percentage": percentage,
    }


# ============================================
# PRESCRIPTION HISTORY ENDPOINTS
# ============================================

@app.post("/api/prescriptions")
async def save_prescription(data: dict, authorization: str = Header(None)) -> Dict[str, Any]:
    """Save prescription with name and image"""
    global prescription_id_counter
    email = verify_token(authorization)

    prescription = {
        "id": prescription_id_counter,
        "user_email": email,
        "name": data.get("name", f"Prescription {prescription_id_counter}"),
        "image": data.get("image"),
        "medicines": data.get("medicines", []),
        "created_at": datetime.utcnow().isoformat(),
    }
    prescriptions[prescription_id_counter] = prescription
    prescription_id_counter += 1

    return {"status": "success", "prescription": prescription}


@app.get("/api/prescriptions")
async def get_prescriptions(authorization: str = Header(None)) -> Dict[str, Any]:
    """Get all prescriptions for user"""
    email = verify_token(authorization)
    user_prescriptions = [p for p in prescriptions.values() if p["user_email"] == email]
    return {"status": "success", "prescriptions": user_prescriptions}


@app.get("/api/prescriptions/{prescription_id}")
async def get_prescription(prescription_id: int, authorization: str = Header(None)) -> Dict[str, Any]:
    """Get specific prescription with all associated data"""
    email = verify_token(authorization)

    if prescription_id not in prescriptions:
        raise HTTPException(status_code=404, detail="Prescription not found")

    prescription = prescriptions[prescription_id]
    if prescription["user_email"] != email:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Get associated calendar items
    calendar = [item for item in calendar_items.values() 
                if item["user_email"] == email and item.get("prescription_id") == prescription_id]
    
    # Get associated tracker items
    tracker = [item for item in tracker_items.values() 
               if item["user_email"] == email and item.get("prescription_id") == prescription_id]
    
    # Get associated notifications
    notifications = [item for item in tracker_items.values() 
                     if item["user_email"] == email and item.get("prescription_id") == prescription_id and not item["taken"]]

    return {
        "status": "success",
        "prescription": prescription,
        "calendar": calendar,
        "tracker": tracker,
        "notifications": notifications,
    }


@app.delete("/api/prescriptions/{prescription_id}")
async def delete_prescription(prescription_id: int, authorization: str = Header(None)) -> Dict[str, Any]:
    """Delete prescription"""
    email = verify_token(authorization)

    if prescription_id not in prescriptions:
        raise HTTPException(status_code=404, detail="Prescription not found")

    prescription = prescriptions[prescription_id]
    if prescription["user_email"] != email:
        raise HTTPException(status_code=403, detail="Unauthorized")

    del prescriptions[prescription_id]
    return {"status": "success", "message": "Prescription deleted"}


# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "ocr_backend": "Gemini 2.5 Pro", "api_key_present": bool(os.getenv("GEMINI_API_KEY"))}


@app.post("/test-predict")
async def test_predict(authorization: str = Header(None)) -> Dict[str, Any]:
    """Test endpoint with mock data"""
    email = verify_token(authorization)
    
    return {
        "status": "success",
        "filename": "test.jpg",
        "medicines": [
            {
                "name": "Paracetamol",
                "dosage": "500mg",
                "frequency": "Morning & Night",
                "duration": "5 days",
                "dosage_code": "1-0-1",
                "meal_context": "After food",
                "confidence": 0.95,
            },
            {
                "name": "Amoxicillin",
                "dosage": "250mg",
                "frequency": "Morning, Afternoon & Night",
                "duration": "7 days",
                "dosage_code": "1-1-1",
                "meal_context": "Before food",
                "confidence": 0.92,
            },
        ],
        "raw_text": "Test prescription data",
    }


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
