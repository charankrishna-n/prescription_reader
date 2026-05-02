# RxAssist AI - Complete Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Install dependencies:**
```bash
cd c:\Users\chara\OneDrive\Documents\seai_final
pip install -r requirements.txt
```

2. **Start the backend:**
```bash
python api.py
```

Backend runs on: `http://localhost:8000`

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Start the frontend:**
```bash
npm run dev
```

Frontend runs on: `http://localhost:5173`

---

## 🔐 Login Credentials

### User Account
- **Email:** test@example.com
- **Password:** password123

### Doctor Account
- **Email:** doctor@example.com
- **Password:** password123

---

## 📡 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/doctor/login` - Doctor login

### Prescriptions
- `POST /predict` - Upload and analyze prescription

### Reminders
- `POST /api/reminders` - Add reminder
- `GET /api/reminders` - Get all reminders
- `PUT /api/reminders/{id}` - Update reminder
- `DELETE /api/reminders/{id}` - Delete reminder

### Health
- `GET /health` - Health check

---

## 🎨 UI Features

### User Dashboard
- ✅ Upload prescription images
- ✅ View extracted medicines
- ✅ Add medicines to tracker
- ✅ Add medicines to calendar
- ✅ Translate medicine instructions
- ✅ Language support (English, Tamil, Hindi)

### Doctor Panel
- ✅ View all patients
- ✅ Monitor adherence
- ✅ Track active medicines
- ✅ Search patients

---

## 🔧 Configuration

### Backend (api.py)
- Port: 8000
- CORS: Enabled for all origins
- JWT Secret: "your-secret-key-change-in-production"

### Frontend (vite.config.js)
- Port: 5173
- API Base URL: http://localhost:8000

---

## 📦 Project Structure

```
seai_final/
├── api.py                          # FastAPI backend
├── prescription_pipeline.py        # OCR pipeline
├── requirements.txt                # Python dependencies
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Header.jsx
    │   │   ├── MedicineCard.jsx
    │   │   └── ProtectedRoute.jsx
    │   ├── lib/
    │   │   ├── api.js              # Axios API client
    │   │   └── AuthContext.jsx     # Auth state management
    │   ├── pages/
    │   │   ├── LoginPage.jsx
    │   │   ├── DoctorLoginPage.jsx
    │   │   ├── Dashboard.jsx
    │   │   └── DoctorPanel.jsx
    │   ├── App.jsx                 # Main app with routing
    │   ├── main.jsx                # Entry point
    │   └── index.css               # Global styles
    ├── package.json
    ├── tailwind.config.js
    └── vite.config.js
```

---

## 🐛 Troubleshooting

### Backend Connection Error
- Ensure backend is running: `python api.py`
- Check port 8000 is not in use
- Verify CORS is enabled

### Login Failed
- Use demo credentials: test@example.com / password123
- Check backend is responding: `http://localhost:8000/health`

### Prescription Upload Error
- Ensure image format is PNG, JPG, or JPEG
- Check file size is reasonable
- Verify backend has access to Gemini API

---

## 🚀 Production Deployment

### Backend
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
npm run build
npm run preview
```

---

## 📝 Notes

- All data is stored in-memory (use database for production)
- JWT tokens expire after 24 hours
- Change SECRET_KEY in production
- Add proper error logging
- Implement rate limiting
- Add database persistence

---

## 📞 Support

For issues or questions, check:
1. Backend logs: `python api.py`
2. Frontend console: Browser DevTools
3. Network tab: Check API calls
4. Health endpoint: `http://localhost:8000/health`
