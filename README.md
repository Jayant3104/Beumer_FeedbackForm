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

---

---
