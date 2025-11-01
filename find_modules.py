#!/usr/bin/env python3
"""
モジュール探索スクリプト
"""
import sys
import importlib
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

modules_to_find = [
    "wordpress.wp_plugin_manager_v01_add_execute",
    "wordpress.wp_dev.wp_taxonomy_agent_v01_basic",
    "agents.wordpress.wp_design_generator_v01_fix_browser",
    "wordpress.wp_plugin_manager",
    "wordpress.wp_dev.wp_taxonomy_agent",
]

print("🔍 モジュール探索開始")
print("=" * 50)

for module_name in modules_to_find:
    try:
        spec = importlib.util.find_spec(module_name)
        if spec:
            print(f"✅ {module_name}")
            print(f"   場所: {spec.origin}")
            print(f"   ローダー: {spec.loader}")
        else:
            print(f"❌ {module_name} - モジュールが見つかりません")

            # 代替パスの探索
            alt_name = module_name.replace("_v01_", "-v01-")
            if alt_name != module_name:
                alt_spec = importlib.util.find_spec(alt_name)
                if alt_spec:
                    print(f"   💡 代替名発見: {alt_name}")
                    print(f"      場所: {alt_spec.origin}")

    except Exception as e:
        print(f"⚠️ {module_name} - 探索エラー: {e}")

print("\n📋 Pythonパス:")
for path in sys.path[:5]:  # 最初の5つだけ表示
    print(f"  - {path}")

print("\n📁 ファイル探索:")
import os

for root, dirs, files in os.walk("."):
    for file in files:
        if "taxonomy" in file or "plugin" in file:
            if file.endswith(".py") and "__pycache__" not in root:
                print(f"  - {os.path.join(root, file)}")
