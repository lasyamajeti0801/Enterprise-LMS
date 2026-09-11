# Enterprise Learning Management System - Installation Guide

This guide details how to install and configure the Enterprise LMS on **Windows, macOS, and Linux** systems.

---

## 📋 System Requirements

* **Python Version**: Python 3.11.x or Python 3.12.x
* **Operating System**: Windows 10/11, macOS 12+ (Monterey, Ventura, Sonoma), or Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+)
* **Disk Space**: ~250 MB for source code, virtual environment, and local SQLite database
* **RAM**: 512 MB minimum (1 GB recommended for enterprise load)
* **External APIs**: **NONE** (100% self-contained local execution)

---

## 🚀 Installation by Operating System

### 1. Windows Installation (PowerShell)

```powershell
# Step 1: Open PowerShell and navigate to your workspace directory
cd "c:\Users\DELL\OneDrive\Desktop\learning system"

# Step 2: Ensure Python 3.12 is installed and accessible
python --version

# Step 3: Create a clean virtual environment
python -m venv venv

# Step 4: Activate the virtual environment
.\venv\Scripts\Activate.ps1
# (If script execution policy prevents activation, run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)

# Step 5: Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Step 6: Verify package installation
pip list
```

### 2. macOS & Linux Installation (Bash / Zsh)

```bash
# Step 1: Clone or navigate to the project directory
cd "learning system"

# Step 2: Verify Python version
python3 --version

# Step 3: Create a virtual environment
python3 -m venv venv

# Step 4: Activate virtual environment
source venv/bin/activate

# Step 5: Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📦 Required Python Packages

The application relies solely on standard, well-maintained, open-source libraries:

| Package | Purpose |
| :--- | :--- |
| `Flask>=3.0.0` | Core WSGI web application framework and routing |
| `SQLAlchemy>=2.0.0` | High-performance ORM and database engine |
| `ReportLab>=4.0.0` | Vector-accurate local PDF certificate generation |
| `Werkzeug>=3.0.0` | Cryptographic password utilities and security middleware |
| `Jinja2>=3.1.0` | Server-rendered modern HTML templates |
| `pytest>=8.0.0` | Automated unit, integration, and E2E test suite |
| `dulwich>=0.21.0` | Pure-Python Git repository manager |

---

## 🛠️ Verifying Installation

To verify that the installation succeeded without errors, run the integrated test suite:

```bash
python -m pytest tests/ -v
```

If all 13 test suites pass, your environment is ready for database seeding and running the application.
