# Security Model & Best Practices

This document provides a detailed overview of the security measures implemented in the Beumer Feedback Form project.

## 1. Authentication (JWT + OTP)

### Flow
1.  **OTP Generation**: When a user requests an OTP, the server uses the `secrets` module (cryptographically secure) to generate a 6-digit code.
2.  **Verification**: Upon entering the correct OTP, the server issues a **JSON Web Token (JWT)** signed with a `JWT_SECRET`.
3.  **Token Storage**: The frontend stores this token in `localStorage`.
4.  **Submission**: All feedback submissions must include this token in the `Authorization: Bearer <token>` header.

### Security Implementation
- **Algorithm**: HS256 (HMAC with SHA-256).
- **Expiration**: Tokens are valid for 24 hours (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).
- **Identity Binding**: The `submitted_by` field in the database is populated directly from the verified email in the JWT, making impersonation impossible.

## 2. Resource Protection

### Rate Limiting
To prevent automated spam and protect the SMTP service, the `/api/send-otp` endpoint enforces a **60-second cooldown** per email address. 
- **Error Code**: `429 Too Many Requests`.
- **UI Feedback**: The frontend identifies this error and shows a countdown timer to the user.

### Proactive Memory Management
Since OTPs are stored in memory (`otp_store`), a **Background Task** runs during every new OTP request to identify and remove all expired OTP records. This prevents memory bloat and protects against memory-exhaustion-based DoS attacks.

## 3. Database Security

### URI Escaping
The application includes a custom utility to safely escape MongoDB connection strings. This ensures that even if your database password contains special characters (like `@`, `:`, or `/`), the connection remains robust and secure.

### Masked Logging
Sensitive database credentials are automatically masked in the server logs (e.g., `mongodb+srv://user:****@cluster...`) to prevent accidental exposure in log files.

## 4. Frontend Security
- **XSS Prevention**: The UI uses `.textContent` and `.innerText` exclusively for rendering user-supplied data to prevent Cross-Site Scripting (XSS).
- **Session Management**: If a user's session expires (JWT becomes invalid), the frontend automatically detects the `401 Unauthorized` response and redirects the user back to the verification page.

---

## 🛠️ Recommended Maintenance
- **Rotate JWT_SECRET**: Change your `JWT_SECRET` periodically in the environment variables.
- **Limit CORS**: Once deployed to a stable URL, update `allow_origins` in `api/index.py` to only include your specific domain.
