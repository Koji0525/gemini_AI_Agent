#!/bin/bash
echo "🤖 自律型エージェントシステム テスト開始"
echo "=========================================="

# ステップ1: test_tasks.py 実行
echo -e "\n📝 ステップ1: test_tasks.py 実行"
if python test_tasks.py 2>&1 | tee test_tasks.log; then
    echo "✅ test_tasks.py 成功"
else
    echo "❌ test_tasks.py でエラー検出"
    echo "🔧 自動修正を試みます..."
    
    # ステップ2: エラー検出 → main_hybrid_fix.py 呼び出し
    python main_hybrid_fix.py --error-log test_tasks.log
fi

# ステップ3: run_multi_agent.py 実行
echo -e "\n🎯 ステップ2: run_multi_agent.py 実行"
if python run_multi_agent.py 2>&1 | tee multi_agent.log; then
    echo "✅ run_multi_agent.py 成功"
else
    echo "❌ run_multi_agent.py でエラー検出"
    echo "🔧 自動修正を試みます..."
    
    # エラー修正
    python main_hybrid_fix.py --error-log multi_agent.log
fi

echo -e "\n=========================================="
echo "🎉 自律システムテスト完了"
