# Enterprise Learning Management System - API & Route Design

This document details the route contracts, HTTP endpoints, role authorizations, and data interactions across the Enterprise LMS blueprints.

---

## 🧭 Route Blueprint Overview

```
+--------------------------------------------------------------------------+
|                               ROUTES MAP                                 |
+-------------------+--------------------+---------------------------------+
| Blueprint         | URL Prefix         | Target Audience / Role          |
+-------------------+--------------------+---------------------------------+
| auth_bp           | /auth              | Public & Authenticated Users    |
| admin_bp          | /admin             | SuperAdmin (Role: admin)        |
| instructor_bp     | /instructor        | Faculty & Staff (Role: instructor)|
| student_bp        | /student           | Students (Role: student)        |
| common_bp         | /                  | Common & Verification Services  |
+-------------------+--------------------+---------------------------------+
```

---

## 1. Authentication Endpoints (`/auth`)

| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET, POST` | `/auth/login` | Public | Role portal login (`?portal=admin\|instructor\|student`) |
| `GET, POST` | `/auth/register` | Public | Self-registration for new students |
| `GET` | `/auth/logout` | Authenticated | Clears session, resets auth tokens, redirects to landing |
| `GET, POST` | `/auth/forgot-password` | Public | Initiates password reset token generation |
| `GET, POST` | `/auth/reset-password/<token>` | Public | Validates reset token and sets new password |

---

## 2. Admin Management Endpoints (`/admin`)

*Strictly protected by `@role_required("admin")`*

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/admin/dashboard` | Executive KPIs (Users, Courses, Revenue, Pass Rates, Activity) |
| `GET` | `/admin/users` | User management registry with search, role filters, and status toggles |
| `POST` | `/admin/users/create` | Provision new administrator, instructor, or student accounts |
| `POST` | `/admin/users/<id>/status` | Toggle user status (`active`, `suspended`, `locked`) |
| `GET` | `/admin/courses` | Institutional course registry and approval review queue |
| `POST` | `/admin/courses/<id>/approve` | Approve and publish pending faculty course proposals |
| `GET` | `/admin/instructors` | Instructor credentials and governance portal |
| `POST` | `/admin/instructors/<id>/status`| Approve or review faculty profiles |
| `GET` | `/admin/audit-logs` | Immutable audit trail query explorer |
| `GET, POST`| `/admin/settings` | Global institutional platform configuration parameters |
| `GET` | `/admin/reports` | Institutional data reporting center and export triggers |
| `GET` | `/admin/reports/export/<type>` | Stream CSV / JSON formatted data exports |

---

## 3. Instructor Portal Endpoints (`/instructor`)

*Strictly protected by `@role_required("instructor")`*

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/instructor/dashboard` | Faculty overview (Assigned courses, active students, pending grading) |
| `GET, POST` | `/instructor/courses` | Course catalog authoring and creation wizard |
| `GET, POST` | `/instructor/courses/<id>/curriculum` | Tree builder for Modules, Lessons, and Study Materials |
| `GET, POST` | `/instructor/courses/<id>/assignments` | Create and manage coursework assignments and grading rubrics |
| `GET, POST` | `/instructor/submissions/<id>/grade` | Grade student work with letter grade, score, and feedback |
| `GET, POST` | `/instructor/courses/<id>/quizzes` | Build timed quizzes and link question bank items |
| `GET, POST` | `/instructor/courses/<id>/attendance` | Schedule attendance sessions and record student presence |
| `GET` | `/instructor/courses/<id>/gradebook` | Comprehensive course gradebook with calculated averages |

---

## 4. Student Portal Endpoints (`/student`)

*Strictly protected by `@role_required("student")`*

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/student/dashboard` | Student home (Active courses, XP level, streak, due dates) |
| `GET` | `/student/catalog` | Browse accredited courses with one-click enrollment |
| `POST` | `/student/enroll/<course_id>` | Enroll in a course (enforces capacity limits) |
| `GET` | `/student/learn/<course_id>` | Split-view interactive course learning player |
| `POST` | `/student/learn/<course_id>/complete/<lesson_id>` | Mark lesson as completed and advance course progress |
| `GET, POST` | `/student/assignments/<id>/submit` | Submit coursework assignment with rich text or file upload |
| `GET` | `/student/quizzes/<id>/take` | Interactive timed quiz runner with auto-countdown |
| `POST` | `/student/quizzes/<id>/submit` | Submit quiz attempt and calculate immediate results |
| `GET` | `/student/quizzes/attempts/<id>/result` | Detailed quiz evaluation breakdown and explanations |
| `GET` | `/student/grades` | Academic transcript, GPA calculations, and course grades |
| `GET` | `/student/certificates` | View and download generated vector PDF certificates |
| `GET` | `/student/certificates/<id>/download`| Stream local vector PDF certificate |
| `GET` | `/student/gamification` | Gamification hub, badges, XP levels, and leaderboards |

---

## 5. Common & Public Endpoints (`/`)

| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Public | 3-Card Portal Landing Page |
| `GET` | `/verify` | Public | Public certificate cryptographic validation search |
| `GET, POST` | `/discussions/<course_id>` | Enrolled | Course discussion forums and instructor answers |
| `GET` | `/calendar` | Authenticated | Institutional academic calendar and deadlines |
| `GET` | `/notifications` | Authenticated | User notification inbox with unread badges |
| `POST` | `/notifications/<id>/read` | Authenticated | Mark notification as read |
