# Enterprise Learning Management System - Troubleshooting & Diagnostics

This guide provides step-by-step diagnostic solutions for common operational and development scenarios encountered when running the Enterprise LMS.

---

## 🔍 Diagnostic Checklist

When encountering unexpected behavior:
1. **Check Log Output**: Inspect `logs/lms.log` for structured stack traces.
2. **Verify Database Seeding**: Ensure `lms_dev.db` exists and has been populated via `python manage.py seed`.
3. **Run Automated Tests**: Execute `python -m pytest tests/ -v` to ensure system integrity.

---

## 🛠️ Common Scenarios and Solutions

### 1. Database Schema Out of Sync or Missing Tables
* **Symptom**: `OperationalError: no such table: users` or `no such column`.
* **Root Cause**: Database was not initialized or migration was interrupted.
* **Resolution**:
  ```bash
  python manage.py init-db
  python manage.py seed
  ```

### 2. User Account Locked Out
* **Symptom**: `Account temporarily locked due to multiple failed login attempts. Please try again in 15 minutes.`
* **Root Cause**: 5 consecutive invalid passwords triggered brute-force defense.
* **Resolution (Admin Portal)**:
  - Log in as SuperAdmin (`admin` / `adminpassword123`).
  - Navigate to **User Management** (`/admin/users`).
  - Find user and click **Unlock Account** or toggle status to `active`.
* **Resolution (CLI / Python Shell)**:
  ```bash
  python -c "from core.database import init_db, get_session; from users.models import User; init_db(); s = get_session(); u = s.query(User).filter_by(username='target_user').first(); u.failed_attempts=0; u.locked_until=None; s.commit(); print('Unlocked!')"
  ```

### 3. Port 5000 Already in Use
* **Symptom**: `OSError: [Errno 98] Address already in use` or `[WinError 10048] Only one usage of each socket address is normally permitted`.
* **Resolution**: Run the server on a different port (e.g. 5050):
  ```bash
  python manage.py runserver 5050
  ```

### 4. PowerShell Script Execution Policy Error (Windows)
* **Symptom**: `.\venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system.`
* **Resolution**:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\venv\Scripts\Activate.ps1
  ```

### 5. ReportLab Font or PDF Rendering Questions
* **Symptom**: Certificate generation questions or PDF customization.
* **Resolution**: ReportLab utilizes standard built-in Helvetica and Helvetica-Bold typefaces, guaranteeing vector fidelity without external system font installations.
