#!/usr/bin/env python3
"""
メトリクス収集スクリプト
24時間テスト用のシステムメトリクスを収集
"""
import time
import psutil
import csv
import os
import sys
from datetime import datetime


def collect_metrics():
    """メトリクス収集のメイン関数"""

    # メトリクスファイル
    metrics_dir = "logs/24h_test"
    os.makedirs(metrics_dir, exist_ok=True)
    metrics_file = f"{metrics_dir}/metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    print(f"📊 メトリクス収集開始: {metrics_file}")

    # メトリクスファイル初期化
    with open(metrics_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["timestamp", "cpu_percent", "memory_percent", "disk_usage", "active_processes"]
        )

    try:
        cycle_count = 0
        while True:
            # システムメトリクス収集
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            active_processes = len(psutil.pids())

            # メトリクス記録
            with open(metrics_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        datetime.now().isoformat(),
                        cpu_percent,
                        memory.percent,
                        disk.percent,
                        active_processes,
                    ]
                )

            cycle_count += 1
            if cycle_count % 12 == 0:  # 1時間ごとにログ出力（5分×12=60分）
                print(
                    f"✅ メトリクス収集 {cycle_count}回目: CPU {cpu_percent}%, メモリ {memory.percent}%"
                )

            # 5分間隔で収集
            time.sleep(300)

    except KeyboardInterrupt:
        print("⏹️ メトリクス収集終了")
    except Exception as e:
        print(f"❌ メトリクス収集エラー: {e}")


if __name__ == "__main__":
    collect_metrics()
