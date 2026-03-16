# Beumer Feedback Form

A modern, responsive multi-page feedback system for Beumer Digitalization. This application features email OTP verification, conditional form sections for different products (FillPac and Bucket Elevator), and secure data storage in MongoDB.

## 🚀 Features

- **JWT Authentication**: Secure, token-based authorization for feedback submissions.
- **OTP Verification**: Secure email-based OTP system with proactive background cleanup.
- **Rate Limiting**: Integrated 60-second cooldown on OTP requests to prevent SMTP abuse.
- **Dynamic Multi-page Form**: Smooth, animated transitions between form sections.
- **Conditional Logic**: Automatically shows/skips feedback fields based on product selection.
- **Responsive Design**: Mobile-first UI with premium aesthetics and custom branding.
- **FastAPI Backend**: Asynchronous Python API optimized for Vercel Serverless.
- **MongoDB Integration**: Secure data storage with automatic identity binding to verified users.

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (ES6+)
- **Backend**: Python 3.12 (FastAPI, PyJWT, Motor)
- **Database**: MongoDB Atlas (Motor Async Driver)
- **Deployment**: Vercel (Serverless Functions)

## 📁 Project Structure

```text
Beumer_FeedbackForm/
├── api/
│   └── index.py            # FastAPI Entry Point (Serverless Function)
├── static/                 # Frontend Assets
│   ├── index.html          # Main SPA Entry
│   ├── style.css           # Modern Custom Styles
│   ├── script.js           # Interactive UI Logic
│   └── assets/             # Branding Assets (Official Logos)
├── vercel.json             # Vercel Routing Configuration
├── requirements.txt        # Backend Dependencies
└── README.md               # Project Documentation
```

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.12 or higher.
- MongoDB Atlas account.
- Gmail App Password for SMTP.

### 2. Local Configuration
Create a `.env` file in the root or `backend/` folder:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/dbname
JWT_SECRET=your_strong_secret_key
JWT_ALGORITHM=HS256
```

### 3. Run Locally
```bash
pip install -r requirements.txt
uvicorn api.index:app --reload
```

## 🚢 Deployment (Vercel)

1. **Push to GitHub**: Ensure your latest code is pushed to your repository.
2. **Import to Vercel**: Connect your GitHub account and import `Beumer_FeedbackForm`.
3. **Environment Variables**: Add `MONGODB_URL`, `SMTP_USER`, `SMTP_PASSWORD`, etc., in Vercel Project Settings.
4. **Deploy**: Vercel will automatically detect the Python API and deploy it as a Serverless Function.

## Flowchart

```mermaid
graph TD

    A[Application Start] --> B[Load Environment Variables using load_dotenv]

    B --> C[Initialize FastAPI App]
    C --> D[Enable CORS Middleware]
    D --> E[Configure Static Directory]
    E --> F[Mount Static Files]

    F --> G[Load SMTP Configuration]
    G --> H[Load JWT Configuration]

    H --> I[MongoDB Configuration]

    I --> J{MONGO_USER & PASS Provided?}

    J -->|Yes| K[Build MongoDB Atlas URL]
    J -->|No| L[Use MONGODB_URL]

    K --> M[escape_mongodb_url Function]
    L --> M

    M --> N[Create AsyncIOMotorClient]
    N --> O[Connect to Database]
    O --> P[Create feedback_collection]

    P --> Q[API Router /api Initialized]

    %% MODELS

    Q --> R[Models Defined]

    R --> S[OtpRequest Class\nemail: EmailStr]
    R --> T[OtpVerify Class\nemail: EmailStr\notp: str]
    R --> U[FeedbackData Class\nsectionA\nsectionB\nsectionC\nsectionD_FillPac\nsectionD_BucketElevator]

    %% OTP REQUEST FLOW

    S --> V[POST /api/send-otp]

    V --> W[Validate Request Using OtpRequest]
    W --> X{SMTP Configured?}

    X -->|No| Y[Return 500 Mail Server Not Configured]

    X -->|Yes| Z[Check OTP Cooldown]

    Z --> AA{Last OTP < 60s?}

    AA -->|Yes| AB[Return 429 Too Many Requests]
    AA -->|No| AC[Generate OTP using generate_otp]

    AC --> AD[Store OTP in otp_store Dictionary]

    AD --> AE[Add Expiration 10 Minutes]

    AE --> AF[Send Email using send_otp_email]

    AF --> AG{SMTP_PORT == 465?}

    AG -->|Yes| AH[SMTP_SSL Connection]
    AG -->|No| AI[SMTP STARTTLS Connection]

    AH --> AJ[Login SMTP]
    AI --> AJ

    AJ --> AK[Send OTP Email]

    AK --> AL[Return Success Response]

    %% OTP VERIFICATION FLOW

    T --> AM[POST /api/verify-otp]

    AM --> AN[Validate Request Using OtpVerify]

    AN --> AO{OTP Exists in otp_store?}

    AO -->|No| AP[Return Error No OTP Found]

    AO -->|Yes| AQ[Check OTP Expiration]

    AQ --> AR{Expired?}

    AR -->|Yes| AS[Delete OTP]
    AS --> AT[Return Expired Error]

    AR -->|No| AU[Compare OTP]

    AU --> AV{OTP Correct?}

    AV -->|No| AW[Return Incorrect OTP]

    AV -->|Yes| AX[Delete OTP Record]

    AX --> AY[Create JWT Token using create_access_token]

    AY --> AZ[Return access_token]

    %% JWT AUTHENTICATION

    AZ --> BA[User Stores Token]

    BA --> BB[User Submits Feedback]

    %% FEEDBACK FLOW

    U --> BC[POST /api/submit-feedback]

    BC --> BD[Authorization Header Required]

    BD --> BE[HTTPBearer Extract Token]

    BE --> BF[get_current_user Function]

    BF --> BG[Decode JWT]

    BG --> BH{Token Valid?}

    BH -->|No| BI[Return 401 Unauthorized]

    BH -->|Yes| BJ[Extract Email]

    BJ --> BK[Validate Request using FeedbackData]

    BK --> BL[Convert Model to Dictionary]

    BL --> BM[Add Metadata\nsubmitted_by=email\ncreated_at=time]

    BM --> BN[Insert into MongoDB feedback_collection]

    BN --> BO[Return Success Response]

    %% CLEANUP

    BO --> BP[Background Task cleanup_expired_otps]

    BP --> BQ[Scan otp_store]

    BQ --> BR[Delete Expired OTPs]

    BR --> BS[System Ready for Next Request]

    %% HEALTH CHECK

    Q --> BT[GET /api/health]
    BT --> BU[Return status ok]
```



