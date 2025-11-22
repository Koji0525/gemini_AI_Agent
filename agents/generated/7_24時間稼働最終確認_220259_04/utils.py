import time
import os
import logging
import random
from datetime import datetime, timedelta
import sys

# logging.basicConfig は main.py で行われるため、ここでは単にロガーを取得する
# rootロガーを使用するか、main.pyで定義された特定のロガーを使用する
logger = logging.getLogger(__name__)

def get_cpu_usage(simulation_mode: bool = True) -> float:
    """
    現在のCPU使用率を返す。
    simulation_mode=True の場合、シミュレーション値を返す。
    simulation_mode=False の場合、psutil を使用して実際のCPU使用率を試みる。
    """
    if simulation_mode:
        # 安定した稼働をシミュレートしつつ、たまにスパイクを発生させる
        base_usage = random.uniform(20.0, 50.0)
        if random.random() < 0.1:  # 10%の確率で高負荷
            base_usage = random.uniform(70.0, 95.0)
        return round(base_usage, 2)
    else:
        try:
            import psutil
            # psutil.cpu_percent() は前回の呼び出しからの経過時間におけるCPU使用率を返す
            # 初回呼び出しは0を返すか、前回の呼び出しがなければ直近1秒間の平均を返す
            return psutil.cpu_percent(interval=1)
        except ImportError:
            logger.error("psutil not installed. Cannot get real CPU usage. Falling back to simulation.")
            return get_cpu_usage(True)  # シミュレーションモードにフォールバック
        except Exception as e:
            logger.error(f"Error getting real CPU usage: {e}. Falling back to simulation.")
            return get_cpu_usage(True)  # シミュレーションモードにフォールバック

def get_memory_usage(simulation_mode: bool = True) -> tuple[float, float, float]:
    """
    現在のメモリ使用率 (%), 総メモリ量 (MB), 使用メモリ量 (MB) を返す。
    simulation_mode=True の場合、シミュレーション値を返す。
    """
    if simulation_mode:
        total_mem_gb = 16.0  # 例として16GB
        total_mem_mb = total_mem_gb * 1024
        
        # ベース使用量 (20-40%)
        base_usage_mb_min = total_mem_mb * 0.20
        base_usage_mb_max = total_mem_mb * 0.40
        
        # ランダムな変動を加えて、徐々に増える傾向をシミュレート
        # この関数自体はstatelessなので、リーク計算はmain.pyで履歴に基づいて行う
        used_mem_mb_lower = total_mem_mb * 0.25 # 最低25%は使う
        used_mem_mb_upper = total_mem_mb * random.uniform(0.40, 0.85) # 最大85%まで変動
        
        used_mem_mb = random.uniform(used_mem_mb_lower, used_mem_mb_upper)
        
        mem_percent = (used_mem_mb / total_mem_mb) * 100
        return round(mem_percent, 2), round(total_mem_mb, 2), round(used_mem_mb, 2)
    else:
        try:
            import psutil
            mem = psutil.virtual_memory()
            return round(mem.percent, 2), round(mem.total / (1024 * 1024), 2), round(mem.used / (1024 * 1024), 2) # %, total MB, used MB
        except ImportError:
            logger.error("psutil not installed. Cannot get real memory usage. Falling back to simulation.")
            return get_memory_usage(True)
        except Exception as e:
            logger.error(f"Error getting real memory usage: {e}. Falling back to simulation.")
            return get_memory_usage(True)

def calculate_memory_leak_rate(memory_history: list[tuple[datetime, float]]) -> float:
    """
    メモリ使用履歴からメモリリークのレート (MB/hour) を計算する。
    memory_history: [(timestamp, used_memory_mb), ...]
    メモリ使用量が減少した場合はリークではないため、0.0を返す。
    """
    if len(memory_history) < 2:
        return 0.0

    # 時系列でソート (念のため)
    sorted_history = sorted(memory_history, key=lambda x: x[0])

    first_time, first_mem = sorted_history[0]
    last_time, last_mem = sorted_history[-1]

    time_diff_seconds = (last_time - first_time).total_seconds()
    if time_diff_seconds <= 0:  # 時間差がない、または負の場合
        return 0.0

    mem_diff_mb = last_mem - first_mem

    # MB/hour に変換
    # メモリ使用量が減った場合はリークではないと判断し、0を返す
    if mem_diff_mb > 0:
        leak_rate_mb_per_hour = (mem_diff_mb / time_diff_seconds) * 3600
        return round(leak_rate_mb_per_hour, 2)
    return 0.0


def get_disk_usage(simulation_mode: bool = True, path: str = './') -> float:
    """
    指定されたパスのディスク使用率を返す。
    simulation_mode=True の場合、シミュレーション値を返す。
    """
    if simulation_mode:
        # 安定した稼働をシミュレートしつつ、たまにスパイクを発生させる
        base_usage = random.uniform(30.0, 60.0)
        if random.random() < 0.05:  # 5%の確率で高負荷
            base_usage = random.uniform(80.0, 98.0)
        return round(base_usage, 2)
    else:
        try:
            import shutil
            total, used, free = shutil.disk_usage(path)
            return round((used / total) * 100, 2)
        except Exception as e:
            logger.error(f"Error getting real disk usage for path {path}: {e}. Falling back to simulation.")
            return get_disk_usage(True, path)

def log_event(level: str, message: str, log_file: str = "logs/general.log"):
    """
    指定されたレベルとメッセージでログを記録する。
    この関数は汎用的なロギング関数として残しておくが、
    main.pyではloggingモジュールを直接使うことを推奨。
    """
    logger_to_use = logging.getLogger('autonomous_system') # main.pyのrootロガーを使う想定
    if level.upper() == 'INFO':
        logger_to_use.info(message)
    elif level.upper() == 'WARNING':
        logger_to_use.warning(message)
    elif level.upper() == 'ERROR':
        logger_to_use.error(message)
    elif level.upper() == 'CRITICAL':
        logger_to_use.critical(message)
    else:
        logger_to_use.debug(message)

def rotate_log_file(log_path: str, max_bytes: int, backup_count: int, logger_instance: logging.Logger):
    """
    ログファイルをローテーションする。
    logging.handlers.RotatingFileHandler の簡易的な代替実装。
    
    Args:
        log_path (str): ローテーション対象のログファイルパス。
        max_bytes (int): ファイルサイズの上限 (バイト)。
        backup_count (int): 保持するバックアップファイルの数。
        logger_instance (logging.Logger): このログファイルを使用しているLoggerインスタンス。
                                          ハンドラを適切に閉じて再オープンするために必要。
    """
    if not os.path.exists(log_path):
        return

    try:
        if os.path.getsize(log_path) >= max_bytes:
            logger_instance.info(f"Log file '{log_path}' reached max size ({max_bytes} bytes). Rotating...")
            
            # 既存のファイルハンドラを閉じる
            for handler in list(logger_instance.handlers): # ハンドラリストをコピーしてイテレート
                if isinstance(handler, logging.FileHandler) and handler.baseFilename == os.path.abspath(log_path):
                    handler.close()
                    logger_instance.removeHandler(handler)

            # 古いバックアップを削除
            for i in range(backup_count - 1, 0, -1):
                s = f"{log_path}.{i}"
                d = f"{log_path}.{i + 1}"
                if os.path.exists(s):
                    if os.path.exists(d):
                        os.remove(d)
                    os.rename(s, d)
            
            # 現在のファイルをバックアップに移動
            if os.path.exists(log_path):
                if os.path.exists(f"{log_path}.1"):
                    os.remove(f"{log_path}.1")
                os.rename(log_path, f"{log_path}.1")
            
            logger_instance.info(f"Log file '{log_path}' rotated successfully.")
            
            # 新しいファイルハンドラを再度追加
            new_handler = logging.FileHandler(log_path, encoding='utf-8')
            new_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger_instance.addHandler(new_handler)

    except Exception as e:
        logger_instance.error(f"Error during log file rotation for {log_path}: {e}")

def simulate_api_call(api_name: str, cost_per_call: float, simulation_mode: bool = True) -> float:
    """
    API呼び出しをシミュレートし、コストを返す。
    simulation_mode=True の場合、単にコストを計算する。
    """
    if simulation_mode:
        # 実際に外部APIを叩かず、コスト計算のみ
        return cost_per_call
    else:
        # ここに実際のAPI呼び出しロジックを実装
        logger.warning(f"Real API call for {api_name} is not implemented in non-simulation mode for this utility.")
        return cost_per_call # 現時点ではシミュレーション値を返す

def send_notification(message: str, notification_type: str, recipients: list[str]):
    """
    人間への通知 (F9) をシミュレートする。
    実際にはメール送信やSlack通知などのAPIを使用する。
    """
    logger.critical(f"--- F9 Human Notification ({notification_type}) ---")
    logger.critical(f"Message: {message}")
    logger.critical(f"Recipients: {', '.join(recipients)}")
    logger.critical(f"--- End F9 Notification ---")
    
    # ここに実際の通知実装を追加
    # 例: メール送信
    # import smtplib
    # from email.mime.text import MIMEText
    # try:
    #     msg = MIMEText(message, _charset='utf-8')
    #     msg['Subject'] = f"Autonomous System Alert: {notification_type}"
    #     msg['From'] = 'autonomous-system@example.com'
    #     msg['To'] = ', '.join(recipients)
    #     with smtplib.SMTP('localhost') as s: # SMTPサーバーの設定
    #         s.send_message(msg)
    #     logger.info(f"Successfully sent F9 notification email to {recipients}")
    # except Exception as e:
    #     logger.error(f"Failed to send F9 notification email: {e}")