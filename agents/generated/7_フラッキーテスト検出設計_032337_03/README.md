# Flaky Test Detection and Remediation Engine

## 概要

このプロジェクトは、テスト自動化エンジン（`agents/efficiency/test_automation_engine.py`）に統合するための、フラッキーテスト（結果が不安定なテスト）を自動的に検出し、修正を提案するロジックの設計とプロトタイプ実装を提供します。目的は、テストスイートの信頼性を高め、誤検出による開発効率の低下を防ぐことです。

フラッキーテストは、同じコードに対してテストを複数回実行しても、成功したり失敗したりするテストを指します。これらはCI/CDパイプラインのボトルネックとなり、開発者の信頼性を損ない、無駄な調査時間とリソースを消費します。本エンジンは、以下の手法を組み合わせてフラッキーテストを特定し、効果的な修正戦略を提供します。

1.  **テスト実行履歴の統計分析**: 過去の実行結果（成功率、実行時間の分散、エラーメッセージのパターン）を分析し、不安定さの兆候を検出します。
2.  **再現性確認のための複数回実行**: 統計分析で候補とされたテストに対し、実際に複数回再実行して不安定さを確認します。
3.  **静的コード解析**: テストコード自体を解析し、`time.sleep`、`random`、グローバル状態へのアクセスといった非決定的要素や、テスト間の依存関係につながる可能性のあるパターンを検出します。
4.  **修正戦略の提案**: 検出されたフラッキーテストに対して、リトライメカニズム、適切な待機時間の挿入、モック/スタブの活用、テスト順序の最適化など、具体的な修正方法を提案します。

## アーキテクチャ

本システムは、既存のテスト自動化エンジン（`TestAutomationEngine`）にアドオンとして機能するよう設計されています。
主要なコンポーネントは以下の通りです。

-   **`FlakyTestDetector`**: フラッキーテスト検出の中核ロジックを担うクラス。テスト履歴の分析、再実行による確認、修正戦略の生成を行います。
-   **`TestHistoryManager`**: テスト実行結果をSQLiteデータベースに永続化し、取得する責務を持つユーティリティクラス。テスト実行履歴の統計分析に不可欠なデータを提供します。
-   **`StaticCodeAnalyzer`**: テストコードを解析し、フラッキーネスの一般的な原因となるパターン（例: `time.sleep`, `random`, グローバル状態へのアクセス）を特定します。
-   **`TestResult`**: 単一のテスト実行結果を表現するデータモデル。
-   **`analyze_test_stability`**: テスト結果のリストを受け取り、統計的な安定性指標を計算するヘルパー関数。
-   **`simulate_test_run`, `run_test_with_retries`**: テスト実行のシミュレーションと、リトライ戦略をデモンストレーションするためのヘルパー関数。

既存の`test_automation_engine.py`は、テストの実行と結果の収集を担当し、その結果を`TestHistoryManager`に記録します。その後、`FlakyTestDetector`がこの履歴データを使用してフラッキーテストを検出します。

## フラッキーテスト検出アルゴリズム

### 1. テスト実行履歴の統計分析

-   **成功率**: 過去N回の実行における失敗回数が、設定された閾値（`flaky_threshold_failure_rate`）を超える場合にフラッキー候補とします。例えば、「5回中2回以上失敗」など。
-   **実行時間の分散**: テストの実行時間が大きく変動する場合、外部要因（ネットワーク遅延、データベース負荷など）に依存している可能性があり、フラッキーの兆候とみなします。実行時間の標準偏差が平均実行時間の一定割合（`duration_variance_threshold`）を超えるかを評価します。
-   **エラーメッセージのパターン**: 繰り返し発生する特定のエラーメッセージがあれば、根本原因の特定に役立ちます。

### 2. 複数回実行による再現性確認

-   統計分析によりフラッキーテストの候補が特定された場合、そのテストを複数回（`rerun_confirmation_count`）再実行します。
-   再実行中に設定された回数（`rerun_failure_threshold`）以上の失敗が確認された場合、そのテストはフラッキーであると確定されます。

### 3. 静的コード解析（概念的統合）

-   `StaticCodeAnalyzer`は、テストコードをAST（Abstract Syntax Tree）として解析し、以下のパターンを検出します。
    -   **時刻依存**: `time.sleep`などの明示的な待機処理。不適切な`sleep`は、環境差や非同期処理のタイミングずれにより失敗を招く可能性があります。
    -   **乱数利用**: `random`モジュールの使用。テスト結果の非決定性を直接引き起こします。
    -   **並行処理/共有状態**: グローバル変数やクラス変数など、テスト間で共有される状態へのアクセスや変更。テストの実行順序によって結果が変わる「テスト間の依存関係」の兆候です。
-   この情報は、統計分析の結果を補強し、フラッキーネスの原因特定のヒントを提供します。

## 検出ロジックの詳細フローチャート

1.  **テストスイート実行**:
    *   `TestAutomationEngine`がテストスイートを実行。
    *   各テストの実行結果（成功/失敗、実行時間、エラーメッセージ）を`TestHistoryManager`がSQLiteデータベースに記録。
2.  **フラッキーテスト検出サイクルの開始**:
    *   `FlakyTestDetector.run_flaky_detection_cycle()`が呼び出される。
    *   `TestHistoryManager`から全てのユニークなテストIDを取得。
3.  **各テストの分析**:
    *   各テストIDに対し、`_determine_flakiness_candidate()`を実行。
        *   `TestHistoryManager.get_test_history()`で過去の実行履歴を取得。
        *   `analyze_test_stability()`で成功率、実行時間分散、共通エラーメッセージを計算。
        *   設定された閾値（`flaky_threshold_failure_rate`, `duration_variance_threshold`, `flaky_threshold_min_runs`）に基づいて、フラッキーテスト候補か判定。
        *   （オプションで）`StaticCodeAnalyzer`でテストコードを解析し、非決定的要素を検出。
    *   候補でなければ安定とみなし次へ。
4.  **再現性確認（再実行）**:
    *   フラッキー候補のテストに対し、`_confirm_flakiness_by_rerun()`を実行。
    *   テストを複数回（`rerun_confirmation_count`）再実行。
    *   再実行中に`rerun_failure_threshold`回以上の失敗があれば、フラッキーテストと確定。
    *   再実行結果も`TestHistoryManager`に記録。
5.  **修正戦略の提案**:
    *   確定されたフラッキーテストに対し、`suggest_remediation()`を呼び出し。
    *   検出された原因（高失敗率、高分散、静的解析の指摘など）に基づいて、具体的な修正案をリストアップ。
6.  **レポート生成**:
    *   検出されたフラッキーテストのリストと、それに対する修正計画を生成し、出力。

## テスト修正戦略の検討

検出されたフラッキーテストに対して、以下の戦略を適用または提案します。

-   **リトライメカニズムの追加**: 一時的なネットワーク問題やリソース競合による失敗の場合、`pytest-rerunfailures`のようなプラグインを活用し、テストを自動的にリトライする。`utils.py`の`run_test_with_retries`関数がそのデモンストレーション。
-   **適切な待機時間（`sleep`）の挿入**: UIテストなどで要素の描画待ちや非同期処理の完了待ちが不十分な場合、固定の`time.sleep`ではなく、条件が満たされるまで待機するスマートな待機（例: `WebDriverWait` for Selenium, `asyncio.sleep` for async operations）を導入。
-   **モックやスタブの活用による外部依存の排除**: データベース、外部API、メッセージキューなどの外部サービスへの依存を、モックやスタブに置き換えることで、テストをより高速かつ決定的にする。
-   **テスト順序の最適化/独立性の確保**: テストケースが互いに影響を与え合う状態（共有リソース、グローバル変数など）は、テストの実行順序によって結果が変わる原因となります。各テストが完全に独立して実行されるように、セットアップ/ティアダウンを徹底し、状態管理を改善します。
-   **並行処理の管理**: 並行テスト環境での競合状態が原因の場合、ロック機構の導入や、テストを独立したプロセスで実行するなどの対策を検討します。

## 実装計画の策定

### 1. 既存の`test_automation_engine.py`への統合方法

-   `FlakyTestDetector`クラスは、`TestAutomationEngine`内でインスタンス化されます。
-   `TestAutomationEngine`のテスト実行サイクル中に、各テストの実行結果は`TestHistoryManager`を通じてデータベースに記録されます。
-   テストスイートの実行完了後、または定期的なスケジュールで、`TestAutomationEngine`から`flaky_detector.run_flaky_detection_cycle()`が呼び出されます。
-   `run_flaky_detection_cycle`は、`pytest`のテストコレクションフェーズで得られるテストIDと、必要に応じてテスト関数の参照を受け取ります。これは`test_automation_engine.py`が`pytest`とどのように連携しているかに依存します。

### 2. データベーススキーマの設計（テスト実行履歴）

SQLite（またはGoogle Sheets）に記録するテスト実行履歴のスキーマは以下の通りです。

**テーブル名: `test_results`**

| カラム名        | データ型  | 制約                               | 説明                                   |
| :-------------- | :-------- | :--------------------------------- | :------------------------------------- |
| `test_id`       | `TEXT`    | `NOT NULL`                         | テストを一意に識別するID (例: `module.py::test_func`) |
| `passed`        | `INTEGER` | `NOT NULL` (0 or 1)                | テストが成功したかどうか (0=失敗, 1=成功) |
| `duration`      | `REAL`    | `NOT NULL`                         | テストの実行時間（秒）                 |
| `error_message` | `TEXT`    | `NULLABLE`                         | 失敗した場合のエラーメッセージ         |
| `timestamp`     | `TEXT`    | `NOT NULL` (ISO format string)     | テストが実行された日時 (UTC推奨)       |
| `attempt_count` | `INTEGER` | `NOT NULL`, `DEFAULT 1`            | リトライの場合の試行回数               |
| `PRIMARY KEY`   |           | `(test_id, timestamp)`             |                                        |

### 3. CI/CDパイプラインとの連携方法

-   **検出フェーズ**:
    -   CI/CDパイプラインのテスト実行ステージで、`TestAutomationEngine`がテスト実行と同時に履歴を記録します。
    -   テスト実行後、専用のステージまたはジョブとして`FlakyTestDetector`を起動し、フラッキーテスト検出を実行します。
    -   検出結果は、CI/CDツールのアーティファクトとして保存されるか、Slack/Teams通知、Jiraチケット作成などの形で開発チームに報告されます。
-   **レポートと可視化**:
    -   検出結果はHTMLレポートやダッシュボード（Grafana, Kibanaなど）に統合され、テストスイートの健康状態を視覚的に把握できるようにします。
-   **自動修正（将来的）**:
    -   特定かつ簡単な修正（例: `pytest-rerunfailures`の自動追加、適切な`sleep`値の提案）は、検出後に自動的にプルリクエストを作成するような仕組みも検討可能です（ただし、これは高度な自動化であり、設計フェーズでは提案に留める）。

## API仕様

### `FlakyTestDetector` クラス

-   `__init__(self, config_path: str = None)`: コンストラクタ。設定ファイルのパスを指定。
-   `run_flaky_detection_cycle(self, all_test_ids_to_check: List[str], test_function_map: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]`:
    -   全てのテストIDのリストと、テスト関数参照のマップを受け取り、フラッキーテスト検出サイクルを実行。
    -   検出されたフラッキーテストのリストと、修正戦略の提案リストを返す。

### `TestHistoryManager` クラス

-   `__init__(self, db_path: str = "test_history.db")`: コンストラクタ。SQLiteデータベースファイルのパスを指定。
-   `record_test_result(self, test_id: str, passed: bool, duration: float, error_message: Optional[str], attempt_count: int = 1)`:
    -   単一のテスト実行結果をデータベースに記録。
-   `get_test_history(self, test_id: str, limit: int = 100) -> List[TestResult]`:
    -   指定されたテストIDの過去の実行履歴を取得。
-   `get_all_test_ids(self) -> List[str]`:
    -   データベースに記録されている全てのユニークなテストIDを取得。

### `StaticCodeAnalyzer` クラス

-   `__init__(self)`: コンストラクタ。
-   `analyze_test_file(self, file_path: str) -> List[str]`:
    -   指定されたテストファイルのパスを解析し、検出されたフラッキーネスの潜在的な原因のリストを文字列で返す。

## 使用方法

### 1. 依存関係のインストール

```bash
pip install --upgrade pip
pip install # 必要なライブラリがあればここに記載 (例: pytest-rerunfailures など)
```
本設計のコードは標準ライブラリ (`sqlite3`, `time`, `random`, `statistics`, `logging`, `ast`, `datetime`, `json`) のみを使用しており、追加のpipインストールは不要です。

### 2. 設定ファイルの準備 (config.json)

```json
{
    "db_path": "flaky_test_data.db",
    "flaky_threshold_failure_rate": 0.25,
    "flaky_threshold_min_runs": 5,
    "rerun_confirmation_count": 5,
    "rerun_failure_threshold": 1,
    "duration_variance_threshold": 0.6,
    "static_analysis_enabled": true
}
```

### 3. フラッキーテスト検出の実行 (main.py)

`main.py`の`if __name__ == "__main__":`ブロックに記載されているサンプルコードを実行することで、システムの動作をデモンストレーションできます。

```bash
python main.py
```

このスクリプトは、テストスイートの実行をシミュレートし、履歴データをデータベースに蓄積します。その後、蓄積されたデータと静的解析に基づいてフラッキーテストを検出し、その結果と修正戦略をコンソールに出力します。

**出力例:**

```
--- Running test suites to build history ---
... (複数回のテスト実行シミュレーション) ...

--- Starting Flaky Test Detection Phase ---
Analyzing test: test_module_a.py::test_example_a
...
Analyzing test: test_module_c.py::test_flaky_case
Test 'test_module_c.py::test_flaky_case' is a flaky candidate: High failure rate (0.33 > 0.30).
Confirming flakiness for test_module_c.py::test_flaky_case by re-running 3 times.
...
Test 'test_module_c.py::test_flaky_case' confirmed as flaky: 1 failures in 3 re-runs.
Confirmed flaky test 'test_module_c.py::test_flaky_case'. Remediation plan generated.
--- Flaky Tests Detected ---
  Test ID: test_module_c.py::test_flaky_case
    Reason: High failure rate (0.33 > 0.30).
--- Remediation Plans ---
Test 'test_module_c.py::test_flaky_case' is identified as flaky due to: High failure rate (0.33 > 0.30).
--- Remediation Suggestions ---
- Investigate common error patterns: Look into the recurring error messages to find root causes.
  - Error: 'Simulated transient failure for test_module_c.py::test_flaky_case at 10:30:15' occurred 1 times.
- Add a retry mechanism: Implement `pytest-rerunfailures` or similar for transient failures.
--- End of Suggestions ---
--- Flaky Test Detection Phase Completed ---

--- Static Analysis Demonstration ---
Static analysis findings for 'mock_test_file.py': ["Function 'test_time_dependent' uses 'time.sleep' (potential for unstable waits).", "Function 'test_random_behavior' uses 'random' module (non-deterministic behavior).", "Function 'test_uses_shared_state_a' potentially accesses global/module-level state (risk of state leakage).", "Function 'test_uses_shared_state_b' potentially accesses global/module-level state (risk of state leakage)."]
```