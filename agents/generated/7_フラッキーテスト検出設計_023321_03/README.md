# Flaky Test Detector for Test Automation Engine

## 概要

このプロジェクトは、テスト自動化エンジン（`agents/efficiency/test_automation_engine.py`）に統合するための、フラッキーテスト（Flaky Tests、結果が不安定なテスト）を自動的に検出し、修正戦略を提案するロジックを設計したものです。テストスイートの信頼性を向上させ、誤検出による開発効率の低下を防ぐことを目的としています。

現代のソフトウェア開発において、テスト自動化は不可欠ですが、一部のテストが環境やタイミングによって成功したり失敗したりする「フラッキー」な振る舞いをすることがあります。これはCI/CDパイプラインを不安定にし、開発者の信頼を損ね、本来問題のないコードをデバッグするために貴重な時間を浪費させる原因となります。

本設計は、テスト実行履歴の統計分析、複数回実行による再現性確認などの手法を用いて、フラッキーテストを効果的に特定します。さらに、特定されたフラッキーテストに対して、リトライメカニズム、適切な待機時間の挿入、モックの活用、テスト順序の最適化といった具体的な修正戦略を提案することで、開発者が問題解決に取り組む際の指針を提供します。

### 目的

- テストスイート全体の信頼性を高める。
- フラッキーテストによるCI/CDパイプラインの不安定化を防ぐ。
- 開発者がフラッキーテストの原因特定と修正にかかるコストを削減する。

## アーキテクチャ

本システムは以下の主要コンポーネントで構成されます。

1.  **`FlakyTestDetector` (main.py):**
    *   フラッキーテストの検出と修正戦略の提案をオーケストレーションするメインクラス。
    *   テスト実行結果の記録、履歴データの取得、`analyze_test_stability`関数の呼び出し、検出閾値の適用、修正戦略の提案を行います。
    *   CI/CDパイプラインの一部として、またはテストスイート実行後の分析ツールとして機能することを想定しています。
    *   テスト自動化エンジン（例: `test_automation_engine.py`）内のテスト実行ロジックにフックされ、各テストの実行前後でデータを収集し、分析結果を報告します。

2.  **`SQLiteManager` (utils.py):**
    *   テスト実行履歴を永続化するためのSQLiteデータベースを管理するユーティリティクラス。
    *   テスト結果の挿入、特定のテストIDまたは期間内のテスト結果の取得機能を提供します。
    *   将来的には、Google Sheetsや他のデータベースへの切り替えも容易なように抽象化されています。

3.  **`analyze_test_stability` (utils.py):**
    *   与えられたテスト実行結果のリストから、成功率、平均実行時間、実行時間の標準偏差などの統計情報を計算する純粋関数。
    *   フラッキーテスト検出の主要な統計分析部分を担います。

4.  **`TestResult` (utils.py):**
    *   個々のテスト実行結果を表現するための`namedtuple`。データベースから取得されるデータ構造を標準化します。

## フラッキーテスト検出アルゴリズム

以下の組み合わせにより、フラッキーテストを効果的に検出します。

1.  **テスト実行履歴の統計分析:**
    *   **成功率:** 過去の実行における成功率が一定の閾値（デフォルト85%）を下回るテストをフラッキー候補とします。
    *   **実行時間の分散:** テストの平均実行時間に対する標準偏差の割合が一定の閾値（デフォルト50%）を超えるテストをフラッキー候補とします。これは、テストの実行環境や外部依存の応答時間が不安定であることを示唆します。

2.  **テストの複数回実行による再現性確認:**
    *   `run_with_flaky_detection_retries`メソッドにより、疑わしいテストや、特に失敗したテストを複数回（デフォルト3回）再実行し、その結果を記録します。
    *   短期間に同じテストが複数回失敗したり、成功と失敗を繰り返したりするパターンを捕捉し、より確実なフラッキー判定に役立てます。

## テスト修正戦略の検討

フラッキーと判定されたテストに対して、以下のような具体的な修正戦略を提案します。

-   **リトライメカニズムの追加:** テストケース自体に、一時的なネットワークエラーやリソース不足を吸収するためのリトライロジックを組み込むことを提案します。
-   **適切な待機時間の挿入:** タイムアウトやアサーションの前に、非同期処理の完了を待つための明示的な待機（例: UIテストにおけるWebDriverWait、ポーリング）を導入することを推奨します。固定の`time.sleep()`は推奨されません。
-   **モックやスタブの活用による外部依存の排除:** データベース、外部API、メッセージキューなどの外部サービスへの依存をモックやスタブに置き換えることで、テストの実行を高速化し、外部要因による不安定さを排除します。
-   **テスト順序の最適化:** テスト間の依存関係を排除し、各テストが独立して実行できるように設計することの重要性を強調します。特定のテストが他のテストの状態に影響を与えないようにします。
-   **テスト環境の一貫性:** 各テスト実行がクリーンで一貫性のある環境で実施されることを保証するための改善案を提示します（例: テストデータベースのリセット、コンテナ化）。

## インストール

1.  **Python環境の準備:**
    Python 3.8以上の環境が必要です。

2.  **依存ライブラリのインストール:**
    このプロジェクトは標準ライブラリ（`sqlite3`, `datetime`, `statistics`, `json`, `logging`, `os`, `time`, `collections`, `typing`）のみを使用しており、追加の外部ライブラリは不要です。

    もし`pytest`のようなテストフレームワークとの統合を想定する場合は、別途インストールが必要です。
    ```bash
    pip install pytest # 既存のtest_automation_engine.pyがpytestを使用している場合
    ```

## 使用方法

### 1. `FlakyTestDetector` の初期化

テスト自動化エンジンの初期化時に`FlakyTestDetector`をインスタンス化します。データベースパスや検出閾値などの設定を渡すことができます。

```python
from main import FlakyTestDetector

# デフォルト設定で初期化
flaky_detector = FlakyTestDetector()

# またはカスタム設定で初期化
custom_config = {
    "flaky_threshold_pass_rate": 0.90, # 成功率90%未満
    "min_history_for_analysis": 5,     # 5回以上の履歴で分析
    "max_retries_for_flaky_detection": 5, # フラッキー検出時の最大リトライ回数
    "wait_time_on_retry_ms": 500,     # リトライ時の待機時間500ms
    "lookback_period_days": 60        # 過去60日間のデータを分析
}
flaky_detector = FlakyTestDetector(db_path="my_custom_test_results.db", config=custom_config)
```

### 2. テスト結果の記録

各テストが実行された後、その結果を`FlakyTestDetector`に記録します。これは通常、テスト自動化エンジンのテスト実行ループ内で行われます。

```python
# 仮のテスト実行関数 (実際のテストランナーをラップするイメージ)
import random

def mock_test_runner(test_id_to_run: str, *args, **kwargs) -> Dict[str, Any]:
    """
    テストIDを受け取り、テストを実行し、結果を辞書で返すモック関数。
    フラッキーな挙動を模倣する。
    """
    if test_id_to_run == "test_flaky_payment" and random.random() < 0.4: # 40%の確率で失敗
        return {'status': 'failed', 'duration': 1.5 + random.random(), 'error_message': 'Payment service timeout or concurrency issue'}
    elif test_id_to_run == "test_stable_login":
        return {'status': 'passed', 'duration': 0.3 + random.random()/5, 'error_message': None}
    else: # 他のテストは安定
        return {'status': 'passed', 'duration': 0.7 + random.random()/2, 'error_message': None}

# 実際のテスト実行と記録の例
test_id = "test_flaky_payment"
result = mock_test_runner(test_id)
flaky_detector.record_test_result(test_id, result['status'], result['duration'], result['error_message'])
```

### 3. フラッキーテストの検出と修正戦略の取得

テストスイート全体の実行後、または定期的に、`detect_flaky_tests`メソッドを呼び出してフラッキーテストを特定します。

```python
# フラッキーテストの検出を実行
detection_report = flaky_detector.detect_flaky_tests()

print("\n--- Flaky Test Detection Report ---")
print(f"Total tests analyzed: {detection_report['analysis_summary']['total_tests_analyzed']}")
print(f"Detected flaky tests count: {detection_report['analysis_summary']['detected_flaky_count']}")

for flaky_test in detection_report['flaky_tests']:
    print(f"\nFlaky Test ID: {flaky_test['test_id']}")
    print(f"  Reason: {flaky_test['reason']}")
    print(f"  Metrics: {flaky_test['metrics']}")

    # 修正戦略の提案を取得
    suggestions = flaky_detector.suggest_fix_strategies(flaky_test)
    print("  Suggested Fixes:")
    for s in suggestions:
        print(f"    - {s}")

# 最新のフラッキーテストステータスレポートの取得
status_report = flaky_detector.get_flaky_test_status_report(num_recent_runs=15)
print("\n--- Flaky Test Status Report (Recent Runs) ---")
# レポートの内容はJSON形式で出力されるため、適宜パースして表示
import json
print(json.dumps(status_report, indent=2))
```

### 4. `run_with_flaky_detection_retries` を用いたテスト実行

`FlakyTestDetector`は、テスト自動化エンジンが個々のテストを実行する際に、リトライロジックを適用できるヘルパーメソッドを提供します。これにより、検出のための複数回実行や、一時的な失敗の自動回復を試みることができます。

```python
test_id_to_run_with_retries = "test_flaky_payment"

final_test_result = flaky_detector.run_with_flaky_detection_retries(
    mock_test_runner, # 実際のテストランナー関数
    test_id_to_run_with_retries
)

print(f"\nFinal result for {test_id_to_run_with_retries}: {final_test_result['status']}")
print(f"  Attempts made: {final_test_result['attempts']}")
print(f"  All run results: {final_test_result['all_run_results']}")
```

## API仕様

### `main.py`

#### `class FlakyTestDetector`

##### `__init__(self, db_path: str = "test_results.db", config: Optional[Dict[str, Any]] = None)`
- **`db_path`**: テスト結果を保存するSQLiteデータベースのファイルパス。
- **`config`**: 検出閾値やリトライ設定をオーバーライドするための辞書。
    - `flaky_threshold_pass_rate` (float): 成功率の閾値 (デフォルト: 0.85)。
    - `flaky_threshold_duration_variance_factor` (float): 平均実行時間に対する標準偏差の比率の閾値 (デフォルト: 0.5)。
    - `min_history_for_analysis` (int): 分析に必要な最小実行履歴数 (デフォルト: 10)。
    - `max_retries_for_flaky_detection` (int): `run_with_flaky_detection_retries`での最大リトライ回数 (デフォルト: 3)。
    - `wait_time_on_retry_ms` (int): リトライ間の待機時間（ミリ秒） (デフォルト: 200)。
    - `lookback_period_days` (int): `detect_flaky_tests`が分析する過去の期間（日） (デフォルト: 30)。

##### `record_test_result(self, test_id: str, status: str, duration: float, error_message: Optional[str] = None)`
- **`test_id`**: テストの一意な識別子。
- **`status`**: テスト結果 (`'passed'`, `'failed'`, `'skipped'`, `'error'`)。
- **`duration`**: テスト実行時間（秒）。
- **`error_message`**: 失敗時のエラーメッセージ（オプション）。

##### `detect_flaky_tests(self, lookback_period_days: Optional[int] = None) -> Dict[str, Any]`
- **`lookback_period_days`**: 過去N日間のデータを分析対象とする（オプション、Noneの場合はコンフィグ値を使用）。
- **戻り値**: 検出されたフラッキーテストと分析のサマリーを含む辞書。

##### `run_with_flaky_detection_retries(self, test_runner_func, test_id: str, *args, **kwargs) -> Dict[str, Any]`
- **`test_runner_func`**: 実際のテストを実行する関数。`{'status': str, 'duration': float, 'error_message': str}`を返すことを期待。
- **`test_id`**: 実行するテストの識別子。
- **`*args, **kwargs`**: `test_runner_func`に渡す追加引数。
- **戻り値**: 最終的なテスト結果、実行回数、全ての実行結果のリストを含む辞書。

##### `suggest_fix_strategies(self, flaky_test_info: Dict[str, Any]) -> List[str]`
- **`flaky_test_info`**: `detect_flaky_tests`から返された単一のフラッキーテスト情報。
- **戻り値**: 提案される修正戦略のリスト。

##### `get_flaky_test_status_report(self, num_recent_runs: int = 20) -> Dict[str, Any]`
- **`num_recent_runs`**: 各テストについて取得する最近の実行履歴の数。
- **戻り値**: フラッキーテストのステータスと詳細な履歴、修正戦略を含むレポート辞書。

### `utils.py`

#### `TestResult` `namedtuple`
- `test_id` (str)
- `status` (str)
- `duration` (float)
- `timestamp` (str)
- `error_message` (Optional[str])

#### `class SQLiteManager`

##### `__init__(self, db_path: str)`
- **`db_path`**: SQLiteデータベースのファイルパス。

##### `create_table(self)`
- `test_results`テーブルを作成します。

##### `insert_result(self, test_id: str, status: str, duration: float, error_message: Optional[str] = None)`
- テスト結果をデータベースに挿入します。

##### `get_results(self, test_id: str, limit: Optional[int] = None) -> List[TestResult]`
- 指定された`test_id`のテスト結果を取得します。`limit`で取得件数を制限できます。

##### `get_results_since(self, period_days: int) -> List[TestResult]`
- 指定された日数以内の全てのテスト実行結果を取得します。

##### `close(self)`
- データベース接続を閉じます。

#### `analyze_test_stability(results: List[TestResult]) -> Dict[str, Any]`
- **`results`**: `TestResult`オブジェクトのリスト。
- **戻り値**: 成功率、平均実行時間、標準偏差などの統計情報を含む辞書。

## データベーススキーマ (`test_results.db`)

SQLiteデータベースには、以下のスキーマを持つ`test_results`テーブルが作成されます。

```sql
CREATE TABLE IF NOT EXISTS test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id TEXT NOT NULL,
    status TEXT NOT NULL,         -- 'passed', 'failed', 'skipped', 'error' など
    duration REAL NOT NULL,       -- テスト実行時間（秒）
    timestamp TEXT NOT NULL,      -- ISOフォーマットのタイムスタンプ (YYYY-MM-DDTHH:MM:SS.mmmmmm)
    error_message TEXT            -- テストが失敗した場合のエラーメッセージ
);
```

## CI/CDパイプラインとの連携方法

本システムは、CI/CDパイプラインに以下の方法で統合することを想定しています。

1.  **テスト実行のフック:**
    *   CI/CDジョブ内でテストスイートを実行する際、各テストの実行前後に`FlakyTestDetector`の`record_test_result`または`run_with_flaky_detection_retries`メソッドを呼び出すように、テストランナーをラップします。
    *   これにより、テスト結果がリアルタイムでデータベースに記録されます。

2.  **定期的なフラッキーテスト検出:**
    *   毎晩、または主要なブランチへのマージ後に、CI/CDパイプラインの一部として`FlakyTestDetector.detect_flaky_tests()`を実行するジョブを追加します。
    *   このジョブは、検出されたフラッキーテストのレポートを生成し、Slack、Jira、または開発者へのメール通知として配信します。

3.  **ゲートチェック:**
    *   もしフラッキーテストが急増した場合や、特定の閾値を超えた場合に、CI/CDパイプラインを「不安定」としてマークし、マージを一時的にブロックするなどのゲートチェックを実装できます。これにより、フラッキーテストが累積するのを防ぎます。

4.  **ダッシュボードへの可視化:**
    *   データベースに蓄積されたデータを活用し、Grafanaなどのダッシュボードツールでフラッキーテストの傾向、成功率の推移、実行時間の変動などを可視化することで、テストスイートの健全性を継続的に監視できます。

## 実装計画と今後の拡張

### 実装計画

1.  **データベース層の確立:** `utils.py` の `SQLiteManager` を完成させ、テスト結果の永続化と取得機能を実装。
2.  **統計分析コアの開発:** `utils.py` の `analyze_test_stability` を実装し、必要な統計メトリクスを計算。
3.  **検出ロジックの実装:** `main.py` の `FlakyTestDetector.detect_flaky_tests` に、統計分析と閾値に基づくフラッキー判定ロジックを実装。
4.  **リトライ機能の実装:** `main.py` の `FlakyTestDetector.run_with_flaky_detection_retries` を実装し、テストの複数回実行をサポート。
5.  **修正戦略の提案:** `main.py` の `FlakyTestDetector.suggest_fix_strategies` に、フラッキーテストの特性に応じた提案ロジックを実装。
6.  **CI/CDパイプラインとの統合インターフェースの設計:** 既存の `test_automation_engine.py` との連携を想定したメソッドシグネチャとデータフローを明確化。
7.  **テストと検証:** 各コンポーネントの単体テストと、統合テストを実施し、フラッキーテストの検出と修正戦略の提案が意図通りに機能することを確認。

### 将来的な拡張

-   **高度な静的コード解析:** テストコードを静的に解析し、非決定的要素（例: `time.sleep()`のハードコード、乱数、グローバル状態、並行処理の競合）を自動的に特定する機能を追加。
-   **機械学習を用いた検出:** 過去の実行履歴だけでなく、コード変更履歴やコミットメッセージ、テスト失敗時のスタックトレースなどを特徴量として、機械学習モデルを用いてフラッキーテストを予測・検出する精度を高める。
-   **AI駆動型修正提案:** 検出されたフラッキーテストに対し、より具体的なコードレベルでの修正提案（例: `sleep`を`wait_until`に変更、モックの自動生成）を行うAIアシスタント機能。
-   **Google Sheets / クラウドDB対応:** SQLiteだけでなく、Google SheetsやPostgreSQL、MySQLなどのクラウドベースのデータベースへのデータ記録をサポートするアダプターを追加。
-   **CI/CDツールとの密な連携:** GitHub Actions, GitLab CI, Jenkinsなどの特定のCI/CDツール向けに、より簡単な統合を可能にするプラグインや拡張機能の開発。
-   **テストの隔離と実行順序の最適化:** フラッキーテストを隔離して実行したり、依存関係を考慮してテスト実行順序を動的に最適化したりする機能を検討。