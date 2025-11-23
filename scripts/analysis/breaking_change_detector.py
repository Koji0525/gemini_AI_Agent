#!/usr/bin/env python3
"""
破壊的変更検知システム

**機能**:
- Git diffからの変更抽出
- 関数シグネチャ変更の検出
- 削除されたメソッド/クラスの検出
- 変更影響範囲の自動計算
- リスクレベルの判定

**作成理由**:
コードの変更が既存システムに与える影響を事前に把握することで、
意図しない破壊的変更を防ぎ、安全なリファクタリングを可能にする。

Google Docstrings形式を使用
"""

import ast
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
from datetime import datetime
import difflib


class BreakingChangeDetector:
    """破壊的変更を検出するクラス.
    
    Attributes:
        dependency_map: 依存関係マップ
        changes: 検出された変更のリスト
    """
    
    def __init__(self, dependency_map: Dict):
        """初期化.
        
        Args:
            dependency_map: 依存関係マップ
        """
        self.dependency_map = dependency_map
        self.changes = []
        
    def analyze_git_diff(self, commit_range: str = "HEAD~1..HEAD") -> List[Dict]:
        """Git diffから変更を分析する.
        
        Args:
            commit_range: コミット範囲（デフォルト: 直前のコミット）
            
        Returns:
            変更のリスト
        """
        print(f"🔍 Git diff分析: {commit_range}")
        
        try:
            # 変更されたPythonファイルを取得
            result = subprocess.run(
                ['git', 'diff', '--name-only', commit_range, '*.py'],
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = [f for f in result.stdout.strip().split('\n') if f]
            print(f"📊 変更ファイル: {len(changed_files)}個")
            
            for file_path in changed_files:
                if not Path(file_path).exists():
                    print(f"  ⚠️  ファイルが存在しません: {file_path}")
                    continue
                
                self._analyze_file_changes(file_path, commit_range)
            
            return self.changes
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git diffエラー: {e}")
            return []
    
    def _analyze_file_changes(self, file_path: str, commit_range: str):
        """ファイルの変更を分析する.
        
        Args:
            file_path: ファイルパス
            commit_range: コミット範囲
        """
        try:
            # 変更前のコード取得
            old_code = subprocess.run(
                ['git', 'show', f'{commit_range.split("..")[0]}:{file_path}'],
                capture_output=True,
                text=True
            ).stdout
            
            # 変更後のコード取得
            with open(file_path, 'r', encoding='utf-8') as f:
                new_code = f.read()
            
            # AST解析
            old_ast = self._parse_ast(old_code)
            new_ast = self._parse_ast(new_code)
            
            if old_ast and new_ast:
                # 関数/クラスの変更を検出
                self._detect_signature_changes(file_path, old_ast, new_ast)
                self._detect_deletions(file_path, old_ast, new_ast)
                
        except Exception as e:
            print(f"  ⚠️  {file_path}: {e}")
    
    def _parse_ast(self, code: str) -> Optional[ast.AST]:
        """コードをASTにパースする.
        
        Args:
            code: Pythonコード
            
        Returns:
            ASTまたはNone
        """
        try:
            return ast.parse(code)
        except:
            return None
    
    def _detect_signature_changes(self, file_path: str, old_ast: ast.AST, new_ast: ast.AST):
        """関数シグネチャの変更を検出する.
        
        Args:
            file_path: ファイルパス
            old_ast: 変更前のAST
            new_ast: 変更後のAST
        """
        old_funcs = self._extract_functions(old_ast)
        new_funcs = self._extract_functions(new_ast)
        
        for func_name, old_sig in old_funcs.items():
            if func_name in new_funcs:
                new_sig = new_funcs[func_name]
                if old_sig != new_sig:
                    # シグネチャ変更を検出
                    impact = self._calculate_impact(file_path)
                    
                    self.changes.append({
                        'type': 'signature_change',
                        'file': file_path,
                        'function': func_name,
                        'old_signature': old_sig,
                        'new_signature': new_sig,
                        'impact': impact['level'],
                        'affected_files': impact['count'],
                        'severity': 'high' if impact['count'] >= 10 else 'medium' if impact['count'] >= 3 else 'low'
                    })
    
    def _detect_deletions(self, file_path: str, old_ast: ast.AST, new_ast: ast.AST):
        """削除された関数/クラスを検出する.
        
        Args:
            file_path: ファイルパス
            old_ast: 変更前のAST
            new_ast: 変更後のAST
        """
        old_funcs = set(self._extract_functions(old_ast).keys())
        new_funcs = set(self._extract_functions(new_ast).keys())
        
        deleted = old_funcs - new_funcs
        
        for func_name in deleted:
            impact = self._calculate_impact(file_path)
            
            self.changes.append({
                'type': 'deletion',
                'file': file_path,
                'function': func_name,
                'impact': impact['level'],
                'affected_files': impact['count'],
                'severity': 'critical' if impact['count'] >= 10 else 'high' if impact['count'] >= 3 else 'medium'
            })
    
    def _extract_functions(self, tree: ast.AST) -> Dict[str, str]:
        """ASTから関数定義を抽出する.
        
        Args:
            tree: AST
            
        Returns:
            関数名→シグネチャのマッピング
        """
        functions = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                args = [arg.arg for arg in node.args.args]
                signature = f"{node.name}({', '.join(args)})"
                functions[node.name] = signature
        
        return functions
    
    def _calculate_impact(self, file_path: str) -> Dict:
        """変更の影響範囲を計算する.
        
        Args:
            file_path: ファイルパス
            
        Returns:
            影響情報
        """
        affected_count = 0
        
        # 依存関係マップから影響を受けるファイルを検索
        for file, info in self.dependency_map.items():
            imports = info.get('imports', [])
            # ファイルパスをモジュール名に変換
            module_name = file_path.replace('/', '.').replace('.py', '')
            
            if any(module_name in imp for imp in imports):
                affected_count += 1
        
        if affected_count >= 10:
            level = 'high'
        elif affected_count >= 3:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'level': level,
            'count': affected_count
        }


def load_dependency_map() -> Dict:
    """依存関係マップを読み込む.
    
    Returns:
        依存関係マップ
    """
    data_file = Path('docs/dependency_map.json')
    
    if not data_file.exists():
        print("❌ dependency_map.json が見つかりません")
        return {}
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get('dependency_map', {})


def analyze_recent_changes(commits: int = 5) -> List[Dict]:
    """最近の変更を分析する.
    
    Args:
        commits: 分析するコミット数
        
    Returns:
        変更のリスト
    """
    print(f"📊 最近{commits}コミットを分析")
    
    dependency_map = load_dependency_map()
    detector = BreakingChangeDetector(dependency_map)
    
    all_changes = []
    
    for i in range(commits):
        commit_range = f"HEAD~{i+1}..HEAD~{i}" if i > 0 else "HEAD~1..HEAD"
        
        try:
            # コミット情報取得
            commit_info = subprocess.run(
                ['git', 'log', '-1', '--format=%H %s', commit_range.split('..')[1]],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            if commit_info:
                print(f"\n🔍 分析中: {commit_info[:60]}...")
                changes = detector.analyze_git_diff(commit_range)
                all_changes.extend(changes)
        except:
            break
    
    return all_changes


def main():
    """メイン処理を実行する."""
    print("="*60)
    print("🔍 破壊的変更検知システム")
    print("="*60)
    print(f"📁 作業ディレクトリ: {Path.cwd()}")
    print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Git リポジトリ確認
    try:
        subprocess.run(['git', 'status'], capture_output=True, check=True)
    except:
        print("❌ Gitリポジトリではありません")
        return
    
    # 最近の変更を分析
    changes = analyze_recent_changes(commits=5)
    
    # 結果保存
    output = {
        'changes': changes,
        'statistics': {
            'total_changes': len(changes),
            'critical': sum(1 for c in changes if c.get('severity') == 'critical'),
            'high': sum(1 for c in changes if c.get('severity') == 'high'),
            'medium': sum(1 for c in changes if c.get('severity') == 'medium'),
            'low': sum(1 for c in changes if c.get('severity') == 'low'),
            'signature_changes': sum(1 for c in changes if c['type'] == 'signature_change'),
            'deletions': sum(1 for c in changes if c['type'] == 'deletion')
        },
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'commits_analyzed': 5
        }
    }
    
    output_dir = Path('docs')
    output_file = output_dir / 'breaking_changes.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # 結果表示
    print("\n" + "="*60)
    print("✅ 破壊的変更検知完了")
    print("="*60)
    
    stats = output['statistics']
    print(f"📊 検出統計:")
    print(f"   総変更数: {stats['total_changes']} 個")
    print(f"   �� Critical: {stats['critical']} 個")
    print(f"   🟠 High: {stats['high']} 個")
    print(f"   🟡 Medium: {stats['medium']} 個")
    print(f"   🟢 Low: {stats['low']} 個")
    print(f"\n📈 変更タイプ:")
    print(f"   シグネチャ変更: {stats['signature_changes']} 個")
    print(f"   削除: {stats['deletions']} 個")
    
    if changes:
        print(f"\n⚠️  検出された破壊的変更 Top 5:")
        for i, change in enumerate(changes[:5], 1):
            severity_icon = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }.get(change['severity'], '⚪')
            
            print(f"\n   {i}. {severity_icon} {change['type'].upper()}")
            print(f"      ファイル: {change['file']}")
            print(f"      関数: {change['function']}")
            print(f"      影響: {change['affected_files']}ファイル")
    else:
        print("\n✅ 破壊的変更は検出されませんでした！")
    
    print(f"\n💾 結果保存先: {output_file.absolute()}")
    print(f"📁 ファイルサイズ: {output_file.stat().st_size / 1024:.1f} KB")
    print("="*60)


if __name__ == '__main__':
    main()
