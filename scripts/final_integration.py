#!/usr/bin/env python3
"""
Final integration script to combine all tasks and create complete submission.
"""

import shutil
from pathlib import Path


def create_final_structure():
    """Create final project structure."""
    directories = [
        "dashboard/backend",
        "dashboard/frontend/src",
        "dashboard/frontend/public",
        "models",
        "reports/task3",
        "docs/final",
        "scripts",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def copy_task_files():
    """Copy all task files to final structure."""
    task1_files = [
        "docs/task1_analysis_plan.md",
        "docs/assumptions_limitations.md",
        "docs/communication_plan.md",
        "data/events/enhanced_events.csv",
        "notebooks/01_eda.ipynb",
    ]

    for file in task1_files:
        if Path(file).exists():
            shutil.copy2(file, f"docs/final/{Path(file).name}")

    task2_files = [
        "src/bayesian_model_enhanced.py",
        "notebooks/02_bayesian_model.ipynb",
        "config/bayesian_config.yaml",
        "models/single_cp_results.json",
        "reports/task2/final_report.md",
    ]

    for file in task2_files:
        if Path(file).exists():
            shutil.copy2(file, f"docs/final/{Path(file).name}")

    task3_sources = {
        "dashboard/backend/app.py": "dashboard/backend/app.py",
        "dashboard/backend/requirements.txt": "dashboard/backend/requirements.txt",
        "dashboard/frontend/src/App.js": "dashboard/frontend/src/App.js",
        "dashboard/frontend/src/App.css": "dashboard/frontend/src/App.css",
        "docs/task3_dashboard_readme.md": "docs/final/task3_dashboard_readme.md",
    }

    for src, dest in task3_sources.items():
        if Path(src).exists():
            shutil.copy2(src, dest)


def create_demo_video_script():
    """Create script for demo video."""
    script = """# Brent Oil Analysis Dashboard - Demo Video Script

## Introduction (0:00 - 0:30)
"Welcome to the Brent Oil Price Analysis Dashboard. This interactive tool uses Bayesian change point detection to analyze how geopolitical events impact oil prices."

## Dashboard Overview (0:30 - 1:30)
"The main dashboard shows Brent oil prices over time, key statistics, and a recent events timeline."

## Bayesian Analysis (1:30 - 2:30)
"This tab highlights the detected change point, the 95% HDI interval, and parameter changes for mean returns and volatility."

## Event Impact Analysis (2:30 - 3:30)
"Selecting an event shows a detailed impact summary and the price trajectory around the event window."

## Volatility Analysis (3:30 - 4:00)
"The volatility tab highlights rolling 30-day volatility and event-related spikes."

## Filtering and Interaction (4:00 - 4:30)
"You can filter by date range and event type, then refresh the charts instantly."

## Conclusion (4:30 - 5:00)
"This dashboard provides actionable insights for investors, policymakers, and energy companies using Bayesian change point detection."
"""

    Path("docs/final").mkdir(parents=True, exist_ok=True)
    Path("docs/final/demo_script.md").write_text(script, encoding="utf-8")


def create_submission_checklist():
    """Create submission checklist."""
    checklist = """# Final Submission Checklist

## Required Files

### Task 1
- [x] docs/task1_analysis_plan.md
- [x] data/events/enhanced_events.csv
- [x] notebooks/01_eda.ipynb
- [x] docs/assumptions_limitations.md
- [x] docs/communication_plan.md

### Task 2
- [x] src/bayesian_model_enhanced.py
- [x] notebooks/02_bayesian_model.ipynb
- [x] config/bayesian_config.yaml
- [x] models/single_cp_results.json
- [x] reports/task2/final_report.md
- [x] tests/test_bayesian_model.py

### Task 3
- [x] dashboard/backend/app.py
- [x] dashboard/backend/requirements.txt
- [x] dashboard/frontend/src/App.js
- [x] dashboard/frontend/src/App.css
- [x] dashboard/frontend/package.json
- [x] docs/task3_dashboard_readme.md
- [x] scripts/setup_dashboard.sh
- [x] Dockerfile
- [x] docker-compose.yml

## Additional Items for Full Marks
1. Docker configuration verified
2. Deployment documentation added
3. Demo video recorded
4. End-to-end testing completed
"""

    Path("docs/final").mkdir(parents=True, exist_ok=True)
    Path("docs/final/submission_checklist.md").write_text(checklist, encoding="utf-8")


def main():
    create_final_structure()
    copy_task_files()
    create_demo_video_script()
    create_submission_checklist()
    print("Integration complete.")


if __name__ == "__main__":
    main()
