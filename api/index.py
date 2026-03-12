from fastapi import FastAPI, HTTPException, APIRouter, BackgroundTasks
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
from motor.motor_asyncio import AsyncIOMotorClient
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends


# Load environment variables
# Check root first, then backend folder for local dev
load_dotenv()
if not os.getenv("MONGO_USER") and not os.getenv("MONGODB_URL"):
    load_dotenv("backend/.env")

app = FastAPI(title="Beumer Feedback API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Determine the absolute path to the static directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Route for the main UI
@app.api_route("/", methods=["GET", "HEAD"])
async def read_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": f"index.html not found at {index_path}. Check your directory structure."}

# Mount the static directory for other assets (CSS, JS)
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
else:
    print(f"WARNING: Static directory not found at {STATIC_DIR}")

# In-memory OTP store: { email: { otp: str, expires_at: datetime } }
otp_store: Dict[str, Dict] = {}

# SMTP Config from .env
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "beumer_default_secret_key_change_me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
security = HTTPBearer()

import urllib.parse
import re

def escape_mongodb_url(url: str) -> str:
    """
    Safely escapes username and password in a mongodb:// or mongodb+srv:// URL
    by identifying the host separator (@) reliably.
    """
    if not url or "localhost" in url:
        return url
        
    prefix = ""
    if url.startswith("mongodb://"):
        prefix = "mongodb://"
    elif url.startswith("mongodb+srv://"):
        prefix = "mongodb+srv://"
    else:
        return url
        
    creds_and_rest = url[len(prefix):]
    if "@" not in creds_and_rest:
        return url
        
    # Find the host part - it starts after the last '@' that precedes the first '/'
    first_slash = creds_and_rest.find("/")
    if first_slash != -1:
        host_area = creds_and_rest[:first_slash]
        path_area = creds_and_rest[first_slash:]
    else:
        host_area = creds_and_rest
        path_area = ""
        
    if "@" not in host_area:
        return url
        
    # The last '@' in the host_area is the separator between credentials and host
    last_at = host_area.rfind("@")
    creds = host_area[:last_at]
    host_only = host_area[last_at:] # includes the '@'
    
    if ":" not in creds:
        user_clean = urllib.parse.unquote(creds)
        return f"{prefix}{urllib.parse.quote_plus(user_clean)}{host_only}{path_area}"
    
    first_colon = creds.find(":")
    user = creds[:first_colon]
    password = creds[first_colon+1:]
    
    user_clean = urllib.parse.unquote(user)
    pass_clean = urllib.parse.unquote(password)
    
    return f"{prefix}{urllib.parse.quote_plus(user_clean)}:{urllib.parse.quote_plus(pass_clean)}{host_only}{path_area}"

# MongoDB Connection
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_DB = os.getenv("MONGO_DB", "beumer_feedback")

# Construct URL if individual variables are provided, otherwise use MONGODB_URL
if MONGO_USER and MONGO_PASS and MONGO_HOST:
    # Safely escape username and password for the URI
    user_escaped = urllib.parse.quote_plus(MONGO_USER)
    pass_escaped = urllib.parse.quote_plus(MONGO_PASS)
    MONGODB_URL = f"mongodb+srv://{user_escaped}:{pass_escaped}@{MONGO_HOST}/?retryWrites=true&w=majority"
    DATABASE_NAME = MONGO_DB
    print(f"Connecting to MongoDB Atlas (via individual vars): {MONGO_HOST}")
else:
    raw_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_URL = escape_mongodb_url(raw_url)
    DATABASE_NAME = os.getenv("DATABASE_NAME", MONGO_DB)
    
    if "localhost" in MONGODB_URL:
        print(f"Connecting to Local MongoDB: {MONGODB_URL}")
    else:
        # Robust masking for logs: find last '@' before first '/' or end of string
        log_url = MONGODB_URL
        prefix_len = log_url.find("//") + 2 if "//" in log_url else 0
        creds_rest = log_url[prefix_len:]
        first_sl = creds_rest.find("/")
        host_a = creds_rest[:first_sl] if first_sl != -1 else creds_rest
        
        if "@" in host_a:
            last_a = host_a.rfind("@")
            crd = host_a[:last_a]
            if ":" in crd:
                col = crd.find(":")
                log_url = log_url[:prefix_len] + crd[:col] + ":****" + log_url[prefix_len + last_a:]
            else:
                log_url = log_url[:prefix_len] + "****" + log_url[prefix_len + last_a:]
                
        print(f"Connecting to MongoDB via MONGODB_URL: {log_url[:60]}...")

# Initializing Client
try:
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    feedback_collection = db["feedback"]
    print(f"Successfully connected to database: {DATABASE_NAME}")
except Exception as e:
    print(f"Database connection failed: {e}")


# ─── Models ───────────────────────────────────────────────────────────────────

class OtpRequest(BaseModel):
    email: EmailStr

class OtpVerify(BaseModel):
    email: EmailStr
    otp: str

class FeedbackData(BaseModel):
    sectionA: Dict[str, Any]
    sectionB: Dict[str, Any]
    sectionC: Dict[str, Any]
    sectionD_FillPac: Optional[Dict[str, Any]] = None
    sectionD_BucketElevator: Optional[Dict[str, Any]] = None


# ─── JWT Helpers ──────────────────────────────────────────────────────────────

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid session. Please verify your email again.")
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired. Please verify your email again.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials.")


# ─── Cleanup Helpers ──────────────────────────────────────────────────────────

def cleanup_expired_otps():
    """Removes all expired OTPs from the in-memory store."""
    now = datetime.utcnow()
    expired_emails = [
        email for email, record in otp_store.items() 
        if now > record.get("expires_at", now)
    ]
    for email in expired_emails:
        del otp_store[email]
    if expired_emails:
        print(f"DEBUG: Cleaned up {len(expired_emails)} expired OTPs from memory.")


# ─── OTP Helpers ──────────────────────────────────────────────────────────────

def generate_otp(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(to_email: str, otp: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your Beumer Feedback Verification Code"
    msg["From"] = SMTP_FROM
    msg["To"] = to_email

    html = f"""
    <html><body style="font-family:Arial,sans-serif;background:#f4f4f4;padding:30px;">
      <div style="background:white;border-radius:8px;padding:30px;max-width:480px;margin:auto;">
        <h2 style="color:#003399;">Beumer Digitalization</h2>
        <p>Your email verification code is:</p>
        <div style="font-size:2.5rem;font-weight:bold;letter-spacing:10px;color:#003399;
                    background:#f0f4ff;padding:20px;border-radius:8px;text-align:center;">
          {otp}
        </div>
        <p style="color:#888;margin-top:20px;">This code expires in <strong>10 minutes</strong>.</p>
        <p style="color:#888;font-size:0.85rem;">If you didn't request this, please ignore this email.</p>
      </div>
    </body></html>
    """
    msg.attach(MIMEText(html, "html"))

    try:
        if SMTP_PORT == 465:
            print(f"DEBUG: Attempting SMTP_SSL connection to {SMTP_HOST}:{SMTP_PORT}")
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_FROM, to_email, msg.as_string())
        else:
            print(f"DEBUG: Attempting SMTP (STARTTLS) connection to {SMTP_HOST}:{SMTP_PORT}")
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_FROM, to_email, msg.as_string())
        print(f"DEBUG: Email successfully sent to {to_email}")
    except smtplib.SMTPException as e:
        print(f"CRITICAL SMTP ERROR: {type(e).__name__}: {str(e)}")
        raise
    except Exception as e:
        print(f"CRITICAL CONNECTION ERROR: {type(e).__name__}: {str(e)}")
        raise


# ─── Endpoints ────────────────────────────────────────────────────────────────

# API Router for namespaced endpoints
api_router = APIRouter(prefix="/api")

@api_router.post("/send-otp")
async def send_otp(request: OtpRequest, background_tasks: BackgroundTasks):
    # Trigger proactive cleanup
    background_tasks.add_task(cleanup_expired_otps)
    
    # Log incoming request for diagnostics (safe log)
    print(f"OTP request for: {request.email}")
    
    # Check if SMTP is configured
    if not SMTP_USER or not SMTP_PASSWORD:
        print("ERROR: SMTP_USER or SMTP_PASSWORD not set in environment.")
        raise HTTPException(
            status_code=500, 
            detail="Mail server is not configured. Please contact administrator."
        )

    try:
        # Check for cooldown (Rate Limiting)
        if request.email in otp_store:
            record = otp_store[request.email]
            # If the last OTP was sent less than 60 seconds ago
            age = datetime.utcnow() - record.get("requested_at", datetime.min)
            if age < timedelta(seconds=60):
                remaining = 60 - int(age.total_seconds())
                raise HTTPException(
                    status_code=429, 
                    detail=f"Please wait {remaining} seconds before requesting a new code."
                )

        otp = generate_otp()
        otp_store[request.email] = {
            "otp": otp,
            "expires_at": datetime.utcnow() + timedelta(minutes=10),
            "requested_at": datetime.utcnow()
        }
        send_otp_email(str(request.email), otp)
        print(f"Successfully sent OTP to {request.email}")
        return {"status": "success", "message": f"OTP sent to {request.email}"}
    except smtplib.SMTPAuthenticationError:
        print(f"SMTP Authentication Error: Failed to login as {SMTP_USER}")
        raise HTTPException(status_code=500, detail="Authentication failed with the email provider.")
    except smtplib.SMTPConnectError:
        print(f"SMTP Connection Error: Could not connect to {SMTP_HOST}:{SMTP_PORT}")
        raise HTTPException(status_code=500, detail="Could not connect to the email server.")
    except Exception as e:
        print(f"Unexpected error in send_otp: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {type(e).__name__}")


@api_router.post("/verify-otp")
async def verify_otp(request: OtpVerify):
    record = otp_store.get(request.email)
    if not record:
        raise HTTPException(status_code=400, detail="No OTP found for this email. Please request a new one.")

    if datetime.utcnow() > record["expires_at"]:
        del otp_store[request.email]
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")

    if request.otp != record["otp"]:
        raise HTTPException(status_code=400, detail="Incorrect OTP. Please try again.")

    del otp_store[request.email]
    
    # Issue JWT on successful verification
    access_token = create_access_token(data={"sub": request.email})
    
    return {
        "status": "success", 
        "message": "Email verified successfully!",
        "access_token": access_token,
        "token_type": "bearer"
    }


@api_router.post("/submit-feedback")
async def submit_feedback(data: FeedbackData, current_user: str = Depends(get_current_user)):
    try:
        feedback_dict = data.model_dump()
        feedback_dict["created_at"] = datetime.utcnow()
        
        # Insert into MongoDB
        result = await feedback_collection.insert_one(feedback_dict)
        
        print(f"Received and saved feedback: {result.inserted_id}")
        return {"status": "success", "message": "Feedback saved successfully", "id": str(result.inserted_id)}
    except Exception as e:
        print(f"Error saving feedback: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while saving feedback")


@api_router.get("/health")
async def health_check():
    return {"status": "ok"}

# Include the router in the app
app.include_router(api_router)

if __name__ == "__main__":
    # Startup Configuration Summary
    print("\n" + "="*50)
    print("BEUMER FEEDBACK API - STARTUP CONFIGURATION")
    print("="*50)
    print(f"SMTP Host: {SMTP_HOST}")
    print(f"SMTP Port: {SMTP_PORT}")
    print(f"SMTP User: {SMTP_USER[:3]}***@{SMTP_USER.split('@')[-1] if '@' in SMTP_USER else '???'}")
    print(f"SMTP Auth: {'[SET]' if SMTP_PASSWORD else '[MISSING]'}")
    print(f"MongoDB:   {DATABASE_NAME}")
    print("="*50 + "\n")

    # Check for critical environment variables on startup
    missing_vars = []
    if not SMTP_USER: missing_vars.append("SMTP_USER")
    if not SMTP_PASSWORD: missing_vars.append("SMTP_PASSWORD")
    if not os.getenv("MONGO_HOST") and not os.getenv("MONGODB_URL"):
        missing_vars.append("MONGO_HOST or MONGODB_URL")
    
    if missing_vars:
        print(f"[!] WARNING: Missing environment variables: {', '.join(missing_vars)}")
        print("[!] OTP service or Database connection may fail.\n")

    uvicorn.run(app, host="127.0.0.1", port=8000)
