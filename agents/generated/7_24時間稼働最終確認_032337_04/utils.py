import psutil
import datetime
import os
import csv
import random
import logging
from collections import deque

logger = logging.getLogger(__name__)

def get_system_resource_usage():
    """
    システムのCPU、メモリ、ディスク使用率を取得する。
    :return: (cpu_percent, memory_percent, disk_percent) のタプル
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        memory_percent = memory_info.percent
        
        # ディスク使用率はルートパーティション('/')またはCドライブの情報を取得
        if os.name == 'posix': # Linux/macOS
            disk_info = psutil.disk_usage('/')
        elif os.name == 'nt': # Windows
            disk_info = psutil.disk_usage('C:\\')
        else:
            logger.warning("Unsupported OS for disk usage monitoring. Skipping disk check.")
            disk_percent = 0.0 # デフォルト値
            
        disk_percent = disk_info.percent
        
        return cpu_percent, memory_percent, disk_percent
    except psutil.NoSuchProcess:
        logger.error("A process was not found while trying to get system resources. This might indicate an issue with psutil.")
        return 0.0, 0.0, 0.0
    except psutil.AccessDenied:
        logger.error("Access denied when trying to get system resources. Run as administrator/root or check permissions.")
        return 0.0, 0.0, 0.0
    except Exception as e:
        logger.error(f"Failed to get system resource usage: {e}")
        return 0.0, 0.0, 0.0

def parse_log_file_for_patterns(log_file_path, patterns, lookback_lines=500):
    """
    指定されたログファイルから特定のパターンを検索し、マッチした行を返す。
    大規模なログファイルを効率的に処理するため、最新のlookback_linesだけを検索する。
    :param log_file_path: ログファイルのパス
    :param patterns: 検索するパターン文字列のリスト
    :param lookback_lines: ファイルの終わりから遡って検索する行数
    :return: マッチした行のリスト
    """
    matched_lines = []
    if not os.path.exists(log_file_path):
        logger.warning(f"Log file not found: {log_file_path}")
        return matched_lines

    try:
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # ファイルの末尾から指定行数だけ読み込む
            lines = deque(f, lookback_lines) # Python 3.6+
            
            for line in lines:
                for pattern in patterns:
                    if pattern in line:
                        matched_lines.append(line)
                        break # 一致したパターンが見つかれば、次の行へ
    except IOError as e:
        logger.error(f"Error reading log file {log_file_path}: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during log parsing for {log_file_path}: {e}")
    return matched_lines

def save_data_to_csv(filepath, data_list):
    """
    辞書のリストをCSVファイルに保存する。
    :param filepath: 保存先のCSVファイルパス
    :param data_list: 保存する辞書のリスト
    """
    if not data_list:
        logger.warning(f"No data to save to CSV: {filepath}")
        return

    try:
        fieldnames = data_list[0].keys()
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data_list)
        logger.info(f"Data successfully saved to {filepath}")
    except IOError as e:
        logger.error(f"Error writing data to CSV file {filepath}: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while saving data to CSV: {e}")

def format_timestamp(dt_object, file_safe=False):
    """
    datetimeオブジェクトをフォーマットされた文字列に変換する。
    :param dt_object: datetimeオブジェクト
    :param file_safe: ファイル名に使用できる形式にするか (コロンなどを除去)
    :return: フォーマットされた文字列
    """
    if file_safe:
        return dt_object.strftime("%Y%m%d_%H%M%S")
    return dt_object.strftime("%Y-%m-%d %H:%M:%S")

def simulate_api_call(api_name, interval_seconds, base_calls_per_minute=10):
    """
    API呼び出し回数をシミュレートする。
    :param api_name: APIの名前
    :param interval_seconds: 監視間隔 (秒)
    :param base_calls_per_minute: 1分あたりのベース呼び出し数
    :return: シミュレートされた呼び出し回数
    """
    # 1秒あたりのベース呼び出し数
    base_calls_per_second = base_calls_per_minute / 60.0
    
    # 区間内の呼び出し数
    calls_in_interval = base_calls_per_second * interval_seconds
    
    # ランダム性を追加 (±20%)
    simulated_calls = int(calls_in_interval * random.uniform(0.8, 1.2))
    
    # 少なくとも1回は呼び出されるようにする (完全にゼロではない場合)
    if simulated_calls == 0 and calls_in_interval > 0:
        simulated_calls = 1

    return simulated_calls

def check_file_rotation(directory, file_extension, max_age_days=30):
    """
    指定されたディレクトリ内でログファイルのローテーションの痕跡があるかを確認する。
    過去のタイムスタンプを持つファイルがあるかチェックする。
    :param directory: ログファイルが存在するディレクトリ
    :param file_extension: ログファイルの拡張子 (例: ".log")
    :param max_age_days: 何日以内の古いファイルを確認するか
    :return: ローテーションの痕跡があればTrue、なければFalse
    """
    if not os.path.exists(directory):
        logger.warning(f"Directory not found for log rotation check: {directory}")
        return False

    current_time = datetime.datetime.now()
    found_old_files = False

    for filename in os.listdir(directory):
        if filename.endswith(file_extension) and not filename.startswith('system_monitor'): # 監視ツール自身のログは除く
            file_path = os.path.join(directory, filename)
            try:
                # ファイル名に日付が含まれるパターン (e.g., system_log_20231027.log)
                # ファイル名の日付をパースして現在と比較
                name_parts = filename.split('_')
                if len(name_parts) >= 3 and name_parts[-2].isdigit() and len(name_parts[-2]) == 8:
                    try:
                        file_date_str = name_parts[-2] # YYYYMMDD形式を想定
                        file_date = datetime.datetime.strptime(file_date_str, "%Y%m%d")
                        if (current_time - file_date).days > 1: # 少なくとも1日以上前のログファイル
                            logger.debug(f"Found older log file by name: {filename}")
                            found_old_files = True
                            break
                    except ValueError:
                        pass # 日付形式でない場合はスキップ

                # 最終更新日時が古いファイル
                mtime_timestamp = os.path.getmtime(file_path)
                mtime_datetime = datetime.datetime.fromtimestamp(mtime_timestamp)
                if (current_time - mtime_datetime).days > max_age_days:
                    logger.debug(f"Found very old log file by modification time: {filename} ({mtime_datetime.strftime('%Y-%m-%d')})")
                    found_old_files = True
                    break
            except Exception as e:
                logger.debug(f"Error checking file {filename} for rotation: {e}")
                continue # エラーが発生しても他のファイルをチェックし続ける
    
    return found_old_files

def calculate_api_usage_stats(api_records_list, monitoring_interval):
    """
    API使用量のリストから、日次呼び出し合計と平均RPSを計算する。
    :param api_records_list: 過去24時間分の分単位の呼び出し数リスト
    :param monitoring_interval: 監視間隔 (秒)
    :return: (daily_calls_sum, rps_avg)
    """
    if not api_records_list:
        return 0, 0.0

    daily_calls_sum = sum(api_records_list)
    
    # 過去1分間のRPSを計算するため、約60秒分のデータを取得
    # monitoring_intervalが60秒であれば、直近の1エントリが1分間の呼び出し数
    # monitoring_intervalが30秒であれば、直近の2エントリが1分間の呼び出し数
    num_entries_for_minute = max(1, 60 // monitoring_interval) # 少なくとも1エントリ
    recent_calls = list(api_records_list)[-num_entries_for_minute:]
    
    if recent_calls:
        recent_calls_sum = sum(recent_calls)
        rps_avg = recent_calls_sum / (monitoring_interval * len(recent_calls))
    else:
        rps_avg = 0.0

    return daily_calls_sum, rps_avg