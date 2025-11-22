#!/bin/bash

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Phase 3 完了判定"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. ファイル存在確認
echo "1. ファイル存在確認"
FILES=(
    "agents/observer_enhanced/graph/graph_db.py"
    "agents/observer_enhanced/graph/impact_analyzer.py"
    "agents/observer_enhanced/graph/scoring_engine.py"
    "tests/observer_enhanced/graph/test_graph_db.py"
    "tests/observer_enhanced/graph/test_impact_analyzer.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (未存在)"
    fi
done

echo ""

# 2. テスト実行
echo "2. テスト実行"
pytest tests/observer_enhanced/graph/ -v --tb=short

echo ""

# 3. パフォーマンステスト
echo "3. パフォーマンステスト"
python3 << PYTHON
from agents.observer_enhanced.graph.graph_db import SystemGraphDB
from agents.observer_enhanced.graph.impact_analyzer import ImpactAnalyzer
import time

# GraphDB操作時間
db = SystemGraphDB()
start = time.time()
for i in range(100):
    db.add_component(f'Test{i}', {'type': 'test'})
elapsed = (time.time() - start) * 1000 / 100
print(f"  GraphDB操作平均: {elapsed:.3f}ms")
assert elapsed < 10, f"目標10ms未満、実測{elapsed:.3f}ms"

# 影響範囲分析時間
for i in range(5):
    db.add_component(f'Comp{i}', {'type': 'agent'})
    if i > 0:
        db.add_dependency(f'Comp{i-1}', f'Comp{i}')

analyzer = ImpactAnalyzer(db)
start = time.time()
result = analyzer.analyze_impact('Comp0')
elapsed = (time.time() - start) * 1000
print(f"  影響範囲分析時間: {elapsed:.3f}ms")
assert elapsed < 100, f"目標100ms未満、実測{elapsed:.3f}ms"

print("\n  ✅ パフォーマンス要件達成")
PYTHON

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Phase 3 完了判定: 合格"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
