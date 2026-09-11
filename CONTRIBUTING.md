# Enterprise Learning Management System - Contributing Guidelines

Thank you for your interest in contributing to the Enterprise Learning Management System. This repository maintains enterprise-grade coding standards, structured code reviews, and automated CI pipelines.

---

## 🏗️ Development Standards

1. **Python Version**: Python 3.12 syntax, type hints, and standard idioms.
2. **Domain-Driven Modularity**:
   - Keep business logic in `services.py` within each domain package.
   - Route handlers (`routes/*_routes.py`) should remain thin controllers.
   - Use `ModelMixin` for all database entities.
3. **Zero External Runtime APIs**:
   - Features must work 100% locally.
   - Do not introduce dependencies that require paid cloud keys or third-party web services.
4. **Code Aesthetics & UI**:
   - Follow the CSS custom property design system (`static/css/main.css`).
   - Use clean semantic HTML and modern accessible layouts.

---

## 🌿 Git Branching Strategy

We follow a structured Git branching model:
* **`main`**: Production-ready, stable releases.
* **`develop`**: Active integration branch.
* **`feature/<domain-action>`**: Feature branches (e.g., `feature/quizzes-timer-auto-submit`, `feature/pdf-certificate-qr`).
* **`bugfix/<issue-name>`**: Targeted fixes for identified issues.

---

## 🔄 Pull Request (PR) Workflow

1. Create a feature branch from `develop`.
2. Implement code changes with accompanying Pytest test suites.
3. Ensure all tests pass: `python -m pytest tests/ -v`.
4. Submit a Pull Request documenting:
   - Summary of changes
   - Domain components affected
   - Verification steps and automated test results
5. See [docs/PULL_REQUESTS.md](file:///c:/Users/DELL/OneDrive/Desktop/learning%20system/docs/PULL_REQUESTS.md) for examples of our 80+ documented Pull Requests.
