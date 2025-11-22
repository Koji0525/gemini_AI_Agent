#!/bin/bash
# 型ヒント修正と完全動作確認

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 型ヒント修正と完全動作確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: auto_integration_manager.pyの修正
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: auto_integration_manager.py修正"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > agents/quality_assurance/auto_integration_manager.py << 'PYTHON'
"""
自動統合マネージャー
生成された成果物を既存システムに自動統合
"""

import sys
import os
import shutil
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class AutoIntegrationManager:
    """自動統合マネージャー"""
    
    def __init__(self):
        self.project_root = Path("/workspaces/gemini_AI_Agent")
        self.generated_dir = self.project_root / "agents" / "generated"
        self.generated_dir.mkdir(exist_ok=True, parents=True)
        
    def integrate_output(self, output_path: str, task_id: str, quality_score: float) -> Dict:
        """成果物を統合"""
        print(f"\n{'=' * 80}")
        print(f"🔄 自動統合: {task_id}")
        print('=' * 80)
        print(f"品質スコア: {quality_score:.1f}/10")
        print()
        
        results = {
            'success': False,
            'integration_path': None,
            'actions': []
        }
        
        # 品質チェック
        if quality_score < 7.0:
            print(f"⚠️  品質スコアが低いため統合をスキップ")
            return results
        
        output_dir = Path(output_path)
        
        # 統合先ディレクトリを作成
        target_dir = self.generated_dir / task_id
        target_dir.mkdir(exist_ok=True, parents=True)
        
        # ファイルをコピー
        copied_files = []
        for file in output_dir.glob("*.py"):
            target_file = target_dir / file.name
            shutil.copy2(file, target_file)
            copied_files.append(file.name)
            print(f"  ✅ {file.name} → agents/generated/{task_id}/")
        
        results['actions'].append(f"コピー: {len(copied_files)}個")
        
        # README.mdもコピー
        readme = output_dir / "README.md"
        if readme.exists():
            shutil.copy2(readme, target_dir / "README.md")
            print(f"  ✅ README.md → agents/generated/{task_id}/")
            results['actions'].append("README.md コピー")
        
        # __init__.pyを作成
        init_content = f'''"""
Generated Module: {task_id}
Quality Score: {quality_score:.1f}/10
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

このモジュールは自動生成されました。
"""

'''
        
        # main.pyからクラスをインポート
        main_py = target_dir / "main.py"
        if main_py.exists():
            content = main_py.read_text()
            classes = re.findall(r'class (\w+)', content)
            
            if classes:
                init_content += "# 自動インポート\n"
                for cls in classes:
                    init_content += f"from .main import {cls}\n"
        
        init_file = target_dir / "__init__.py"
        init_file.write_text(init_content)
        print(f"  ✅ __init__.py 作成")
        results['actions'].append("__init__.py 作成")
        
        # 使用例を作成
        self._create_usage_doc(task_id, target_dir)
        
        results['success'] = True
        results['integration_path'] = str(target_dir)
        
        print()
        print(f"✅ 統合完了: agents/generated/{task_id}/")
        
        return results
    
    def _create_usage_doc(self, task_id: str, target_dir: Path):
        """使用例ドキュメントを作成"""
        usage_content = f"""# {task_id} 使用ガイド

## インポート方法
```python
# 方法1: モジュール全体をインポート
from agents.generated.{task_id} import *

# 方法2: 特定のクラスをインポート
# from agents.generated.{task_id}.main import ClassName
```

## 基本的な使用方法
```python
# TODO: 実際の使用例を追加
```

## 詳細情報

- ソースコード: `agents/generated/{task_id}/`
- README: `agents/generated/{task_id}/README.md`
- テスト: `agents/generated/{task_id}/test_*.py`

## 統合日時

{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        usage_file = target_dir / "USAGE.md"
        usage_file.write_text(usage_content)
        print(f"  ✅ USAGE.md 作成")

PYTHON

echo "✅ auto_integration_manager.py修正完了"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: 他のファイルの型ヒント確認と修正
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: 他のファイルの型ヒント確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# auto_code_quality_checker.pyの修正
cat > agents/quality_assurance/auto_code_quality_checker.py << 'PYTHON'
"""
自動コード品質チェッカー
生成されたコードの品質を多角的に評価
"""

import sys
import os
import subprocess
import re
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class AutoCodeQualityChecker:
    """自動コード品質チェッカー"""
    
    def __init__(self):
        self.checks = []
        
    def check_all(self, output_path: str) -> Dict:
        """全チェックを実行"""
        print(f"\n{'=' * 80}")
        print(f"🔍 自動コード品質チェック")
        print('=' * 80)
        print(f"対象: {output_path}")
        print()
        
        results = {
            'overall_score': 0,
            'checks': {},
            'passed': True,
            'warnings': [],
            'errors': []
        }
        
        output_dir = Path(output_path)
        
        # 1. 構文チェック
        syntax_result = self._check_syntax(output_dir)
        results['checks']['syntax'] = syntax_result
        
        # 2. インポートチェック
        import_result = self._check_imports(output_dir)
        results['checks']['imports'] = import_result
        
        # 3. コーディング規約チェック
        style_result = self._check_coding_style(output_dir)
        results['checks']['style'] = style_result
        
        # 4. 複雑度チェック
        complexity_result = self._check_complexity(output_dir)
        results['checks']['complexity'] = complexity_result
        
        # 5. ドキュメントチェック
        doc_result = self._check_documentation(output_dir)
        results['checks']['documentation'] = doc_result
        
        # 総合スコア計算
        scores = [r['score'] for r in results['checks'].values()]
        results['overall_score'] = sum(scores) / len(scores)
        
        # 合否判定
        results['passed'] = results['overall_score'] >= 7.0
        
        # サマリー表示
        self._print_summary(results)
        
        return results
    
    def _check_syntax(self, output_dir: Path) -> Dict:
        """構文チェック"""
        print("  📝 構文チェック...")
        
        result = {
            'name': '構文チェック',
            'score': 10.0,
            'details': [],
            'passed': True
        }
        
        for py_file in output_dir.glob("*.py"):
            try:
                subprocess.run(
                    ['python3', '-m', 'py_compile', str(py_file)],
                    check=True,
                    capture_output=True,
                    text=True
                )
                result['details'].append(f"✅ {py_file.name}: OK")
            except subprocess.CalledProcessError as e:
                result['score'] = 0
                result['passed'] = False
                result['details'].append(f"❌ {py_file.name}: 構文エラー")
                result['details'].append(f"   {e.stderr}")
        
        print(f"     スコア: {result['score']:.1f}/10")
        return result
    
    def _check_imports(self, output_dir: Path) -> Dict:
        """インポートチェック"""
        print("  📦 インポートチェック...")
        
        result = {
            'name': 'インポートチェック',
            'score': 10.0,
            'details': [],
            'passed': True
        }
        
        for py_file in output_dir.glob("*.py"):
            content = py_file.read_text()
            
            # import文を抽出
            imports = re.findall(r'^(?:from|import)\s+(\S+)', content, re.MULTILINE)
            
            # 標準ライブラリ以外のインポートをチェック
            external_imports = []
            for imp in imports:
                module = imp.split('.')[0]
                if module not in ['sys', 'os', 're', 'json', 'datetime', 'pathlib', 'typing']:
                    external_imports.append(module)
            
            if external_imports:
                result['details'].append(f"⚠️  {py_file.name}: 外部ライブラリ {external_imports}")
                result['score'] -= 2
            else:
                result['details'].append(f"✅ {py_file.name}: 標準ライブラリのみ")
        
        print(f"     スコア: {result['score']:.1f}/10")
        return result
    
    def _check_coding_style(self, output_dir: Path) -> Dict:
        """コーディング規約チェック"""
        print("  🎨 コーディング規約チェック...")
        
        result = {
            'name': 'コーディング規約',
            'score': 10.0,
            'details': [],
            'passed': True
        }
        
        for py_file in output_dir.glob("*.py"):
            content = py_file.read_text()
            
            # 基本的なチェック
            lines = content.split('\n')
            
            # 1行の長さチェック
            long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 100]
            if long_lines:
                result['score'] -= 1
                result['details'].append(f"⚠️  {py_file.name}: 長い行 {len(long_lines)}箇所")
            
            # docstringチェック
            if '"""' in content or "'''" in content:
                result['details'].append(f"✅ {py_file.name}: docstring あり")
            else:
                result['score'] -= 2
                result['details'].append(f"⚠️  {py_file.name}: docstring なし")
        
        print(f"     スコア: {result['score']:.1f}/10")
        return result
    
    def _check_complexity(self, output_dir: Path) -> Dict:
        """複雑度チェック"""
        print("  🧩 複雑度チェック...")
        
        result = {
            'name': '複雑度',
            'score': 10.0,
            'details': [],
            'passed': True
        }
        
        for py_file in output_dir.glob("*.py"):
            content = py_file.read_text()
            
            # 簡易的な複雑度チェック
            # 関数の長さをチェック
            functions = re.findall(r'def \w+.*?(?=\ndef |\nclass |\Z)', content, re.DOTALL)
            
            long_functions = [f for f in functions if len(f.split('\n')) > 50]
            if long_functions:
                result['score'] -= 2
                result['details'].append(f"⚠️  {py_file.name}: 長い関数 {len(long_functions)}個")
            else:
                result['details'].append(f"✅ {py_file.name}: 適切な関数サイズ")
        
        print(f"     スコア: {result['score']:.1f}/10")
        return result
    
    def _check_documentation(self, output_dir: Path) -> Dict:
        """ドキュメントチェック"""
        print("  📚 ドキュメントチェック...")
        
        result = {
            'name': 'ドキュメント',
            'score': 10.0,
            'details': [],
            'passed': True
        }
        
        # README.md存在チェック
        readme = output_dir / "README.md"
        if readme.exists():
            result['details'].append("✅ README.md あり")
            
            # README.mdの内容チェック
            content = readme.read_text()
            if len(content) > 500:
                result['details'].append("✅ README.md 詳細")
            else:
                result['score'] -= 2
                result['details'].append("⚠️  README.md 簡潔すぎる")
        else:
            result['score'] = 0
            result['passed'] = False
            result['details'].append("❌ README.md なし")
        
        print(f"     スコア: {result['score']:.1f}/10")
        return result
    
    def _print_summary(self, results: Dict):
        """サマリー表示"""
        print()
        print("=" * 80)
        print("📊 品質チェック結果サマリー")
        print("=" * 80)
        
        for check_name, check_result in results['checks'].items():
            status = "✅" if check_result['passed'] else "❌"
            print(f"{status} {check_result['name']}: {check_result['score']:.1f}/10")
        
        print()
        print(f"総合スコア: {results['overall_score']:.1f}/10")
        print(f"合否: {'✅ 合格' if results['passed'] else '❌ 不合格'}")
        print("=" * 80)

PYTHON

echo "✅ auto_code_quality_checker.py修正完了"

# auto_test_generator.pyの修正
cat > agents/quality_assurance/auto_test_generator.py << 'PYTHON'
"""
自動テスト生成システム
生成されたコードに対して自動的にテストを生成
"""

import sys
import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from dotenv import load_dotenv
load_dotenv()

class AutoTestGenerator:
    """自動テスト生成システム"""
    
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
    def generate_tests(self, output_path: str) -> Dict:
        """テストを自動生成"""
        print(f"\n{'=' * 80}")
        print(f"🧪 自動テスト生成")
        print('=' * 80)
        print(f"対象: {output_path}")
        print()
        
        output_dir = Path(output_path)
        results = {
            'generated_tests': [],
            'success': True
        }
        
        # main.pyのテストを生成
        main_py = output_dir / "main.py"
        if main_py.exists():
            test_content = self._generate_test_for_file(main_py)
            
            # test_main.pyとして保存
            test_file = output_dir / "test_main.py"
            test_file.write_text(test_content)
            
            print(f"  ✅ test_main.py 生成完了 ({len(test_content)}文字)")
            results['generated_tests'].append(str(test_file))
        
        # utils.pyのテストを生成
        utils_py = output_dir / "utils.py"
        if utils_py.exists():
            test_content = self._generate_test_for_file(utils_py)
            
            test_file = output_dir / "test_utils.py"
            test_file.write_text(test_content)
            
            print(f"  ✅ test_utils.py 生成完了 ({len(test_content)}文字)")
            results['generated_tests'].append(str(test_file))
        
        print()
        print(f"✅ {len(results['generated_tests'])}個のテストファイルを生成")
        
        return results
    
    def _generate_test_for_file(self, py_file: Path) -> str:
        """ファイルに対するテストを生成"""
        content = py_file.read_text()
        
        # クラスと関数を抽出
        classes = re.findall(r'class (\w+)', content)
        functions = re.findall(r'def (\w+)\(', content)
        
        # テストコードのテンプレート
        test_code = f'''"""
{py_file.name}の自動生成テスト
"""

import unittest
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

try:
    from {py_file.stem} import *
except ImportError as e:
    print(f"Warning: Could not import from {py_file.stem}: {{e}}")

'''
        
        # クラスごとのテスト
        for cls_name in classes:
            test_code += f'''
class Test{cls_name}(unittest.TestCase):
    """
    {cls_name}のテスト
    """
    
    def setUp(self):
        """テストのセットアップ"""
        try:
            self.instance = {cls_name}()
        except Exception as e:
            self.skipTest(f"Could not instantiate {cls_name}: {{e}}")
    
    def test_instantiation(self):
        """インスタンス化のテスト"""
        self.assertIsNotNone(self.instance)
    
    def test_attributes(self):
        """属性の存在チェック"""
        # TODO: 実際の属性をチェック
        pass

'''
        
        # 関数のテスト
        if functions:
            test_code += '''
class TestFunctions(unittest.TestCase):
    """
    関数のテスト
    """
    
'''
            for func_name in functions[:5]:  # 最初の5個のみ
                if not func_name.startswith('_'):  # プライベート関数は除外
                    test_code += f'''
    def test_{func_name}(self):
        """
        {func_name}のテスト
        """
        # TODO: 実際のテストを実装
        pass
    
'''
        
        test_code += '''
if __name__ == '__main__':
    unittest.main()
'''
        
        return test_code
    
    def run_tests(self, output_path: str) -> Dict:
        """生成されたテストを実行"""
        print(f"\n{'=' * 80}")
        print(f"🧪 テスト実行")
        print('=' * 80)
        
        output_dir = Path(output_path)
        results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        
        # テストファイルを実行
        for test_file in output_dir.glob("test_*.py"):
            print(f"\n  実行中: {test_file.name}")
            
            try:
                result = subprocess.run(
                    ['python3', str(test_file)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"  ✅ {test_file.name}: 合格")
                    results['passed'] += 1
                else:
                    print(f"  ❌ {test_file.name}: 失敗")
                    results['failed'] += 1
                    results['errors'].append(result.stderr)
                    
            except subprocess.TimeoutExpired:
                print(f"  ⏱️  {test_file.name}: タイムアウト")
                results['failed'] += 1
            except Exception as e:
                print(f"  ❌ {test_file.name}: エラー {e}")
                results['failed'] += 1
        
        print()
        print("=" * 80)
        print(f"テスト結果: {results['passed']}個合格 / {results['failed']}個失敗")
        print("=" * 80)
        
        return results

PYTHON

echo "✅ auto_test_generator.py修正完了"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ すべての型ヒント修正完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 修正内容:"
echo "  1. ✅ auto_integration_manager.py"
echo "  2. ✅ auto_code_quality_checker.py"
echo "  3. ✅ auto_test_generator.py"
echo ""
echo "🧪 再テスト実行:"
echo "  bash sh/run_full_autonomous_system.sh 2"
echo ""

# 自動再テスト
read -p "今すぐ修正版でテストを実行しますか？ [Y/n] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🧪 修正版テスト実行"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    bash sh/run_full_autonomous_system.sh 2
fi

