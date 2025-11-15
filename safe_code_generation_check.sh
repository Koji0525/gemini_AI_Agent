#!/bin/bash

echo "=== 安全なコード生成確認 ==="

# 1. 構文チェック
echo "🔍 構文チェック..."
python3 -m py_compile agents/task_executor_enhanced.py
if [ $? -ne 0 ]; then
    echo "❌ 構文エラーがあります"
    exit 1
fi
echo "✅ 構文チェック完了"

# 2. インポートテスト
echo "🔍 インポートテスト..."
python3 -c "
try:
    from agents.task_executor_enhanced import TaskExecutorEnhanced
    print('✅ TaskExecutorEnhanced インポート成功')
    
    # 簡単なインスタンス化テスト
    executor = TaskExecutorEnhanced()
    print('✅ インスタンス化成功')
except Exception as e:
    print(f'❌ インポートエラー: {e}')
    exit(1)
"

# 3. メソッド存在確認
echo "🔍 メソッド存在確認..."
python3 -c "
from agents.task_executor_enhanced import TaskExecutorEnhanced
executor = TaskExecutorEnhanced()

required_methods = ['_execute_implementation', '_generate_high_quality_cli']
for method in required_methods:
    if hasattr(executor, method):
        print(f'✅ {method} メソッド存在')
    else:
        print(f'❌ {method} メソッド不存在')
        exit(1)
"

echo "🎉 すべての安全チェック完了"
