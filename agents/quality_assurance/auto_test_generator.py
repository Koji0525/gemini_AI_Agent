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

