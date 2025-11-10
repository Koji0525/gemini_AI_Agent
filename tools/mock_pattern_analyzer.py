#!/usr/bin/env python3
"""モックパターン分析ツール"""

import re
from pathlib import Path


class MockPatternAnalyzer:
    """モックパターンを分析"""
    
    def __init__(self):
        self.good_patterns = []
        self.bad_patterns = []
        self.examples = {}
    
    def analyze_patterns(self):
        """パターンを分析"""
        
        print("🔍 モック設計パターン分析")
        print("=" * 80)
        
        # tests/unit/test_observability_manager.py を分析（成功例）
        self._analyze_good_example(
            "tests/unit/test_observability_manager.py"
        )
        
        # tests/unit/test_knowledge_manager.py を分析（要改善）
        self._analyze_bad_example(
            "tests/unit/test_knowledge_manager.py"
        )
        
        self._print_report()
    
    def _analyze_good_example(self, filepath: str):
        """良い例を分析"""
        if not Path(filepath).exists():
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n✅ 良い例: {filepath}")
        print("-" * 80)
        
        # パターン1: フィクスチャの使用
        fixtures = re.findall(r'def (\w+)\(self, (\w+)\):', content)
        if fixtures:
            print(f"✅ フィクスチャ使用: {len(fixtures)}個")
            for test_name, fixture in fixtures[:3]:
                print(f"   • {test_name} -> {fixture}")
        
        # パターン2: モックの返り値設定
        return_values = re.findall(
            r'\.return_value\s*=\s*\{[^}]+\}',
            content
        )
        if return_values:
            print(f"\n✅ 構造化された返り値: {len(return_values)}個")
            print(f"   例: {return_values[0][:60]}...")
        
        # パターン3: assertの使用
        asserts = re.findall(r'assert \w+', content)
        if asserts:
            print(f"\n✅ アサーション: {len(asserts)}個")
    
    def _analyze_bad_example(self, filepath: str):
        """悪い例を分析"""
        if not Path(filepath).exists():
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n\n⚠️ 要改善: {filepath}")
        print("-" * 80)
        
        # 問題1: フィクスチャ未定義
        undefined_fixtures = re.findall(
            r'def \w+\(self, (mock_\w+)\):',
            content
        )
        
        # conftest.py に存在するかチェック
        conftest_path = Path("tests/conftest.py")
        if conftest_path.exists():
            with open(conftest_path, 'r', encoding='utf-8') as f:
                conftest_content = f.read()
            
            missing = []
            for _, fixture in undefined_fixtures:
                if f"def {fixture}" not in conftest_content:
                    missing.append(fixture)
            
            if missing:
                print(f"❌ 未定義フィクスチャ: {len(missing)}個")
                for fix in missing[:3]:
                    print(f"   • {fix}")
    
    def _print_report(self):
        """レポートを表示"""
        print(f"\n{'='*80}")
        print("📋 パターン分析サマリー")
        print(f"{'='*80}")
        
        print("\n✅ 推奨パターン:")
        print("  1. conftest.pyでフィクスチャ定義")
        print("  2. 構造化された返り値（dict, list）")
        print("  3. side_effectで動的な振る舞い")
        print("  4. 明確なアサーション")
        
        print("\n❌ 避けるべきパターン:")
        print("  1. インラインでのモック定義")
        print("  2. Noneや空の返り値")
        print("  3. 実装への強い依存")
        print("  4. グローバル変数の使用")


def main():
    analyzer = MockPatternAnalyzer()
    analyzer.analyze_patterns()


if __name__ == '__main__':
    main()
