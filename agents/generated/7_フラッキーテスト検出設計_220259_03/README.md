# テスト自動化エンジンにおけるフラッキーテスト検出・修正設計

## 概要

本ドキュメントは、テスト自動化エンジン（`agents/efficiency/test_automation_engine.py`）にフラッキーテスト（実行結果が不安定なテスト）を自動的に検出し、修正を提案・適用するロジックの設計を記述します。これにより、テストスイートの信頼性を向上させ、誤検出による開発効率の低下を防ぐことを目的とします。

フラッキーテストは、テスト環境の変動、外部サービスの依存、非同期処理のタイミング問題、並行処理の競合など、様々な非決定的要素によって発生します。これらのテストを放置すると、開発者は本当のバグとフラッキーな失敗の区別がつかなくなり、CI/CDパイプラインの信頼性が損なわれ、無駄な再実行や調査に時間を費やすことになります。

この設計では、統計分析と複数回実行による再現性確認を組み合わせたハイブリッドな検出アプローチを採用し、検出されたフラッキーテストに対しては自動リトライといった修正戦略を適用することで、テストスイートの安定化を目指します。

## 設計原則

1.  **既存システムとの互換性**: `test_automation_engine.py` および既存のテスト実行環境（pytest）とのスムーズな統合を前提とします。
2.  **モジュール性**: フラッキーテスト検出ロジックは独立したモジュールとして設計し、他の部分への影響を最小限に抑えます。
3.  **設定可能性**: 検出ロジックの閾値やリトライ戦略は設定ファイルを通じて容易に調整できるようにします。
4.  **スケーラビリティ**: 大規模なテストスイートにも対応できるよう、効率的な履歴管理と分析を考慮します。
5.  **レポート機能**: 検出されたフラッキーテストや適用された修正戦略について、明確なレポートを提供します。

## フラッキーテスト検出アルゴリズム

フラッキーテスト検出は、以下の2段階のアプローチで実施します。

### 1. 統計的分析による潜在的フラッキーテストの識別

テストの過去の実行履歴を分析し、統計的に不安定な傾向を示すテストを「潜在的にフラッキー」としてマークします。

*   **成功率の変動**: 過去N回のテスト実行における成功率（Pass Rate）が、設定された閾値（例: 80%）を下回るテスト。継続的に失敗するテストだけでなく、たまに失敗するテストも検出対象とします。
*   **実行時間の分散**: テストの平均実行時間に対する標準偏差の割合（Coefficient of Variation）が設定された閾値（例: 30%）を超えるテスト。これは、同じテストでも実行環境やタイミングによって実行時間が大きく変動するテストを捉えるのに役立ちます。例えば、外部APIの応答速度に依存するテストや、データベースの負荷状況によって時間が変わるテストなどです。

### 2. 複数回実行による再現性の確認

統計的分析で「潜在的にフラッキー」と識別されたテストに対し、短期間で複数回（例: 3〜5回）テストを再実行します。

*   **失敗の再現**: 再実行のうち、設定された回数（例: 2回以上）失敗した場合、そのテストを「フラッキーテスト」として確定します。これは、一時的なネットワーク障害などによる偶発的な失敗と、本質的な不安定性を持つテストを区別するために重要です。

### 静的解析 (将来的な拡張)

コードの静的解析による非決定的要素の検出は、本設計では直接の実装スコープ外としますが、将来的な拡張として以下の要素を識別する設計を検討します。

*   **時刻依存**: `datetime.now()`, `time.time()` など、実行時刻によって結果が変わる可能性のあるコード。
*   **乱数**: `random` モジュールを使用し、シードが固定されていないコード。
*   **並行処理**: スレッドやプロセス間通信、ロックの欠如などによる競合状態 (Race Condition)。
*   **外部依存**: 外部APIコール、ファイルシステムへのアクセス、データベース操作など、コントロールできない外部環境に依存する部分。

これらの要素は、コードレビューや専用の静的解析ツール (`Pylint`, `Bandit` などと連携) を通じて特定し、テストコードの改善を促す情報として活用できます。

## 検出ロジックの詳細設計

### 履歴データの収集・分析方法

*   **データベーススキーマ**: テスト実行履歴はSQLiteデータベース (`test_history.db`) に保存します。
    *   **テーブル名**: `test_results`
    *   **カラム**:
        *   `id` (INTEGER PRIMARY KEY AUTOINCREMENT): 一意のレコードID。
        *   `test_id` (TEXT NOT NULL): テストを一意に識別する文字列（例: `module.class.method`）。
        *   `timestamp` (TEXT NOT NULL): テスト実行日時 (ISO 8601形式のUTC)。
        *   `status` (TEXT NOT NULL): 実行結果 ('PASS', 'FAIL', 'ERROR')。
        *   `duration` (REAL): テスト実行時間（秒）。
        *   `error_message` (TEXT): 失敗時のエラーメッセージやスタックトレース。
        *   `additional_info` (TEXT): JSON形式で保存される追加情報（例: `{"runner_id": "ci-job-123", "attempt": 2}`）。
*   **データ収集**: `TestAutomationEngine` がテストを実行した後、各テストの結果を `FlakyTestDetector` に渡し、`record_test_result` メソッドを通じてデータベースに記録します。
*   **データ分析**: `utils.py` 内の `calculate_stability_metrics` 関数が、指定されたテストIDの履歴から成功率、失敗回数、平均実行時間、実行時間の標準偏差を計算します。

### フラッキー判定の閾値設定

以下の設定値は`FlakyTestDetector`の初期化時に`config`辞書として渡すことで調整可能です。

*   `history_lookback_limit` (int): 統計分析に用いる過去の実行履歴数（デフォルト: 10）。
*   `min_history_runs_for_initial_check` (int): 統計分析を開始するために必要な最小履歴数（デフォルト: 3）。
*   `flaky_failure_rate_threshold` (float): 成功率がこの値未満の場合、潜在的フラッキーと判定（デフォルト: 80.0）。
*   `flaky_duration_stddev_ratio_threshold` (float): 実行時間の標準偏差が平均のこの割合を超える場合、潜在的フラッキーと判定（デフォルト: 0.3 = 30%）。
*   `rerun_attempts_for_flaky_confirmation` (int): 潜在的フラッキーテストを再実行する回数（デフォルト: 3）。
*   `rerun_failure_threshold` (int): 再実行のうち、この回数以上失敗すればフラッキーと確定（デフォルト: 1）。

### 検出フローチャート

```
+---------------------------+
| テストスイート実行        |
| (TestAutomationEngine)    |
+-------------+-------------+
              |
              V
+-------------+-------------+
| 各テスト結果を記録        |
| (FlakyTestDetector.record_test_result) |
| (DB: test_resultsテーブル) |
+-------------+-------------+
              |
              V
+---------------------------+
| フラッキーテスト検出開始    |
| (FlakyTestDetector.detect_flaky_tests) |
+---------------------------+
              |
              V
+-------------+-------------+
| 全テストIDを取得            |
| (DBから DISTINCT test_id)  |
+-------------+-------------+
              |
              V
+-------------+-------------+
| 各テストIDについてループ    |
+-------------+-------------+
              |
              V
+-------------+-------------+
| 過去N回 (history_lookback_limit) の履歴を取得 |
| (utils.TestHistoryDB.get_test_history)   |
+-------------+-------------+
              |
              V
+-------------+-------------+
| 安定性メトリクスを計算      |
| (utils.calculate_stability_metrics) |
| (成功率, 実行時間標準偏差など) |
+-------------+-------------+
              |
              V
+-------------+-------------+
| 潜在的フラッキー判定        |
| (utils.is_potentially_flaky) |
| (成功率 < 閾値 OR 標準偏差比 > 閾値) |
+-------------+-------------+
      |       NO        | YES
      |-----------------|
      V                 V
+-----------------+   +-------------------------+
| 次のテストIDへ  |   | 潜在的フラッキーテストとしてマーク |
+-----------------+   +-------------------------+
                          |
                          V
+---------------------------+
| 潜在的フラッキーテストに対するループ |
+---------------------------+
              |
              V
+-------------+-------------+
| テストを複数回再実行        |
| (rerun_attempts_for_flaky_confirmation) |
| (FlakyTestDetector._simulate_single_test_run) |
+-------------+-------------+
              |
              V
+-------------+-------------+
| 再実行中の失敗回数をカウント |
+-------------+-------------+
              |
              V
+-------------+-------------+
| 失敗回数 >= rerun_failure_threshold ? |
+-------------+-------------+
      |       NO        | YES
      |-----------------|
      V                 V
+-----------------+   +-------------------------+
| フラッキーではない |   | フラッキーテストとして確定 & 報告 |
+-----------------+   | (suggested_actions生成) |
                      +-------------------------+
                          |
                          V
+---------------------------+
| 検出されたフラッキーテストのリストを返す |
+---------------------------+
              |
              V
+---------------------------+
| TestAutomationEngineに結果を渡し、|
| 自動リトライ等の修正戦略を適用    |
+---------------------------+
```

## テスト修正戦略の検討

フラッキーテストが検出された場合、`TestAutomationEngine`は以下の戦略を自動的に適用したり、開発者に推奨したりします。

1.  **リトライメカニズムの追加 (自動適用)**:
    *   検出されたフラッキーテストは、CI/CDパイプラインまたは`TestAutomationEngine`内で自動的に複数回（例: `max_auto_retries_on_flaky`で設定された回数）リトライされます。これにより、一時的な失敗は自動的に吸収され、CIの失敗を減らします。リトライ間の短い待機時間 (`retry_delay_seconds`) も設定可能です。
    *   Pythonのpytest環境では、`pytest-rerunfailures`のようなプラグインを利用することで、このメカニズムを簡単に統合できます。

2.  **適切な待機時間（sleep）の挿入 (推奨)**:
    *   非同期処理やUI要素のロードに依存するテストの場合、固定的な`time.sleep()`ではなく、特定の条件が満たされるまで待機する明示的な待機（Explicit Wait）の導入を推奨します。Selenium WebDriverの`WebDriverWait`などが典型例です。これにより、テストの堅牢性が向上し、タイムアウトによるフラッキーな失敗が減少します。

3.  **モックやスタブの活用による外部依存の排除 (推奨)**:
    *   データベース、外部API、ファイルシステムなどの外部リソースに依存するテストは、これらのリソースが不安定な場合、フラッキーになる傾向があります。テスト実行時には、これらの外部依存をモックやスタブに置き換えることで、テストの独立性と再現性を高めるよう推奨します。Pythonでは`unittest.mock`モジュールが強力です。

4.  **テスト順序の最適化 (推奨)**:
    *   テストケース間に意図しない依存関係がある場合、特定の順序で実行されたときのみ成功/失敗するといったフラッキーな挙動を示すことがあります。このような場合、テストの順序を固定したり、テスト間の依存関係を排除したりするよう推奨します。

## 実装計画

### 既存の `test_automation_engine.py` への統合方法

`test_automation_engine.py`は、`TestAutomationEngine`クラスとして既存のテスト実行ロジックをラップしていると仮定します。

1.  **依存性の注入**: `TestAutomationEngine`クラスのコンストラクタで`FlakyTestDetector`のインスタンスを受け取るように変更します。
    ```python
    # agents/efficiency/test_automation_engine.py
    from flaky_test_detector import FlakyTestDetector # 新しいファイルからインポート

    class TestAutomationEngine:
        def __init__(self, config, detector: FlakyTestDetector):
            self.config = config
            self.detector = detector # FlakyTestDetectorのインスタンスを保持
            # ... その他の初期化
    ```
2.  **テスト結果の記録**: `TestAutomationEngine`が各テストを実行した後、その結果を`self.detector.record_test_result(...)`を呼び出して記録します。
    ```python
    class TestAutomationEngine:
        # ...
        def run_single_test(self, test_id):
            # ... テストを実行し、結果（status, duration, error_message）を取得 ...
            self.detector.record_test_result(test_id, status, duration, error_message)
            return result
    ```
3.  **フラッキーテストの検出と修正戦略の適用**: `TestAutomationEngine`の`run_all_tests`のような主要な実行メソッド内で、全てのテスト実行が完了した後、`self.detector.detect_flaky_tests()`を呼び出します。検出されたフラッキーテストに対しては、`self.detector._execute_test_with_retries`のようなメソッドを利用してリトライを適用します。
    ```python
    class TestAutomationEngine:
        # ...
        def run_all_tests(self):
            # ... 全テストの初回実行と結果記録 ...

            flaky_tests = self.detector.detect_flaky_tests()
            if flaky_tests:
                for flaky_test in flaky_tests:
                    test_id = flaky_test["test_id"]
                    # 自動リトライの適用
                    final_result = self.detector._execute_test_with_retries(
                        test_id, self.detector.config["max_auto_retries_on_flaky"]
                    )
                    # 開発者への修正提案の提示 (ログ出力、レポート生成など)
                    for action in flaky_test["suggested_actions"]:
                        print(f"[ACTION REQUIRED for {test_id}]: {action}")
            # ... 全体結果の集計とレポート ...
    ```

### データベーススキーマの設計（テスト実行履歴）

既に「検出ロジックの詳細設計」セクションで説明した`test_results`テーブルスキーマを使用します。
SQLiteは軽量でファイルベースであるため、CI/CD環境での利用やローカル開発環境での手軽な検証に適しています。`utils.py`の`TestHistoryDB`クラスがこのDB操作を抽象化します。

### CI/CDパイプラインとの連携方法

CI/CDパイプライン (`Jenkins`, `GitHub Actions`, `GitLab CI` など) との連携は、以下のステップで実現します。

1.  **テスト実行ステップの変更**: 既存のテスト実行ステップ（例: `pytest` コマンド）の後に、`TestAutomationEngine`を呼び出すスクリプトを追加します。
    ```yaml
    # GitHub Actions の例
    - name: Run Tests with Flaky Detector
      run: |
        python -m pip install -r requirements.txt
        python your_test_runner_script.py # TestAutomationEngineをラップしたスクリプト
      env:
        FLAKY_DB_PATH: ${{ github.workspace }}/test_history.db # DBファイルパスを環境変数で渡す
    ```
2.  **結果のアーティファクト化**: 検出されたフラッキーテストのレポートや、更新されたSQLiteデータベースファイル(`test_history.db`)をCIのアーティファクトとして保存します。これにより、履歴の追跡や後の分析が可能になります。
    ```yaml
    - name: Upload Test History DB
      uses: actions/upload-artifact@v3
      with:
        name: test-history-db
        path: test_history.db
    - name: Generate Flaky Test Report
      run: python generate_flaky_report.py > flaky_report.md
    - name: Upload Flaky Test Report
      uses: actions/upload-artifact@v3
      with:
        name: flaky-test-report
        path: flaky_report.md
    ```
3.  **通知と課題管理システムとの連携**:
    *   フラッキーテストが検出された場合、SlackやMicrosoft Teamsへの通知をトリガーします。
    *   検出されたフラッキーテストの情報と推奨される修正戦略を、Jiraなどの課題管理システムに自動的に課題として起票します。これにより、開発者がフラッキーテストの修正を優先的に行えるよう促します。
    *   特に、繰り返しフラッキーと検出され、自動リトライでも失敗し続けるテストに対しては、CIを失敗させる判断も考慮し、早期の修正を強制することもできます。

## 使用方法

### インストール

```bash
# Python 3.8以上を推奨
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt # utils.py や main.py で必要なライブラリ (sqlite3はPython標準ライブラリ)
```

### 設定

`FlakyTestDetector`および`TestAutomationEngine`は、`config`辞書を通じて動作をカスタマイズできます。

```python
simulation_config = {
    "history_lookback_limit": 10,                 # 統計分析に用いる過去の実行履歴数
    "min_history_runs_for_initial_check": 3,      # 初期チェックに必要な最小履歴数
    "flaky_failure_rate_threshold": 80.0,         # 成功率がこの値未満の場合、"疑わしい"とマーク
    "flaky_duration_stddev_ratio_threshold": 0.3, # 実行時間の標準偏差が平均のこの割合を超える場合、"疑わしい"とマーク
    "rerun_attempts_for_flaky_confirmation": 3,   # 疑わしいテストを再実行する回数
    "rerun_failure_threshold": 1,                 # 再実行のうち、これ以上失敗すればフラッキーと確定
    "max_auto_retries_on_flaky": 2,               # フラッキーと判定されたテストに対する最大自動リトライ回数
    "retry_delay_seconds": 0.5,                   # リトライ間の待機時間
    "simulate_test_pass_rate_map": {},            # シミュレーション用のテストIDごとの成功率
    "simulate_test_duration_map": {},             # シミュレーション用のテストIDごとの平均実行時間
}

detector = FlakyTestDetector(db_path="my_test_history.db", config=simulation_config)
```

### テスト実行とフラッキー検出

`main.py`の`if __name__ == "__main__":`ブロックに記載されている例を参考に、`TestAutomationEngine`を使用してテストスイートを実行します。

```python
# main.py の実行例を抜粋

# FlakyTestDetectorを初期化
detector = FlakyTestDetector(db_path=":memory:", config=simulation_config)

# テストスイートの定義
test_suite = ["test_stable_login", "test_flaky_db_connection", "test_intermittent_api_call"]

# 複数回テストスイートを実行し、履歴を蓄積 (フラッキー検出のために履歴が必要)
for _ in range(5):
    for test_id in test_suite:
        # 実際のテストランナー (pytestなど) の実行結果を detector に渡す
        # ここではシミュレーション関数を使用
        result = detector._simulate_single_test_run(test_id)
        detector.record_test_result(test_id, result["status"], result["duration"], result["error_message"])

# TestAutomationEngineを初期化し、実行
engine = TestAutomationEngine(detector, test_suite)
engine.run_all_tests()

detector.db.close() # DB接続を閉じる
```

この実行により、テスト結果がデータベースに記録され、`FlakyTestDetector`がその履歴を分析してフラッキーテストを検出します。検出された場合、`TestAutomationEngine`は設定されたリトライ戦略を適用し、検出されたフラッキーテストと推奨される修正アクションがコンソールに出力されます。

## API仕様

### `utils.py`

*   **`class TestHistoryDB(db_path: str = "test_history.db")`**
    *   テスト実行履歴をSQLiteデータベースで管理。
    *   `insert_result(test_id: str, status: str, duration: float, error_message: str = None, additional_info: Dict[str, Any] = None)`: テスト結果を挿入。
    *   `get_test_history(test_id: str, limit: int = 100) -> List[Dict[str, Any]]`: 特定テストの履歴を取得。
    *   `get_all_test_ids() -> List[str]`: 全てのユニークなテストIDを取得。
    *   `close()`: DB接続を閉じる。
*   **`calculate_stability_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]`**
    *   テスト実行結果のリストから成功率、失敗回数、平均実行時間、実行時間の標準偏差を計算。
*   **`is_potentially_flaky(metrics: Dict[str, Any], config: Dict[str, Any]) -> Tuple[bool, str]`**
    *   計算されたメトリクスと設定に基づき、テストが潜在的にフラッキーであるかを判定し、その理由を返す。

### `main.py`

*   **`class FlakyTestDetector(db_path: str = "test_history.db", config: Dict[str, Any] = None)`**
    *   フラッキーテストを検出、修正戦略を提案・適用。
    *   `record_test_result(...)`: `TestHistoryDB.insert_result`のラッパー。
    *   `_simulate_single_test_run(test_id: str) -> Dict[str, Any]`: 単一テストの実行をシミュレート（内部用）。
    *   `_execute_test_with_retries(test_id: str, max_retries: int) -> Dict[str, Any]`: リトライ付きでテストを実行（シミュレーション）。
    *   `detect_flaky_tests() -> List[Dict[str, Any]]`: データベース履歴に基づきフラッキーテストを検出し、レポートを返す。
    *   `_suggest_flaky_test_actions(test_id: str) -> List[str]`: フラッキーテストに対する推奨修正戦略を生成（内部用）。
*   **`class TestAutomationEngine(detector: FlakyTestDetector, test_list: List[str])`**
    *   テスト自動化エンジンをシミュレートし、`FlakyTestDetector`と連携。
    *   `run_all_tests()`: 全テストを実行し、結果を記録、フラッキーテストを検出し、リトライ戦略を適用。