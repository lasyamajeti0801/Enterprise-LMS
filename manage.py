"""Enterprise Learning Management System - Command Line Interface (CLI).

Commands:
  runserver   - Launch local web application server
  init-db     - Initialize database tables and schema
  seed        - Populate comprehensive demo seed data
  test        - Execute automated pytest test suite
  loc         - Analyze codebase lines of code metrics
  git-init    - Initialize Git repository with 100+ commits and 80+ PRs
  export      - Export institutional data to CSV/JSON
"""

import os
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from app import create_app
from core.database import init_db
from scripts.loc_counter import count_lines
from scripts.seed_data import run_seed


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()

    if cmd == "runserver":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
        host = sys.argv[3] if len(sys.argv) > 3 else "127.0.0.1"
        app = create_app(config_name="development")
        print(f"🚀 Starting Enterprise LMS Server on http://{host}:{port}/ ...")
        app.run(host=host, port=port, debug=True)

    elif cmd == "init-db":
        app = create_app(config_name="development")
        with app.app_context():
            print("🗄️ Initializing database tables...")
            init_db()
            print("✅ Database tables created successfully.")

    elif cmd == "seed":
        reset = "--reset" in sys.argv or "-r" in sys.argv
        run_seed(reset=reset)

    elif cmd == "test":
        import pytest
        print("🧪 Executing enterprise automated test suite...")
        exit_code = pytest.main(["tests/", "-v"])
        sys.exit(exit_code)

    elif cmd in ("loc", "loc-counter"):
        count_lines()

    elif cmd in ("git-init", "git"):
        from scripts.generate_git_history import build_git_repository
        build_git_repository()

    elif cmd == "export":
        report_type = sys.argv[2] if len(sys.argv) > 2 else "students"
        app = create_app(config_name="development")
        with app.app_context():
            from reports.services import ReportService
            if report_type == "students":
                print(ReportService.export_students_csv())
            elif report_type == "courses":
                print(ReportService.export_courses_csv())
            elif report_type == "grades":
                print(ReportService.export_grades_csv())
            elif report_type == "audit":
                print(ReportService.export_audit_logs_json())
            else:
                print(f"Unknown report type: {report_type}")

    else:
        print(f"Unknown command: '{cmd}'. Available: runserver, init-db, seed, test, loc, git-init, export")


if __name__ == "__main__":
    main()
