#!/bin/bash
# ====================================
# 【完全修正版】システムテスト
# サービスアカウント認証を含む
# ====================================

cd /workspaces/gemini_AI_Agent || exit 1

echo "🔧 システムテスト（完全修正版）"
echo "================================"

# ====
# 重要: 環境変数の完全設定
# ====
echo ""
echo "📋 ステップ1: 環境変数設定"

# .envから読み込み
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
    echo "✅ .env 読み込み完了"
else
    echo "❌ .env ファイルが見つかりません"
    exit 1
fi

# サービスアカウントファイルの設定（必須）
export SERVICE_ACCOUNT_FILE="${SERVICE_ACCOUNT_FILE:-configuration/service_account.json}"
export GOOGLE_APPLICATION_CREDENTIALS="${GOOGLE_APPLICATION_CREDENTIALS:-configuration/service_account.json}"

echo ""
echo "🔑 設定確認:"
echo "   SERVICE_ACCOUNT_FILE: $SERVICE_ACCOUNT_FILE"
echo "   GOOGLE_APPLICATION_CREDENTIALS: $GOOGLE_APPLICATION_CREDENTIALS"
echo "   SPREADSHEET_ID: ${SPREADSHEET_ID:0:20}..."

# ファイル存在確認
if [ -f "$SERVICE_ACCOUNT_FILE" ]; then
    echo "   ✅ サービスアカウントファイル存在"
else
    echo "   ❌ サービスアカウントファイルが見つかりません: $SERVICE_ACCOUNT_FILE"
    exit 1
fi

# ====
# システムテスト実行
# ====
echo ""
echo "📊 ステップ2: Google Sheets接続テスト"
echo "======================================"

python3 << 'FULL_TEST'
import sys
import os
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

try:
    # 環境変数の最終確認
    print("🔐 環境変数確認:")
    sa_file = os.environ.get('SERVICE_ACCOUNT_FILE')
    print(f"   SERVICE_ACCOUNT_FILE: {sa_file}")
    
    if sa_file and os.path.exists(sa_file):
        print(f"   ✅ ファイル存在確認")
    else:
        print(f"   ❌ ファイルが見つかりません")
        exit(1)
    
    spreadsheet_id = os.environ.get('SPREADSHEET_ID')
    print(f"   SPREADSHEET_ID: {spreadsheet_id[:20] if spreadsheet_id else 'N/A'}...")
    print()
    
    # GoogleSheetsManager初期化
    from tools.sheets_manager import GoogleSheetsManager
    
    print("🔧 GoogleSheetsManager初期化中...")
    sheets_mgr = GoogleSheetsManager(spreadsheet_id)
    print("✅ GoogleSheetsManager初期化成功\n")
    
    # 各シートのデータ取得
    print("📊 データ取得テスト:")
    sheets = ['pm_tasks', 'task_execution_log', 'progress_dashboard', 'project_goal']
    
    all_success = True
    for sheet_name in sheets:
        try:
            data = sheets_mgr.get_tasks(sheet_name)
            print(f"   ✅ {sheet_name}: {len(data)}件")
        except Exception as e:
            print(f"   ❌ {sheet_name}: {str(e)[:60]}")
            all_success = False
    
    if not all_success:
        print("\n⚠️ 一部のシートでエラーが発生しました")
        exit(1)
    
    # 実行待ちタスクの確認
    print("\n🎯 実行待ちタスク確認:")
    tasks = sheets_mgr.get_tasks('pm_tasks')
    pending = [t for t in tasks if t.get('status') == 'pending']
    in_progress = [t for t in tasks if t.get('status') == 'in_progress']
    completed = [t for t in tasks if t.get('status') == 'completed']
    
    print(f"   総タスク数: {len(tasks)}件")
    print(f"   実行待ち: {len(pending)}件")
    print(f"   実行中: {len(in_progress)}件")
    print(f"   完了: {len(completed)}件")
    
    if pending:
        print("\n📋 実行待ちタスク（上位5件）:")
        for i, task in enumerate(pending[:5], 1):
            task_id = task.get('task_id', 'N/A')
            title = task.get('task_title', 'N/A')
            agent = task.get('agent_type', 'N/A')
            priority = task.get('priority', 'N/A')
            
            print(f"\n   {i}. タスクID: {task_id}")
            print(f"      タイトル: {title[:50]}")
            print(f"      エージェント: {agent}")
            print(f"      優先度: {priority}")
    
    # 最近の実行ログ
    print("\n📝 最近の実行ログ（直近5件）:")
    logs = sheets_mgr.get_tasks('task_execution_log')
    if logs and len(logs) > 0:
        recent = logs[-5:]
        for log in recent:
            task_id = log.get('task_id', 'N/A')
            status = log.get('status', 'N/A')
            score = log.get('quality_score', 'N/A')
            agent = log.get('agent_type', 'N/A')
            print(f"   🆔 {task_id}: {status} | 品質: {score} | {agent}")
    
    # 品質スコア統計
    print("\n⭐ 品質スコア統計:")
    scored_logs = [l for l in logs if l.get('quality_score')]
    if scored_logs:
        scores = []
        for log in scored_logs:
            try:
                score = float(log.get('quality_score', 0))
                scores.append(score)
            except:
                pass
        
        if scores:
            avg_score = sum(scores) / len(scores)
            high_quality = len([s for s in scores if s >= 8])
            low_quality = len([s for s in scores if s < 7])
            
            print(f"   スコア付きタスク: {len(scores)}件")
            print(f"   平均スコア: {avg_score:.2f}/10")
            print(f"   高品質（8点以上）: {high_quality}件 ({high_quality/len(scores)*100:.1f}%)")
            print(f"   要改善（7点未満）: {low_quality}件 ({low_quality/len(scores)*100:.1f}%)")
    
    print("\n" + "=" * 60)
    print("🎉 すべてのテスト成功！")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ エラー発生: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
FULL_TEST

# ====
# WordPress設定確認
# ====
echo ""
echo "📊 ステップ3: WordPress設定確認"
echo "================================"

python3 << 'WP_CHECK'
import os

print("🔐 WordPress設定:")
wp_vars = ['WP_URL', 'WP_USER', 'WP_PASS']

all_set = True
for var in wp_vars:
    value = os.environ.get(var)
    if value:
        # マスク処理
        if var == 'WP_URL':
            masked = value[:30] + '...' if len(value) > 30 else value
        else:
            masked = '***'
        print(f"   ✅ {var}: {masked}")
    else:
        print(f"   ❌ {var}: 未設定")
        all_set = False

if all_set:
    print("\n✅ WordPress設定完了")
else:
    print("\n⚠️ WordPress設定が不完全です")
    print("   .envファイルに以下を追加してください:")
    print("   WP_URL=https://your-site.com")
    print("   WP_USER=your-username")
    print("   WP_PASS=your-password")
WP_CHECK

# ====
# 最終サマリー
# ====
echo ""
echo "================================"
echo "✅ システムテスト完了"
echo "================================"
echo ""
echo "🎯 次のアクション:"
echo "   1. タスクを実行: python3 run_pm_tasks_adaptive.py --max-tasks 3"
echo "   2. WordPress設定（未設定の場合）"
echo "   3. PM Agent自動化テスト"
echo ""
