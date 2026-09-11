# Enterprise Learning Management System - Setup & Configuration

This document covers system initialization, configuration environments, database migrations, and operational settings for the Enterprise LMS.

---

## ⚙️ Configuration Architecture

The LMS uses a multi-environment configuration pattern defined in `config/settings.py`:
* **`DevelopmentConfig`**: Local SQLite database (`lms_dev.db`), verbose logging, dynamic debug reloader enabled.
* **`TestingConfig`**: In-memory SQLite (`:memory:`), mock authentication tokens, disabled CSRF for rapid Pytest execution.
* **`ProductionConfig`**: Optimized connection pooling, hardened security headers, strict session cookies (`HttpOnly`, `SameSite=Lax`), secure secret key validation.

### Environment Variables

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `LMS_ENV` | `development` | Active environment: `development`, `testing`, `production` |
| `SECRET_KEY` | `enterprise-lms-secure-default-key-3.12` | Cryptographic session signing key |
| `DATABASE_URL` | `sqlite:///lms_dev.db` | SQLAlchemy connection string (SQLite, PostgreSQL, MySQL) |
| `PORT` | `5000` | Port for the local WSGI development server |
| `LOG_LEVEL` | `INFO` | Logging threshold (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `MAX_UPLOAD_SIZE_MB` | `16` | Maximum file upload size for assignment submissions |

---

## 🗄️ Database Initialization

The database schema and default lookup tables are automatically initialized during seeding.

### 1. Seeding Default Roles and Institutional Data
```bash
python manage.py seed
```

This populates:
* **Default RBAC Roles**: `admin`, `instructor`, `student`, `guest`
* **25+ Core Permissions**: `course:create`, `course:publish`, `grade:submit`, `attendance:record`, `user:manage`, `audit:read`, etc.
* **Default System Settings**: Institutional name, grading scale formulas, certificate verification prefixes, registration flags.
* **Gamification Badges**: `First Step`, `Quiz Ace`, `Code Architect`, `Course Master`, `Streak Champion`.
* **Realistic Course Curriculum**: CS-101, AI-301, SEC-201 with modules, lessons, notes, quizzes, and assignments.
* **Test Users**: SuperAdmin, 3 Instructors, and 5 Students.

---

## 🪵 Logging & Diagnostics

Logging is configured in `config/logging_config.py` with structured output:
* Log files are saved to `logs/lms.log`.
* Automatic log rotation triggers when the file reaches 5 MB (retaining 5 backups).
* Critical security events, login attempts, role boundary violations, and grade modifications are logged with high-resolution timestamps.
