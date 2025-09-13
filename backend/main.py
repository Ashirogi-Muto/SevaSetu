import os
import os
import json
import uuid
import math
from datetime import datetime
from collections import Counter, defaultdict
from dotenv import load_dotenv
from typing import Optional, List, Dict
from enum import Enum

# FastAPI Imports
from fastapi import FastAPI, APIRouter, HTTPException, Form, UploadFile, File, Security, Query, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Pydantic Imports
from pydantic import BaseModel, Field, EmailStr

# Supabase Imports
from supabase import create_client, Client

# Local Module Imports
from ai_service import classify_report_with_real_ai
from auth_service import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    decode_access_token
)


# --- 1. Core Setup ---
load_dotenv()
# (Keep all your existing env variable loading)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
AI_API_URL = os.getenv("AI_API_URL")

if not all([SUPABASE_URL, SUPABASE_KEY, API_SECRET_KEY, AI_API_URL]):
    raise RuntimeError("All required environment variables must be set.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# --- Helper Functions ---
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    # Radius of earth in kilometers
    r = 6371
    distance = r * c
    
    return distance


# --- Security Middleware ---
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


# --- 2. Security & Authentication Setup ---
# Simple API Key for general service protection
api_key_header = APIKeyHeader(name="X-API-Key")
async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

# OAuth2 / JWT for User Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency to get the current user from a JWT.
    This will be used to protect user-specific routes.
    """
    email = decode_access_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    # Fetch the user from the database
    user_res = supabase.table("users").select("id, email, name").eq("email", email).single().execute()
    if not user_res.data:
        raise HTTPException(status_code=401, detail="User not found")
        
    return user_res.data


# --- 3. Schemas: Pydantic Data Models ---
# (Keep all existing schemas: ReportStatus, ReportData, etc.)
# ...

# --- NEW: Auth Schemas ---
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class ReportStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"

class ReportData(BaseModel):
    description: str = Field(..., min_length=10, max_length=500)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)

class ReportResponse(BaseModel):
    id: int
    created_at: datetime
    description: str
    latitude: float
    longitude: float
    category: Optional[str] = None
    status: ReportStatus
    image_urls: List[str] = []
    department_id: Optional[int] = None
    user_id: Optional[int] = None # Added user_id

class ReportStatusUpdate(BaseModel):
    status: ReportStatus

class AnalyticsData(BaseModel):
    total_reports: int
    reports_by_category: Dict[str, int]
    reports_by_status: Dict[str, int]

# Dashboard Models
class RecentReport(BaseModel):
    id: str
    issue: str
    status: str
    time: str

class DepartmentPerformance(BaseModel):
    name: str
    resolved: int
    total: int
    rate: float

class KpiData(BaseModel):
    totalReports: int
    reportsResolved: int
    avgResolutionTime: str
    activeDepartments: int

class DashboardData(BaseModel):
    kpis: KpiData
    recentReports: List[RecentReport]
    departmentPerformance: List[DepartmentPerformance]

# Department Models
class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr

class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None

class DepartmentResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime


# --- 4. API Routers ---
# --- NEW: Auth Router ---
auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@auth_router.post("/register", status_code=201)
def register_user(user: UserCreate):
    # Check if user already exists
    existing_user = supabase.table("users").select("id").eq("email", user.email).execute()
    if existing_user.data:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = get_password_hash(user.password)
    new_user_data = {
        "name": user.name,
        "email": user.email,
        "hashed_password": hashed_password
    }
    
    insert_res = supabase.table("users").insert(new_user_data).execute()
    if not insert_res.data:
        raise HTTPException(status_code=500, detail="Could not create user account.")
        
    return {"message": "User registered successfully"}

@auth_router.post("/login", response_model=Token)
def login_for_access_token(form_data: UserLogin):
    user_res = supabase.table("users").select("*").eq("email", form_data.email).single().execute()
    if not user_res.data:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    user = user_res.data
    if not verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    access_token = create_access_token(data={"sub": user['email']})
    return {"access_token": access_token, "token_type": "bearer"}


# --- Reports Router (Now with User Authentication) ---
reports_router = APIRouter(prefix="/api/reports", tags=["Reports"])

@reports_router.post("/", status_code=201, response_model=ReportResponse)
async def submit_report(
    report_data_json: str = Form(...),
    images: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user) # <-- This protects the route
):
    try:
        report_data = ReportData.parse_raw(report_data_json)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {e}")

    # Step 1: Save the report with the user's ID
    initial_db_data = report_data.model_dump()
    initial_db_data['category'] = "Classification Pending"
    initial_db_data['user_id'] = current_user['id'] # <-- Link report to the user
    
    report_res = supabase.table("reports").insert(initial_db_data).execute()
    if not report_res.data:
        raise HTTPException(status_code=500, detail="Failed to save initial report.")
    
    # ... (Keep the rest of the image upload and AI logic the same)
    report_id = report_res.data[0]['id']
    
    uploaded_image_urls = []
    for image in images:
        file_ext = image.filename.split('.')[-1]
        file_name = f"{report_id}_{uuid.uuid4()}.{file_ext}"
        try:
            file_content = await image.read()
            supabase.storage.from_("report-images").upload(file=file_content, path=file_name, file_options={"content-type": image.content_type})
            public_url = supabase.storage.from_("report-images").get_public_url(file_name)
            uploaded_image_urls.append(public_url)
            supabase.table("report_images").insert({"report_id": report_id, "image_url": public_url}).execute()
        except Exception as e:
            print(f"ERROR: Failed to upload image {image.filename}: {e}")
            continue
    
    ai_category = await classify_report_with_real_ai(report_data.description, uploaded_image_urls)
    
    department_id = None
    try:
        mapping_res = supabase.table("category_department_mapping").select("department_id").eq("category_name", ai_category).single().execute()
        if mapping_res.data:
            department_id = mapping_res.data['department_id']
    except Exception as e:
        print(f"WARNING: No routing rule for category '{ai_category}'. Error: {e}")

    update_data = {"category": ai_category, "department_id": department_id}
    update_res = supabase.table("reports").update(update_data).eq("id", report_id).execute()
    
    if not update_res.data:
        raise HTTPException(status_code=500, detail="Failed to update report with AI classification.")
    
    final_report = update_res.data[0]
    final_report['image_urls'] = uploaded_image_urls
    return final_report


@reports_router.get("/", response_model=List[ReportResponse])
def get_user_reports(
    current_user: dict = Depends(get_current_user) # <-- Protect the route
):
    """
    Retrieves all reports submitted by the currently authenticated user.
    """
    user_id = current_user['id']
    query = supabase.table("reports").select("*").eq("user_id", user_id)
    
    # (The rest of the logic to get images remains the same)
    reports_res = query.order("created_at", desc=True).execute()
    if not reports_res.data:
        return []
    
    reports = reports_res.data
    report_ids = [r['id'] for r in reports]
    images_res = supabase.table("report_images").select("report_id, image_url").in_("report_id", report_ids).execute()
    
    images_map = defaultdict(list)
    for image in images_res.data:
        images_map[image['report_id']].append(image['image_url'])
        
    for report in reports:
        report['image_urls'] = images_map.get(report['id'], [])
        
    return reports

# The public, filterable endpoint for the admin dashboard remains
@reports_router.get("/all", response_model=List[ReportResponse])
def get_all_reports_for_admin(
    # ... (Keep the existing filtering and pagination logic)
    status: Optional[ReportStatus] = Query(None, description="Filter reports by their status."),
    category: Optional[str] = Query(None, description="Filter reports by their category."),
    department_id: Optional[int] = Query(None, description="Filter reports by department ID."),
    # Location filtering parameters
    center_lat: Optional[float] = Query(None, description="Center latitude for location filtering."),
    center_lon: Optional[float] = Query(None, description="Center longitude for location filtering."),
    radius_km: Optional[float] = Query(10.0, description="Radius in kilometers for location filtering (default: 10km)."),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    query = supabase.table("reports").select("*")
    if status:
        query = query.eq("status", status.value)
    if category:
        query = query.eq("category", category)
    if department_id:
        query = query.eq("department_id", department_id)
    
    reports_res = query.order("created_at", desc=True).execute()
    if not reports_res.data:
        return []
    
    reports = reports_res.data
    
    # Apply location filtering if coordinates are provided
    if center_lat is not None and center_lon is not None:
        filtered_reports = []
        for report in reports:
            if report.get('latitude') is not None and report.get('longitude') is not None:
                distance = calculate_distance(
                    center_lat, center_lon, 
                    report['latitude'], report['longitude']
                )
                if distance <= radius_km:
                    # Add distance to report for potential sorting
                    report['distance_km'] = round(distance, 2)
                    filtered_reports.append(report)
        reports = filtered_reports
    
    # Apply pagination after filtering
    paginated_reports = reports[skip:skip + limit]
    
    # Get images for the paginated reports
    if paginated_reports:
        report_ids = [r['id'] for r in paginated_reports]
        images_res = supabase.table("report_images").select("report_id, image_url").in_("report_id", report_ids).execute()
        
        images_map = defaultdict(list)
        for image in images_res.data:
            images_map[image['report_id']].append(image['image_url'])
            
        for report in paginated_reports:
            report['image_urls'] = images_map.get(report['id'], [])
    
    return paginated_reports


# We will keep the old API Key security for the admin-only status update endpoint
@reports_router.put("/{id}/status", response_model=ReportResponse, dependencies=[Security(get_api_key)])
def update_report_status(id: int, status_update: ReportStatusUpdate):
    # (This function remains the same)
    response = supabase.table("reports").update({"status": status_update.status.value}).eq("id", id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail=f"Report with ID {id} not found.")
    
    updated_report = response.data[0]
    images_res = supabase.table("report_images").select("image_url").eq("report_id", id).execute()
    updated_report['image_urls'] = [img['image_url'] for img in images_res.data]
    
    return updated_report

# (Keep analytics router the same)
analytics_router = APIRouter(prefix="/api/analytics", tags=["Analytics"])
@analytics_router.get("/", response_model=AnalyticsData)
def get_analytics():
    response = supabase.table("reports").select("category, status").execute()
    all_reports = response.data
    return {
        "total_reports": len(all_reports),
        "reports_by_category": Counter(r['category'] for r in all_reports if r['category']),
        "reports_by_status": Counter(r['status'] for r in all_reports if r['status'])
    }

# Dashboard Router
dashboard_router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

# Departments Router
departments_router = APIRouter(prefix="/api/departments", tags=["Departments"])

@departments_router.get("/", response_model=List[DepartmentResponse])
def get_all_departments():
    """Get all departments sorted alphabetically by name."""
    response = supabase.table("departments").select("*").order("name").execute()
    if not response.data:
        return []
    return response.data

@departments_router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(department_id: int):
    """Get a specific department by ID."""
    response = supabase.table("departments").select("*").eq("id", department_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail=f"Department with ID {department_id} not found.")
    return response.data

@departments_router.post("/", status_code=201, response_model=DepartmentResponse, dependencies=[Security(get_api_key)])
def create_department(department: DepartmentCreate):
    """Create a new department. Requires API key for admin access."""
    # Check if department with same name already exists
    existing_dept = supabase.table("departments").select("id").eq("name", department.name).execute()
    if existing_dept.data:
        raise HTTPException(status_code=400, detail="Department with this name already exists.")
    
    # Check if email is already used
    existing_email = supabase.table("departments").select("id").eq("email", department.email).execute()
    if existing_email.data:
        raise HTTPException(status_code=400, detail="Department with this email already exists.")
    
    response = supabase.table("departments").insert(department.model_dump()).execute()
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create department.")
    return response.data[0]

@departments_router.put("/{department_id}", response_model=DepartmentResponse, dependencies=[Security(get_api_key)])
def update_department(department_id: int, department_update: DepartmentUpdate):
    """Update a department. Requires API key for admin access."""
    # Check if department exists
    existing_dept = supabase.table("departments").select("*").eq("id", department_id).single().execute()
    if not existing_dept.data:
        raise HTTPException(status_code=404, detail=f"Department with ID {department_id} not found.")
    
    # Only update provided fields
    update_data = {}
    if department_update.name is not None:
        # Check if new name conflicts with existing departments (excluding current one)
        name_conflict = supabase.table("departments").select("id").eq("name", department_update.name).neq("id", department_id).execute()
        if name_conflict.data:
            raise HTTPException(status_code=400, detail="Department with this name already exists.")
        update_data["name"] = department_update.name
    
    if department_update.email is not None:
        # Check if new email conflicts with existing departments (excluding current one)
        email_conflict = supabase.table("departments").select("id").eq("email", department_update.email).neq("id", department_id).execute()
        if email_conflict.data:
            raise HTTPException(status_code=400, detail="Department with this email already exists.")
        update_data["email"] = department_update.email
    
    if not update_data:
        # No changes provided, return current department
        return existing_dept.data
    
    response = supabase.table("departments").update(update_data).eq("id", department_id).execute()
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to update department.")
    return response.data[0]

@departments_router.delete("/{department_id}", dependencies=[Security(get_api_key)])
def delete_department(department_id: int):
    """Delete a department. Requires API key for admin access."""
    # Check if department exists
    existing_dept = supabase.table("departments").select("id").eq("id", department_id).single().execute()
    if not existing_dept.data:
        raise HTTPException(status_code=404, detail=f"Department with ID {department_id} not found.")
    
    # Check if department has active reports
    active_reports = supabase.table("reports").select("id").eq("department_id", department_id).neq("status", "resolved").execute()
    if active_reports.data:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete department. It has {len(active_reports.data)} active reports. Please resolve or reassign them first."
        )
    
    response = supabase.table("departments").delete().eq("id", department_id).execute()
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to delete department.")
    
    return {"message": f"Department with ID {department_id} has been deleted successfully."}
@dashboard_router.get("/", response_model=DashboardData)
def get_dashboard_data():
    # Get recent reports (last 10)
    recent_reports_res = supabase.table("reports").select("*").order("created_at", desc=True).limit(10).execute()
    recent_reports_data = []
    
    for report in recent_reports_res.data:
        # Calculate time ago
        created_time = datetime.fromisoformat(report["created_at"].replace('Z', '+00:00'))
        current_time = datetime.now(created_time.tzinfo)
        time_ago = current_time - created_time
        
        if time_ago.days > 0:
            time_str = f"{time_ago.days} days ago"
        elif time_ago.total_seconds() > 3600:
            time_str = f"{int(time_ago.total_seconds() // 3600)} hours ago"
        else:
            time_str = f"{int(time_ago.total_seconds() // 60)} minutes ago"
        recent_reports_data.append(
            RecentReport(
                id=str(report["id"]),
                issue=report["description"],
                status=report["status"],
                time=time_str
            )
        )
    
    # Get all reports for KPIs
    all_reports_res = supabase.table("reports").select("status").execute()
    total_reports = len(all_reports_res.data)
    resolved_reports = len([r for r in all_reports_res.data if r["status"] == "resolved"])
    
    # Mocked Department Performance (you can replace with real data)
    department_performance_data = [
        DepartmentPerformance(name="Public Works", resolved=156, total=200, rate=78),
        DepartmentPerformance(name="Transportation", resolved=89, total=110, rate=81),
        DepartmentPerformance(name="Parks & Recreation", resolved=67, total=75, rate=89),
        DepartmentPerformance(name="Public Safety", resolved=134, total=145, rate=92),
    ]
    
    return DashboardData(
        kpis=KpiData(
            totalReports=total_reports,
            reportsResolved=resolved_reports,
            avgResolutionTime="3.2 days", # Mocked
            activeDepartments=4 # Mocked
        ),
        recentReports=recent_reports_data,
        departmentPerformance=department_performance_data
    )


# --- 5. Main FastAPI Application ---
app = FastAPI(
    title="Civic Issue Reporting API (with User Auth)",
    description="Full backend with user registration, login, and protected routes.",
    version="3.0.0"
)

# Get allowed origins from environment or use defaults for development
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174").split(",")

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Restrict to specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Explicit methods only
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],  # Explicit headers only
)

# Add the new auth router
app.include_router(auth_router)
app.include_router(reports_router)
app.include_router(analytics_router)
app.include_router(dashboard_router)
app.include_router(departments_router)

@app.get("/")
def read_root():
    return {"status": "API is running with JWT authentication. Visit /docs to test."}