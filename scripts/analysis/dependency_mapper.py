#!/usr/bin/env python3
"""
依存関係マッピングツール

**機能**:
- Pythonファイルのインポート関係を抽出
- 依存関係グラフをJSON形式で出力
- 重要モジュールの特定

**作成理由**: 
Phase 1の最初のステップとして、既存コードベースの依存関係を可視化し、
変更影響範囲を分析可能にするため。これにより既存システムを破壊せずに
安全な開発が可能になる。

Google Docstrings形式を使用
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
from datetime import datetime


def extract_imports(file_path: Path) -> List[str]:
    """Pythonファイルからインポート文を抽出する.
    
    Args:
        file_path: 対象ファイルのパス
        
    Returns:
        インポートモジュールのリスト
        
    Raises:
        Exception: ファイル読み込みまたはパースエラー時
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        return imports
    except Exception as e:
        # 構文エラーやエンコードエラーは静かにスキップ
        return []


def build_dependency_map(project_root: str = ".") -> Dict:
    """プロジェクト全体の依存関係マップを構築する.
    
    Args:
        project_root: プロジェクトのルートディレクトリ（デフォルト: "."）
        
    Returns:
        依存関係マップの辞書。キーはファイルパス、値は以下を含む辞書:
            - imports: プロジェクト内インポートのリスト
            - all_imports: 全インポートのリスト
            - import_count: プロジェクト内インポート数
            - total_imports: 全インポート数
            - file_size: ファイルサイズ（バイト）
    """
    root_path = Path(project_root)
    python_files = list(root_path.rglob('*.py'))
    
    dependency_map = {}
    skipped = 0
    
    print(f"📂 {len(python_files)}個のPythonファイルを検出")
    
    for file_path in python_files:
        # 除外パターン
        exclude_patterns = [
            '__pycache__', 'venv', '.git', 'site-packages',
            '.venv', 'env', 'build', 'dist', '.pytest_cache'
        ]
        
        if any(pattern in str(file_path) for pattern in exclude_patterns):
            skipped += 1
            continue
        
        try:
            relative_path = str(file_path.relative_to(root_path))
        except ValueError:
            relative_path = str(file_path)
            
        imports = extract_imports(file_path)
        
        # プロジェクト内のインポートのみ抽出
        project_prefixes = [
            'agents', 'core_agents', 'task_executor',
            'knowledge_system', 'tools', 'scripts', 'browser_control',
            'configuration'
        ]
        
        project_imports = [
            imp for imp in imports
            if any(imp.startswith(prefix) for prefix in project_prefixes)
        ]
        
        # 全ファイルを記録（インポートがなくても）
        dependency_map[relative_path] = {
            'imports': project_imports,
            'all_imports': imports[:20],  # 最初の20個のみ保存（容量削減）
            'import_count': len(project_imports),
            'total_imports': len(imports),
            'file_size': file_path.stat().st_size
        }
    
    print(f"✅ {len(dependency_map)}個のファイルを分析（{skipped}個をスキップ）")
    return dependency_map


def analyze_critical_modules(dependency_map: Dict) -> Dict:
    """重要なモジュール（多くのファイルから参照されているモジュール）を分析する.
    
    Args:
        dependency_map: 依存関係マップ
        
    Returns:
        分析結果の辞書。以下を含む:
            - most_depended: 依存度の高いモジュールのリスト（上位20件）
            - total_modules: 総モジュール数
            - total_dependencies: 総依存関係数
            - dependency_stats: 影響度別の統計
    """
    # 各モジュールに依存している数をカウント
    dependents = defaultdict(int)
    for file, data in dependency_map.items():
        for imp in data['imports']:
            dependents[imp] += 1
    
    # 依存度の高いモジュールをソート
    critical = sorted(dependents.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'most_depended': critical[:20],
        'total_modules': len(dependency_map),
        'total_dependencies': sum(d['import_count'] for d in dependency_map.values()),
        'dependency_stats': {
            'high_impact': len([v for v in dependents.values() if v >= 5]),
            'medium_impact': len([v for v in dependents.values() if 2 <= v < 5]),
            'low_impact': len([v for v in dependents.values() if v == 1]),
            'no_dependents': len([v for v in dependents.values() if v == 0])
        }
    }


def main():
    """メイン処理を実行する."""
    print("="*60)
    print("🔍 依存関係マッピングツール")
    print("="*60)
    print(f"📁 作業ディレクトリ: {Path.cwd()}")
    print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 依存関係マップ構築
    dep_map = build_dependency_map()
    
    if not dep_map:
        print("⚠️  Pythonファイルが見つかりませんでした")
        return
    
    # クリティカルパス分析
    print("\n📊 クリティカルパス分析中...")
    analysis = analyze_critical_modules(dep_map)
    
    # 結果保存
    output = {
        'dependency_map': dep_map,
        'analysis': analysis,
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'working_directory': str(Path.cwd()),
            'version': '1.0.0'
        }
    }
    
    output_dir = Path('docs')
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / 'dependency_map.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # 結果表示
    print("\n" + "="*60)
    print("✅ 依存関係マップ作成完了")
    print("="*60)
    print(f"📊 総モジュール数: {analysis['total_modules']}")
    print(f"📊 総依存関係数: {analysis['total_dependencies']}")
    print(f"\n📈 影響度分析:")
    print(f"   🔴 高影響(5+参照): {analysis['dependency_stats']['high_impact']} modules")
    print(f"   🟡 中影響(2-4参照): {analysis['dependency_stats']['medium_impact']} modules")
    print(f"   🟢 低影響(1参照): {analysis['dependency_stats']['low_impact']} modules")
    print(f"   ⚪ 依存なし: {analysis['dependency_stats']['no_dependents']} modules")
    
    print(f"\n🏆 最も依存されているモジュール Top 10:")
    for i, (module, count) in enumerate(analysis['most_depended'][:10], 1):
        print(f"   {i:2d}. {count:3d}回 - {module}")
    
    print(f"\n💾 結果保存先: {output_file.absolute()}")
    print(f"📁 ファイルサイズ: {output_file.stat().st_size / 1024:.1f} KB")
    print("="*60)


if __name__ == '__main__':
    main()
