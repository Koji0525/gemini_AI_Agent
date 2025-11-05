#!/usr/bin/env python3
import json
from pathlib import Path

stats_files = sorted(Path("logs").glob("stats_*.json"))

print("📊 自律システム実行履歴\n")
print(f"{'日時':<20} {'実行':<6} {'エラー':<6} {'修正':<6} {'時間':<8}")
print("-" * 60)

for f in stats_files[-10:]:  # 最新10件
    with open(f) as fp:
        data = json.load(fp)

    timestamp = f.stem.replace("stats_", "")
    print(
        f"{timestamp:<20} {data['tasks_executed']:<6} {data['errors_found']:<6} "
        f"{data['auto_fixed']:<6} {data['total_runtime']:.2f}秒"
    )
