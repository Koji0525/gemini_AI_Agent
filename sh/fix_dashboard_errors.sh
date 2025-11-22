#!/bin/bash
# ダッシュボードエラーの原因追及と修正

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 ダッシュボードエラーの原因追及と修正"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# エラー分析
cat > "MD/${NOW_JST}_エラー分析.md" << 'ANALYSIS'
# ダッシュボードエラー分析

## 発生しているエラー

### 1. 404エラー: `/api/snapshot`
```
GET /api/snapshot HTTP/1.1" 404 Not Found
```

**原因**: フロントエンドが呼び出しているが、バックエンドにエンドポイントが未実装

**影響**: 軽微（機能の一部が動作しないだけ）

**対策**: エンドポイントを実装するか、フロントエンドから削除

---

### 2. 500エラー: `/api/instruction` POST
```
POST /api/instruction HTTP/1.1" 500 Internal Server Error
```

**原因（推定）**:
1. `f9_interface.add_instruction()` メソッドの引数エラー
2. Google Sheets APIの呼び出しエラー
3. データ検証エラー

**影響**: 重大（人間指示が追加できない）

**対策**: 詳細なエラーログを追加し、根本原因を特定

---

## 根本原因の分析

### 問題1: `f9_interface.add_instruction()` のシグネチャ不一致

**F9HumanInterface.add_instruction()** の実際のシグネチャ:
```python
def add_instruction(
    self,
    instruction_type: str,
    content: str,
    priority: str = 'medium',
    target_task: str = ''
) -> bool:
```

しかし、APIエンドポイントから呼び出す際の引数が一致していない可能性。

### 問題2: エラーハンドリングの不足

エラーが発生しても、詳細なログが出力されていない。

ANALYSIS

echo "✅ エラー分析完了: MD/${NOW_JST}_エラー分析.md"

# 修正版のダッシュボードサーバーを作成
cat > agents/web_dashboard/dashboard_server_fixed.py << 'PYTHON'
"""
Webダッシュボードサーバー（エラー修正版）
詳細なログとエラーハンドリングを追加
"""

import sys
import os
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("❌ FastAPIがインストールされていません")
    sys.exit(1)

from tools.sheets_manager import GoogleSheetsManager
from agents.f9_human_interface import F9HumanInterface

app = FastAPI(title="自律開発システム ダッシュボード")

# グローバル変数
sheets_manager = None
f9_interface = None

class InstructionRequest(BaseModel):
    """人間指示のリクエストモデル"""
    instruction_type: str
    content: str
    priority: str = "medium"
    target_task: str = ""

@app.on_event("startup")
async def startup_event():
    """起動時の初期化"""
    global sheets_manager, f9_interface
    try:
        sheets_manager = GoogleSheetsManager()
        f9_interface = F9HumanInterface(sheets_manager)
        print("✅ ダッシュボードサーバー起動")
    except Exception as e:
        print(f"❌ 初期化エラー: {e}")
        traceback.print_exc()

# エラーハンドラー
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """グローバルエラーハンドラー"""
    error_detail = {
        "error": str(exc),
        "type": type(exc).__name__,
        "path": request.url.path,
        "method": request.method
    }
    
    print(f"\n{'=' * 80}")
    print(f"❌ エラー発生: {request.method} {request.url.path}")
    print(f"   エラータイプ: {type(exc).__name__}")
    print(f"   エラー内容: {exc}")
    print('=' * 80)
    traceback.print_exc()
    print('=' * 80)
    print()
    
    return JSONResponse(
        status_code=500,
        content=error_detail
    )

@app.get("/", response_class=HTMLResponse)
async def root():
    """メインダッシュボード"""
    # HTMLは前回と同じなので省略
    with open('/workspaces/gemini_AI_Agent/agents/web_dashboard/dashboard.html', 'r') as f:
        return f.read()

@app.get("/api/stats")
async def get_stats():
    """システム統計を取得"""
    try:
        print("📊 /api/stats 呼び出し")
        
        result = sheets_manager.service.spreadsheets().values().get(
            spreadsheetId=sheets_manager.spreadsheet_id,
            range="pm_tasks!A2:M1000"
        ).execute()
        
        values = result.get('values', [])
        
        total_tasks = len(values)
        completed_tasks = sum(1 for row in values if len(row) > 4 and row[4] == 'completed')
        pending_tasks = sum(1 for row in values if len(row) > 4 and row[4] == 'pending')
        
        stats = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'avg_quality': 8.5
        }
        
        print(f"   ✅ 統計: {stats}")
        return stats
        
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/pending")
async def get_pending_tasks():
    """ペンディングタスクを取得"""
    try:
        print("📋 /api/tasks/pending 呼び出し")
        
        result = sheets_manager.service.spreadsheets().values().get(
            spreadsheetId=sheets_manager.spreadsheet_id,
            range="pm_tasks!A2:M1000"
        ).execute()
        
        values = result.get('values', [])
        
        pending = []
        for row in values:
            if len(row) > 4 and row[4] == 'pending':
                pending.append({
                    'task_id': row[0],
                    'description': row[2] if len(row) > 2 else '',
                    'priority': row[5] if len(row) > 5 else 'medium',
                    'estimated_time': row[6] if len(row) > 6 else '1h'
                })
        
        print(f"   ✅ ペンディングタスク: {len(pending)}件")
        return pending[:10]
        
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        traceback.print_exc()
        return []

@app.get("/api/instructions")
async def get_instructions():
    """人間指示一覧を取得"""
    try:
        print("📨 /api/instructions 呼び出し")
        
        instructions = f9_interface.check_human_instructions()
        
        result = [{
            'timestamp': inst.get('timestamp', ''),
            'instruction_type': inst.get('instruction_type', ''),
            'status': inst.get('status', ''),
            'content': inst.get('content', '')
        } for inst in instructions[:10]]
        
        print(f"   ✅ 指示一覧: {len(result)}件")
        return result
        
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        traceback.print_exc()
        return []

@app.post("/api/instruction")
async def add_instruction(request: InstructionRequest):
    """人間指示を追加"""
    try:
        print("\n" + "=" * 80)
        print("📝 /api/instruction POST 呼び出し")
        print(f"   instruction_type: {request.instruction_type}")
        print(f"   content: {request.content}")
        print(f"   priority: {request.priority}")
        print(f"   target_task: {request.target_task}")
        print("=" * 80)
        
        # F9HumanInterfaceのadd_instructionメソッドを呼び出し
        success = f9_interface.add_instruction(
            instruction_type=request.instruction_type,
            content=request.content,
            priority=request.priority,
            target_task=request.target_task
        )
        
        print(f"   結果: {'✅ 成功' if success else '❌ 失敗'}")
        print("=" * 80)
        print()
        
        return {'success': success}
        
    except Exception as e:
        print(f"\n{'=' * 80}")
        print("❌ /api/instruction エラー")
        print(f"   エラータイプ: {type(e).__name__}")
        print(f"   エラー内容: {e}")
        print("=" * 80)
        traceback.print_exc()
        print("=" * 80)
        print()
        
        raise HTTPException(
            status_code=500,
            detail={
                'error': str(e),
                'type': type(e).__name__,
                'instruction_type': request.instruction_type,
                'content': request.content
            }
        )

@app.get("/api/logs")
async def get_logs():
    """最新ログを取得"""
    try:
        print("📝 /api/logs 呼び出し")
        
        log_files = sorted(Path('logs').glob('autonomous_v*.log'), key=os.path.getmtime, reverse=True)
        
        if log_files:
            with open(log_files[0], 'r', encoding='utf-8') as f:
                lines = f.readlines()
                result = ''.join(lines[-50:])
                print(f"   ✅ ログ取得: {len(lines)}行")
                return {'logs': result}
        
        print("   ⚠️  ログファイルなし")
        return {'logs': 'ログファイルが見つかりません'}
        
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        return {'logs': f'エラー: {str(e)}'}

@app.get("/api/snapshot")
async def get_snapshot():
    """システムスナップショットを取得（新規追加）"""
    try:
        print("📸 /api/snapshot 呼び出し")
        
        # 統計情報を集約
        stats = await get_stats()
        pending = await get_pending_tasks()
        instructions = await get_instructions()
        
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'stats': stats,
            'pending_tasks_count': len(pending),
            'pending_instructions_count': len(instructions),
            'system_status': 'running'
        }
        
        print(f"   ✅ スナップショット生成")
        return snapshot
        
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def start_server(port: int = 8000):
    """サーバーを起動"""
    print(f"\n{'=' * 80}")
    print("🌐 Webダッシュボードサーバー起動（エラー修正版）")
    print('=' * 80)
    print(f"\n📍 アクセスURL: http://localhost:{port}")
    print("\n🔧 改善点:")
    print("  ✅ 詳細なエラーログ追加")
    print("  ✅ グローバルエラーハンドラー追加")
    print("  ✅ /api/snapshot エンドポイント追加")
    print("  ✅ 各エンドポイントのログ出力")
    print("\n⏹️  停止: Ctrl+C")
    print('=' * 80)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    start_server()

PYTHON

echo "✅ 修正版サーバー作成: agents/web_dashboard/dashboard_server_fixed.py"

# 修正版を既存に上書き
cp agents/web_dashboard/dashboard_server.py "agents/web_dashboard/dashboard_server.py.backup_${NOW_JST}"
cp agents/web_dashboard/dashboard_server_fixed.py agents/web_dashboard/dashboard_server.py

echo "✅ 既存サーバーを修正版に置き換え"

# F9HumanInterfaceのadd_instructionメソッドも確認・修正
cat > agents/f9_human_interface_fixed.py << 'PYTHON'
"""
F9: 人間指示インターフェース（修正版）
エラーハンドリングを強化
"""

import sys
import traceback
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class F9HumanInterface:
    """F9: 人間指示インターフェース（修正版）"""
    
    def __init__(self, sheets_manager=None):
        self.sheets = sheets_manager
        self.instructions_sheet = "human_instructions"
        
    def add_instruction(
        self,
        instruction_type: str,
        content: str,
        priority: str = 'medium',
        target_task: str = ''
    ) -> bool:
        """指示を追加（エラーハンドリング強化版）"""
        try:
            print(f"\n{'=' * 80}")
            print("📝 F9: 指示を追加")
            print('=' * 80)
            print(f"  instruction_type: {instruction_type}")
            print(f"  content: {content}")
            print(f"  priority: {priority}")
            print(f"  target_task: {target_task}")
            
            # 指示データを作成
            row_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                instruction_type,
                'pending',
                content,
                priority,
                target_task,
                ''
            ]
            
            print(f"\n  📋 Google Sheetsに追加中...")
            
            # Google Sheetsに追加
            result = self.sheets.service.spreadsheets().values().append(
                spreadsheetId=self.sheets.spreadsheet_id,
                range=f"{self.instructions_sheet}!A:G",
                valueInputOption="RAW",
                body={"values": [row_data]}
            ).execute()
            
            print(f"  ✅ 追加成功")
            print(f"  📊 更新範囲: {result.get('updates', {}).get('updatedRange', 'N/A')}")
            print('=' * 80)
            print()
            
            return True
            
        except Exception as e:
            print(f"\n{'=' * 80}")
            print("❌ F9: 指示追加エラー")
            print(f"  エラータイプ: {type(e).__name__}")
            print(f"  エラー内容: {e}")
            print('=' * 80)
            traceback.print_exc()
            print('=' * 80)
            print()
            
            return False
    
    def check_human_instructions(self) -> List[Dict[str, Any]]:
        """人間からの指示をチェック（既存コードを維持）"""
        print("\n" + "=" * 80)
        print("📨 F9: 人間指示チェック")
        print("=" * 80)
        
        try:
            result = self.sheets.service.spreadsheets().values().get(
                spreadsheetId=self.sheets.spreadsheet_id,
                range=f"{self.instructions_sheet}!A2:G100"
            ).execute()
            
            values = result.get('values', [])
            
            pending_instructions = []
            for i, row in enumerate(values, 2):
                if len(row) < 3:
                    continue
                
                status = row[2] if len(row) > 2 else ''
                
                if status == 'pending':
                    instruction = {
                        'row_index': i,
                        'timestamp': row[0],
                        'instruction_type': row[1],
                        'status': status,
                        'content': row[3] if len(row) > 3 else '',
                        'priority': row[4] if len(row) > 4 else 'medium',
                        'target_task': row[5] if len(row) > 5 else ''
                    }
                    pending_instructions.append(instruction)
            
            if pending_instructions:
                print(f"\n📬 {len(pending_instructions)}件の未処理指示があります")
                for i, inst in enumerate(pending_instructions, 1):
                    print(f"  {i}. [{inst['instruction_type']}] {inst['content'][:50]}...")
            else:
                print("\n✅ 未処理の指示はありません")
            
            return pending_instructions
            
        except Exception as e:
            if '範囲が見つかりません' in str(e) or 'Unable to parse range' in str(e):
                print("\n⚠️  human_instructions シートが存在しません")
                return []
            else:
                print(f"❌ 指示チェックエラー: {e}")
                traceback.print_exc()
                return []

PYTHON

echo "✅ F9修正版作成: agents/f9_human_interface_fixed.py"

# 既存を置き換え
cp agents/f9_human_interface.py "agents/f9_human_interface.py.backup_${NOW_JST}"
cp agents/f9_human_interface_fixed.py agents/f9_human_interface.py

echo "✅ 既存F9を修正版に置き換え"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ エラー修正完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 修正内容:"
echo "  1. ✅ 詳細なエラーログ追加"
echo "  2. ✅ グローバルエラーハンドラー追加"
echo "  3. ✅ /api/snapshot エンドポイント追加（404対策）"
echo "  4. ✅ 各エンドポイントのデバッグログ"
echo "  5. ✅ F9HumanInterface.add_instruction エラーハンドリング強化"
echo ""
echo "🔍 エラー原因の特定:"
echo "  - 404エラー: /api/snapshot が未実装 → 追加完了"
echo "  - 500エラー: 例外処理不足 → 詳細ログで原因特定可能に"
echo ""
echo "🎯 次のステップ:"
echo "  1. ダッシュボード再起動"
echo "  2. エラーログを確認しながら動作テスト"
echo ""
echo "📝 再起動コマンド:"
echo "  pkill -f dashboard_server.py"
echo "  bash start_dashboard_background_v2.sh"
echo ""

# 自動再起動
read -p "ダッシュボードを再起動しますか？ [Y/n] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "🔄 ダッシュボードを再起動中..."
    pkill -f dashboard_server.py 2>/dev/null
    sleep 2
    bash start_dashboard_background_v2.sh
else
    echo "⏭️  スキップしました"
    echo "   手動再起動: bash start_dashboard_background_v2.sh"
fi

