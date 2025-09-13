# SevaSetu - Civic Issue Reporting Platform

SevaSetu is a modern, full-stack application designed to bridge the gap between citizens and local authorities. It empowers users to report civic issues (like potholes, streetlight outages, or waste management problems), which are then intelligently classified and routed to the appropriate municipal departments for resolution.

## 🚀 Live Demo

You can access the live, deployed application here:

**Citizen Portal:** https://seva-setu-beryl.vercel.app/

**Admin Portal:** https://seva-setu-zmqj.vercel.app/

## ✨ Features Included

### ✅ Citizen Portal
- Interactive location picker with maps
- Report submission with image upload
- User authentication and report tracking

### ✅ Admin Portal
- Complete departments CRUD management
- Location-based report filtering (10km radius)
- Advanced filtering (status, category, department)
- Analytics dashboard with KPIs

### ✅ Backend Features
- Department management API
- Geographic distance filtering
- AI-powered report classification
- User authentication with JWT

### ✅ Branding & UX
- Complete SEVASETU branding across all portals
- Government UX4G design standards
- Responsive design for all devices

## 🛠️ Tech Stack

| Service | Technology |
|---------|------------|
| Backend API | Python, FastAPI, Supabase (PostgreSQL), JWT |
| AI Model Server | Python, FastAPI, TensorFlow/Keras |
| Citizen Portal | React, TypeScript, Vite, Tailwind CSS, Shadcn/ui |
| Admin Portal | React, TypeScript, Vite, Tailwind CSS, Shadcn/ui |
| Database | Supabase (PostgreSQL) |
| Deployment | Vercel (Frontend), Railway / Render (Backend) |

## 📂 Project Structure

```
/
├── backend/           # FastAPI main server
├── ai_model_server/   # AI classification server
├── admin-portal/      # React admin dashboard
├── citizen-portal/    # React citizen interface
├── setup-sevasetu.bat # (Windows) Install all dependencies
├── start-sevasetu.bat # (Windows) Start all services
└── stop-sevasetu.bat  # (Windows) Stop all services
```

## ⚙️ Getting Started: Local Setup

Follow these steps to run the entire platform on your local machine.

### Prerequisites

- Python 3.10+ installed and in your PATH
- Node.js 16+ installed and in your PATH
- A Supabase account with a database configured
- Bun (optional, for frontend package management)

### 1. Clone & Configure

First, clone the repository and set up your environment variables.

```bash
git clone https://github.com/your-username/SevaSetu.git
cd SevaSetu
```

You must create a `.env` file in the `/backend` directory with your Supabase URL/Key, a secret key, and the local AI server URL.

```env
# backend/.env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
API_SECRET_KEY=generate_a_strong_secret_key
AI_API_URL=http://127.0.0.1:8001/api/classify
```

### 2. Install & Run

#### Quick Start (Windows Users)

Convenience scripts are provided for a one-command setup.

**Install all dependencies:**
```bash
setup-sevasetu.bat
```

**Start all services:**
```bash
start-sevasetu.bat
```

**Stop all services:**
```bash
stop-sevasetu.bat
```

#### Manual Setup (All Platforms)

Run each service in a separate terminal.

**Terminal 1: Backend API**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Terminal 2: AI Model Server**
```bash
cd ai_model_server
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

**Terminal 3: Admin Portal**
```bash
cd admin-portal
bun install  # or npm install
npm run dev
```

**Terminal 4: Citizen Portal**
```bash
cd citizen-portal
bun install  # or npm install
npm run dev
```

### Local Service URLs

| Service | Local URL | Description |
|---------|-----------|-------------|
| Backend API | http://localhost:8000 | Main API server |
| API Documentation | http://localhost:8000/docs | Interactive API docs |
| AI Model Server | http://localhost:8001 | AI classification service |
| Admin Portal | http://localhost:5173 | Government admin dashboard |
| Citizen Portal | http://localhost:5174 | Citizen reporting portal |

## 🌐 Deployment

This project is configured for easy deployment on modern hosting platforms.

- **Frontend Portals** (admin-portal, citizen-portal): Deployed on Vercel.
- **Backend Services** (backend, ai_model_server): Deployed on Railway or Render.

For a detailed, step-by-step guide on deploying this application, please see the `DEPLOYMENT.md` file.