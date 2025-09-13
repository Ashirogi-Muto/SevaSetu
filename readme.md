# SEVASETU Platform - Quick Start Guide

## 🚀 Quick Start (One Command)

### First Time Setup
```bash
setup-sevasetu.bat
```
This will install all dependencies for backend, AI server, and both frontend portals.

### Start All Services
```bash
start-sevasetu.bat
```
This will start all 4 services in separate windows:
- Backend API (Port 8000)
- AI Model Server (Port 8001)
- Admin Portal (Port 5173)
- Citizen Portal (Port 5174)

### Stop All Services
```bash
stop-sevasetu.bat
```
This will gracefully stop all running services.

## 📋 Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| Backend API | http://localhost:8000 | Main API server |
| API Documentation | http://localhost:8000/docs | Interactive API docs |
| AI Model Server | http://localhost:8001 | AI classification service |
| Admin Portal | http://localhost:5173 | Government admin dashboard |
| Citizen Portal | http://localhost:5174 | Citizen reporting interface |

## 🔑 Default Credentials

**Admin Portal Login:**
- Email: `admin@sevasetu.gov`
- Password: `admin123`

## 📁 Project Structure

```
f:\hackathon\
├── backend/           # FastAPI main server
├── ai_model_server/   # AI classification server  
├── admin-portal/      # React admin dashboard
├── citizen-portal/    # React citizen interface
├── start-sevasetu.bat # Start all services
├── stop-sevasetu.bat  # Stop all services
└── setup-sevasetu.bat # Install dependencies
```

## 🛠️ Manual Commands (if needed)

### Backend API
```bash
cd f:\hackathon\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### AI Model Server
```bash
cd f:\hackathon\ai_model_server
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Admin Portal
```bash
cd f:\hackathon\admin-portal
npm run dev
```

### Citizen Portal
```bash
cd f:\hackathon\citizen-portal
npm run dev -- --port 5174
```

## ⚠️ Prerequisites

- Python 3.10+ installed and in PATH
- Node.js 16+ installed and in PATH
- Supabase account with database configured
- Environment variables set in backend/.env

## 🔧 Environment Setup

Make sure you have `.env` file in the backend directory with:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
API_SECRET_KEY=your_api_secret_key
AI_API_URL=http://127.0.0.1:8001/api/classify
```

## 🎯 Features Included

✅ **Citizen Portal**
- Interactive location picker with maps
- Report submission with image upload
- User authentication and report tracking

✅ **Admin Portal** 
- Complete departments CRUD management
- Location-based report filtering (10km radius)
- Advanced filtering (status, category, department)
- Analytics dashboard with KPIs

✅ **Backend Features**
- Department management API
- Geographic distance filtering
- AI-powered report classification
- User authentication with JWT

✅ **Branding**
- Complete SEVASETU branding across all portals
- Government UX4G design standards
- Responsive design for all devices