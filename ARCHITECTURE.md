# Enterprise Learning Management System - Architecture Guide

## 1. Architectural Philosophy

The Enterprise Learning Management System (LMS) is architected following **Domain-Driven Design (DDD)** and **Clean / Hexagonal Architecture** patterns in modern Python 3.12. 

The architecture strictly separates business rules from database storage and presentation layers, ensuring that:
1. Every domain is a self-contained bounded context with its own models, services, and invariants.
2. Web controllers (Flask Blueprints) are thin and delegate all domain workflows to Service classes.
3. Database transactions are managed explicitly via SQLAlchemy 2.0 scoped sessions and the Unit of Work pattern.
4. The system operates 100% locally with zero external API dependencies or proprietary cloud services.

```
+-------------------------------------------------------------------------+
|                           PRESENTATION LAYER                            |
|  - High-Aesthetic 3-Card Portal Landing (/auth/login?portal=...)        |
|  - Role-Scoped Jinja2 Templates (Admin, Instructor, Student)            |
|  - Modern Vanilla CSS Design System (CSS Custom Properties & Glass)     |
|  - Zero-Dependency Interactive JS (Quiz Timer, Canvas/SVG Charts)       |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                            APPLICATION LAYER                            |
|  - Flask Application Factory (app.py)                                   |
|  - Blueprints: auth_bp, admin_bp, instructor_bp, student_bp, common_bp  |
|  - Core Security Middleware & Session Guard                             |
|  - Event Dispatcher Bus (gamification hooks, audit log triggers)       |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                              DOMAIN LAYER                               |
|  - 20+ Domain Packages:                                                 |
|    roles, permissions, users, students, instructors, authentication     |
|    courses, modules, lessons, materials, curriculum                     |
|    enrollment, progress, attendance                                     |
|    question_bank, quizzes, examinations, assignments, grading           |
|    certificates (ReportLab Vector PDF Engine)                           |
|    gamification (XP, Badges, Streaks), skills (Competencies)            |
|    discussions, notifications, calendar_events, audit, settings         |
|    analytics, reports (CSV/JSON), search (Full-text)                    |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                          INFRASTRUCTURE LAYER                           |
|  - SQLAlchemy 2.0 ORM Scoped Session Management                         |
|  - SQLite (Local Embedded) / PostgreSQL Compatible                      |
|  - PBKDF2 Password Hashing (200,000 SHA-256 Iterations)                 |
|  - ReportLab PDF Vector Engine (Local Font & Geometry Calculation)      |
|  - Rotating Structured File Logger (5MB Rolling Archives)               |
+-------------------------------------------------------------------------+
```

---

## 2. Domain Packages Overview

Each domain package is structured with distinct responsibilities:
* `models.py`: Declarative SQLAlchemy 2.0 ORM entity definitions inheriting from `ModelMixin` (UUID identifier, `created_at`, `updated_at`).
* `services.py`: Encapsulated domain logic, validation checks, and state transitions.

### Key Domain Engines

| Domain | Description & Key Responsibilities |
| :--- | :--- |
| **`authentication`** | Secure session management, role-based login portals, password reset flows, brute-force lockout monitoring (5 attempts / 15-minute lock). |
| **`roles & permissions`** | Granular RBAC hierarchy with 25+ institutional permissions (`course:create`, `grade:submit`, `user:manage`, `audit:read`, etc.). |
| **`courses & curriculum`** | Hierarchical educational structure: Course &rarr; Modules &rarr; Lessons &rarr; Lesson Materials & Notes. Lifecycle states: `draft` &rarr; `pending_approval` &rarr; `published` &rarr; `archived`. |
| **`enrollment & progress`** | Manages course capacity, prerequisite validation, granular lesson completions, overall completion percentages, and completion status. |
| **`attendance`** | Instructor-led lecture attendance sessions, student attendance tracking (`present`, `late`, `absent`, `excused`), and percentage calculation. |
| **`question_bank`** | Reusable question repository supporting Multiple Choice (Single), Multi-select, True/False, and Short Answer with automated grading logic. |
| **`quizzes & examinations`** | Timed assessments with automated countdown timers, attempt tracking, instant scoring, feedback delivery, and passing thresholds. |
| **`assignments & grading`** | Due date tracking, file upload handling, rich-text submissions, instructor rubric grading, and weighted GPA calculations. |
| **`certificates`** | Local ReportLab vector PDF generator producing professional credentials with cryptographic 16-character verification codes. |
| **`gamification & skills`** | Student motivation engine: XP points, 5 level milestones, badge awards, daily login streaks, and course competency mastery. |
| **`analytics & reports`** | Aggregated institutional metrics, completion rates, GPA averages, active student counts, and CSV/JSON data export engines. |

---

## 3. Data Flow & Security Boundary

1. **Request Ingestion**: Incoming HTTP requests pass through security middleware enforcing `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff`, and `X-XSS-Protection`.
2. **Authentication & RBAC**: The `@login_required` and `@role_required("admin", "instructor", "student")` decorators inspect the active session, resolving the authenticated `User` and their assigned permissions.
3. **Portal Boundary Isolation**: If a student attempts to access an `/admin/*` or `/instructor/*` route, the access is immediately intercepted and forbidden with a standardized `403 Forbidden` error.
4. **Service Execution**: The route invokes the appropriate domain service method. Services enforce input validation (`core/validators.py`) and raise domain exceptions (`core/exceptions.py`).
5. **Database Unit of Work**: Changes are staged via `get_session()` and committed atomically. On error, rollback is triggered automatically.
6. **Audit & Event Dispatching**: Domain events trigger the `EventDispatcher`, recording immutable audit trail entries in `AuditLog` and evaluating gamification badge criteria asynchronously.

---

## 4. Vector PDF Rendering Pipeline

The certificate generation engine (`certificates/services.py`) utilizes **ReportLab** to build crisp, scalable, vector PDF certificates without any external network calls:
* Custom color palette matching the LMS brand (Deep Navy `#1a365d`, Slate `#4a5568`, Gold `#d69e2e`).
* Double ornamental vector borders with corner rosettes.
* Dynamic typography scaling for student name, course title, and completion date.
* Unique verification code: `CERT-<UUID_HASH[:12]>` embedded directly onto the certificate.
* Public verification endpoint `/verify` allows employers and institutions to validate credentials instantly.
