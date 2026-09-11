# Enterprise Learning Management System - Security & Compliance Guide

This document outlines the security architecture, authentication mechanisms, access controls, data protection policies, and vulnerability mitigations implemented in the Enterprise LMS.

---

## 🛡️ Security Architecture Overview

The system is engineered following **Defense-in-Depth** and zero-trust boundary principles:

```
+--------------------------------------------------------------------------+
|                            SECURITY PERIMETER                            |
+--------------------------------------------------------------------------+
| 1. HTTP Security Headers (X-Frame-Options, X-Content-Type-Options, etc.) |
| 2. Session Security (HttpOnly, SameSite=Lax, Cryptographic Signatures)  |
| 3. Brute Force Protection (5 Failed Attempts -> 15-Minute Account Lock)  |
| 4. PBKDF2 Password Hashing (200,000 SHA-256 Iterations + Salt)          |
| 5. Granular RBAC Boundary Gates (@role_required("admin|instructor|..."))|
| 6. Parameterized SQL Queries (SQLAlchemy 2.0 ORM - Zero SQL Injection)   |
| 7. Input Validation & HTML Sanitization (Strict format constraints)     |
| 8. Immutable Audit Trail Logging (Security-sensitive event persistence)  |
+--------------------------------------------------------------------------+
```

---

## 🔒 1. Cryptographic Password Hashing

* **Algorithm**: PBKDF2 with SHA-256 HMAC.
* **Work Factor**: 200,000 hash iterations.
* **Salt Management**: Cryptographically secure 16-byte random salt generated per user.
* **Implementation**: Managed in `core/security.py` using `werkzeug.security`. Raw passwords are never stored in plaintext or persisted to disk.

---

## 🚪 2. Brute Force Attack Mitigation

* Failed login attempts are recorded against the user record in `User.failed_attempts`.
* If a user exceeds **5 consecutive failed attempts**, the account is locked for **15 minutes** (`User.locked_until = get_utc_now() + timedelta(minutes=15)`).
* Login attempts during the lockout window return a descriptive error message and log a security audit event.

---

## 🏰 3. Role-Based Access Control (RBAC)

The LMS enforces strict RBAC matrices across four primary roles:
1. **`admin`**: Full institutional access (Users, Audit Logs, Settings, Approvals).
2. **`instructor`**: Course creation, curriculum management, quiz builder, grading, and attendance.
3. **`student`**: Course catalog, learning player, quiz participation, assignments, certificates.
4. **`guest`**: Public catalog browsing, landing portal navigation, certificate verification.

Cross-role access violations are intercepted by route decorators and immediately yield a `403 Forbidden` response.

---

## 🛡️ 4. OWASP Top 10 Mitigations

| Vulnerability | Platform Defense Strategy |
| :--- | :--- |
| **A01: Broken Access Control** | Explicit `@role_required` decorators on every privileged endpoint; boundary separation by portal. |
| **A02: Cryptographic Failures** | PBKDF2-HMAC-SHA256 password hashing; SHA-256 certificate verification codes. |
| **A03: Injection (SQL / Command)** | 100% Parameterized queries via SQLAlchemy 2.0 ORM; zero dynamic SQL concatenation. |
| **A05: Security Misconfiguration** | Hardened response headers (`X-Frame-Options: SAMEORIGIN`, `X-XSS-Protection: 1; mode=block`). |
| **A07: Identification & Auth Failures** | Account lockout protection after 5 failed attempts; secure session cookie signing. |
| **A09: Security Logging & Monitoring** | Structured logging in `logs/lms.log` and persistent database `AuditLog` records. |
