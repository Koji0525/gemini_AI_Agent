#!/usr/bin/env python3
"""品質スコア実際データ連携モジュール - レート制限対策版"""
import sys
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ['DISPLAY'] = ':1'

from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import get_config


class QualityScoreIntegratorV2:
    """品質スコア実際データ連携クラス - キャッシュ機能付き"""
    
    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = sheets_manager
        self.config = get_config()
        # キャッシュ: 1回の読み込みで全データを保持
        self._quality_cache: Optional[Dict[str, float]] = None
        self._cache_timestamp: float = 0
        self._cache_ttl: int = 300  # キャッシュ有効期間: 5分
    
    def get_actual_quality_scores(self, force_refresh: bool = False) -> Dict[str, float]:
        """
        実際の品質スコアを実行ログから取得（キャッシュ付き）
        
        Args:
            force_refresh: True の場合、キャッシュを無視して再取得
        
        Returns:
            タスクIDをキーとした品質スコアの辞書
        """
        # キャッシュの有効性チェック
        current_time = time.time()
        if (not force_refresh and 
            self._quality_cache is not None and 
            (current_time - self._cache_timestamp) < self._cache_ttl):
            print(f"✅ キャッシュから品質スコアを取得: {len(self._quality_cache)}件")
            return self._quality_cache
        
        # 新規取得
        actual_scores = {}
        
        try:
            print("🔄 スプレッドシートから品質スコアを取得中...")
            # スプレッドシートにアクセス（1回のみ）
            spreadsheet = self.sheets.gc.open_by_key(self.config.get("SPREADSHEET_ID"))
            log_sheet = spreadsheet.worksheet("task_execution_log")
            
            # 実行ログを取得（1回のみ）
            logs = log_sheet.get_all_records()
            print(f"✅ 実行ログ取得: {len(logs)}件")
            
            # ログを解析して品質スコアを抽出
            for log in logs:
                task_id = log.get('task_id', '')
                if not task_id:
                    continue
                
                # 品質スコアをログから抽出
                quality_score = self._extract_quality_from_log(log)
                if quality_score > 0:
                    # 同じタスクIDが複数ある場合は最新のスコアを採用
                    if str(task_id) not in actual_scores:
                        actual_scores[str(task_id)] = quality_score
                    else:
                        # より高いスコアを採用（品質改善の傾向を反映）
                        actual_scores[str(task_id)] = max(
                            actual_scores[str(task_id)], 
                            quality_score
                        )
            
            print(f"📊 品質スコア取得完了: {len(actual_scores)}件")
            
            # キャッシュに保存
            self._quality_cache = actual_scores
            self._cache_timestamp = current_time
            
            return actual_scores
            
        except Exception as e:
            print(f"❌ 品質スコア取得エラー: {e}")
            # エラー時は空の辞書を返す（キャッシュは更新しない）
            return {}
    
    def _extract_quality_from_log(self, log: Dict) -> float:
        """
        ログデータから品質スコアを抽出
        
        Args:
            log: ログの1行（辞書形式）
        
        Returns:
            品質スコア（0.0-10.0）、取得できない場合は0.0
        """
        # 1. 明示的なquality_scoreフィールドを検索
        for key, value in log.items():
            if 'quality' in key.lower() and isinstance(value, (int, float)) and value > 0:
                return float(value)
        
        # 2. 文字列から品質スコアをパターンマッチングで抽出
        for key, value in log.items():
            if value and isinstance(value, str):
                # パターン: "品質スコア: 8.5" または "quality: 9" など
                patterns = [
                    r'品質スコア[：:\s]*(\d+\.?\d*)',
                    r'品質[：:\s]*(\d+\.?\d*)',
                    r'quality[：:\s]*(\d+\.?\d*)',
                    r'score[：:\s]*(\d+\.?\d*)',
                    r'評価[：:\s]*(\d+\.?\d*)/10'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, value, re.IGNORECASE)
                    if matches:
                        score = float(matches[0])
                        if 0 <= score <= 10:  # スコアの範囲チェック
                            return score
        
        # 3. デフォルト値（実際には取得失敗を表す）
        return 0.0

    def calculate_goal_quality(
        self, 
        goal_id: str, 
        tasks: List[Dict],
        use_cache: bool = True
    ) -> float:
        """
        親目標の平均品質スコアを計算
        
        Args:
            goal_id: 親目標ID
            tasks: 目標に属するタスクのリスト
            use_cache: キャッシュを使用するかどうか
        
        Returns:
            平均品質スコア（1回の取得で全タスク分を計算）
        """
        # キャッシュされた品質スコアを取得（1回のみ）
        actual_scores = self.get_actual_quality_scores(force_refresh=not use_cache)
        goal_task_scores = []
        
        # タスクごとにキャッシュから品質スコアを取得
        for task in tasks:
            task_id = task.get('id') or task.get('task_id')
            if task_id and str(task_id) in actual_scores:
                score = actual_scores[str(task_id)]
                if score > 0:  # 有効なスコアのみ
                    goal_task_scores.append(score)
        
        if goal_task_scores:
            avg_quality = sum(goal_task_scores) / len(goal_task_scores)
            print(f"🎯 目標 {goal_id}: 平均品質 {avg_quality:.1f} ({len(goal_task_scores)}タスク)")
            return round(avg_quality, 1)
        else:
            print(f"⚠️ 目標 {goal_id}: 品質データなし（デフォルト値使用）")
            return 8.5  # デフォルト値
    
    def clear_cache(self):
        """キャッシュをクリア"""
        self._quality_cache = None
        self._cache_timestamp = 0
        print("🗑️ 品質スコアキャッシュをクリアしました")


# ==
# テスト実行
# ==
async def test_quality_integration():
    """品質スコア取得のテスト"""
    print("="*70)
    print("🧪 品質スコア実際データ連携テスト（レート制限対策版）")
    print("="*70)
    
    config = get_config()
    sheets = GoogleSheetsManager(
        spreadsheet_id=config.get("SPREADSHEET_ID"),
        service_account_file=config.get("SERVICE_ACCOUNT_FILE")
    )
    
    integrator = QualityScoreIntegratorV2(sheets)
    
    # 1回目: 新規取得
    print("\n【1回目の取得】")
    actual_scores = integrator.get_actual_quality_scores()
    print(f"取得した品質スコア: {len(actual_scores)}件")
    
    # サンプル表示
    for task_id, score in list(actual_scores.items())[:5]:
        print(f"  - タスク {task_id}: {score}")
    
    # 2回目: キャッシュから取得（APIアクセスなし）
    print("\n【2回目の取得（キャッシュ）】")
    actual_scores_cached = integrator.get_actual_quality_scores()
    print(f"キャッシュから取得: {len(actual_scores_cached)}件")
    
    # 3回目: 強制リフレッシュ
    print("\n【3回目の取得（強制リフレッシュ）】")
    actual_scores_refresh = integrator.get_actual_quality_scores(force_refresh=True)
    print(f"再取得: {len(actual_scores_refresh)}件")
    
    print("\n✅ テスト完了")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_quality_integration())
