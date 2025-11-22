import os
import time
import datetime
import logging
import json
import yaml
import csv
from collections import deque
import psutil # For system resource monitoring

# utils.pyからのインポートを想定
from utils import (
    get_system_resource_usage,
    parse_log_file_for_patterns,
    save_data_to_csv,
    format_timestamp,
    simulate_api_call,
    check_file_rotation,
    calculate_api_usage_stats
)

# ロギング設定
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("system_monitor.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

class SystemMonitor:
    """
    24時間自律稼働システムの最終確認を行うための監視ツール。
    システムリソース、API使用量、ログイベントを監視し、異常を検出する。
    """

    def __init__(self, config_path="config.yaml"):
        """
        SystemMonitorの初期化。設定ファイルを読み込み、必要なディレクトリを準備する。
        :param config_path: 設定ファイルのパス
        """
        self.config = self._load_config(config_path)
        self.monitoring_interval = self.config['monitoring']['interval_seconds']
        self.monitoring_duration_hours = self.config['monitoring']['duration_hours']
        self.log_directory = self.config['monitoring']['log_directory']
        self.output_data_directory = self.config['monitoring']['output_data_directory']
        self.resource_thresholds = self.config['monitoring']['resource_thresholds']
        self.api_config = self.config['api_monitoring']
        self.log_analysis_config = self.config['log_analysis']
        self.notification_config = self.config['notifications']

        self._prepare_directories()
        self.monitoring_data = []
        self.api_usage_records = {} # {api_name: deque(max_len=60*24)} for 24 hours (minute-level)
        for api_name in self.api_config:
            self.api_usage_records[api_name] = deque(maxlen=60 * 24) # Store minute-level usage for 24 hours

        logger.info("SystemMonitor initialized successfully with configuration from %s", config_path)
        logger.info(f"Monitoring interval: {self.monitoring_interval} seconds")
        logger.info(f"Expected monitoring duration: {self.monitoring_duration_hours} hours")

    def _load_config(self, config_path):
        """
        設定ファイルを読み込む。
        :param config_path: 設定ファイルのパス
        :return: 読み込まれた設定辞書
        :raises FileNotFoundError: 設定ファイルが見つからない場合
        :raises yaml.YAMLError: 設定ファイルの解析に失敗した場合
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found at {config_path}. Please ensure it exists.")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file {config_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading config: {e}")
            raise

    def _prepare_directories(self):
        """
        出力ディレクトリが存在しない場合に作成する。
        """
        os.makedirs(self.output_data_directory, exist_ok=True)
        os.makedirs(self.log_directory, exist_ok=True) # 監視対象のログディレクトリも念のため確認
        logger.info(f"Ensured output data directory exists: {self.output_data_directory}")
        logger.info(f"Ensured log directory exists: {self.log_directory}")

    def _monitor_resources(self):
        """
        システムリソース（CPU, メモリ, ディスク）を監視し、閾値を超えた場合に警告する。
        :return: 監視結果の辞書
        """
        try:
            cpu_percent, memory_percent, disk_percent = get_system_resource_usage()
            timestamp = datetime.datetime.now()
            
            resource_data = {
                "timestamp": format_timestamp(timestamp),
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent
            }
            self.monitoring_data.append(resource_data)

            logger.info(f"Resource Usage: CPU={cpu_percent:.2f}%, Memory={memory_percent:.2f}%, Disk={disk_percent:.2f}%")

            # 閾値チェック
            if cpu_percent > self.resource_thresholds['cpu_percent_high']:
                self._send_notification(
                    f"CRITICAL: CPU usage {cpu_percent:.2f}% exceeded threshold {self.resource_thresholds['cpu_percent_high']}%!"
                )
            if memory_percent > self.resource_thresholds['memory_percent_high']:
                self._send_notification(
                    f"CRITICAL: Memory usage {memory_percent:.2f}% exceeded threshold {self.resource_thresholds['memory_percent_high']}%!"
                )
            if disk_percent > self.resource_thresholds['disk_percent_high']:
                self._send_notification(
                    f"CRITICAL: Disk usage {disk_percent:.2f}% exceeded threshold {self.resource_thresholds['disk_percent_high']}%!"
                )
            
            return resource_data
        except psutil.Error as e:
            logger.error(f"Error getting system resources: {e}")
            return {}
        except Exception as e:
            logger.error(f"An unexpected error occurred during resource monitoring: {e}")
            return {}

    def _monitor_api_usage(self):
        """
        API使用量を監視し、レート制限や日次制限に近づいていないかを確認する。
        API呼び出しはシミュレートされる。
        :return: APIごとの使用量辞書
        """
        api_current_usage = {}
        current_time = datetime.datetime.now()
        
        # 1分あたりのAPI呼び出しをシミュレート
        for api_name, settings in self.api_config.items():
            try:
                # Simulate a few API calls per minute
                simulated_calls = simulate_api_call(api_name, self.monitoring_interval)
                self.api_usage_records[api_name].append(simulated_calls)

                # Calculate current RPS and daily usage based on collected data
                current_minute_usage = sum(list(self.api_usage_records[api_name])[-min(60 // (self.monitoring_interval // 60) +1, len(self.api_usage_records[api_name])):]) # Rough estimate for last minute
                current_daily_usage = sum(self.api_usage_records[api_name]) # Sum of all collected data for 24 hours

                # For simplicity, we assume the total calls stored in deque represents the daily count if maxlen is 24*60
                api_current_usage[api_name] = {
                    "current_daily_calls": current_daily_usage,
                    "current_rps": simulated_calls / self.monitoring_interval if self.monitoring_interval > 0 else 0
                }

                logger.info(f"API Usage for {api_name}: Daily Calls={current_daily_usage}/{settings['max_daily_calls']}, RPS={api_current_usage[api_name]['current_rps']:.2f}/{settings['max_rps']}")

                # レート制限チェック
                if api_current_usage[api_name]['current_rps'] > settings['max_rps'] * 0.8: # 80%を超えたら警告
                    self._send_notification(
                        f"WARNING: {api_name} RPS ({api_current_usage[api_name]['current_rps']:.2f}) approaching limit {settings['max_rps']}!", level="WARNING"
                    )
                if current_daily_usage > settings['max_daily_calls'] * 0.9: # 90%を超えたら警告
                    self._send_notification(
                        f"CRITICAL: {api_name} daily calls ({current_daily_usage}) approaching limit {settings['max_daily_calls']}!", level="CRITICAL"
                    )
            except Exception as e:
                logger.error(f"Error monitoring API {api_name}: {e}")
        return api_current_usage

    def _analyze_logs(self):
        """
        指定されたログディレクトリ内のログファイルを分析し、エラーや学習イベントを検出する。
        """
        detected_events = []
        log_files = [os.path.join(self.log_directory, f) for f in os.listdir(self.log_directory) if f.endswith('.log')]
        
        for log_file in log_files:
            try:
                # エラーパターン検出
                error_matches = parse_log_file_for_patterns(log_file, self.log_analysis_config['error_patterns'])
                for line in error_matches:
                    detected_events.append({"type": "ERROR", "file": log_file, "line": line.strip()})
                    if any(pattern in line for pattern in ["F7 Failed", "F9 Triggered"]):
                        self._send_notification(
                            f"CRITICAL: Error handling event detected in {log_file}: {line.strip()}", level="CRITICAL"
                        )
                    elif any(pattern in line for pattern in ["ERROR", "Exception"]):
                         self._send_notification(
                            f"ERROR: Critical error detected in {log_file}: {line.strip()}", level="ERROR"
                        )

                # 学習パターン検出
                learning_matches = parse_log_file_for_patterns(log_file, self.log_analysis_config['learning_patterns'])
                for line in learning_matches:
                    detected_events.append({"type": "LEARNING", "file": log_file, "line": line.strip()})
                    if "F8 Triggered" in line:
                         self._send_notification(
                            f"INFO: F8 (Self-evolution) triggered in {log_file}: {line.strip()}", level="INFO"
                        )
                    elif "Knowledge Updated" in line:
                         self._send_notification(
                            f"INFO: Knowledge base updated in {log_file}: {line.strip()}", level="INFO"
                        )

            except IOError as e:
                logger.error(f"Error reading log file {log_file}: {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred during log analysis for {log_file}: {e}")
        
        if detected_events:
            logger.warning(f"Detected {len(detected_events)} significant events in logs.")
            # 詳細を記録
            with open(os.path.join(self.output_data_directory, "detected_log_events.json"), 'a', encoding='utf-8') as f:
                json.dump({"timestamp": format_timestamp(datetime.datetime.now()), "events": detected_events}, f, ensure_ascii=False, indent=2)
                f.write("\n") # 各エントリの後に改行

    def _check_log_management(self):
        """
        ログファイルのローテーションや存在を確認する。
        """
        log_files = [f for f in os.listdir(self.log_directory) if f.endswith('.log')]
        if not log_files:
            logger.warning(f"No log files found in {self.log_directory}. Is the main system running and logging?")
            return

        # 最新のログファイルを取得
        latest_log_file = max(log_files, key=lambda f: os.path.getmtime(os.path.join(self.log_directory, f)))
        latest_log_path = os.path.join(self.log_directory, latest_log_file)
        
        # ログファイルの最終更新日時が古すぎないかチェック (例: 1時間以内)
        if (time.time() - os.path.getmtime(latest_log_path)) > 3600: # 1 hour
            self._send_notification(f"WARNING: Latest log file '{latest_log_file}' is older than 1 hour. Log output might be stalled.", level="WARNING")
        
        # ローテーションの痕跡を確認 (例えば、過去の日付のログファイルがあるか)
        if check_file_rotation(self.log_directory, ".log", max_age_days=7):
            logger.info("Evidence of log file rotation found in the last 7 days.")
        else:
            logger.warning("No clear evidence of log file rotation found in the last 7 days. Please check log rotation configuration.")

    def _send_notification(self, message, level="INFO"):
        """
        通知を送信する（実際にはログに出力する）。
        将来的にSlack, Emailなどの通知システムと統合する。
        :param message: 通知メッセージ
        :param level: 通知レベル (INFO, WARNING, ERROR, CRITICAL)
        """
        if not self.notification_config['enabled']:
            return

        full_message = f"[NOTIFICATION - {level}] {message}"
        if level == "CRITICAL":
            logger.critical(full_message)
        elif level == "ERROR":
            logger.error(full_message)
        elif level == "WARNING":
            logger.warning(full_message)
        else:
            logger.info(full_message)
        
        # 将来的に通知APIを呼び出す場合、ここに実装
        # 例: send_slack_message(message)
        # 例: send_email(subject="System Monitor Alert", body=message)

    def run_monitoring_loop(self):
        """
        メインの監視ループを実行する。
        指定された期間、システムを監視し続ける。
        """
        start_time = time.time()
        end_time = start_time + (self.monitoring_duration_hours * 3600)
        logger.info(f"Starting system monitoring for approximately {self.monitoring_duration_hours} hours.")

        iteration = 0
        while time.time() < end_time:
            iteration += 1
            current_timestamp = datetime.datetime.now()
            logger.info(f"--- Monitoring Iteration {iteration} at {format_timestamp(current_timestamp)} ---")

            # 1. 長時間稼働テスト (リソース監視)
            self._monitor_resources()

            # 4. API使用量の監視
            self._monitor_api_usage()

            # 2. エラーハンドリングの検証 & 3. 学習サイクルの動作確認
            # ログファイルを分析することで間接的に検証・確認
            self._analyze_logs()

            # 5. ログ管理の確認
            self._check_log_management()

            time_elapsed = time.time() - start_time
            if time_elapsed < (self.monitoring_interval * iteration): # スリープ時間を調整して正確なインターバルを維持
                sleep_duration = (self.monitoring_interval * iteration) - time_elapsed
                if sleep_duration > 0:
                    logger.debug(f"Sleeping for {sleep_duration:.2f} seconds...")
                    time.sleep(sleep_duration)
            else:
                logger.warning(f"Monitoring loop is lagging behind. Current interval took longer than {self.monitoring_interval}s.")

        logger.info(f"Monitoring loop completed after {self.monitoring_duration_hours} hours.")
        self.generate_report()

    def generate_report(self):
        """
        収集した監視データに基づいて最終レポートを生成する。
        """
        report_filename = os.path.join(self.output_data_directory, f"monitoring_report_{format_timestamp(datetime.datetime.now(), file_safe=True)}.txt")
        csv_filename = os.path.join(self.output_data_directory, f"resource_monitoring_data_{format_timestamp(datetime.datetime.now(), file_safe=True)}.csv")

        # リソース監視データをCSVに保存
        if self.monitoring_data:
            save_data_to_csv(csv_filename, self.monitoring_data)
            logger.info(f"Detailed resource monitoring data saved to {csv_filename}")
        else:
            logger.warning("No resource monitoring data collected to generate CSV.")

        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(f"--- System Monitoring Report ({format_timestamp(datetime.datetime.now())}) ---\n\n")
            f.write(f"Monitoring Duration: {self.monitoring_duration_hours} hours\n")
            f.write(f"Monitoring Interval: {self.monitoring_interval} seconds\n")
            f.write(f"Log Directory: {self.log_directory}\n")
            f.write(f"Output Data Directory: {self.output_data_directory}\n\n")

            f.write("=== Resource Monitoring Summary ===\n")
            if self.monitoring_data:
                cpu_values = [d['cpu_percent'] for d in self.monitoring_data if 'cpu_percent' in d]
                mem_values = [d['memory_percent'] for d in self.monitoring_data if 'memory_percent' in d]
                disk_values = [d['disk_percent'] for d in self.monitoring_data if 'disk_percent' in d]

                if cpu_values: f.write(f"CPU Usage: Max={max(cpu_values):.2f}%, Avg={sum(cpu_values)/len(cpu_values):.2f}%\n")
                if mem_values: f.write(f"Memory Usage: Max={max(mem_values):.2f}%, Avg={sum(mem_values)/len(mem_values):.2f}%\n")
                if disk_values: f.write(f"Disk Usage: Max={max(disk_values):.2f}%, Avg={sum(disk_values)/len(disk_values):.2f}%\n")
            else:
                f.write("No resource data collected.\n")
            f.write("\n")

            f.write("=== API Usage Summary ===\n")
            for api_name, records in self.api_usage_records.items():
                if records:
                    daily_calls_sum, rps_avg = calculate_api_usage_stats(list(records), self.monitoring_interval)
                    f.write(f"{api_name}:\n")
                    f.write(f"  Estimated Daily Calls: {daily_calls_sum} (Max: {self.api_config[api_name]['max_daily_calls']})\n")
                    f.write(f"  Average RPS: {rps_avg:.2f} (Max: {self.api_config[api_name]['max_rps']})\n")
                else:
                    f.write(f"{api_name}: No usage data collected.\n")
            f.write("\n")

            f.write("=== Log Analysis Summary ===\n")
            # 検出されたイベントのサマリーをここに含める
            try:
                with open(os.path.join(self.output_data_directory, "detected_log_events.json"), 'r', encoding='utf-8') as event_file:
                    events_data = [json.loads(line) for line in event_file.readlines()]
                    error_count = sum(1 for data in events_data for event in data['events'] if event['type'] == 'ERROR')
                    learning_count = sum(1 for data in events_data for event in data['events'] if event['type'] == 'LEARNING')
                    f.write(f"Total Critical Errors/F7/F9 events detected: {error_count}\n")
                    f.write(f"Total F8/Learning events detected: {learning_count}\n")
                    f.write(f"Refer to 'detected_log_events.json' for full details.\n")
            except FileNotFoundError:
                f.write("No 'detected_log_events.json' file found. No significant events may have been logged or monitored duration was too short.\n")
            except json.JSONDecodeError as e:
                f.write(f"Error reading 'detected_log_events.json': {e}. File might be corrupted.\n")
            f.write("\n")

            f.write("=== Final Checklist Status (Refer to README.md for full checklist) ===\n")
            f.write("・6時間以上の連続稼働: " + ("達成" if time.time() - start_time >= (self.monitoring_duration_hours * 3600) else "未達成") + "\n")
            f.write("・エラー時の自動修復(F7)/リトライ: ログ分析でF7/リトライイベントを検出したか確認。\n")
            f.write("・学習サイクル(F8)の自動実行: ログ分析でF8イベントを検出したか確認。\n")
            f.write("・API使用量が許容範囲内: 上記API使用量サマリーを確認。\n")
            f.write("・詳細なチェックリスト: 本ツールはチェックリスト作成を補助。README.md参照。\n")

        logger.info(f"Monitoring report generated at {report_filename}")

if __name__ == "__main__":
    try:
        # 設定ファイルの初期化 (存在しない場合はデフォルトを作成)
        default_config_path = "config.yaml"
        if not os.path.exists(default_config_path):
            logger.info(f"'{default_config_path}' not found. Creating a default configuration file.")
            default_config_content = {
                'monitoring': {
                    'interval_seconds': 60,
                    'duration_hours': 6, # Minimum 6 hours for testing
                    'resource_thresholds': {
                        'cpu_percent_high': 80,
                        'memory_percent_high': 90,
                        'disk_percent_high': 95
                    },
                    'log_directory': 'logs/',
                    'output_data_directory': 'monitor_data/'
                },
                'api_monitoring': {
                    'claude_api': {
                        'max_daily_calls': 100000,
                        'max_rps': 5
                    },
                    'google_sheets_api': {
                        'max_daily_calls': 50000,
                        'max_rps': 10
                    }
                },
                'log_analysis': {
                    'error_patterns': ['ERROR', 'Exception', 'F7 Failed', 'F9 Triggered', 'Retry limit exceeded'],
                    'learning_patterns': ['F8 Triggered', 'Knowledge Updated', 'Pattern Learned']
                },
                'notifications': {
                    'enabled': True
                }
            }
            with open(default_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config_content, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Default '{default_config_path}' created. Please review and adjust as needed.")

        monitor = SystemMonitor(config_path=default_config_path)
        monitor.run_monitoring_loop()
    except Exception as e:
        logger.critical(f"An unhandled error occurred in the main execution block: {e}", exc_info=True)