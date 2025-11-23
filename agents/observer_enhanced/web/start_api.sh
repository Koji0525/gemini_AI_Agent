#!/bin/bash
# APIサーバー起動スクリプト（改良版v2）

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 依存関係可視化APIサーバー起動"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. dependency_graph.json が存在しないか古い場合は再生成
JSON_FILE="agents/observer_enhanced/web/dependency_graph.json"

if [ ! -f "$JSON_FILE" ] || [ ! -s "$JSON_FILE" ]; then
    echo "⚠️  dependency_graph.json が存在しないか空です"
    echo "🔍 プロジェクトをスキャンします..."
    
    python3 << 'PYSCAN'
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, '/workspaces/gemini_AI_Agent')
from agents.observer_enhanced.static_analyzer import StaticDependencyAnalyzer

analyzer = StaticDependencyAnalyzer()
analyzer.scan_project()

# NetworkXグラフからJSON形式に変換
graph = analyzer.graph
nodes = []
for node_id in graph.nodes():
    node_data = graph.nodes[node_id]
    nodes.append({
        'id': node_id,
        'type': node_data.get('type', 'file'),
        'file': node_data.get('file', node_id),
        'lines': node_data.get('lines', 0),
        'imports': node_data.get('imports', []),
        'imported_by': node_data.get('imported_by', [])
    })

edges = []
for source, target in graph.edges():
    edge_data = graph.edges[source, target]
    edges.append({
        'source': source,
        'target': target,
        'type': edge_data.get('type', 'import'),
        'line': edge_data.get('line', 0)
    })

result = {
    'nodes': nodes,
    'edges': edges,
    'metadata': {
        'total_nodes': len(nodes),
        'total_edges': len(edges),
        'generated_at': time.strftime('%Y-%m-%d %H:%M:%S')
    }
}

output_path = Path('agents/observer_enhanced/web/dependency_graph.json')
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"✅ スキャン完了: ノード{len(nodes)}個、エッジ{len(edges)}個")
PYSCAN
fi

# 2. APIサーバーを起動
echo ""
echo "🌐 APIサーバーを起動..."
cd agents/observer_enhanced/web
python3 api_server.py
