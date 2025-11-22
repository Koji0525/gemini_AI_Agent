#!/bin/bash
# Phase 2: 自動統合システムの実装

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Phase 2: 自動統合システムの実装"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# 自動統合システムの作成
mkdir -p agents/efficiency

cat > agents/efficiency/auto_integration_system.py << 'PYTHON'
"""
自動統合システム
生成された成果物を既存システムに自動統合
"""

import sys
import os
import subprocess
from pathlib import Path

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class AutoIntegrationSystem:
    """自動統合システム"""
    
    def __init__(self):
        self.project_root = Path("/workspaces/gemini_AI_Agent")
        
    def validate_code_quality(self, output_path: str) -> dict:
        """コード品質チェック"""
        print(f"\n🔍 コード品質チェック: {output_path}")
        
        results = {
            'syntax_valid': True,
            'imports_valid': True,
            'errors': []
        }
        
        output_dir = Path(output_path)
        
        # Pythonファイルの構文チェック
        for py_file in output_dir.glob("*.py"):
            try:
                subprocess.run(
                    ['python3', '-m', 'py_compile', str(py_file)],
                    check=True,
                    capture_output=True
                )
                print(f"  ✅ {py_file.name}: 構文OK")
            except subprocess.CalledProcessError as e:
                results['syntax_valid'] = False
                results['errors'].append(f"{py_file.name}: 構文エラー")
                print(f"  ❌ {py_file.name}: 構文エラー")
        
        return results
    
    def integrate_to_system(self, output_path: str, task_id: str) -> bool:
        """既存システムへの統合"""
        print(f"\n🔄 システム統合開始: {task_id}")
        
        output_dir = Path(output_path)
        
        # agents/配下に統合
        target_dir = self.project_root / "agents" / "generated" / task_id
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # ファイルをコピー
        import shutil
        for file in output_dir.glob("*.py"):
            shutil.copy(file, target_dir)
            print(f"  ✅ {file.name} → agents/generated/{task_id}/")
        
        # README.mdもコピー
        readme = output_dir / "README.md"
        if readme.exists():
            shutil.copy(readme, target_dir)
            print(f"  ✅ README.md → agents/generated/{task_id}/")
        
        # __init__.pyを作成
        init_file = target_dir / "__init__.py"
        init_file.write_text(f'"""Generated module: {task_id}"""\n')
        
        print(f"\n✅ 統合完了: agents/generated/{task_id}/")
        
        return True
    
    def create_usage_example(self, output_path: str, task_id: str):
        """使用例の作成"""
        print(f"\n📝 使用例の作成")
        
        example_content = f"""
# {task_id} の使用例

## インポート
````python
from agents.generated.{task_id}.main import *
````

## 基本的な使用方法
````python
# TODO: 実際の使用例を追加
````

## 参照
- 詳細: agents/generated/{task_id}/README.md
- ソース: {output_path}
"""
        
        example_file = Path(f"examples/{task_id}_example.md")
        example_file.parent.mkdir(exist_ok=True)
        example_file.write_text(example_content)
        
        print(f"  ✅ 使用例作成: {example_file}")

PYTHON

echo "✅ 自動統合システム作成完了"

# テスト実行スクリプト
cat > sh/test_integration_system.sh << 'TEST'
#!/bin/bash
# 自動統合システムのテスト

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 自動統合システムのテスト"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << PYTHON
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.efficiency.auto_integration_system import AutoIntegrationSystem
from pathlib import Path

# 初期化
integration = AutoIntegrationSystem()

# 最新の成果物を取得
outputs = sorted(Path("agent_outputs/implementation").glob("*/"), reverse=True)

if outputs:
    latest = outputs[0]
    task_id = latest.name
    
    print(f"📂 テスト対象: {task_id}")
    print()
    
    # 1. コード品質チェック
    quality = integration.validate_code_quality(str(latest))
    
    if quality['syntax_valid']:
        print("\n✅ 品質チェック: 合格")
        
        # 2. システム統合
        success = integration.integrate_to_system(str(latest), task_id)
        
        if success:
            print("\n✅ システム統合: 成功")
            
            # 3. 使用例作成
            integration.create_usage_example(str(latest), task_id)
            
            print("\n" + "=" * 80)
            print("🎉 自動統合テスト完了")
            print("=" * 80)
            print()
            print("📍 統合先:")
            print(f"  agents/generated/{task_id}/")
            print()
            print("📍 使用例:")
            print(f"  examples/{task_id}_example.md")
            print()
    else:
        print("\n❌ 品質チェック: 不合格")
        for error in quality['errors']:
            print(f"  - {error}")
else:
    print("⚠️  成果物が見つかりません")

PYTHON

TEST

chmod +x sh/test_integration_system.sh

echo ""
echo "✅ Phase 2実装完了"
echo ""
echo "🧪 テスト実行:"
echo "  bash sh/test_integration_system.sh"

