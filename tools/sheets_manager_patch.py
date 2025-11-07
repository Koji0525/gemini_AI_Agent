#!/usr/bin/env python3
"""
GoogleSheetsManager パッチ - 範囲指定メソッド追加
"""

import sys
from pathlib import Path

# sheets_manager.pyに追加するメソッド
RANGE_METHOD = '''
    def read_range(self, range_spec: str) -> List[List[Any]]:
        """
        範囲指定で読み込み
        
        Args:
            range_spec: 'sheet_name!A1:Z10' または 'sheet_name' 形式
            
        Returns:
            List[List[Any]]: セルデータの2次元配列
            
        Examples:
            >>> sheets.read_range('project_goal!A1:Z1')  # ヘッダー行のみ
            >>> sheets.read_range('pm_tasks!A2:Z100')    # データ行
            >>> sheets.read_range('project_goal')        # シート全体
        """
        try:
            # 範囲指定のパース
            if '!' in range_spec:
                sheet_name, cell_range = range_spec.split('!', 1)
            else:
                sheet_name = range_spec
                cell_range = None
            
            # ワークシート取得
            worksheet = self.spreadsheet.worksheet(sheet_name)
            
            # データ取得
            if cell_range:
                data = worksheet.get(cell_range)
                self.logger.info(f"✅ {range_spec}: {len(data)}行取得")
            else:
                data = worksheet.get_all_values()
                self.logger.info(f"✅ {sheet_name}: {len(data)}行取得")
            
            return data
            
        except Exception as e:
            self.logger.error(f"❌ 範囲読み込みエラー ({range_spec}): {e}")
            return []
'''

print("=" * 60)
print("📦 GoogleSheetsManager パッチ")
print("=" * 60)
print("\n追加するメソッド:")
print(RANGE_METHOD)
print("\n" + "=" * 60)
print("✅ read_range メソッドを sheets_manager.py に追加してください")
print("   場所: write_sheet メソッドの後")
print("=" * 60)
