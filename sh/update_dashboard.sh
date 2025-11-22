#!/bin/bash
# ダッシュボード更新

cd /workspaces/gemini_AI_Agent

python3 << PYTHON
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.robustness.monitoring_dashboard import MonitoringDashboard

dashboard = MonitoringDashboard()
file_path = dashboard.generate_dashboard()

print(f"✅ ダッシュボード更新: {file_path}")

PYTHON

