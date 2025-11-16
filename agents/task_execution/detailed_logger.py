"""
タスク実行詳細ログ生成モジュール
目的: タスク実行結果を詳細に記録し、auto_logsに保存
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class DetailedLogger:
    """タスク実行の詳細ログを生成"""
    
    def __init__(self, base_output_dir: str = "agent_outputs"):
        self.base_output_dir = Path(base_output_dir)
        self.auto_logs_dir = self.base_output_dir / "auto_logs"
        self.details_dir = self.auto_logs_dir / "details"
        
        # ディレクトリ作成
        self.auto_logs_dir.mkdir(parents=True, exist_ok=True)
        self.details_dir.mkdir(parents=True, exist_ok=True)
    
    def create_detailed_log(
        self, 
        task_id: str,
        task_description: str,
        execution_result: Dict[str, Any],
        output_files: List[str] = None
    ) -> str:
        """
        詳細なログを生成
        
        Args:
            task_id: タスクID
            task_description: タスク説明
            execution_result: 実行結果の辞書
            output_files: 生成されたファイルのリスト
        
        Returns:
            生成されたログファイルのパス
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"task_{task_id}_{timestamp}_detailed.log"
        log_path = self.auto_logs_dir / log_filename
        
        # ログ内容を構築
        log_content = self._build_log_content(
            task_id,
            task_description,
            execution_result,
            output_files or []
        )
        
        # ファイルに書き込み
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(log_content)
        
        # 詳細情報をJSONでも保存
        json_path = self.details_dir / f"task_{task_id}_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'task_id': task_id,
                'description': task_description,
                'timestamp': timestamp,
                'result': execution_result,
                'output_files': output_files or []
            }, f, indent=2, ensure_ascii=False)
        
        return str(log_path)
    
    def _build_log_content(
        self,
        task_id: str,
        description: str,
        result: Dict[str, Any],
        output_files: List[str]
    ) -> str:
        """ログ内容を構築"""
        
        lines = []
        lines.append("=" * 80)
        lines.append(f"タスク実行詳細ログ")
        lines.append("=" * 80)
        lines.append("")
        
        # 基本情報
        lines.append("【基本情報】")
        lines.append(f"  タスクID      : {task_id}")
        lines.append(f"  タスク内容    : {description}")
        lines.append(f"  実行日時      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"  ステータス    : {result.get('status', 'unknown')}")
        lines.append("")
        
        # 実行結果サマリー
        lines.append("【実行結果サマリー】")
        if 'summary' in result:
            lines.append(f"  {result['summary']}")
        else:
            lines.append(f"  実行成功")
        lines.append("")
        
        # 生成ファイル情報
        lines.append("【生成ファイル一覧】")
        if output_files:
            for i, file_path in enumerate(output_files, 1):
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    lines.append(f"  {i}. {file_path}")
                    lines.append(f"     サイズ: {size:,} bytes ({self._format_size(size)})")
                else:
                    lines.append(f"  {i}. {file_path} (ファイルが見つかりません)")
            lines.append(f"  合計: {len(output_files)} ファイル")
        else:
            lines.append("  生成ファイルなし")
        lines.append("")
        
        # 品質スコア
        if 'quality_score' in result:
            lines.append("【品質評価】")
            lines.append(f"  品質スコア: {result['quality_score']}/10")
            if 'quality_description' in result:
                lines.append(f"  評価詳細: {result['quality_description']}")
            lines.append("")
        
        # 実行ログ詳細
        if 'execution_log' in result:
            lines.append("【実行ログ詳細】")
            lines.append(result['execution_log'])
            lines.append("")
        
        # ナレッジベース参照情報
        if 'knowledge_references' in result:
            lines.append("【参照したナレッジ】")
            for ref in result['knowledge_references']:
                lines.append(f"  - {ref.get('title', 'N/A')}")
                lines.append(f"    類似度: {ref.get('similarity', 0):.3f}")
            lines.append("")
        
        # エラー情報（ある場合）
        if 'error' in result:
            lines.append("【エラー情報】")
            lines.append(f"  エラー内容: {result['error']}")
            if 'error_trace' in result:
                lines.append("  スタックトレース:")
                lines.append(result['error_trace'])
            lines.append("")
        
        # メトリクス
        lines.append("【実行メトリクス】")
        lines.append(f"  実行時間: {result.get('elapsed_time', 'N/A')}")
        lines.append(f"  リトライ回数: {result.get('retry_count', 0)}")
        lines.append("")
        
        lines.append("=" * 80)
        lines.append("ログ生成完了")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _format_size(self, size_bytes: int) -> str:
        """バイト数を読みやすい形式に変換"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
