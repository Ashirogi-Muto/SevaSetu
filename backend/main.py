import os
import json
import uuid
from datetime import datetime
from collections import Counter, defaultdict
from dotenv import load_dotenv
from typing import Optional, List, Dict
from enum import Enum

# FastAPI Imports
from fastapi import FastAPI, APIRouter, HTTPException, Form, UploadFile, File, Security, Query # <-- Corrected APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

# Pydantic Imports
from pydantic import BaseModel, Field

# Supabase Imports
from supabase import create_client, Client

# Local Module Imports
from ai_service import classify_report_with_real_ai


# --- 1. Core Setup ---
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
AI_API_URL = os.getenv("AI_API_URL")

if not all([SUPABASE_URL, SUPABASE_KEY, API_SECRET_KEY, AI_API_URL]):
    raise RuntimeError("Supabase credentials, API_SECRET_KEY, and AI_API_URL must be set in the .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# --- 2. Security Setup ---
api_key_header = APIKeyHeader(name="X-API-Key")
async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_SECRET_KEY:
        return api_key
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")


# --- 3. Schemas ---
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

class ReportStatusUpdate(BaseModel):
    status: ReportStatus

class AnalyticsData(BaseModel):
    total_reports: int
    reports_by_category: Dict[str, int]
    reports_by_status: Dict[str, int]


# --- 4. API Routers ---
reports_router = APIRouter(prefix="/api/reports", tags=["Reports"])

@reports_router.post("/", status_code=201, response_model=ReportResponse, dependencies=[Security(get_api_key)])
async def submit_report(
    report_data_json: str = Form(...),
    images: List[UploadFile] = File(...)
):
    try:
        report_data = ReportData.parse_raw(report_data_json)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {e}")

    # Step 1: Save the basic report data to get an ID.
    initial_db_data = report_data.model_dump()
    initial_db_data['category'] = "Classification Pending"
    report_res = supabase.table("reports").insert(initial_db_data).execute()
    if not report_res.data:
        raise HTTPException(status_code=500, detail="Failed to save initial report.")
    
    report_id = report_res.data[0]['id']
    
    # Step 2: Upload images to storage.
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
    
    # Step 3: Call the AI service.
    ai_category = await classify_report_with_real_ai(report_data.description, uploaded_image_urls)
    
    # Step 4: Look up the department.
    department_id = None
    try:
        mapping_res = supabase.table("category_department_mapping").select("department_id").eq("category_name", ai_category).single().execute()
        if mapping_res.data:
            department_id = mapping_res.data['department_id']
    except Exception as e:
        print(f"WARNING: No routing rule for category '{ai_category}'. Error: {e}")

    # Step 5: Update the report with the final AI category and department ID.
    update_data = {"category": ai_category, "department_id": department_id}
    update_res = supabase.table("reports").update(update_data).eq("id", report_id).execute()
    
    if not update_res.data:
        raise HTTPException(status_code=500, detail="Failed to update report with AI classification.")
    
    # Step 6: Prepare and return the final, complete response.
    final_report = update_res.data[0]
    final_report['image_urls'] = uploaded_image_urls
    return final_report

@reports_router.get("/", response_model=List[ReportResponse])
def get_all_reports(
    status: Optional[ReportStatus] = Query(None, description="Filter reports by their status."),
    category: Optional[str] = Query(None, description="Filter reports by their category."),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    query = supabase.table("reports").select("*")
    if status:
        query = query.eq("status", status.value)
    if category:
        query = query.eq("category", category)
    reports_res = query.order("created_at", desc=True).range(skip, skip + limit - 1).execute()
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

@reports_router.put("/{id}/status", response_model=ReportResponse, dependencies=[Security(get_api_key)])
def update_report_status(id: int, status_update: ReportStatusUpdate):
    response = supabase.table("reports").update({"status": status_update.status.value}).eq("id", id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail=f"Report with ID {id} not found.")
    
    updated_report = response.data[0]
    images_res = supabase.table("report_images").select("image_url").eq("report_id", id).execute()
    updated_report['image_urls'] = [img['image_url'] for img in images_res.data]
    
    return updated_report

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


# --- 5. Main FastAPI Application ---
app = FastAPI(
    title="Civic Issue Reporting API (Final Logic)",
    description="API with a robust, sequential submission flow.",
    version="2.5.3"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reports_router)
app.include_router(analytics_router)

@app.get("/")
def read_root():
    return {"status": "API is running with corrected final logic. Visit /docs to test."}