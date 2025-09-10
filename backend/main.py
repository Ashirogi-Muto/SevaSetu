import os
import json
import uuid
from datetime import datetime
from collections import Counter
from dotenv import load_dotenv
from typing import Optional, List, Dict

# --- FastAPI Imports ---
from fastapi import FastAPI, APIRouter, HTTPException, Form, UploadFile, File, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

# --- Pydantic Imports ---
from pydantic import BaseModel, Field

# --- Supabase Imports ---
from supabase import create_client, Client

# --- Local Module Imports ---
from ai_service import classify_report_simulated


# --- 1. Core Setup: Env Vars and Database Client ---
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY") # <-- New

if not all([SUPABASE_URL, SUPABASE_KEY, API_SECRET_KEY]):
    raise RuntimeError("Supabase URL/Key and API_SECRET_KEY must be set in the .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# --- 2. Security Setup ---
# This sets up the mechanism to check for a header named "X-API-Key"
api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key: str = Security(api_key_header)):
    """
    Dependency function to validate the API key from the request header.
    """
    if api_key == API_SECRET_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=403, detail="Could not validate credentials"
        )


# --- 3. Schemas: Pydantic Data Models ---
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
    status: str
    image_urls: List[str] = []

class ReportStatusUpdate(BaseModel):
    status: str

class AnalyticsData(BaseModel):
    total_reports: int
    reports_by_category: Dict[str, int]
    reports_by_status: Dict[str, int]


# --- 4. API Routers: Grouped Endpoints ---
reports_router = APIRouter(prefix="/api/reports", tags=["Reports"])

# Apply the security dependency to the POST endpoint
@reports_router.post("/", status_code=201, response_model=ReportResponse, dependencies=[Security(get_api_key)])
def submit_report(
    report_data_json: str = Form(...),
    images: List[UploadFile] = File(...)
):
    try:
        report_data = ReportData.parse_raw(report_data_json)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format for report_data_json: {e}")

    ai_category = classify_report_simulated(report_data.description)
    
    db_report_data = report_data.model_dump()
    db_report_data['category'] = ai_category
    report_res = supabase.table("reports").insert(db_report_data).execute()
    if not report_res.data:
        raise HTTPException(status_code=500, detail="Failed to save report.")
    
    inserted_report = report_res.data[0]
    report_id = inserted_report['id']
    
    uploaded_image_urls = []
    for image in images:
        file_ext = image.filename.split('.')[-1]
        file_name = f"{report_id}_{uuid.uuid4()}.{file_ext}"
        try:
            file_content = image.file.read()
            supabase.storage.from_("report-images").upload(file=file_content, path=file_name, file_options={"content-type": image.content_type})
            public_url = supabase.storage.from_("report-images").get_public_url(file_name)
            uploaded_image_urls.append(public_url)
            supabase.table("report_images").insert({"report_id": report_id, "image_url": public_url}).execute()
        except Exception as e:
            print(f"ERROR: Failed to upload image {image.filename}: {e}")
            continue
            
    inserted_report['image_urls'] = uploaded_image_urls
    return inserted_report

@reports_router.get("/", response_model=List[ReportResponse])
def get_all_reports():
    reports_res = supabase.table("reports").select("*").order("created_at", desc=True).execute()
    all_reports = reports_res.data
    images_res = supabase.table("report_images").select("report_id, image_url").execute()
    
    images_map = {}
    for image in images_res.data:
        report_id = image['report_id']
        if report_id not in images_map:
            images_map[report_id] = []
        images_map[report_id].append(image['image_url'])
        
    for report in all_reports:
        report['image_urls'] = images_map.get(report['id'], [])
        
    return all_reports

# Apply the security dependency to the PUT endpoint
@reports_router.put("/{id}/status", response_model=ReportResponse, dependencies=[Security(get_api_key)])
def update_report_status(id: int, status_update: ReportStatusUpdate):
    response = supabase.table("reports").update({"status": status_update.status}).eq("id", id).execute()
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
    title="Civic Issue Reporting API (Secure)",
    description="API for reporting and managing civic issues, secured with an API Key.",
    version="1.0.0"
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
    return {"status": "API is running. POST and PUT endpoints are now secured. Visit /docs to test."}
