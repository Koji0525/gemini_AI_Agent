#!/usr/bin/env python3
"""
必須コンポーネント問題の解決を確認
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from agents.integration_controller_v45_fixed import \
        FixedIntegrationControllerV45

    print("🔍 必須コンポーネント問題解決の確認")
    print("=" * 60)

    # コントローラーを初期化
    controller = FixedIntegrationControllerV45()

    # コンポーネント状態を確認
    print("\n📊 コンポーネント状態確認:")
    for name, component in controller.components.items():
        status = "✅" if component else "❌"
        print(f"  {status} {name}: {type(component).__name__}")

    # 必須コンポーネントの確認
    required_components = ["data_accessor", "smart_engine"]
    missing_components = [key for key in required_components if not controller.components.get(key)]

    if not missing_components:
        print("\n🎉 必須コンポーネント問題は解決しました！")
        print("✅ すべての必須コンポーネントが正常にロードされています")
    else:
        print(f"\n❌ 必須コンポーネントが不足しています: {missing_components}")

    # システム健全性チェック
    print("\n🩺 システム健全性確認:")
    health_status = controller.check_system_health()

    if health_status >= 0.8:
        print("✅ システムは健全です")
    elif health_status >= 0.5:
        print("⚠️ システムに軽微な問題があります")
    else:
        print("❌ システムに重大な問題があります")

except Exception as e:
    print(f"❌ 確認エラー: {e}")
    import traceback

    traceback.print_exc()
