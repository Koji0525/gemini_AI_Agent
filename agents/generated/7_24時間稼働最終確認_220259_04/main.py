import time
import logging
import json
import os
import sys
from datetime import datetime, timedelta
import random

# utils.py からインポート
# プロジェクトのルートがPythonのパスに含まれていることを前提とします
try:
    from utils import (
        get_cpu_usage, get_memory_usage, get_disk_usage,
        log_event, rotate_log_file, simulate_api_call, send_notification,
        calculate_memory_leak_rate
    )
except ImportError as e:
    print(f"Error importing utility functions: {e}")
    print("Please ensure utils.py is in the same directory or in PYTHONPATH.")
    sys.exit(1)

class AutonomousSystemMonitor:
    """
    24時間自律稼働システムの最終確認を行う監視システム。
    リソース監視、エラーハンドリング、学習サイクル、API使用量監視、ログ管理を統合する。
    """
    def __init__(self, config_path: str = "config.json"):
        """
        監視システムを初期化する。
        設定ファイルを読み込み、ロギングを設定し、内部状態を初期化する。

        Args:
            config_path (str): 設定ファイルへのパス。
        """
        self.config = self._load_config(config_path)
        self._setup_logging()
        self.start_time = datetime.now()
        self.last_learning_trigger = datetime.now()
        self.error_count_since_last_learning = 0
        self.api_usage = {
            "Claude_API": {"count": 0, "cost": 0.0, "last_minute_calls": 0, "last_minute_reset": datetime.now()},
            "Google_Sheets_API": {"count": 0, "cost": 0.0, "last_minute_calls": 0, "last_minute_reset": datetime.now()}
        }
        self.known_issues = []  # F8 (自己進化) で蓄積されるナレッジベースの代わり
        self.system_status = {"healthy": True, "message": "System operational"}
        self.memory_history = []  # メモリリーク検出のための履歴
        self.last_cpu_check_time = datetime.now() - timedelta(seconds=self.config.get("resource_check_interval_seconds", 300) + 1) # 初回実行を保証
        self.last_disk_check_time = datetime.now() - timedelta(seconds=self.config.get("resource_check_interval_seconds", 300) + 1) # 初回実行を保証

        logging.info(f"Autonomous System Monitor initialized with config: {json.dumps(self.config, indent=2)}")
        if self.config.get("simulation_mode"):
            logging.warning("System is running in SIMULATION MODE. Resource metrics and error handling are simulated.")
        else:
            logging.info("System is running in REAL MODE. Attempting to fetch real system metrics.")

    def _load_config(self, config_path: str) -> dict:
        """
        設定ファイルを読み込む。ファイルが見つからない場合はデフォルト設定を使用する。
        
        Args:
            config_path (str): 設定ファイルへのパス。

        Returns:
            dict: 読み込まれた設定。
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logging.info(f"Successfully loaded configuration from {config_path}")
            return config
        except FileNotFoundError:
            logging.error(f"Config file not found: {config_path}. Using default settings.")
            return self._get_default_config()
        except json.JSONDecodeError:
            logging.error(f"Error decoding config file: {config_path}. Using default settings.")
            return self._get_default_config()
        except Exception as e:
            logging.error(f"An unexpected error occurred while loading config: {e}. Using default settings.")
            return self._get_default_config()

    def _get_default_config(self) -> dict:
        """
        デフォルト設定を返す。

        Returns:
            dict: デフォルト設定の辞書。
        """
        return {
            "monitor_interval_seconds": 60,
            "resource_check_interval_seconds": 300, # 5分ごと
            "cpu_threshold_percent": 80,
            "memory_threshold_percent": 85,
            "disk_threshold_percent": 90,
            "memory_leak_check_window_minutes": 30,
            "memory_leak_rate_threshold_mb_per_hour": 10,
            "max_retries_on_error": 3,
            "f7_healing_probability": 0.7, # 自己修復の初期成功確率
            "learning_cycle_trigger_hours": 6,
            "learning_cycle_trigger_errors": 50,
            "claude_api_cost_per_call": 0.015, # シミュレーション値
            "google_sheets_api_cost_per_call": 0.0001, # シミュレーション値
            "claude_api_rate_limit_per_minute": 100,
            "google_sheets_api_rate_limit_per_minute": 1000,
            "log_file": "logs/monitor.log",
            "error_log_file": "logs/errors.log",
            "api_log_file": "logs/api_usage.log",
            "max_log_size_mb": 10,
            "log_backup_count": 5,
            "human_notification_emails": ["admin@example.com", "devops@example.com"],
            "simulation_mode": True # シミュレーションモードを有効化
        }

    def _setup_logging(self):
        """
        ロギングを設定する。ログディレクトリの作成とファイルハンドラの追加を含む。
        """
        log_dir = os.path.dirname(self.config["log_file"])
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # 基本ロガー (monitor.log)
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(self.config["log_file"], encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        # エラーロガー (errors.log)
        self.error_logger = logging.getLogger('error_logger')
        self.error_logger.setLevel(logging.ERROR)
        if not self.error_logger.handlers: # 重複登録防止
            error_handler = logging.FileHandler(self.config["error_log_file"], encoding='utf-8')
            error_handler.setFormatter(logging.Formatter(log_format))
            self.error_logger.addHandler(error_handler)

        # APIロガー (api_usage.log)
        self.api_logger = logging.getLogger('api_logger')
        self.api_logger.setLevel(logging.INFO)
        if not self.api_logger.handlers: # 重複登録防止
            api_handler = logging.FileHandler(self.config["api_log_file"], encoding='utf-8')
            api_handler.setFormatter(logging.Formatter(log_format))
            self.api_logger.addHandler(api_handler)

        logging.info("Logging configured successfully.")

    def _check_system_resources(self):
        """
        システムリソースを監視する (CPU, メモリ, ディスク)。
        閾値を超えた場合にアラートを発生させる。
        """
        current_time = datetime.now()
        simulation_mode = self.config["simulation_mode"]
        
        # CPU使用率の監視
        if (current_time - self.last_cpu_check_time).total_seconds() >= self.config["resource_check_interval_seconds"]:
            cpu_usage = get_cpu_usage(simulation_mode)
            logging.info(f"Current CPU Usage: {cpu_usage:.2f}%")
            if cpu_usage > self.config["cpu_threshold_percent"]:
                self._handle_alert("HIGH_CPU_USAGE", f"CPU usage ({cpu_usage:.2f}%) exceeded threshold ({self.config['cpu_threshold_percent']}%)")
            self.last_cpu_check_time = current_time

        # メモリ使用率とメモリリークの確認
        mem_usage_percent, total_mem_mb, used_mem_mb = get_memory_usage(simulation_mode)
        self.memory_history.append((current_time, used_mem_mb))
        
        # 指定された期間分の履歴を保持
        mem_leak_window = timedelta(minutes=self.config["memory_leak_check_window_minutes"])
        self.memory_history = [(t, m) for t, m in self.memory_history if t > current_time - mem_leak_window]

        logging.info(f"Current Memory Usage: {used_mem_mb:.2f}MB ({mem_usage_percent:.2f}%) of {total_mem_mb:.2f}MB")
        if mem_usage_percent > self.config["memory_threshold_percent"]:
            self._handle_alert("HIGH_MEMORY_USAGE", f"Memory usage ({mem_usage_percent:.2f}%) exceeded threshold ({self.config['memory_threshold_percent']}%)")

        # メモリリーク検出は十分なデータが揃ってから実施
        if len(self.memory_history) >= 2 and (self.memory_history[-1][0] - self.memory_history[0][0]) >= mem_leak_window * 0.8:
            leak_rate_mb_per_hour = calculate_memory_leak_rate(self.memory_history)
            logging.info(f"Estimated Memory Leak Rate: {leak_rate_mb_per_hour:.2f} MB/hour (over last {self.config['memory_leak_check_window_minutes']} min)")
            if leak_rate_mb_per_hour > self.config["memory_leak_rate_threshold_mb_per_hour"]:
                self._handle_alert("MEMORY_LEAK_DETECTED", f"Memory leak detected at {leak_rate_mb_per_hour:.2f} MB/hour, exceeding threshold {self.config['memory_leak_rate_threshold_mb_per_hour']} MB/hour")

        # ディスク容量の確認
        if (current_time - self.last_disk_check_time).total_seconds() >= self.config["resource_check_interval_seconds"]:
            disk_usage = get_disk_usage(simulation_mode)
            logging.info(f"Current Disk Usage: {disk_usage:.2f}%")
            if disk_usage > self.config["disk_threshold_percent"]:
                self._handle_alert("HIGH_DISK_USAGE", f"Disk usage ({disk_usage:.2f}%) exceeded threshold ({self.config['disk_threshold_percent']}%)")
            self.last_disk_check_time = current_time

    def _handle_alert(self, alert_type: str, message: str, retry_count: int = 0) -> bool:
        """
        システムアラートを処理し、エラーハンドリングロジックを適用する。
        F7 (自己修復), リトライ, F9 (人間通知) を含む。

        Args:
            alert_type (str): アラートの種類。
            message (str): アラートの詳細メッセージ。
            retry_count (int): 現在のリトライ回数。

        Returns:
            bool: 問題が解決されたかどうか (True: 解決, False: 未解決)。
        """
        self.error_count_since_last_learning += 1
        self.system_status["healthy"] = False
        self.system_status["message"] = f"Alert: {alert_type} - {message}"
        self.error_logger.error(f"[{alert_type}] {message} (Retry: {retry_count}/{self.config['max_retries_on_error']})")
        logging.error(f"System alert triggered: [{alert_type}] {message}")

        # F7 (自己修復) の試行
        if alert_type in self.known_issues:
            logging.info(f"Known issue '{alert_type}' detected. Attempting F7 self-healing based on learned patterns.")
            if random.random() < self.config['f7_healing_probability']:  # F7の成功をシミュレート
                logging.info(f"F7 (Self-Healing) successful for '{alert_type}'. System recovered.")
                self.system_status["healthy"] = True
                self.system_status["message"] = "System operational after F7 healing."
                self.error_logger.info(f"F7 (Self-Healing) successful for '{alert_type}'.")
                return True
            else:
                logging.warning(f"F7 (Self-Healing) failed for '{alert_type}'.")

        # リトライの試行
        if retry_count < self.config["max_retries_on_error"]:
            logging.warning(f"Attempting retry for '{alert_type}'. Retry count: {retry_count + 1}")
            time.sleep(2)  # リトライの遅延をシミュレート
            
            # リトライ後に成功する確率を少し高める (シミュレーション)
            if random.random() < (0.5 + retry_count * 0.1): 
                logging.info(f"Retry {retry_count + 1} for '{alert_type}' succeeded. System recovered.")
                self.system_status["healthy"] = True
                self.system_status["message"] = "System operational after retry."
                self.error_logger.info(f"Retry {retry_count + 1} for '{alert_type}' succeeded.")
                return True
            else:
                logging.warning(f"Retry {retry_count + 1} for '{alert_type}' failed.")
                return self._handle_alert(alert_type, message, retry_count + 1) # 再帰的にリトライを試みる
        else:
            # F9 (人間通知)
            logging.critical(f"Max retries reached for '{alert_type}'. Triggering F9 (Human Notification).")
            send_notification(
                f"CRITICAL: Autonomous system requires manual intervention for '{alert_type}' - {message}",
                "F9_CRITICAL",
                self.config["human_notification_emails"]
            )
            self.error_logger.critical(f"F9 (Human Notification) sent for '{alert_type}'. Manual intervention required.")
            self.system_status["message"] = f"CRITICAL: Manual intervention needed for {alert_type}."
            return False

    def _simulate_error(self):
        """
        ランダムなエラーをシミュレートする (テスト用)。
        """
        if random.random() < 0.08:  # 8%の確率でエラー発生
            error_types = ["NETWORK_FAILURE", "DB_CONNECTION_ERROR", "PROCESSING_TIMEOUT", "API_AUTH_ERROR", "DISK_FULL_SIM"]
            error_type = random.choice(error_types)
            error_message = f"Simulated {error_type} at {datetime.now().isoformat()}"
            logging.warning(f"Simulating an error: {error_type}")
            self._handle_alert(error_type, error_message)

    def _monitor_api_usage(self):
        """
        API使用量を監視し、レート制限への対処を確認する。
        """
        current_time = datetime.now()
        simulation_mode = self.config["simulation_mode"]
        
        # Claude API
        if (current_time - self.api_usage["Claude_API"]["last_minute_reset"]).total_seconds() >= 60:
            self.api_usage["Claude_API"]["last_minute_calls"] = 0
            self.api_usage["Claude_API"]["last_minute_reset"] = current_time

        if random.random() < 0.35:  # 35%の確率でClaude APIコールをシミュレート
            calls = random.randint(1, 10)
            if self.api_usage["Claude_API"]["last_minute_calls"] + calls > self.config["claude_api_rate_limit_per_minute"]:
                logging.warning(f"Claude API rate limit approaching! Attempting to make {calls} calls, but only {self.config['claude_api_rate_limit_per_minute'] - self.api_usage['Claude_API']['last_minute_calls']} remaining this minute.")
                calls = max(0, self.config["claude_api_rate_limit_per_minute"] - self.api_usage["Claude_API"]["last_minute_calls"])
                if calls > 0:
                    logging.info(f"Claude API: Limiting calls to {calls} due to rate limit.")
                else:
                    logging.warning("Claude API: Rate limit hit. Backing off for this cycle.")
                    calls = 0 # 今サイクルはこれ以上コールしない

            for _ in range(calls):
                cost = simulate_api_call("Claude_API", self.config["claude_api_cost_per_call"], simulation_mode)
                self.api_usage["Claude_API"]["count"] += 1
                self.api_usage["Claude_API"]["cost"] += cost
                self.api_usage["Claude_API"]["last_minute_calls"] += 1
                self.api_logger.info(f"Claude API call. Total: {self.api_usage['Claude_API']['count']} calls, Cost: ${self.api_usage['Claude_API']['cost']:.4f}")

        # Google Sheets API
        if (current_time - self.api_usage["Google_Sheets_API"]["last_minute_reset"]).total_seconds() >= 60:
            self.api_usage["Google_Sheets_API"]["last_minute_calls"] = 0
            self.api_usage["Google_Sheets_API"]["last_minute_reset"] = current_time

        if random.random() < 0.65:  # 65%の確率でGoogle Sheets APIコールをシミュレート
            calls = random.randint(1, 20)
            if self.api_usage["Google_Sheets_API"]["last_minute_calls"] + calls > self.config["google_sheets_api_rate_limit_per_minute"]:
                logging.warning(f"Google Sheets API rate limit approaching! Attempting {calls} calls, but only {self.config['google_sheets_api_rate_limit_per_minute'] - self.api_usage['Google_Sheets_API']['last_minute_calls']} remaining this minute.")
                calls = max(0, self.config["google_sheets_api_rate_limit_per_minute"] - self.api_usage["Google_Sheets_API"]["last_minute_calls"])
                if calls > 0:
                    logging.info(f"Google Sheets API: Limiting calls to {calls} due to rate limit.")
                else:
                    logging.warning("Google Sheets API: Rate limit hit. Backing off for this cycle.")
                    calls = 0

            for _ in range(calls):
                cost = simulate_api_call("Google_Sheets_API", self.config["google_sheets_api_cost_per_call"], simulation_mode)
                self.api_usage["Google_Sheets_API"]["count"] += 1
                self.api_usage["Google_Sheets_API"]["cost"] += cost
                self.api_usage["Google_Sheets_API"]["last_minute_calls"] += 1
                self.api_logger.info(f"Google Sheets API call. Total: {self.api_usage['Google_Sheets_API']['count']} calls, Cost: ${self.api_usage['Google_Sheets_API']['cost']:.4f}")

        logging.info(f"API Usage Summary: Claude Calls={self.api_usage['Claude_API']['count']}, Cost=${self.api_usage['Claude_API']['cost']:.4f} | Google Sheets Calls={self.api_usage['Google_Sheets_API']['count']}, Cost=${self.api_usage['Google_Sheets_API']['cost']:.4f}")

    def _manage_logs(self):
        """
        ログファイルのローテーションと重要イベント記録の確認を行う。
        エラーログの通知は `_handle_alert` で行われる。
        """
        max_bytes = self.config["max_log_size_mb"] * 1024 * 1024
        backup_count = self.config["log_backup_count"]

        # 各ログファイルをローテーション
        rotate_log_file(self.config["log_file"], max_bytes, backup_count, logging.getLogger('root'))
        rotate_log_file(self.config["error_log_file"], max_bytes, backup_count, self.error_logger)
        rotate_log_file(self.config["api_log_file"], max_bytes, backup_count, self.api_logger)
        
        # 重要イベントの記録はloggingモジュールが自動で行うため、ここでは管理タスクのみ

    def _trigger_learning_cycle(self):
        """
        F8 (自己進化) の学習サイクルをトリガーし、ナレッジ蓄積とパターン学習の効果をシミュレートする。
        """
        current_time = datetime.now()
        time_elapsed = (current_time - self.last_learning_trigger).total_seconds() / 3600  # 時間を時間単位に変換

        if time_elapsed >= self.config["learning_cycle_trigger_hours"] or \
           self.error_count_since_last_learning >= self.config["learning_cycle_trigger_errors"]:
            
            logging.info(f"F8 (Self-Evolution) learning cycle triggered! Reason: {'Time elapsed' if time_elapsed >= self.config['learning_cycle_trigger_hours'] else 'Error count'}")
            
            # ナレッジ蓄積のシミュレーション: 新しい問題タイプを学習
            # 既存のKnown_issuesリストにランダムな新しい問題を追加
            possible_new_issues = ["API_AUTH_ERROR", "DB_CONNECTION_ERROR", "NETWORK_FAILURE", "PROCESSING_TIMEOUT", "INVALID_INPUT_FORMAT"]
            new_issue_to_learn = random.choice(possible_new_issues)

            if new_issue_to_learn not in self.known_issues and random.random() < 0.8:  # 80%の確率で新しい問題を学習
                self.known_issues.append(new_issue_to_learn)
                logging.info(f"F8: New knowledge acquired: '{new_issue_to_learn}' is now a known issue for F7 self-healing.")
            else:
                logging.info(f"F8: Refined existing knowledge or no new issues to learn from this cycle (already known or learning failed).")

            # パターン学習の効果測定: F7の成功確率を徐々に上げることで表現
            if self.config['f7_healing_probability'] < 0.95:  # 最大95%まで
                self.config['f7_healing_probability'] = min(0.95, self.config['f7_healing_probability'] + 0.01)
                logging.info(f"F8: Pattern learning effect - F7 healing probability increased to {self.config['f7_healing_probability']:.2f}")
            else:
                logging.info(f"F8: F7 healing probability is already at maximum ({self.config['f7_healing_probability']:.2f}).")


            self.last_learning_trigger = current_time
            self.error_count_since_last_learning = 0
            logging.info(f"F8 (Self-Evolution) cycle completed. Current known issues: {self.known_issues}")
            return True
        return False

    def generate_final_checklist(self) -> str:
        """
        最終チェックリストを作成し、ログに出力およびファイルに保存する。

        Returns:
            str: 生成されたチェックリストの内容。
        """
        checklist_output = f"""
======================================================
AUTONOMOUS SYSTEM 24H OPERATION FINAL CHECKLIST
Generated: {datetime.now().isoformat()}
======================================================

Purpose: Ensure the autonomous system is production-ready for 24/7 unattended operation.

---

1.  Pre-Startup Checks:
    [ ] Configuration file (config.json) loaded and verified.
    [ ] All necessary services (e.g., database, external APIs) are reachable.
    [ ] Sufficient disk space available (initial check).
    [ ] Log directories created and writeable.
    [ ] Network connectivity confirmed.
    [ ] System clock synchronized.
    [ ] Backup and recovery procedures confirmed.
    [ ] Monitoring tools (if external) are active.
    [ ] System time synchronized (NTP configured).

---

2.  In-Operation Monitoring Checklist:
    [ ] Continuous CPU usage monitoring: Max {self.config['cpu_threshold_percent']}% threshold. (Check logs/monitor.log)
    [ ] Continuous Memory usage monitoring: Max {self.config['memory_threshold_percent']}% threshold. (Check logs/monitor.log)
    [ ] Memory leak detection: Rate max {self.config['memory_leak_rate_threshold_mb_per_hour']} MB/hour over {self.config['memory_leak_check_window_minutes']} minutes. (Check logs/monitor.log for 'MEMORY_LEAK_DETECTED' alerts)
    [ ] Continuous Disk usage monitoring: Max {self.config['disk_threshold_percent']}% threshold. (Check logs/monitor.log)
    [ ] Error handling (F7/Retries/F9) verified:
        [ ] F7 Self-healing attempts recorded and successful where applicable. (Check logs/errors.log for 'F7 (Self-Healing) successful')
        [ ] Retry mechanisms engaged up to {self.config['max_retries_on_error']} times. (Check logs/errors.log for 'Retry X for ...')
        [ ] F9 Human notifications triggered for unrecoverable errors. (Check logs/errors.log for 'F9 (Human Notification) sent' and notification alerts)
    [ ] Learning cycle (F8) operation confirmed:
        [ ] Triggered by time ({self.config['learning_cycle_trigger_hours']} hours) or error count ({self.config['learning_cycle_trigger_errors']} errors). (Check logs/monitor.log for 'F8 (Self-Evolution) learning cycle triggered!')
        [ ] Knowledge accumulation evidenced (e.g., new 'known_issues' in system state). (Check logs/monitor.log for 'New knowledge acquired')
        [ ] Pattern learning effect observed (e.g., improved F7 success rate). (Check logs/monitor.log for 'F7 healing probability increased')
    [ ] API usage monitoring:
        [ ] Claude API calls and costs tracked. (Check logs/api_usage.log)
        [ ] Google Sheets API calls and costs tracked. (Check logs/api_usage.log)
        [ ] Rate limit handling observed (check logs/api_usage.log and monitor.log for warnings).
    [ ] Log management:
        [ ] Log file rotation confirmed (check logs/ directory for rotated files like monitor.log.1, errors.log.1 etc.).
        [ ] All critical events recorded in monitor.log and error.log.
        [ ] Error logs generating appropriate alerts/notifications (if F9 triggered).
    [ ] System overall health status (checked periodically).
    [ ] External dependencies (e.g., database, message queues) stability.

---

3.  Post-Operation / Shutdown Checks:
    [ ] All logs reviewed for any unhandled errors or warnings.
    [ ] Final API usage report generated and reviewed for cost overruns or unexpected spikes.
    [ ] System resources returned to normal levels after stopping (if applicable).
    [ ] No new persistent errors or degraded performance introduced.
    [ ] System shutdown gracefully (if applicable).
    [ ] Generated final report (this checklist) reviewed and archived.
    [ ] Data integrity verified (if applicable, e.g., database consistency checks).

======================================================
Current System Status at Completion:
  - Total Uptime: {(datetime.now() - self.start_time)}
  - Health: {self.system_status['message']}
  - Current F7 Healing Probability: {self.config['f7_healing_probability']:.2f}
  - Known Issues (Learned by F8): {self.known_issues if self.known_issues else "None yet"}
  - Total API Calls (Claude): {self.api_usage['Claude_API']['count']} (${self.api_usage['Claude_API']['cost']:.4f})
  - Total API Calls (Google Sheets): {self.api_usage['Google_Sheets_API']['count']} (${self.api_usage['Google_Sheets_API']['cost']:.4f})
======================================================
"""
        logging.info("--- Generating Final Checklist ---")
        print(checklist_output)  # コンソールにも出力
        checklist_file_path = os.path.join(os.path.dirname(self.config["log_file"]), "final_checklist.md")
        try:
            with open(checklist_file_path, "w", encoding='utf-8') as f:
                f.write(checklist_output)
            logging.info(f"Final checklist saved to {checklist_file_path}")
        except IOError as e:
            logging.error(f"Failed to save final checklist to {checklist_file_path}: {e}")
        return checklist_output

    def run_monitor(self, duration_hours: int = 6):
        """
        指定された期間、システムを監視するメインループを実行する。
        duration_hours=0 の場合、無限ループ。

        Args:
            duration_hours (int): 監視を行う期間 (時間単位)。0の場合は無限。
        """
        if duration_hours > 0:
            logging.info(f"Starting autonomous system monitor for {duration_hours} hours...")
            end_time = datetime.now() + timedelta(hours=duration_hours)
        else:
            logging.info("Starting autonomous system monitor in continuous mode (duration_hours=0)...")
            end_time = None

        cycle_count = 0
        try:
            while True:
                cycle_count += 1
                current_time = datetime.now()
                logging.info(f"\n--- Monitoring Cycle {cycle_count} at {current_time.isoformat()} ---")

                if end_time and current_time >= end_time:
                    logging.info(f"Monitoring duration of {duration_hours} hours completed.")
                    break

                self._check_system_resources()
                self._simulate_error()  # エラーハンドリングテストのためにランダムなエラーをシミュレート
                self._monitor_api_usage()
                self._manage_logs()
                self._trigger_learning_cycle()

                logging.info(f"Cycle {cycle_count} completed. System status: {self.system_status['message']}")
                time.sleep(self.config["monitor_interval_seconds"])
        except KeyboardInterrupt:
            logging.info("\nMonitor stopped manually via KeyboardInterrupt.")
        except Exception as e:
            logging.critical(f"An unexpected critical error occurred during monitoring: {e}", exc_info=True)
            self._handle_alert("CRITICAL_MONITOR_FAILURE", f"Monitor itself encountered a critical error: {e}")
        finally:
            self.generate_final_checklist()
            logging.info("Exiting application. Final checklist generated.")

if __name__ == "__main__":
    # 設定ファイルが存在しない場合に備えてデフォルト設定を作成
    # logsディレクトリが存在しない場合もここで作成
    default_config_instance = AutonomousSystemMonitor(config_path="non_existent_path") # デフォルト設定を取得するための一時的なインスタンス化
    log_dir = os.path.dirname(default_config_instance.config["log_file"])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    config_file_path = "config.json"
    if not os.path.exists(config_file_path):
        print(f"[{datetime.now().isoformat()}] WARNING: {config_file_path} not found. Creating with default values.")
        with open(config_file_path, "w", encoding='utf-8') as f:
            json.dump(default_config_instance._get_default_config(), f, indent=2, ensure_ascii=False)
        print(f"[{datetime.now().isoformat()}] INFO: Default {config_file_path} created. Please review and adjust if necessary.")

    monitor = AutonomousSystemMonitor(config_file_path)
    
    # タスク説明に合わせて最低6時間の連続稼働をシミュレート
    # 実際の本番運用では duration_hours=0 で無限ループ
    monitor.run_monitor(duration_hours=6) # 6時間稼働テスト