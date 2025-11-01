#!/bin/bash
# ====================================
# 【マスター実行スクリプト】
# WordPressエージェント完全自律化プロジェクト
# ====================================

echo "🎯 WordPressエージェント完全自律化プロジェクト"
echo "============================================="
echo ""
echo "最終目標: WordPressのすべての業務を完全自動化"
echo ""

cd /workspaces/gemini_AI_Agent || {
    echo "❌ プロジェクトディレクトリが見つかりません"
    echo "   現在の場所: $(pwd)"
    echo "   正しいディレクトリで実行してください"
    exit 1
}

# ====
# 使用方法の表示
# ====
show_usage() {
    cat << 'EOF'
使用方法:
  ./master_execution.sh [オプション]

オプション:
  --phase1    Phase 1のみ実行（WordPress専門エージェント復活）
  --phase2    Phase 2のみ実行（Gemini AI統合）
  --phase3    Phase 3のみ実行（完全自律化）
  --all       全フェーズを順次実行（デフォルト）
  --status    現在のシステム状態を表示
  --help      このヘルプを表示

例:
  ./master_execution.sh --phase1
  ./master_execution.sh --all
  ./master_execution.sh --status

EOF
}

# ====
# システム状態確認
# ====
check_system_status() {
    echo "📊 システム状態確認"
    echo "==================="
    
    python3 -c "
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

try:
    from tools.sheets_manager import GoogleSheetsManager
    sheets_mgr = GoogleSheetsManager('1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s')
    
    # 各シートのデータ数確認
    sheets = ['project_goal', 'pm_tasks', 'task_execution_log', 'progress_dashboard']
    print('')
    for sheet in sheets:
        try:
            data = sheets_mgr.get_all_records(sheet)
            print(f'✅ {sheet}: {len(data)}件')
        except Exception as e:
            print(f'❌ {sheet}: エラー')
    
    # 最新の実行状況
    logs = sheets_mgr.get_all_records('task_execution_log')
    if logs:
        recent = logs[-5:]
        print('')
        print('📝 最近の実行（直近5件）:')
        for log in recent:
            task_id = log.get('task_id', 'N/A')
            status = log.get('status', 'N/A')
            score = log.get('quality_score', 'N/A')
            print(f'   🆔 {task_id}: {status} (品質: {score})')
            
    # システム健全性評価
    print('')
    print('🏥 システム健全性:')
    
    # 1. 認証状態
    print('   認証: ✅ Google Sheets接続成功')
    
    # 2. データ整合性
    tasks = sheets_mgr.get_all_records('pm_tasks')
    pending = [t for t in tasks if t.get('status') == 'pending']
    print(f'   実行待ちタスク: {len(pending)}件')
    
    # 3. 品質評価
    scored = [l for l in logs if l.get('quality_score')]
    if scored:
        avg = sum(float(l.get('quality_score', 0)) for l in scored) / len(scored)
        print(f'   平均品質スコア: {avg:.2f}/10')
    
except Exception as e:
    print(f'❌ システムチェック失敗: {e}')
    import traceback
    traceback.print_exc()
" 2>&1
    
    echo ""
}

# ====
# Phase 1 実行
# ====
run_phase1() {
    echo ""
    echo "🔧 Phase 1: WordPress専門エージェント復活"
    echo "=========================================="
    
    if [ -f "phase1_wp_restoration.sh" ]; then
        bash phase1_wp_restoration.sh
    else
        echo "⚠️ phase1_wp_restoration.sh が見つかりません"
        echo "スクリプトファイルをプロジェクトルートに配置してください"
        return 1
    fi
    
    echo ""
    echo "✅ Phase 1 完了"
    echo "次のアクション: 検出された問題を修正してください"
    echo ""
}

# ====
# Phase 2 実行
# ====
run_phase2() {
    echo ""
    echo "🤖 Phase 2: Gemini AI統合"
    echo "========================="
    
    if [ -f "phase2_ai_integration.sh" ]; then
        bash phase2_ai_integration.sh
    else
        echo "⚠️ phase2_ai_integration.sh が見つかりません"
        return 1
    fi
    
    echo ""
    echo "✅ Phase 2 完了"
    echo ""
}

# ====
# Phase 3 実行
# ====
run_phase3() {
    echo ""
    echo "🚀 Phase 3: 完全自律化"
    echo "======================"
    
    if [ -f "phase3_autonomous_cycle.sh" ]; then
        bash phase3_autonomous_cycle.sh
    else
        echo "⚠️ phase3_autonomous_cycle.sh が見つかりません"
        return 1
    fi
    
    echo ""
    echo "✅ Phase 3 完了"
    echo ""
}

# ====
# メイン処理
# ====
case "${1:-}" in
    --help)
        show_usage
        exit 0
        ;;
    --status)
        check_system_status
        exit 0
        ;;
    --phase1)
        check_system_status
        run_phase1
        ;;
    --phase2)
        check_system_status
        run_phase2
        ;;
    --phase3)
        check_system_status
        run_phase3
        ;;
    --all|"")
        echo "📋 全フェーズを順次実行します"
        echo ""
        check_system_status
        
        read -p "Phase 1を実行しますか？ (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            run_phase1
        fi
        
        read -p "Phase 2を実行しますか？ (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            run_phase2
        fi
        
        read -p "Phase 3を実行しますか？ (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            run_phase3
        fi
        
        echo ""
        echo "🎉 すべてのフェーズ完了！"
        ;;
    *)
        echo "❌ 不明なオプション: $1"
        show_usage
        exit 1
        ;;
esac

echo ""
echo "============================================="
echo "🎯 次のステップ:"
echo "   1. 検出された問題を修正"
echo "   2. テストを実行"
echo "   3. 次のフェーズに進む"
echo "============================================="
