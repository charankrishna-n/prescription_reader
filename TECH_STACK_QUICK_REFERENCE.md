# RxAssist AI - Quick Reference Guide

## 🎯 Tech Stack Overview

### Frontend Stack
```
┌─────────────────────────────────────────┐
│         React 18.2 (UI Framework)       │
├─────────────────────────────────────────┤
│  Vite 5.0 (Build Tool)                  │
│  Tailwind CSS 3.3 (Styling)             │
│  Axios 1.6 (HTTP Client)                │
│  React Router 6.14 (Routing)            │
│  Lucide React (Icons)                   │
│  Framer Motion 10.16 (Animations)       │
│  Context API (State Management)         │
└─────────────────────────────────────────┘
```

### Backend Stack
```
┌─────────────────────────────────────────┐
│    FastAPI 0.104 (Web Framework)        │
├─────────────────────────────────────────┤
│  Uvicorn 0.24 (ASGI Server)             │
│  PyJWT 2.8 (Authentication)             │
│  Pydantic (Data Validation)             │
│  Google Gemini 2.5 Pro (AI/Vision)      │
│  PIL/Pillow (Image Processing)          │
│  In-Memory Storage (Database)           │
└─────────────────────────────────────────┘
```

### AI/ML Stack
```
┌─────────────────────────────────────────┐
│   Google Gemini 2.5 Pro API             │
├─────────────────────────────────────────┤
│  Multimodal Vision Model                │
│  Prescription OCR                       │
│  Structured JSON Output                 │
│  Confidence Scoring                     │
└─────────────────────────────────────────┘
```

---

## 🔧 Core Algorithms

### 1️⃣ JWT Authentication (HS256)
```
User Login
    ↓
Verify Credentials
    ↓
Generate JWT Token
    ↓
Store in localStorage
    ↓
Add to API Headers
    ↓
Verify on Backend
```

### 2️⃣ Real-Time Alarm System
```
Every 1 Second:
    ↓
Check Current Time (HH:MM)
    ↓
Compare with Alarm Times
    ↓
If Match Found:
    ├── Play Audio (800Hz, 2s)
    ├── Show Browser Notification
    ├── Display Visual Indicator
    └── Mark as Triggered (60s)
```

### 3️⃣ Prescription Analysis
```
Upload Image
    ↓
Send to Gemini API
    ↓
AI Extracts:
    ├── Medicine Name
    ├── Dosage
    ├── Frequency
    ├── Duration
    ├── Meal Context
    └── Confidence Score
    ↓
Display in UI
```

### 4️⃣ Camera Capture
```
Request Camera Access
    ↓
Stream to Video Element
    ↓
On Capture:
    ├── Get Canvas Context
    ├── Mirror Image
    ├── Draw Frame
    ├── Convert to Blob
    └── Create File Object
    ↓
Display Preview
```

### 5️⃣ State Management
```
AuthContext
├── User Info
├── JWT Token
├── Login/Logout
└── User Type

DataContext
├── Medicines
├── Calendar Items
├── Tracker Items
├── Notifications
├── Prescriptions
└── CRUD Operations
```

### 6️⃣ Data Persistence
```
localStorage
├── User Profile (JSON)
├── JWT Token
└── Prescription Images (Base64)

Backend In-Memory
├── Users
├── Medicines
├── Calendar Items
├── Tracker Items
└── Notifications
```

### 7️⃣ Adherence Calculation
```
Total Medicines = Count of all medicines
Medicines Taken = Count of checked items
Adherence % = (Medicines Taken / Total) × 100
```

### 8️⃣ Calendar Date Mapping
```
Get Month/Year
    ↓
Calculate Days in Month
    ↓
Calculate First Day
    ↓
Create 7-Column Grid
    ↓
Map Medicines to Dates
    ↓
Display with Badges
```

### 9️⃣ Notification Permission
```
Check API Available
    ↓
Check Permission Status
    ↓
If Not Granted:
    └── Request Permission
    ↓
If Granted:
    └── Show Notification
```

### 🔟 Audio Alert Generation
```
Create AudioContext
    ↓
Create Oscillator (800Hz)
    ↓
Create GainNode
    ↓
Connect Nodes
    ↓
Set Volume (0.3)
    ↓
Exponential Ramp Down (2s)
    ↓
Play Sound
```

---

## 📊 API Endpoints

### Authentication
```
POST /api/auth/login
POST /api/doctor/login
```

### Prescriptions
```
POST /predict                    (Upload & Analyze)
POST /api/prescriptions          (Save)
GET /api/prescriptions           (List)
GET /api/prescriptions/{id}      (Details)
DELETE /api/prescriptions/{id}   (Delete)
```

### Calendar
```
GET /api/calendar
POST /api/calendar
DELETE /api/calendar/{id}
```

### Tracker
```
GET /api/tracker
POST /api/tracker
PUT /api/tracker/{id}
DELETE /api/tracker/{id}
```

### Notifications
```
GET /api/notifications
POST /api/notifications
DELETE /api/notifications/{id}
```

### Other
```
GET /api/adherence
GET /health
```

---

## 🎨 Frontend Components

```
App.jsx
├── LoginTab
├── DoctorLoginTab
├── UploadTab (Camera + File Upload)
├── CalendarTab (Month View + Medicine List)
├── TrackerTab (Daily Checklist)
├── NotificationsTab (Alarm Management)
├── AdherenceTab (Statistics)
├── DoctorPanel (Patient Management)
└── ProfileTab (User Info + Prescriptions)
```

---

## 🔐 Security Features

| Feature | Technology | Details |
|---------|-----------|---------|
| Authentication | JWT HS256 | Token-based auth |
| CORS | FastAPI Middleware | Cross-origin control |
| Input Validation | Pydantic | Type & range checking |
| Password | In-Memory (Demo) | bcrypt in production |
| HTTPS | SSL/TLS | Encrypted transmission |
| Error Handling | Generic Messages | No sensitive info leak |

---

## 📈 Performance Features

### Frontend
- Code splitting with Vite
- Memoization with useCallback
- Lazy loading components
- Image optimization (Base64)
- Debounced search

### Backend
- Async/await operations
- In-memory caching
- Fast data retrieval
- Minimal dependencies

### Network
- Axios interceptors
- Request batching
- Browser caching
- Gzip compression

---

## 🚀 Deployment Stack

### Frontend
- Vite Build
- Netlify/Vercel
- Environment variables

### Backend
- Docker containers
- AWS/GCP/Azure
- Gunicorn + Nginx
- Environment variables

---

## 📦 Key Dependencies

### Frontend (11 packages)
```
react@18.2.0
react-dom@18.2.0
react-router-dom@6.14.0
axios@1.6.0
lucide-react@0.263.1
framer-motion@10.16.0
vite@5.0.0
tailwindcss@3.3.0
postcss@8.4.0
autoprefixer@10.4.0
```

### Backend (8 packages)
```
fastapi@0.104.1
uvicorn@0.24.0
python-multipart@0.0.6
PyJWT@2.8.1
pydantic@2.0.0
google-generativeai@0.3.0
pillow@10.0.0
python-dotenv@1.0.0
```

---

## 🎯 Technology Breakdown

| Category | Count | Technologies |
|----------|-------|--------------|
| Frontend Frameworks | 3 | React, Vite, Tailwind |
| Backend Frameworks | 2 | FastAPI, Uvicorn |
| AI/ML Services | 1 | Google Gemini |
| Browser APIs | 6 | getUserMedia, Canvas, Web Audio, Notification, localStorage, Fetch |
| Algorithms | 12 | JWT, Alarm, Prescription, Camera, State, Persistence, Audio, Calendar, Adherence, Validation, Permission, Form |
| UI Components | 24+ | Lucide Icons |
| HTTP Client | 1 | Axios |
| State Management | 1 | Context API |
| Styling | 1 | Tailwind CSS |
| **Total** | **40+** | **Modern Tech Stack** |

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                         │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    Upload      Calendar      Tracker
    Image       Medicine      Medicine
        │            │            │
        └────────────┼────────────┘
                     │
        ┌────────────▼────────────┐
        │   React Components      │
        │   (Context API State)   │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   Axios HTTP Client     │
        │   (JWT Interceptor)     │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   FastAPI Backend       │
        │   (Pydantic Validation) │
        └────────────┬────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    Gemini API   In-Memory    JWT Auth
    (Prescription) Storage    (Verify)
        │            │            │
        └────────────┼────────────┘
                     │
        ┌────────────▼────────────┐
        │   Response to Client    │
        │   (JSON Data)           │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   Update UI State       │
        │   Display Results       │
        └─────────────────────────┘
```

---

## 💡 Key Innovations

1. **Real-Time Alarm System**: Uses setInterval for precise time checking
2. **Camera Integration**: HTML5 Canvas for image capture and mirroring
3. **AI-Powered OCR**: Google Gemini for prescription analysis
4. **Context API**: Lightweight state management without Redux
5. **JWT Authentication**: Secure token-based authentication
6. **Web Audio API**: Programmatic alarm sound generation
7. **Browser Notifications**: Desktop alerts for medicine reminders
8. **localStorage Persistence**: Client-side data persistence
9. **Responsive Design**: Tailwind CSS for all screen sizes
10. **Modern Build Tool**: Vite for fast development and optimized builds

---

## 📚 Learning Resources

- **React**: https://react.dev
- **FastAPI**: https://fastapi.tiangolo.com
- **Tailwind CSS**: https://tailwindcss.com
- **Google Gemini**: https://ai.google.dev
- **JWT**: https://jwt.io
- **Web Audio API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
- **Canvas API**: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API

---

## 🎓 Conclusion

RxAssist AI is built with a modern, scalable tech stack combining:
- **Frontend**: React + Vite + Tailwind for responsive UI
- **Backend**: FastAPI + Uvicorn for high-performance APIs
- **AI**: Google Gemini for intelligent prescription analysis
- **Algorithms**: 12+ custom algorithms for core functionality
- **Security**: JWT authentication with CORS protection
- **Performance**: Optimized with caching, lazy loading, and async operations

This creates a robust, user-friendly medicine management and adherence tracking system!
