#!/usr/bin/env python3
"""
修正版シートバリデータ - 正しいシート作成方法を実装
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from browser_control.sheets_manager import GoogleSheetsManager
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
import time

class FixedSheetValidator:
    """修正版シート検証と自動修復クラス"""
    
    def __init__(self):
        self.sheets_manager = GoogleSheetsManager()
        self.service = self._build_sheets_service()
        self.SPREADSHEET_ID = '1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s'
        
        self.required_sheets = {
            'project_goal': ['goal_id', 'goal_description', 'status', 'created_at'],
            'pm_tasks': ['task_id', 'parent_goal_id', 'description', 'status'],
            'task_execution_log': ['log_id', 'task_id', 'timestamp', 'status'],
            'quality_feedback': ['feedback_id', 'task_id', 'quality_score', 'review_status']
        }
    
    def _build_sheets_service(self):
        """Sheets API サービスを構築"""
        try:
            service_account_file = '/workspaces/gemini_AI_Agent/configuration/service_account.json'
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            return build('sheets', 'v4', credentials=credentials)
        except Exception as e:
            print(f"❌ APIサービス構築エラー: {e}")
            return None
    
    def get_existing_sheets(self):
        """既存シートの一覧を取得"""
        try:
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.SPREADSHEET_ID
            ).execute()
            sheets = spreadsheet.get('sheets', [])
            return [sheet['properties']['title'] for sheet in sheets]
        except Exception as e:
            print(f"❌ シート一覧取得エラー: {e}")
            return []
    
    def create_sheet(self, sheet_name):
        """新しいシートを作成（正しい方法）"""
        try:
            print(f"📝 {sheet_name}シートを作成します...")
            
            # バッチ更新リクエストでシート追加
            batch_update_request = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
            }
            
            response = self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.SPREADSHEET_ID,
                body=batch_update_request
            ).execute()
            
            print(f"✅ {sheet_name}シート作成リクエスト成功")
            
            # シート作成後の待機
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"❌ {sheet_name}シート作成エラー: {e}")
            return False
    
    def validate_all_sheets(self):
        """全必須シートを検証"""
        print("🔍 必須シート検証開始...")
        
        if not self.service:
            print("❌ APIサービスが利用できません")
            return False
        
        # 既存シートを取得
        existing_sheets = self.get_existing_sheets()
        print(f"📊 既存シート: {existing_sheets}")
        
        results = {}
        for sheet_name, required_columns in self.required_sheets.items():
            if sheet_name in existing_sheets:
                result = self.validate_sheet_content(sheet_name, required_columns)
                results[sheet_name] = result
            else:
                results[sheet_name] = {
                    'status': 'missing',
                    'error': 'シートが存在しません'
                }
        
        # 結果集計
        total_sheets = len(results)
        valid_sheets = sum(1 for r in results.values() if r['status'] == 'valid')
        
        print(f"\n�� 検証結果: {valid_sheets}/{total_sheets} シート正常")
        
        for sheet_name, result in results.items():
            status_icon = "✅" if result['status'] == 'valid' else "❌"
            print(f"  {status_icon} {sheet_name}: {result['status']}")
            
            if result['status'] != 'valid' and 'error' in result:
                print(f"     エラー: {result['error']}")
        
        return all(r['status'] == 'valid' for r in results.values())
    
    def validate_sheet_content(self, sheet_name, required_columns=None):
        """シートの内容を検証"""
        try:
            # シート存在確認
            test_data = self.sheets_manager.read_range(f'{sheet_name}!A1:Z1')
            
            if not test_data:
                return {
                    'status': 'empty',
                    'error': 'シートが空です'
                }
            
            # ヘッダー確認
            headers = test_data[0] if test_data else []
            
            if required_columns:
                missing_columns = [col for col in required_columns if col not in headers]
                if missing_columns:
                    return {
                        'status': 'invalid_headers',
                        'error': f'必須カラム不足: {missing_columns}'
                    }
            
            return {
                'status': 'valid',
                'headers': headers,
                'row_count': len(self.sheets_manager.read_range(f'{sheet_name}!A2:Z1000')) if test_data else 0
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def repair_all_missing_sheets(self):
        """全不足シートを修復（正しい方法）"""
        print("🚀 自動修復を開始...")
        
        if not self.service:
            print("❌ APIサービスが利用できないため修復できません")
            return False
        
        # 既存シートを取得
        existing_sheets = self.get_existing_sheets()
        
        repair_results = {}
        for sheet_name, required_columns in self.required_sheets.items():
            if sheet_name not in existing_sheets:
                print(f"🛠️  {sheet_name} シートを作成します...")
                
                # シート作成
                sheet_created = self.create_sheet(sheet_name)
                
                if sheet_created:
                    # ヘッダーを追加
                    time.sleep(2)  # 作成後の待機
                    success = self.sheets_manager.append_rows(sheet_name, [required_columns])
                    repair_results[sheet_name] = success
                    
                    if success:
                        print(f"✅ {sheet_name} シート作成完了")
                    else:
                        print(f"⚠️  {sheet_name} シート作成したがヘッダー追加失敗")
                else:
                    repair_results[sheet_name] = False
            else:
                # シートは存在するが内容を検証
                validation = self.validate_sheet_content(sheet_name, required_columns)
                repair_results[sheet_name] = (validation['status'] == 'valid')
        
        repaired_count = sum(1 for result in repair_results.values() if result)
        total_count = len(repair_results)
        
        print(f"\n📊 自動修復結果: {repaired_count}/{total_count} シート正常")
        
        for sheet_name, success in repair_results.items():
            status_icon = "✅" if success else "❌"
            print(f"  {status_icon} {sheet_name}")
        
        return all(repair_results.values())

def main():
    """メイン実行"""
    validator = FixedSheetValidator()
    
    print("�� 修正版スプレッドシート整合性チェック")
    print("=" * 50)
    
    # 検証実行
    is_valid = validator.validate_all_sheets()
    
    if not is_valid:
        print("\n⚠️ シートに問題があります。自動修復を実行しますか？")
        response = input("   自動修復を実行しますか？ (y/N): ")
        if response.lower() in ['y', 'yes']:
            success = validator.repair_all_missing_sheets()
            if success:
                print("🎉 自動修復完了")
            else:
                print("❌ 自動修復に失敗しました")
        else:
            print("💡 後で実行する場合: python3 tools/sheet_validator_fixed.py --repair")
    
    return is_valid

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--repair':
        validator = FixedSheetValidator()
        success = validator.repair_all_missing_sheets()
        sys.exit(0 if success else 1)
    else:
        success = main()
        sys.exit(0 if success else 1)
