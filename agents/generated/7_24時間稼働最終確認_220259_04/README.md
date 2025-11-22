# Autonomous 24-Hour Operation Final Verification System

## 概要

このプロジェクトは、24時間自律稼働するシステムが**本番運用可能な状態であることの最終確認**を行うために設計された包括的な監視・検証ツールです。無人での長時間稼働において問題が発生しないことを保証することを目的としています。

現代の自律システムは、単に機能するだけでなく、予期せぬ問題に自律的に対応し、継続的に学習・改善する能力が求められます。この検証システムは、以下の主要な機能をシミュレーション環境（または実際のシステムとの連携も可能）で稼働させ、その動作の堅牢性と信頼性を評価します。最終的には、システムの全体的な健全性を判断し、本番運用に必要な詳細な最終チェックリストを自動生成することで、デプロイ前の最終的な安心を提供します。

**【目的】**
システムが24時間無人で稼働しても問題が発生せず、自律的に運用を継続できることを保証する。

## 特徴

*   **長時間稼働テストのシミュレーション**:
    *   CPU、メモリ、ディスク使用率の継続的な監視を行い、定義された閾値を超えた場合に異常を検知します。
    *   システムリソースの安定性を長期間にわたって評価します。
*   **メモリリーク検出**:
    *   一定期間におけるメモリ使用量の履歴を詳細に分析し、潜在的なメモリリークの兆候を早期に特定します。これにより、システムの安定性を損なう可能性のある問題を未然に防ぎます。
*   **高度なエラーハンドリング検証**:
    *   **F7 (自己修復)**: 検出された一般的なエラーに対し、システムが自動的に修復プロセスを開始し、正常な状態に回復できるかを確認します。
    *   **リトライ機構**: 一時的なネットワーク障害や外部サービスの問題など、一時的な性質のエラーに対して、最大設定回数までの自動リトライ処理が正しく機能するかを検証します。
    *   **F9 (人間通知)**: 自己修復やリトライの試行がすべて失敗し、システムが自律的に解決できないと判断した場合に、事前に設定された担当者（人間）への緊急通知（メールなど）が正確に発火することを確認します。
*   **学習サイクルの動作確認 (F8: 自己進化)**:
    *   システムは、設定された一定時間経過後、または一定数のエラーが発生した場合に、**F8 (自己進化)** 学習サイクルを自動的にトリガーします。
    *   **ナレッジ蓄積**: 学習サイクル中に発生した新しい問題パターンや解決策を「既知の問題（`known_issues`）」としてシステム内部に蓄積します。これにより、将来的に同じ問題が発生した際のF7（自己修復）の成功率を向上させます。
    *   **パターン学習の効果測定**: 学習サイクルによって、F7の成功確率が徐々に向上する様子をシミュレートし、システムの自己改善能力を評価します。
*   **API使用量の監視**:
    *   Claude API および Google Sheets API など、外部APIの仮想的な使用量をリアルタイムで計測し、総コストと呼び出し回数を追跡します。
    *   設定されたレート制限にシステムがどのように対処するか（例: バックオフ、呼び出し制限）を確認し、APIプロバイダからのペナルティを回避するためのメカニズムが機能しているかを検証します。
*   **堅牢なログ管理**:
    *   ログファイルのサイズが設定された閾値を超えた場合に、自動的にローテーションされる機能を確認します。これにより、ディスク容量の無駄な消費を防ぎます。
    *   すべての重要イベント、警告、およびエラーが適切なログファイルに正確に記録されていることを確認します。
    *   特に、エラーログからF9通知が適切にトリガーされるかを確認し、運用上の問題を見逃さないことを保証します。
*   **最終チェックリストの自動生成**:
    *   稼働テストの完了時に、システムの起動前、稼働中、および停止時に確認すべき詳細な項目を含むチェックリストが自動的に生成されます。このチェックリストは、本番運用環境へのデプロイ前に最終的なレビューと承認を行うための重要なドキュメントとなります。

## システムアーキテクチャ (概念図)

```
+---------------------+
|   Autonomous System |        (External Dependencies / Environment)
|     (Target)        | <---------------------------------------------> [ External APIs (Claude, Google Sheets), Database, Network ]
+----------+----------+
           |
           v
+---------------------+     +-----------------+     +-----------------+
| AutonomousSystem    |     |   Logging       |     |   Notification  |
| Monitor (main.py)   |---->|   System        |---->|   Module (F9)   |
|                     |     | (monitor.log,   |     | (Email/PagerDuty) |
| - Resource Checks   |     |  error.log,     |     +-----------------+
| - Error Handler(F7) |     |  api_usage.log) |
| - Retries (up to N) |     +-----------------+
| - Learning Cycle(F8)|       (Rotated Logs)
| - API Usage Tracker |
| - Health Status     |
| - Checklist Gen.    |
+----------+----------+
           |
           v
+---------------------+
| Utility Functions   |
|    (utils.py)       |
|                     |
| - Get CPU/Mem/Disk  | (Simulated or Real psutil calls)
| - Log Rotation      |
| - API Call Sim.     | (Cost/Rate Limit Simulation)
| - Mem Leak Calc.    |
| - Notif. Trigger    |
+---------------------+

```

## インストール

1.  Python 3.9 以上がインストールされていることを確認してください。
2.  プロジェクトファイルをダウンロードまたはクローンします。
    ```bash
    git clone <repository_url>
    cd autonomous-system-monitor
    ```
3.  必要なPythonライブラリをインストールします。
    本シミュレーションはPythonの標準ライブラリを中心に構成されています。
    `simulation_mode`を`false`にして実際のシステムリソースを監視したい場合は、`psutil`ライブラリのインストールが必要です。
    ```bash
    # 実際のシステムリソース監視を行う場合
    pip install psutil
    ```

## 設定

システムの設定は `config.json` ファイルで行います。
このファイルが存在しない場合、初回起動時にデフォルト設定で自動生成されます。
自動生成された設定ファイルを確認し、必要に応じて環境に合わせて編集してください。

**`config.json` の例:**

```json
{
  "monitor_interval_seconds": 60,
  "resource_check_interval_seconds": 300,
  "cpu_threshold_percent": 80,
  "memory_threshold_percent": 85,
  "disk_threshold_percent": 90,
  "memory_leak_check_window_minutes": 30,
  "memory_leak_rate_threshold_mb_per_hour": 10,
  "max_retries_on_error": 3,
  "f7_healing_probability": 0.7,
  "learning_cycle_trigger_hours": 6,
  "learning_cycle_trigger_errors": 50,
  "claude_api_cost_per_call": 0.015,
  "google_sheets_api_cost_per_call": 0.0001,
  "claude_api_rate_limit_per_minute": 100,
  "google_sheets_api_rate_limit_per_minute": 1000,
  "log_file": "logs/monitor.log",
  "error_log_file": "logs/errors.log",
  "api_log_file": "logs/api_usage.log",
  "max_log_size_mb": 10,
  "log_backup_count": 5,
  "human_notification_emails": ["admin@example.com", "devops@example.com"],
  "simulation_mode": true
}
```

各設定項目の詳細は以下の通りです。

*   `monitor_interval_seconds`: 各監視サイクルの実行間隔（秒）。
*   `resource_check_interval_seconds`: CPUとディスク使用率のチェック頻度（秒）。メモリは各監視サイクルでチェックされます。
*   `cpu_threshold_percent`, `memory_threshold_percent`, `disk_threshold_percent`: それぞれCPU、メモリ、ディスク使用率の警告を発生させる閾値（パーセンテージ）。
*   `memory_leak_check_window_minutes`: メモリリーク検出のために分析するメモリ使用履歴の期間（分）。
*   `memory_leak_rate_threshold_mb_per_hour`: 1時間あたりのメモリ増加量がこの値を超えた場合にメモリリークと判断する閾値（MB）。
*   `max_retries_on_error`: エラー発生時にF7自己修復の後に試行する最大リトライ回数。
*   `f7_healing_probability`: F7 (自己修復) が成功する初期確率（0.0～1.0）。F8学習サイクルによって動的に変動します。
*   `learning_cycle_trigger_hours`: F8 (自己進化) 学習サイクルを自動的にトリガーする時間間隔（時間）。
*   `learning_cycle_trigger_errors`: F8 (自己進化) 学習サイクルを自動的にトリガーするエラー発生回数。
*   `claude_api_cost_per_call`, `google_sheets_api_cost_per_call`: 各API呼び出し1回あたりの仮想コスト。API使用量監視の計算に使用されます。
*   `claude_api_rate_limit_per_minute`, `google_sheets_api_rate_limit_per_minute`: 各APIの1分あたりの仮想的なレート制限。
*   `log_file`, `error_log_file`, `api_log_file`: 各種ログファイルの出力パス。
*   `max_log_size_mb`: 各ログファイルの最大サイズ（MB）。このサイズを超えると自動的にローテーションされます。
*   `log_backup_count`: 保持するログバックアップファイルの数。
*   `human_notification_emails`: F9 (人間通知) が発火した場合に通知を送るEメールアドレスのリスト。
*   `simulation_mode`: `true` に設定すると、`utils.py` の関数は擬似的なシステムメトリクスとAPI動作をシミュレートします。`false` に設定すると、`psutil` などのライブラリを使用して実際のシステムリソースの取得を試みます。

## 使用方法

1.  必要に応じて `config.json` を編集します。
2.  `main.py` スクリプトを実行します。デフォルトでは、タスク要件に合わせて6時間の連続稼働テストが実行されます。
    ```bash
    python main.py
    ```
    システムを無期限に稼働させたい場合（例: 本番運用時）は、`main.py` の `monitor.run_monitor(duration_hours=6)` を `monitor.run_monitor(duration_hours=0)` に変更して実行してください。

3.  すべてのログファイルは `logs/` ディレクトリに生成されます。
    *   `monitor.log`: システムの一般的な稼働状況、各監視サイクルの結果、F8学習サイクルに関する情報。
    *   `errors.log`: 発生したエラー、F7自己修復、リトライ、F9人間通知に関する詳細な記録。
    *   `api_usage.log`: 外部API呼び出しの記録、コスト、レート制限に関する情報。
    *   `final_checklist.md`: 稼働テスト終了時に自動生成される、本番運用前の最終確認チェックリスト。

4.  稼働中に `Ctrl+C` を押すと、テストが中断され、その時点までの稼働実績に基づいた最終チェックリストが生成されます。

## 成功基準の確認

以下の項目が、ログファイルの分析と最終チェックリストのレビューを通じて達成されることを確認します。

*   **6時間以上の連続稼働が成功する**:
    *   `monitor.log` に `Monitoring duration of X hours completed.` のログが記録されていることを確認します。
    *   長時間の稼働中にシステムがクラッシュしたり、重大な障害で停止しなかったことを確認します。
*   **エラー時の自動修復が正常に動作する**:
    *   `errors.log` をレビューし、`F7 (Self-Healing) successful` または `Retry X for '...' succeeded` のログが適切に記録されていることを確認します。
    *   F9 (人間通知) が、本当にシステムが自律解決できない重大な問題に対してのみ発火し、過度に通知が送られていないことを確認します。
*   **学習サイクルが自動実行される**:
    *   `monitor.log` に `F8 (Self-Evolution) learning cycle triggered!` のログが定期的に記録されていることを確認します（設定された時間間隔またはエラー回数に基づきます）。
    *   `Known issues` リストが更新され、`F7 healing probability` が徐々に増加しているログ（`F8: Pattern learning effect - F7 healing probability increased`）が確認できることを検証します。
*   **API使用量が許容範囲内に収まる**:
    *   `api_usage.log` および `monitor.log` に記録されたAPI使用量のサマリーを確認し、想定されるコスト範囲内に収まっていることを検証します。
    *   レート制限に関する警告（`API rate limit approaching!` または `Rate limit hit.`）が適切に記録され、システムがそれに対処している（例: 呼び出しを制限している）ことを確認します。
*   **詳細なチェックリストが作成される**:
    *   `logs/final_checklist.md` ファイルが生成されており、その内容がシステムの稼働実績を正確に反映し、本番運用に必要なすべての確認項目を網羅していることを確認します。

## 補足: `sh/run_autonomous_24h_v3.sh` との連携

この `main.py` スクリプトは、タスク説明にある `sh/run_autonomous_24h_v3.sh` のようなシェルスクリプトから呼び出されることを想定して設計されています。例えば、`run_autonomous_24h_v3.sh` スクリプトは以下のような基本的な構造を持つことができます。

```bash
#!/bin/bash

# ログディレクトリのパス
LOG_DIR="logs"
CONFIG_FILE="config.json"

# ログディレクトリが存在しない場合は作成
mkdir -p "$LOG_DIR"

echo "==================================================="
echo " Starting 24-hour Autonomous System Verification "
echo "==================================================="
echo "Started at: $(date)"
echo "Configuration file: $CONFIG_FILE"
echo "Log directory: $LOG_DIR"
echo "---------------------------------------------------"

# Pythonスクリプトをバックグラウンドで実行し、標準出力/エラーをファイルにリダイレクト
# main.pyは自身のロギング機構を持っているため、ここでは主にスクリプト自体の出力やエラーをキャプチャ
python3 main.py > "$LOG_DIR/console_output.log" 2>&1 &
PYTHON_PID=$!
echo "Autonomous System Monitor started with PID: $PYTHON_PID."
echo "Monitoring for 6 hours (as configured in main.py by default)."
echo "Detailed logs are available in $LOG_DIR/."
echo "---------------------------------------------------"

# main.pyで設定された duration_hours に合わせて待機
# 例えば、main.pyが6時間稼働するように設定されている場合
sleep 6h 5m # 少し余裕を持たせて待機

# プロセスがまだ実行中であるか確認し、必要であれば強制終了
# (duration_hours=0で無限ループの場合など、外部から終了させる必要がある場合)
if kill -0 $PYTHON_PID 2>/dev/null; then
    echo "Monitor process (PID: $PYTHON_PID) is still running after expected duration. Terminating gracefully..."
    kill $PYTHON_PID
    sleep 5 # プロセスが終了するのを待つ
fi

echo "---------------------------------------------------"
echo "6-hour run complete. Reviewing logs and final report."
echo "Generated files in $LOG_DIR/:"
ls -lh "$LOG_DIR"/
echo "---------------------------------------------------"
echo "Final verification step: Please review logs/final_checklist.md for comprehensive system status."
echo "==================================================="
echo " Verification Finished "
echo "==================================================="
```
（`run_autonomous_24h_v3.sh` の具体的な実装は本タスクの直接的な要求範囲外ですが、連携方法の理解を助けるために例を記述しました。）

## API仕様

### `AutonomousSystemMonitor` クラス (`main.py`)

*   `__init__(self, config_path: str = "config.json")`:
    *   監視システムのインスタンスを初期化します。
    *   指定されたパスから設定ファイルを読み込み、ロギングシステムを設定し、内部の状態変数を初期化します。
*   `run_monitor(self, duration_hours: int = 6)`:
    *   システム監視のメインループを実行します。
    *   `duration_hours` 引数で監視期間を時間単位で指定できます（`0` を指定すると無限に稼働）。
    *   定期的にリソースチェック、エラーシミュレーション、API監視、ログ管理、学習サイクルのトリガーを行います。
*   `generate_final_checklist(self) -> str`:
    *   稼働テストの完了時に、起動前、稼働中、停止時の確認項目を含む詳細な最終チェックリストを生成します。
    *   生成されたチェックリストはコンソールに出力され、`logs/final_checklist.md` に保存されます。

### ユーティリティ関数 (`utils.py`)

*   `get_cpu_usage(simulation_mode: bool = True) -> float`:
    *   現在のCPU使用率をパーセンテージで返します。`simulation_mode`が`True`の場合、擬似的な値を返します。
*   `get_memory_usage(simulation_mode: bool = True) -> tuple[float, float, float]`:
    *   現在のメモリ使用率（パーセンテージ）、総メモリ量（MB）、使用メモリ量（MB）をタプルで返します。`simulation_mode`が`True`の場合、擬似的な値を返します。
*   `calculate_memory_leak_rate(memory_history: list[tuple[datetime, float]]) -> float`:
    *   メモリ使用量の履歴データ（タイムスタンプと使用メモリ量のペアのリスト）から、1時間あたりのメモリリーク率（MB/hour）を計算して返します。メモリ使用量が減少している場合は`0.0`を返します。
*   `get_disk_usage(simulation_mode: bool = True, path: str = './') -> float`:
    *   指定されたパス（デフォルトは現在のディレクトリ）のディスク使用率をパーセンテージで返します。`simulation_mode`が`True`の場合、擬似的な値を返します。
*   `log_event(level: str, message: str, log_file: str = "logs/general.log")`:
    *   指定されたログレベルとメッセージでイベントをログに記録します。これは一般的なロギング補助関数ですが、`main.py`では通常、`logging`モジュールを直接使用します。
*   `rotate_log_file(log_path: str, max_bytes: int, backup_count: int, logger_instance: logging.Logger)`:
    *   指定されたログファイルが最大サイズを超えた場合に、自動的にファイルをローテーション（バックアップおよび新規ファイル作成）します。`logger_instance` を引数に取ることで、ロガーのハンドラを適切に管理します。
*   `simulate_api_call(api_name: str, cost_per_call: float, simulation_mode: bool = True) -> float`:
    *   特定のAPIへの呼び出しをシミュレートし、その呼び出しにかかる仮想コストを返します。`simulation_mode`が`True`の場合、外部APIへの実際の呼び出しは行いません。
*   `send_notification(message: str, notification_type: str, recipients: list[str])`:
    *   F9 (人間通知) として、指定されたメッセージと通知タイプを、指定された受信者リストに送信するプロセスをシミュレートします。実際の通知メカニズム（メール、Slackなど）の実装は、この関数内に含めることができます。

---