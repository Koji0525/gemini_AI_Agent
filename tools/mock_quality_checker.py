#!/usr/bin/env python3
"""
モック設計品質チェッカー

7つの観点からモックの品質を評価:
1. モック範囲の適切性
2. インターフェース整合性
3. テストの独立性
4. モックの現実性
5. メンテナンス性
6. パフォーマンス
7. カバレッジ
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class MockQualityChecker:
    """モック品質チェッカー"""
    
    def __init__(self):
        self.test_files = []
        self.mock_usage = defaultdict(list)
        self.issues = []
        self.recommendations = []
        self.score = 0
        
    def analyze_test_directory(self, test_dir: str = "tests"):
        """テストディレクトリを分析"""
        test_path = Path(test_dir)
        
        for test_file in test_path.rglob("test_*.py"):
            if 'disabled' not in str(test_file) and 'broken' not in str(test_file):
                self.test_files.append(test_file)
                self._analyze_file(test_file)
        
        return self._generate_report()
    
    def _analyze_file(self, filepath: Path):
        """ファイルを分析"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content)
        
        # 1. モックの使用状況を収集
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Mock(), patch()などの検出
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['Mock', 'MagicMock', 'AsyncMock']:
                        self.mock_usage[filepath].append({
                            'type': node.func.id,
                            'line': node.lineno
                        })
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'patch':
                        self.mock_usage[filepath].append({
                            'type': 'patch',
                            'line': node.lineno,
                            'target': self._get_patch_target(node)
                        })
    
    def _get_patch_target(self, node) -> str:
        """patchのターゲットを取得"""
        if node.args:
            arg = node.args[0]
            if isinstance(arg, ast.Constant):
                return arg.value
        return "unknown"
    
    def _check_mock_scope(self) -> Tuple[int, List[str]]:
        """
        観点1: モック範囲の適切性
        - 外部依存のみモック: Good
        - 内部ロジックをモック: Bad
        """
        score = 100
        issues = []
        
        external_targets = [
            'genai', 'google', 'requests', 'openai',
            'sheets', 'spreadsheet', 'api'
        ]
        
        internal_patterns = [
            'self.', 'super()', 'os.path', 'time.'
        ]
        
        for filepath, mocks in self.mock_usage.items():
            for mock in mocks:
                if mock['type'] == 'patch':
                    target = mock.get('target', '')
                    
                    # 外部依存のモック（良い）
                    if any(ext in target.lower() for ext in external_targets):
                        continue
                    
                    # 内部ロジックのモック（悪い）
                    if any(pat in target for pat in internal_patterns):
                        score -= 10
                        issues.append(
                            f"⚠️ {filepath.name}:{mock['line']} - "
                            f"内部ロジックをモック: {target}"
                        )
        
        return max(0, score), issues
    
    def _check_interface_consistency(self) -> Tuple[int, List[str]]:
        """
        観点2: インターフェース整合性
        - モックが実装と同じメソッド/属性を持つか
        """
        score = 100
        issues = []
        
        # 実装ファイルとの比較（簡易版）
        for filepath, mocks in self.mock_usage.items():
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # return_value の使用チェック
            if 'return_value' in content:
                # return_value が正しい型を返しているか
                return_value_matches = re.findall(
                    r'return_value\s*=\s*(.+)',
                    content
                )
                
                for match in return_value_matches:
                    # 適切な返り値かチェック
                    if match.strip() in ['None', '[]', '{}', '""']:
                        score -= 5
                        issues.append(
                            f"⚠️ {filepath.name} - "
                            f"空の返り値: {match}"
                        )
        
        return max(0, score), issues
    
    def _check_test_independence(self) -> Tuple[int, List[str]]:
        """
        観点3: テストの独立性
        - グローバル変数の使用: Bad
        - フィクスチャの共有: Good
        """
        score = 100
        issues = []
        
        for filepath in self.test_files:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
            
            # グローバル変数の検出
            global_vars = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    if isinstance(node.targets[0], ast.Name):
                        # クラスやメソッドの外の代入
                        if node.col_offset == 0:
                            var_name = node.targets[0].id
                            if not var_name.startswith('_'):
                                global_vars.append(var_name)
            
            if global_vars:
                score -= len(global_vars) * 10
                issues.append(
                    f"⚠️ {filepath.name} - "
                    f"グローバル変数: {', '.join(global_vars)}"
                )
        
        return max(0, score), issues
    
    def _check_mock_realism(self) -> Tuple[int, List[str]]:
        """
        観点4: モックの現実性
        - 現実的な返り値: Good
        - 固定値のみ: Bad
        """
        score = 100
        issues = []
        
        for filepath in self.test_files:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # side_effect の使用（動的な振る舞い）
            side_effect_count = content.count('side_effect')
            
            # return_value の使用（静的な返り値）
            return_value_count = content.count('return_value')
            
            if return_value_count > 0:
                # side_effectの比率が低い
                if side_effect_count == 0:
                    score -= 20
                    issues.append(
                        f"⚠️ {filepath.name} - "
                        f"すべて固定返り値（side_effect未使用）"
                    )
                elif side_effect_count / return_value_count < 0.2:
                    score -= 10
                    issues.append(
                        f"ℹ️ {filepath.name} - "
                        f"動的な振る舞いが少ない"
                    )
        
        return max(0, score), issues
    
    def _check_maintainability(self) -> Tuple[int, List[str]]:
        """
        観点5: メンテナンス性
        - フィクスチャの使用: Good
        - インラインモック: Bad
        """
        score = 100
        issues = []
        
        # conftest.py の存在確認
        conftest_exists = Path("tests/conftest.py").exists()
        
        if not conftest_exists:
            score -= 30
            issues.append("❌ conftest.py が存在しない")
        else:
            # conftest.py のフィクスチャ数
            with open("tests/conftest.py", 'r', encoding='utf-8') as f:
                content = f.read()
                fixture_count = content.count('@pytest.fixture')
            
            if fixture_count < 5:
                score -= 10
                issues.append(
                    f"⚠️ フィクスチャが少ない（{fixture_count}個）"
                )
        
        return max(0, score), issues
    
    def _check_performance(self) -> Tuple[int, List[str]]:
        """
        観点6: パフォーマンス
        - 高速なテスト: Good
        - 実データアクセス: Bad
        """
        score = 100
        issues = []
        
        for filepath in self.test_files:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 実データベースアクセスの検出
            db_patterns = [
                'sqlite3.connect',
                'pymongo.MongoClient',
                'psycopg2.connect'
            ]
            
            for pattern in db_patterns:
                if pattern in content:
                    score -= 20
                    issues.append(
                        f"❌ {filepath.name} - "
                        f"実DBアクセス: {pattern}"
                    )
            
            # 実APIコールの検出
            api_patterns = [
                'requests.get(',
                'requests.post(',
                'urllib.request'
            ]
            
            for pattern in api_patterns:
                if pattern in content and '@patch' not in content:
                    score -= 15
                    issues.append(
                        f"⚠️ {filepath.name} - "
                        f"実APIコール: {pattern}"
                    )
        
        return max(0, score), issues
    
    def _check_coverage(self) -> Tuple[int, List[str]]:
        """
        観点7: カバレッジ
        - 主要なエラーケースをカバー: Good
        - ハッピーパスのみ: Bad
        """
        score = 100
        issues = []
        
        for filepath in self.test_files:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # エラーテストの存在
            error_test_count = len(re.findall(
                r'def test_.*error|def test_.*exception|def test_.*failure',
                content,
                re.IGNORECASE
            ))
            
            # 成功テストの存在
            success_test_count = len(re.findall(
                r'def test_.*success|def test_.*basic',
                content,
                re.IGNORECASE
            ))
            
            if success_test_count > 0:
                if error_test_count == 0:
                    score -= 20
                    issues.append(
                        f"⚠️ {filepath.name} - "
                        f"エラーケースのテストがない"
                    )
                elif error_test_count / success_test_count < 0.3:
                    score -= 10
                    issues.append(
                        f"ℹ️ {filepath.name} - "
                        f"エラーケースが少ない"
                    )
        
        return max(0, score), issues
    
    def _generate_report(self) -> Dict:
        """レポート生成"""
        print("\n🔍 モック設計品質診断レポート")
        print("=" * 80)
        
        # 各観点の評価
        checks = [
            ("1️⃣ モック範囲の適切性", self._check_mock_scope),
            ("2️⃣ インターフェース整合性", self._check_interface_consistency),
            ("3️⃣ テストの独立性", self._check_test_independence),
            ("4️⃣ モックの現実性", self._check_mock_realism),
            ("5️⃣ メンテナンス性", self._check_maintainability),
            ("6️⃣ パフォーマンス", self._check_performance),
            ("7️⃣ カバレッジ", self._check_coverage),
        ]
        
        total_score = 0
        results = {}
        
        for name, check_func in checks:
            score, issues = check_func()
            total_score += score
            results[name] = {'score': score, 'issues': issues}
            
            print(f"\n{name}")
            print(f"スコア: {score}/100")
            
            if issues:
                for issue in issues[:5]:  # 最初の5件のみ表示
                    print(f"  {issue}")
                if len(issues) > 5:
                    print(f"  ... 他 {len(issues) - 5}件")
        
        # 総合評価
        avg_score = total_score / len(checks)
        print(f"\n{'='*80}")
        print(f"📊 総合スコア: {avg_score:.1f}/100")
        
        if avg_score >= 90:
            grade = "S（優秀）"
            comment = "モック設計は非常に優れています！"
        elif avg_score >= 80:
            grade = "A（良好）"
            comment = "モック設計は良好ですが、改善の余地があります"
        elif avg_score >= 70:
            grade = "B（普通）"
            comment = "モック設計は基本的ですが、重要な改善が必要です"
        elif avg_score >= 60:
            grade = "C（要改善）"
            comment = "モック設計に問題があります。早急な改善が必要"
        else:
            grade = "D（不良）"
            comment = "モック設計を根本から見直す必要があります"
        
        print(f"評価: {grade}")
        print(f"{comment}")
        
        return {
            'total_score': avg_score,
            'grade': grade,
            'results': results
        }


def main():
    """メイン処理"""
    checker = MockQualityChecker()
    report = checker.analyze_test_directory()
    
    # 推奨事項の表示
    print(f"\n{'='*80}")
    print("💡 改善推奨事項")
    print(f"{'='*80}")
    
    recommendations = []
    
    # スコアが低い観点に対する推奨
    for name, data in report['results'].items():
        if data['score'] < 80:
            if "モック範囲" in name:
                recommendations.append(
                    "• 外部依存のみモック化し、内部ロジックは実装を使う"
                )
            elif "インターフェース" in name:
                recommendations.append(
                    "• モックの返り値を実装と一致させる"
                )
            elif "独立性" in name:
                recommendations.append(
                    "• グローバル変数を避け、フィクスチャを使う"
                )
            elif "現実性" in name:
                recommendations.append(
                    "• side_effectで動的な振る舞いを実装する"
                )
            elif "メンテナンス" in name:
                recommendations.append(
                    "• conftest.pyで共通フィクスチャを定義する"
                )
            elif "パフォーマンス" in name:
                recommendations.append(
                    "• 実DBやAPIアクセスを完全にモック化する"
                )
            elif "カバレッジ" in name:
                recommendations.append(
                    "• エラーケースのテストを追加する"
                )
    
    if recommendations:
        for rec in set(recommendations):  # 重複を削除
            print(rec)
    else:
        print("✅ 現在の設計で問題ありません")
    
    print(f"\n{'='*80}")


if __name__ == '__main__':
    main()
