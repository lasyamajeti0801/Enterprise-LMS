# Enterprise Learning Management System - Administrator Guide

This guide is for institutional administrators responsible for managing users, approving faculty course proposals, auditing security logs, configuring system parameters, and exporting analytics reports.

---

## 🔑 Accessing the Admin Portal

1. Navigate to the landing page and click **Admin Portal** (or visit `/auth/login?portal=admin`).
2. Enter default admin credentials:
   - **Username**: `admin`
   - **Password**: `adminpassword123`
3. Upon authentication, you will be directed to the **Admin Executive Dashboard** (`/admin/dashboard`).

---

## 📊 1. Executive Dashboard KPIs

The Administrator Dashboard provides immediate visibility into institutional metrics:
* **Total Users**: Breakdown of students, instructors, and administrators.
* **Active Courses**: Published vs. pending proposal courses.
* **Enrollment Metrics**: Total enrollments and active learning sessions.
* **System Health**: Active sessions, database size, and audit log events.

---

## 👥 2. User Governance & Role Management

Navigate to **User Management** (`/admin/users`):
* **Create Users**: Provision accounts with assigned roles (`admin`, `instructor`, `student`).
* **Search & Filter**: Search by name or email, and filter by status (`active`, `suspended`, `locked`).
* **Account Status Controls**: Suspend users violating institutional policy or unlock accounts locked by brute-force triggers.

---

## 📚 3. Course Governance & Approvals

Navigate to **Course Management** (`/admin/courses`):
* Review courses submitted by faculty.
* Inspect course descriptions, syllabus structure, and instructor assignments.
* Click **Approve Course** to transition a course from `pending_approval` to `published`, making it visible in the student catalog.

---

## 📜 4. Security Audit Trail

Navigate to **Audit Logs** (`/admin/audit-logs`):
* Inspect an immutable record of all critical system actions:
  - User logins, failed authentication attempts, and password resets.
  - Course status transitions (creation, approval, archiving).
  - Grade modifications and certificate issuances.
* Filter logs by action type, user, or IP address.

---

## 📈 5. Institutional Reporting & Exports

Navigate to **Reports Center** (`/admin/reports`):
* Generate and stream structured exports:
  - **Enrollments Report**: CSV / JSON export of student course enrollments and progress.
  - **Grades & Transcripts**: Institutional GPA distributions and final grades.
  - **Audit Logs**: Security compliance archive exports.

---

## ⚙️ 6. System Settings

Navigate to **System Settings** (`/admin/settings`):
* Configure platform parameters:
  - **Platform Name**: Customize institutional branding.
  - **Allow Self-Registration**: Toggle public student registration.
  - **Passing Grade Threshold**: Set institutional default passing percentage.
  - **Certificate Code Prefix**: Customize cryptographic certificate prefixes (e.g., `CERT-`).
