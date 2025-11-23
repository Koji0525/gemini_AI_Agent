#!/usr/bin/env python3
"""
循環依存検出エンジン

**機能**:
- モジュール間の循環依存を検出
- DFS（深さ優先探索）による閉路検出
- 循環パスの可視化
- 重要度による分類

**作成理由**:
循環依存はコードの保守性を低下させ、リファクタリングを困難にする。
早期に検出して解消することで、システムの品質を向上させる。

Google Docstrings形式を使用
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from datetime import datetime


class CycleDetector:
    """循環依存を検出するクラス.
    
    Attributes:
        graph: 依存関係グラフ（隣接リスト形式）
        visited: 訪問済みノード
        rec_stack: 再帰スタック（現在の経路）
        cycles: 検出された循環依存のリスト
    """
    
    def __init__(self, dependency_map: Dict):
        """初期化.
        
        Args:
            dependency_map: 依存関係マップ
        """
        self.graph = self._build_graph(dependency_map)
        self.visited = set()
        self.rec_stack = set()
        self.cycles = []
        self.paths = {}  # 循環パスの詳細
        
    def _build_graph(self, dependency_map: Dict) -> Dict[str, Set[str]]:
        """依存関係グラフを構築する.
        
        Args:
            dependency_map: 依存関係マップ
            
        Returns:
            グラフ（隣接リスト）
        """
        graph = defaultdict(set)
        
        for file, info in dependency_map.items():
            imports = info.get('imports', [])
            for imp in imports:
                # モジュール名からファイルパスに変換
                file_path = imp.replace('.', '/') + '.py'
                if file_path in dependency_map:
                    graph[file].add(file_path)
        
        return graph
    
    def detect_cycles(self) -> List[List[str]]:
        """すべての循環依存を検出する.
        
        Returns:
            循環依存のリスト
        """
        print("🔍 循環依存検出開始...")
        
        for node in self.graph:
            if node not in self.visited:
                self._dfs(node, [])
        
        print(f"✅ 検出完了: {len(self.cycles)}個の循環依存")
        return self.cycles
    
    def _dfs(self, node: str, path: List[str]):
        """深さ優先探索で循環を検出する.
        
        Args:
            node: 現在のノード
            path: 現在の経路
        """
        self.visited.add(node)
        self.rec_stack.add(node)
        path = path + [node]
        
        for neighbor in self.graph.get(node, []):
            if neighbor not in self.visited:
                self._dfs(neighbor, path)
            elif neighbor in self.rec_stack:
                # 循環を検出
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                
                # 正規化（最小要素から始まるように）
                min_idx = cycle.index(min(cycle[:-1]))
                normalized_cycle = cycle[min_idx:-1] + cycle[:min_idx] + [cycle[min_idx]]
                
                # 重複チェック
                if normalized_cycle not in self.cycles:
                    self.cycles.append(normalized_cycle)
                    self._analyze_cycle(normalized_cycle)
        
        self.rec_stack.remove(node)
    
    def _analyze_cycle(self, cycle: List[str]):
        """循環の詳細を分析する.
        
        Args:
            cycle: 循環パス
        """
        cycle_key = ' -> '.join(cycle)
        
        # 重要度の判定
        length = len(cycle) - 1  # 最後の要素は最初の要素の繰り返し
        if length == 2:
            severity = "high"
            description = "2ファイル間の直接循環（即座に解消すべき）"
        elif length <= 4:
            severity = "medium"
            description = f"{length}ファイルの循環（リファクタリング推奨）"
        else:
            severity = "low"
            description = f"{length}ファイルの長い循環（段階的に解消）"
        
        self.paths[cycle_key] = {
            'cycle': cycle,
            'length': length,
            'severity': severity,
            'description': description
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


def main():
    """メイン処理を実行する."""
    print("="*60)
    print("🔄 循環依存検出エンジン")
    print("="*60)
    print(f"📁 作業ディレクトリ: {Path.cwd()}")
    print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 依存関係マップ読み込み
    dependency_map = load_dependency_map()
    
    if not dependency_map:
        print("❌ 依存関係データがありません")
        return
    
    print(f"📊 {len(dependency_map)}個のファイルを分析")
    
    # 循環依存検出
    detector = CycleDetector(dependency_map)
    cycles = detector.detect_cycles()
    
    # 結果保存
    output = {
        'cycles': [
            {
                'path': cycle,
                'details': detector.paths.get(' -> '.join(cycle), {})
            }
            for cycle in cycles
        ],
        'statistics': {
            'total_cycles': len(cycles),
            'high_severity': sum(1 for c in cycles 
                               if detector.paths.get(' -> '.join(c), {}).get('severity') == 'high'),
            'medium_severity': sum(1 for c in cycles 
                                 if detector.paths.get(' -> '.join(c), {}).get('severity') == 'medium'),
            'low_severity': sum(1 for c in cycles 
                              if detector.paths.get(' -> '.join(c), {}).get('severity') == 'low')
        },
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_files_analyzed': len(dependency_map)
        }
    }
    
    output_dir = Path('docs')
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / 'circular_dependencies.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # 結果表示
    print("\n" + "="*60)
    print("✅ 循環依存検出完了")
    print("="*60)
    
    stats = output['statistics']
    print(f"📊 検出統計:")
    print(f"   総循環数: {stats['total_cycles']} 個")
    print(f"   🔴 高重要度: {stats['high_severity']} 個（2ファイル間）")
    print(f"   🟡 中重要度: {stats['medium_severity']} 個（3-4ファイル）")
    print(f"   🟢 低重要度: {stats['low_severity']} 個（5ファイル以上）")
    
    if cycles:
        print(f"\n🔄 検出された循環依存 Top 10:")
        for i, cycle in enumerate(cycles[:10], 1):
            details = detector.paths.get(' -> '.join(cycle), {})
            severity = details.get('severity', 'unknown')
            severity_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(severity, '⚪')
            
            print(f"\n   {i}. {severity_icon} {details.get('description', '')}")
            print(f"      パス: {' → '.join([Path(f).name for f in cycle])}")
    else:
        print("\n✅ 循環依存は検出されませんでした！")
    
    print(f"\n💾 結果保存先: {output_file.absolute()}")
    print(f"📁 ファイルサイズ: {output_file.stat().st_size / 1024:.1f} KB")
    print("="*60)


if __name__ == '__main__':
    main()
