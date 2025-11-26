#!/bin/bash
echo "============================================================"
echo "gemini_AI_Agent 実運用システム（v34詳細版）"
echo "============================================================"
echo ""

case "$1" in
    f1)
        echo "F1: ゴール分解実行（2000文字詳細版）"
        echo "------------------------------------------------------------"
        python3 core_agents/pm_agent_v34_epic.py
        ;;
    f2)
        echo "F2: タスク実行"
        echo "------------------------------------------------------------"
        python3 run_pending_tasks.py --limit 1
        ;;
    auto)
        bash "$0" f1
        bash "$0" f2
        ;;
    *)
        echo "使用方法:"
        echo "  bash $0 f1    # ゴール分解（2000文字詳細）"
        echo "  bash $0 f2    # タスク実行"
        echo "  bash $0 auto  # F1→F2自動"
        ;;
esac
