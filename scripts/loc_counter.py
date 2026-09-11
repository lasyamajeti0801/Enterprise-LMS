"""Enterprise Code Metric & Lines of Code (LOC) Analyzer."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def count_lines():
    """Analyze Python source lines, templates, CSS, JS, and documentation."""
    stats = {
        "python": {"files": 0, "lines": 0, "blank": 0, "comment": 0, "code": 0},
        "templates": {"files": 0, "lines": 0},
        "styles": {"files": 0, "lines": 0},
        "scripts_js": {"files": 0, "lines": 0},
        "docs": {"files": 0, "lines": 0},
    }

    module_breakdown = {}

    for root, dirs, files in os.walk(BASE_DIR):
        if ".git" in root or "__pycache__" in root or ".pytest_cache" in root or "uploads" in root or "logs" in root:
            continue

        rel_dir = os.path.relpath(root, BASE_DIR)
        top_module = rel_dir.split(os.sep)[0] if rel_dir != "." else "root"

        for f in files:
            file_path = os.path.join(root, f)
            ext = os.path.splitext(f)[1].lower()

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
                    lines = fp.readlines()
            except Exception:
                continue

            total = len(lines)

            if ext == ".py":
                stats["python"]["files"] += 1
                stats["python"]["lines"] += total
                blank = sum(1 for l in lines if not l.strip())
                comment = sum(1 for l in lines if l.strip().startswith("#"))
                code = total - blank - comment
                stats["python"]["blank"] += blank
                stats["python"]["comment"] += comment
                stats["python"]["code"] += code

                module_breakdown[top_module] = module_breakdown.get(top_module, 0) + total

            elif ext == ".html":
                stats["templates"]["files"] += 1
                stats["templates"]["lines"] += total
            elif ext == ".css":
                stats["styles"]["files"] += 1
                stats["styles"]["lines"] += total
            elif ext == ".js":
                stats["scripts_js"]["files"] += 1
                stats["scripts_js"]["lines"] += total
            elif ext == ".md":
                stats["docs"]["files"] += 1
                stats["docs"]["lines"] += total

    print("================================================================")
    print("      ENTERPRISE LMS - CODEBASE SIZE & METRICS REPORT           ")
    print("================================================================")
    print(f" Python Source Files   : {stats['python']['files']} files")
    print(f" Python Total Lines    : {stats['python']['lines']:,} lines")
    print(f" Python Code Lines     : {stats['python']['code']:,} lines")
    print(f" Python Comment Lines  : {stats['python']['comment']:,} lines")
    print(f" Python Blank Lines    : {stats['python']['blank']:,} lines")
    print("----------------------------------------------------------------")
    print(f" Jinja2 HTML Templates : {stats['templates']['files']} files | {stats['templates']['lines']:,} lines")
    print(f" CSS Design System     : {stats['styles']['files']} files | {stats['styles']['lines']:,} lines")
    print(f" JavaScript Engines    : {stats['scripts_js']['files']} files | {stats['scripts_js']['lines']:,} lines")
    print(f" Markdown Documentation: {stats['docs']['files']} files | {stats['docs']['lines']:,} lines")
    print("================================================================")
    print(" Module Breakdown (Lines of Python Code):")
    for mod, count in sorted(module_breakdown.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {mod:20s}: {count:,} lines")
    print("================================================================")


if __name__ == "__main__":
    count_lines()
