#!/bin/bash

echo "=========================================="
echo "📝 task_execution_log 実装詳細"
echo "=========================================="

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. sheets_manager.py の save_task_output"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

grep -A 50 "async def save_task_output" tools/sheets_manager.py | head -60

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. 現在のコードでの呼び出し箇所"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "run_complete_with_wp.py の該当部分:"
grep -B 3 -A 10 "save_task_output" run_complete_with_wp.py | tail -15

echo ""
echo "=========================================="

