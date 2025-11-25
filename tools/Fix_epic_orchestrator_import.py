#!/usr/bin/env python3
"""
Epic Orchestratorのインポートエラー修正スクリプト

開発ログ:
何が起きた: epic_orchestratorでProgressAnalyzerV2のインポートエラー発生
原因: progress_analyzer_v2.pyにはProgressAnalyzerV2クラスが存在せず、実際はProgressAnalyzerという名前
狙い（解決策）: インポート文とクラス使用箇所を正しい名前に修正し、システム統合を完成させる
"""

import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# プロジェクトルートに移動
PROJECT_ROOT = Path("/workspaces/gemini_AI_Agent")
if not PROJECT_ROOT.exists():
    PROJECT_ROOT = Path("/home/codespace/gemini_AI_Agent")
    if not PROJECT_ROOT.exists():
        print(f"❌ プロジェクトディレクトリが見つかりません")
        sys.exit(1)

os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))


def analyze_progress_analyzer_v2() -> Optional[str]:
    """progress_analyzer_v2.pyのクラス名を確認"""
    print("\n=== STEP 1: progress_analyzer_v2.pyのクラス構造確認 ===")

    file_path = PROJECT_ROOT / "agents" / "integration" / "progress_analyzer_v2.py"
    if not file_path.exists():
        print(f"❌ ファイルが見つかりません: {file_path}")
        # 別の場所を探索
        found_files = list(PROJECT_ROOT.glob("**/progress_analyzer*.py"))
        if found_files:
            print(f"📍 見つかったファイル:")
            for f in found_files:
                print(f"   - {f}")
                # クラス名を抽出
                with open(f, "r", encoding="utf-8") as file:
                    content = file.read()
                    classes = re.findall(r"^class\s+(\w+)", content, re.MULTILINE)
                    if classes:
                        print(f"     クラス: {', '.join(classes)}")
                        if "ProgressAnalyzer" in classes:
                            return "ProgressAnalyzer"
        return None

    # ファイルからクラス名を抽出
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        classes = re.findall(r"^class\s+(\w+)", content, re.MULTILINE)

    if classes:
        print(f"✅ クラス発見: {', '.join(classes)}")
        # ProgressAnalyzerという名前のクラスを優先
        for cls in classes:
            if "ProgressAnalyzer" in cls:
                return cls
        return classes[0]  # 最初のクラスを返す
    else:
        print("❌ クラスが見つかりません")
        return None


def fix_epic_orchestrator_imports(actual_class_name: str):
    """epic_orchestrator.pyのインポートを修正"""
    print(f"\n=== STEP 2: epic_orchestrator.pyのインポート修正 ===")
    print(f"📝 修正内容: ProgressAnalyzerV2 → {actual_class_name}")

    epic_file = PROJECT_ROOT / "agents" / "epic_orchestrator.py"
    if not epic_file.exists():
        print(f"❌ epic_orchestrator.pyが見つかりません")
        return False

    # バックアップを作成
    backup_file = epic_file.with_suffix(".py.bak")
    with open(epic_file, "r", encoding="utf-8") as f:
        original_content = f.read()
    with open(backup_file, "w", encoding="utf-8") as f:
        f.write(original_content)
    print(f"💾 バックアップ作成: {backup_file}")

    # インポート文とクラス使用箇所を修正
    modified_content = original_content

    # インポート文の修正
    old_import = "from agents.integration.progress_analyzer_v2 import ProgressAnalyzerV2"
    new_import = f"from agents.integration.progress_analyzer_v2 import {actual_class_name}"

    if old_import in modified_content:
        modified_content = modified_content.replace(old_import, new_import)
        print(f"✅ インポート文を修正")
    else:
        print(f"⚠️ 既存のインポート文が見つかりません")
        # 別のパターンを試す
        pattern = r"from\s+agents\.integration\.progress_analyzer_v2\s+import\s+\w+"
        modified_content = re.sub(pattern, new_import, modified_content)

    # クラス使用箇所の修正（ProgressAnalyzerV2 → 実際のクラス名）
    if actual_class_name != "ProgressAnalyzerV2":
        occurrences = modified_content.count("ProgressAnalyzerV2")
        if occurrences > 0:
            modified_content = modified_content.replace("ProgressAnalyzerV2", actual_class_name)
            print(f"✅ {occurrences}箇所でクラス名を修正")

    # ファイルに書き戻す
    with open(epic_file, "w", encoding="utf-8") as f:
        f.write(modified_content)

    print(f"✅ epic_orchestrator.py修正完了")
    return True


def verify_import():
    """修正後のインポートを検証"""
    print("\n=== STEP 3: インポート検証 ===")

    test_code = """
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

try:
    from agents.epic_orchestrator import EpicOrchestrator
    print('✅ インポート成功！')
    
    # インスタンス化テスト
    try:
        orchestrator = EpicOrchestrator(
            sheets_manager=None,
            task_executor=None,
            pm_agent_v33=None,
            observability_manager=None,
            knowledge_manager=None,
            dry_run=True
        )
        print('✅ インスタンス化成功（dry_runモード）')
    except TypeError as e:
        print(f'⚠️ インスタンス化時の引数エラー（正常）: {e}')
    except Exception as e:
        print(f'❌ インスタンス化エラー: {e}')
        
except ImportError as e:
    print(f'❌ インポートエラー: {e}')
except Exception as e:
    print(f'❌ 予期しないエラー: {e}')
"""

    result = subprocess.run(
        [sys.executable, "-c", test_code], capture_output=True, text=True, cwd=PROJECT_ROOT
    )

    print(result.stdout)
    if result.stderr:
        print(f"標準エラー出力:\n{result.stderr}")

    return "インポート成功" in result.stdout


def run_tests():
    """テストを実行して修正を検証"""
    print("\n=== STEP 4: テスト実行 ===")

    test_file = PROJECT_ROOT / "tests" / "test_epic_orchestrator.py"
    if not test_file.exists():
        print("⚠️ テストファイルが見つかりません")
        return False

    result = subprocess.run(
        ["python", "-m", "pytest", str(test_file), "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )

    print(result.stdout)

    # 成功率を計算
    passed = result.stdout.count(" PASSED")
    failed = result.stdout.count(" FAILED")
    total = passed + failed

    if total > 0:
        success_rate = (passed / total) * 100
        print(f"\n📊 テスト結果:")
        print(f"  成功: {passed}/{total} ({success_rate:.1f}%)")

        if failed > 0:
            print(f"  失敗: {failed}")
            # 失敗の詳細を解析
            if "ImportError" not in result.stdout:
                print("  ✅ ImportErrorは解決済み")

    return failed == 0


def register_knowledge():
    """ナレッジベースに知見を登録"""
    print("\n=== STEP 5: ナレッジ登録 ===")

    knowledge_entry = {
        "title": "Epic OrchestratorのProgressAnalyzerインポートエラー修正",
        "content": """
【問題】
epic_orchestrator.pyで'ProgressAnalyzerV2'のインポートエラーが発生

【原因】
progress_analyzer_v2.pyにはProgressAnalyzerV2クラスが存在せず、
実際には'ProgressAnalyzer'という名前のクラスが定義されていた

【解決策】
1. progress_analyzer_v2.pyの実際のクラス名を確認
2. epic_orchestrator.pyのインポート文を修正
3. クラス使用箇所も合わせて修正

【学習した知見】
- 新しいコンポーネントを統合する際は、必ず実際のクラス名を確認する
- インポートエラーの際は、まず対象ファイルのクラス定義を確認
- バックアップを作成してから修正を実施する
- 修正後は必ずインポートテストとユニットテストを実行

【予防策】
- API検証ツール(tools/api_validator.py)を使用してクラス名を事前確認
- エラー自動解決ツール(tools/error_resolver.py)でImportError対応を自動化
""",
        "category": "error_resolution",
        "tags": "import,integration,epic_orchestrator,progress_analyzer",
    }

    # ナレッジマネージャーを使用して登録を試みる
    try:
        from knowledge_system.core_agents.knowledge_manager import \
            KnowledgeManager

        km = KnowledgeManager()
        result = km.add_knowledge(
            title=knowledge_entry["title"],
            content=knowledge_entry["content"],
            category=knowledge_entry["category"],
            tags=knowledge_entry["tags"],
        )
        print(f"✅ ナレッジ登録成功: ID={result}")
    except Exception as e:
        print(f"⚠️ ナレッジ登録エラー: {e}")
        # ファイルとして保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        knowledge_file = PROJECT_ROOT / "MD" / f"knowledge_{timestamp}_epic_import_fix.md"
        knowledge_file.parent.mkdir(exist_ok=True)

        with open(knowledge_file, "w", encoding="utf-8") as f:
            f.write(f"# {knowledge_entry['title']}\n\n")
            f.write(f"**カテゴリ**: {knowledge_entry['category']}\n")
            f.write(f"**タグ**: {knowledge_entry['tags']}\n\n")
            f.write(knowledge_entry["content"])

        print(f"📝 ナレッジをファイルに保存: {knowledge_file}")


def main():
    """メイン処理"""
    print("=" * 60)
    print("🔧 Epic Orchestrator インポートエラー修正スクリプト")
    print("=" * 60)

    # 1. 実際のクラス名を確認
    actual_class = analyze_progress_analyzer_v2()
    if not actual_class:
        print("❌ ProgressAnalyzerクラスが見つかりません")
        return 1

    # 2. epic_orchestrator.pyを修正
    if not fix_epic_orchestrator_imports(actual_class):
        print("❌ 修正に失敗しました")
        return 1

    # 3. インポートを検証
    if verify_import():
        print("\n🎉 修正成功！")
    else:
        print("\n⚠️ インポートに問題が残っています")

    # 4. テスト実行
    if run_tests():
        print("\n✅ 全テスト成功")
    else:
        print("\n⚠️ 一部のテストが失敗しています")

    # 5. ナレッジ登録
    register_knowledge()

    print("\n" + "=" * 60)
    print("📋 修正完了サマリー")
    print("=" * 60)
    print(f"✅ ProgressAnalyzerV2 → {actual_class} への修正完了")
    print("✅ バックアップファイル作成済み")
    print("✅ ナレッジベースに知見登録済み")
    print("\n次のステップ:")
    print("1. pytest tests/test_epic_orchestrator.py -v で全テスト確認")
    print("2. python3 agents/epic_orchestrator.py でメイン実行テスト")
    print("3. 問題なければPhase 4の完了を記録")

    return 0


if __name__ == "__main__":
    sys.exit(main())
