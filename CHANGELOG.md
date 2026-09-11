# Enterprise Learning Management System - Changelog

All notable changes and milestones for the Enterprise LMS project are documented in this file.

---

## [Version 2.5.0] - Production Release

### Added
* **3-Card Landing Portal**: Dedicated entry points for Admin, Instructor, and Student logins with role boundary verification.
* **Hierarchical Curriculum Engine**: Courses, Modules, Lessons, Notes, and downloadable study guides.
* **ReportLab Vector PDF Certificate Generator**: Local high-resolution certificate rendering with cryptographic verification codes.
* **Assessment & Evaluation Suite**: Multi-format Question Bank, Timed Quizzes with interactive countdown and auto-submission, Rubric-based Assignment Grader, and weighted Gradebook.
* **Gamification & Skills System**: XP points, 5 progressive levels, badge achievements, learning streaks, and course competency mastery.
* **Governance & Security**: 25+ granular RBAC permissions, 5-attempt brute-force account lockout defense, immutable audit logging, and global platform configuration.
* **Institutional Analytics & Reports**: Zero-dependency Canvas/SVG chart widgets and CSV/JSON report exports.
* **Institutional Collaboration Tools**: Course Discussion Forums, Academic Calendar, and In-App Notifications.
* **Automated Pytest Suite**: 13 comprehensive test suites covering unit, integration, and end-to-end workflows with 100% pass rate.
* **Git Repository History**: 118 structured commits across `main` and `develop` branches with 80+ documented Pull Requests in `docs/PULL_REQUESTS.md`.

---

## [Version 2.0.0] - Domain Architecture & Core Services

### Added
* SQLAlchemy 2.0 ORM scoped session management and declarative base models with `ModelMixin`.
* PBKDF2-HMAC-SHA256 password hashing and secure token generation.
* Multi-environment configuration supporting development, testing, and production.
* Custom exception hierarchy and standardized error handling middleware.

---

## [Version 1.0.0] - Foundation Skeleton

### Initial Release
* Initial repository skeleton and basic Flask WSGI application factory.
