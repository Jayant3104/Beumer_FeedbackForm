# Beumer Feedback Form

A modern, responsive multi-page feedback system for Beumer Digitalization. This application features email OTP verification, conditional form sections for different products (FillPac and Bucket Elevator), and secure data storage in MongoDB.

## 🚀 Features

- **OTP Verification**: Secure email-based OTP system using Gmail SMTP.
- **Dynamic Multi-page Form**: Smooth transitions between form sections.
- **Conditional Logic**: Shows specific feedback fields based on product selection (FillPac/Bucket Elevator).
- **Responsive Design**: Mobile-friendly UI with modern glassmorphism aesthetics.
- **FastAPI Backend**: High-performance asynchronous API.
- **MongoDB Integration**: Flexible data storage for feedback submissions.

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (ES6+)
- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **Database**: MongoDB Atlas (Motor Async Driver)
- **Email**: SMTP (Gmail App Passwords)

## 📁 Project Structure

```text
Beumer_FeedbackForm/
├── api/
│   └── index.py            # Core Backend Logic (FastAPI)
├── static/                 # Frontend Assets
│   ├── index.html          # Main Entry Point
│   ├── style.css           # Custom Styles
│   ├── script.js           # Form & UI Logic
│   └── assets/             # Images & Icons
├── backend/
│   └── .env                # Environment Variables (Local)
├── requirements.txt        # Python Dependencies
└── README.md               # Project Documentation
```

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.11 or higher installed.
- A MongoDB Atlas account (free tier works great).
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords) created.

### 2. Configure Environment `.env`
Create a file at `backend/.env` with the following content:
```env
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-digit-app-password
SMTP_FROM=your-email@gmail.com

# MongoDB Atlas Configuration
MONGO_USER=your-db-user
MONGO_PASS=your-db-pass
MONGO_HOST=cluster-url.mongodb.net
MONGO_DB=Cluster0
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Locally
```bash
uvicorn api.index:app --reload
```
Open **http://localhost:8000** in your browser.

## 🚢 Deployment (Render)

1. Connect your Github repository to **Render**.
2. Create a new **Web Service**.
3. Set Build Command: `pip install -r requirements.txt`
4. Set Start Command: `uvicorn api.index:app --host 0.0.0.0 --port $PORT`
5. Upload your `.env` file via Render's **Secret Files** feature.

---
Produced for Beumer Digitalization by Antigravity.
