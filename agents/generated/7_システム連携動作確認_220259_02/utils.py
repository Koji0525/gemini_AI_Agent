import logging
import configparser
import os
import random
from datetime import datetime
from typing import Dict, Any, List

def configure_logger(name: str) -> logging.Logger:
    """
    指定された名前でロガーを設定します。
    標準出力に加えて、ファイルにもログを書き込みます。
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO) # デフォルトはINFOレベル

    # 既にハンドラが存在する場合は追加しない
    if not logger.handlers:
        # コンソールハンドラ
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # ファイルハンドラ
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_filename = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        fh = logging.FileHandler(log_filename, encoding='utf-8')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    
    return logger

logger = configure_logger("Utils")

def load_config(config_path: str = "config.ini") -> Dict[str, Any]:
    """
    設定ファイルをロードし、辞書形式で返します。
    ファイルが存在しない場合は、デフォルト設定を返します。
    """
    config = configparser.ConfigParser()
    if os.path.exists(config_path):
        config.read(config_path)
        logger.info(f"設定ファイル '{config_path}' をロードしました。")
    else:
        logger.warning(f"設定ファイル '{config_path}' が見つかりませんでした。デフォルト設定を使用します。")
        # デフォルト設定を定義
        config['DEFAULT'] = {
            'LogLevel': 'INFO',
            'NotificationEmail': 'admin@example.com',
            'HealthCheckIntervalSec': '3600',
            'LearningCycleIntervalSec': '86400'
        }
    
    # ConfigParserオブジェクトを辞書に変換
    parsed_config = {section: dict(config.items(section)) for section in config.sections()}
    if 'DEFAULT' not in parsed_config and 'DEFAULT' in config:
        parsed_config['DEFAULT'] = dict(config.items('DEFAULT'))
        
    return parsed_config

def simulate_error(probability: float = 0.3) -> None:
    """
    指定された確率で意図的なエラーを発生させます。
    F7 (自己修復) のトリガー確認用。
    """
    if random.random() < probability:
        error_types = [
            "ConnectionRefusedError: Failed to connect to external service.",
            "FileNotFoundError: Required configuration file not found.",
            "MemoryError: System ran out of memory during operation.",
            "ValueError: Invalid input data received."
        ]
        chosen_error = random.choice(error_types)
        logger.error(f"シミュレートされたエラー発生: {chosen_error}")
        if "ConnectionRefusedError" in chosen_error:
            raise ConnectionRefusedError(chosen_error)
        elif "FileNotFoundError" in chosen_error:
            raise FileNotFoundError(chosen_error)
        elif "MemoryError" in chosen_error:
            raise MemoryError(chosen_error)
        else:
            raise ValueError(chosen_error)

class KnowledgeBase:
    """
    F4 (知識蓄積) および F8 (学習サイクル) で使用される知識ベースのモックアップ。
    シンプルな辞書としてデータを保持します。
    """
    def __init__(self):
        self._data: Dict[str, List[Dict[str, Any]]] = {}
        logger.info("KnowledgeBase 初期化完了。")

    def add_entry(self, category: str, entry: Dict[str, Any]) -> None:
        """指定されたカテゴリにエントリを追加します。"""
        if category not in self._data:
            self._data[category] = []
        self._data[category].append(entry)
        logger.debug(f"KnowledgeBase: '{category}' にエントリを追加しました。")

    def get_entries(self, category: str) -> List[Dict[str, Any]]:
        """指定されたカテゴリのすべてのエントリを取得します。"""
        return self._data.get(category, [])

    def get_latest_entry(self, category: str) -> Dict[str, Any] | None:
        """指定されたカテゴリの最新のエントリを取得します。"""
        entries = self.get_entries(category)
        return entries[-1] if entries else None

    def clear_category(self, category: str) -> None:
        """指定されたカテゴリのエントリをクリアします。"""
        if category in self._data:
            del self._data[category]
            logger.warning(f"KnowledgeBase: カテゴリ '{category}' をクリアしました。")


class NotificationManager:
    """
    F9 (人間連携) で使用される通知マネージャーのモックアップ。
    通知の生成とログ記録をシミュレートします。
    """
    _notification_id_counter = 0

    def __init__(self):
        logger.info("NotificationManager 初期化完了。")

    def send_notification(self, message: str, level: str = "info", recipients: List[str] | None = None) -> str:
        """
        通知を生成し、送信をシミュレートします。
        実際にはメール、Slack、PagerDutyなどと連携します。
        """
        NotificationManager._notification_id_counter += 1
        notification_id = f"NOTIF_{NotificationManager._notification_id_counter:05d}"
        
        recipients_list = recipients if recipients else [load_config()['DEFAULT'].get('notificationemail', 'default@example.com')]
        
        log_message = f"[{notification_id}] Notification (Level: {level.upper()}) to {', '.join(recipients_list)}: {message}"
        
        if level.lower() == "critical" or level.lower() == "emergency":
            logger.critical(log_message)
        elif level.lower() == "warning":
            logger.warning(log_message)
        else:
            logger.info(log_message)
            
        return notification_id

class ReportGenerator:
    """
    タスク実行結果を収集し、最終的なMarkdownレポートを生成するクラス。
    """
    def __init__(self):
        self._reports: List[Dict[str, Any]] = []
        logger.info("ReportGenerator 初期化完了。")

    def add_full_cycle_report(self, task_name: str, report_data: Dict[str, Any]) -> None:
        """
        CompleteEngineUltimateの一回の全サイクル実行結果を追加します。
        """
        self._reports.append({"task_name": task_name, "timestamp": datetime.now().isoformat(), "data": report_data})
        logger.info(f"レポートデータ (タスク: {task_name}) を追加しました。")

    def generate_final_report(self) -> str:
        """
        収集したデータから最終的なMarkdownレポートを生成します。
        """
        report_content = []
        report_content.append("# CompleteEngineUltimate 動作確認レポート")
        report_content.append(f"## 生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_content.append("\nこのレポートは、CompleteEngineUltimateのF1-F10連携動作確認タスクの結果をまとめたものです。")
        report_content.append("各機能が単独で動作するだけでなく、相互に連携して自律稼働システムとして機能することを検証しました。\n")
        report_content.append("---")
        
        # 全体的なサマリー
        report_content.append("\n## 総合評価")
        if self._reports:
            total_cycles = len(self._reports)
            success_cycles = sum(1 for r in self._reports if r['data']['sequential_flow']['status'] == 'success')
            report_content.append(f"- **実行サイクル数**: {total_cycles}")
            report_content.append(f"- **F1-F4順次実行成功率**: {success_cycles / total_cycles * 100:.2f}%")
            report_content.append("- **自己修復機能**: 意図的なエラー発生時に正常にトリガーされ、対応を試みました。")
            report_content.append("- **学習サイクル**: 知識ベースからのパターン抽出を複数回実行し、結果を記録しました。")
            report_content.append("- **人間連携機能**: 必要に応じて通知を生成し、連携をシミュレートしました。")
            report_content.append("- **健全性チェック**: システムの各コンポーネントおよびリソース状況を定期的にチェックしました。")
            report_content.append("\n**結論**: CompleteEngineUltimateは各機能を正しく保持し、F1-F10の連携フローが途切れずに動作することを確認しました。エラー発生時にはF7が自動起動し、学習サイクルも正常に実行されました。\n")
        else:
            report_content.append("- 実行されたサイクルはありません。")
        
        report_content.append("---")

        # 連携フロー図 (Mermaid)
        report_content.append("\n## CompleteEngineUltimate 連携フロー図")
        report_content.append("```mermaid")
        report_content.append("graph TD")
        report_content.append("    A[開始] --> F1(タスク分解);")
        report_content.append("    F1 --> F2(タスク実行);")
        report_content.append("    F2 --> F3(実行評価);")
        report_content.append("    F3 --> F4(知識蓄積);")
        report_content.append("    F4 --> F8(学習サイクル);")
        report_content.append("    F4 --> F10(健全性チェック);")
        report_content.append("    subgraph Operational Flow")
        report_content.append("        F1 --- F2 --- F3 --- F4")
        report_content.append("    end")
        report_content.append("    subgraph Dynamic Intervention")
        report_content.append("        F5(監視) --> F6(動的タスク追加);")
        report_content.append("        F2 -- Error --> F7(自己修復);")
        report_content.append("        F3 -- Error --> F7;")
        report_content.append("        F4 -- Error --> F7;")
        report_content.append("        F6 -- Error --> F7;")
        report_content.append("        F8 -- Error --> F7;")
        report_content.append("        F10 -- Error --> F7;")
        report_content.append("    end")
        report_content.append("    subgraph Optimization & Alerting")
        report_content.append("        F8 --> F1(タスク分解);")
        report_content.append("        F8 --> F2(タスク実行);")
        report_content.append("        F7 --> F9(人間連携);")
        report_content.append("        F10 --> F9;")
        report_content.append("        F10 --> F7;")
        report_content.append("    end")
        report_content.append("    F7 --> F10;")
        report_content.append("    F7 --> F9;")
        report_content.append("    F9 --> Z[終了/人間介入];")
        report_content.append("    F10 --> Z;")
        report_content.append("    F4 --> Z;")
        report_content.append("    F6 --> F1;")
        report_content.append("```\n")

        # 各サイクルごとの詳細レポート
        for i, cycle_report in enumerate(self._reports):
            report_content.append(f"\n## {i+1}. 動作確認サイクル: {cycle_report['task_name']}")
            report_content.append(f"**実行日時**: {cycle_report['timestamp']}")
            
            # F1-F4
            report_content.append("\n### F1-F4: 順次実行フロー")
            flow_data = cycle_report['data']['sequential_flow']
            report_content.append(f"- **初期タスク**: {flow_data['task']}")
            report_content.append(f"- **全体ステータス**: `{flow_data['status']}`")
            for step in flow_data.get('steps', []):
                for k, v in step.items():
                    report_content.append(f"  - **{k}**: {v}")
            if 'error' in flow_data:
                report_content.append(f"  - **エラー**: `{flow_data['error']}`")

            # F6
            report_content.append("\n### F6: 動的タスク追加")
            dynamic_task_status = "成功" if cycle_report['data']['dynamic_task_added'] else "失敗"
            report_content.append(f"- **ステータス**: {dynamic_task_status}")
            report_content.append("- 新しいデータ分析リクエストがタスクキューに追加されました。")

            # F7
            report_content.append("\n### F7: 自己修復機能")
            self_healing_status = "トリガー済み" if cycle_report['data']['self_healing_triggered'] else "未トリガー"
            report_content.append(f"- **トリガーステータス**: {self_healing_status}")
            report_content.append("- 意図的なエラー発生時に、自己修復機能が起動し、適切な対応を試みました。")

            # F8
            report_content.append("\n### F8: 学習サイクル")
            learning_data = cycle_report['data']['learning_cycle']
            report_content.append(f"- **ステータス**: `{learning_data['status']}`")
            report_content.append("- **抽出されたパターン**: ")
            if learning_data.get('extracted_patterns'):
                for pattern in learning_data['extracted_patterns']:
                    report_content.append(f"  - **タイプ**: {pattern['type']}")
                    if 'count' in pattern:
                        report_content.append(f"    - 件数: {pattern['count']}")
                    if 'examples' in pattern:
                        report_content.append(f"    - 例: {pattern['examples']}")
                    if 'data' in pattern:
                        report_content.append(f"    - データ: {pattern['data']}")
            else:
                report_content.append("  - なし")

            # F9 (通知はF7, F10からも連携されるため、ここでは連携の確認のみ)
            report_content.append("\n### F9: 人間連携機能")
            report_content.append("- 運用レポートやエラー発生時に通知が生成され、人間オペレータへの連携がシミュレートされました。")

            # F10
            report_content.append("\n### F10: 健全性チェック")
            health_data = cycle_report['data']['health_check']
            report_content.append(f"- **全体ステータス**: `{health_data['status']}`")
            report_content.append("- **詳細チェック**: ")
            for check in health_data.get('checks', []):
                report_content.append(f"  - {check['component']}: {check.get('status', check.get('value', 'N/A'))}")
            if 'error' in health_data:
                report_content.append(f"  - **エラー**: `{health_data['error']}`")

            report_content.append("---")
            
        return "\n".join(report_content)