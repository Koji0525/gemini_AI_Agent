# Flaky Test Detector for Test Automation Engine

## 概要

このプロジェクトは、テスト自動化エンジン（`agents/efficiency/test_automation_engine.py`）に組み込むことを目的とした、フラッキーテスト（結果が不安定なテスト）を自動的に検出し、修正戦略を提案するためのロジックを設計・実装します。テストスイートの信頼性を向上させ、誤検出による開発効率の低下を防ぐことが主な目的です。

フラッキーテストは、同じコードベースと同じテスト環境で実行しても、結果が「成功」と「失敗」の間でランダムに変動するテストを指します。これにより、開発者はCI/CDパイプラインでのテスト失敗に混乱し、信頼性の低いテストスイートは開発サイクルを遅延させ、生産性を低下させます。本システムは、このようなフラッキーテストを効果的に特定し、その原因と対策を提示することで、開発チームがテスト品質を向上させる手助けをします。

## フラッキーテストの主な原因

フラッキーテストの一般的な原因には以下のようなものがあります。

1.  **非決定性要素**:
    *   **時間依存**: `sleep`の不足、タイムアウトの競合、システム時刻への依存。
    *   **並行処理/競合状態**: スレッドやプロセスの同期不足、共有リソースへのアクセス競合。
    *   **乱数**: テストデータ生成に予測不可能な乱数を使用。
2.  **外部依存**:
    *   **データベース**: テスト間のデータ依存性、トランザクション管理の不備。
    *   **ネットワーク/API**: 外部サービスの可用性、応答時間の変動、ネットワーク遅延。
    *   **ファイルシステム**: 一時ファイルのクリーンアップ不足、競合アクセス。
3.  **テスト環境の変動**:
    *   テスト実行順序への依存。
    *   テスト環境のOS、メモリ、CPUリソースの変動。
    *   キャッシュや状態の残留。

## 検出アプローチ

本システムでは、以下の複数のアプローチを組み合わせてフラッキーテストを検出します。

1.  **テスト実行履歴の統計分析**:
    *   過去のテスト実行結果（成功/失敗、実行時間）をデータベースに記録します。
    *   特定のテストIDに対して、過去N回分の実行履歴を分析し、成功率、失敗率、平均実行時間、実行時間の標準偏差を算出します。
    *   失敗率が設定された閾値（例: 過去10回中2回以上失敗）を超過する場合、フラッキーテストと判定します。
2.  **テストの複数回実行による再現性確認**:
    *   疑わしいテスト、またはテストスイート全体を短期間に複数回（例: 5回）実行します。
    *   複数回実行中に、特定のテストが設定された閾値（例: 5回中2回以上失敗）の頻度で失敗した場合、フラッキーテストと判定します。このアプローチは、一時的な競合状態や時間依存性を顕在化させるのに有効です。

## 修正戦略の検討と提案

フラッキーテストと検出された場合、以下の修正戦略を提案します。これらの提案は、開発者がフラッキーテストの根本原因を特定し、修正する手助けをすることを目的としています。一部の戦略はCI/CDパイプラインとの連携により自動適用が可能です。

1.  **リトライメカニズムの追加**:
    *   pytest-rerunfailuresのようなプラグインを活用し、テストが失敗した場合に自動的に数回再実行を試みます。これにより、一時的な環境要因による失敗を許容し、CI/CDの誤検出を減らします。
    *   提案内容: `--reruns=N --reruns-delay=M` オプションの追加。
2.  **適切な待機時間（sleep）の挿入**:
    *   非同期処理やUIテストにおいて、要素のロードや処理完了を待つための適切な待機処理（`WebDriverWait`、ポーリング機構など）の導入を推奨します。固定の`time.sleep()`は、過度な遅延を引き起こす可能性があるため、最後の手段としてのみ検討されます。
3.  **モックやスタブの活用による外部依存の排除**:
    *   データベース、外部API、ファイルシステムなどの外部依存をモック化またはスタブ化することで、テストを外部要因から隔離し、決定性を高めます。`unittest.mock`などのライブラリを活用します。
4.  **テスト順序依存性の調査と解消**:
    *   テストが他のテストの実行順序に依存して失敗する場合、その依存関係を特定し、各テストが独立して実行できるようにリファクタリングすることを推奨します。`pytest-randomly`のようなツールでテスト順序をシャッフルし、依存性を検出するアプローチも有効です。
5.  **環境分離**:
    *   テスト実行環境をDockerコンテナなどで完全に分離し、テストごとにクリーンな状態を保証することで、環境起因のフラッキーネスを排除します。

## システムアーキテクチャ

本システムは、既存のテスト自動化エンジン（`agents/efficiency/test_automation_engine.py`）への統合を想定しており、以下の主要コンポーネントで構成されます。

1.  **`FlakkyTestDetector` (main.py)**:
    *   フラッキーテスト検出のメインロジックを実装します。
    *   pytestコマンドの実行、結果のパース、`TestHistoryManager`への記録、検出アルゴリズムの実行、修正戦略の提案を担当します。
2.  **`TestHistoryManager` (utils.py)**:
    *   テスト実行履歴（`test_runs`テーブル）とフラッキーテスト情報（`flaky_tests`テーブル）をSQLiteデータベースに保存・管理します。
    *   テスト結果の保存、履歴の取得、フラッキーテスト情報の更新などのDB操作を提供します。
3.  **`utils.py` のその他のヘルパー関数**:
    *   テスト履歴から安定性指標を計算する関数 (`analyze_test_stability`)。
    *   pytestのリトライオプションを生成する関数 (`generate_pytest_rerun_options`)。
    *   待機時間挿入の提案を生成する関数 (`generate_sleep_suggestion`)。
4.  **`TestAutomationEngineIntegration` (main.py)**:
    *   既存の`test_automation_engine.py`との連携をシミュレートするクラスです。テストの実行、結果の記録、検出、修正提案といった一連のフローを統合します。

### データベーススキーマ

テスト実行履歴はSQLiteに記録されます。

#### `test_runs` テーブル

各テスト実行の詳細を記録します。

| カラム名            | データ型        | 制約                      | 説明                                         |
| :------------------ | :-------------- | :------------------------ | :------------------------------------------- |
| `id`                | INTEGER         | PRIMARY KEY AUTOINCREMENT | 一意の実行ID                                 |
| `test_id`           | TEXT            | NOT NULL                  | テストのユニークID (例: `module.class::method`) |
| `timestamp`         | DATETIME        | NOT NULL                  | 実行日時 (ISO形式文字列)                     |
| `result`            | TEXT            | NOT NULL                  | 'passed' または 'failed'                     |
| `duration`          | REAL            |                           | 実行時間 (秒)                                |
| `details`           | TEXT            |                           | 失敗時のエラーメッセージなど                 |

#### `flaky_tests` テーブル

フラッキーと判定されたテストの情報を記録します。

| カラム名              | データ型        | 制約                      | 説明                                         |
| :-------------------- | :-------------- | :------------------------ | :------------------------------------------- |
| `id`                  | INTEGER         | PRIMARY KEY AUTOINCREMENT | 一意のフラッキーテストID                     |
| `test_id`             | TEXT            | NOT NULL UNIQUE           | フラッキーと判定されたテストのID             |
| `detection_timestamp` | DATETIME        | NOT NULL                  | 最初にフラッキーと検出された日時             |
| `reason`              | TEXT            |                           | フラッキーと判定された理由                   |
| `status`              | TEXT            | NOT NULL                  | 'detected', 'investigating', 'fixed' などの状態 |
| `last_updated`        | DATETIME        | NOT NULL                  | 最終更新日時                                 |
| `fix_suggestion`      | TEXT            |                           | 適用された、または提案されている修正策 (JSON形式) |

## インストール

本プロジェクトをセットアップするには、Pythonと以下のパッケージが必要です。

```bash
# Python 3.8+ が必要です
python --version

# 仮想環境の作成とアクティベートを推奨
python -m venv venv
source venv/bin/activate # macOS/Linux
# venv\Scripts\activate # Windows

# 必要なPythonパッケージのインストール
pip install pytest pytest-json-report # pytest-json-reportはJSON形式のレポート出力に必要です
```

## 使用方法

### 1. `FlakkyTestDetector` の初期化

```python
from main import FlakkyTestDetector

# デフォルト設定でDetectorを初期化
detector = FlakkyTestDetector(db_path='my_test_history.db')

# カスタム設定を使用する場合
custom_config = {
    "history_based_min_runs": 15,
    "history_based_failure_threshold": 0.15,
    "rerun_based_num_reruns": 7,
    "rerun_based_failure_threshold": 0.3,
    "pytest_path": "/usr/local/bin/pytest" # 特定のpytest実行パス
}
detector_with_config = FlakkyTestDetector(db_path='my_custom_history.db', config=custom_config)
```

### 2. テストの実行と結果の記録

テスト自動化エンジンがテストを実行した後、その結果を `FlakkyTestDetector` に記録します。
`_execute_pytest_command` は内部ヘルパーですが、既存エンジンが生成した結果を`record_test_run_results`に渡すことを想定しています。

```python
# 例: テストスイート全体を実行し、結果を記録
# このメソッドはpytestを実行し、その結果をDBに自動的に記録します
test_results = detector._execute_pytest_command("./tests/my_suite.py")
# detector.record_test_run_results(test_results) # _execute_pytest_command 内部で記録されます
```

### 3. フラッキーテストの検出

記録された履歴データや複数回実行アプローチに基づいてフラッキーテストを検出します。

```python
# 履歴ベースの検出
flaky_tests_history = detector.detect_flaky_tests_history_based()
print(f"Detected {len(flaky_tests_history)} flaky tests based on history.")

# 複数回実行ベースの検出 (特定のテストファイルまたはスイートに対して)
flaky_tests_rerun = detector.detect_flaky_tests_rerun_based("./tests/my_suite.py")
print(f"Detected {len(flaky_tests_rerun)} flaky tests based on reruns.")
```

### 4. 修正戦略の提案と適用

検出されたフラッキーテストに対して修正戦略を提案し、一部を自動適用します。

```python
# 例: 特定のフラッキーテストIDに対する修正戦略を提案
flaky_test_id = "path/to/my_test_file.py::test_flaky_method"
proposals = detector.propose_fix_strategies(flaky_test_id)

print(f"Proposals for {flaky_test_id}:")
for p in proposals['proposals']:
    print(f"- Type: {p['type']}, Description: {p['description']}")

# 例: 提案された修正戦略の一部を適用（この実装ではログ出力が主）
detector.apply_suggested_fix(flaky_test_id, "retry_mechanism")
```

### 5. フラッキーテストのステータス取得

現在トラッキングされているフラッキーテストの状態を取得します。

```python
current_flaky_status = detector.get_flaky_tests_status()
for status in current_flaky_status:
    print(f"Test: {status['test_id']}, Status: {status['status']}, Reason: {status['reason']}")
```

### 6. `TestAutomationEngineIntegration` を使用したエンドツーエンドの実行

`main.py` の `if __name__ == "__main__":` ブロックに示されているように、`TestAutomationEngineIntegration` クラスを使用して、テスト実行から検出、修正提案までのフロー全体をシミュレートできます。

```python
from main import FlakkyTestDetector, TestAutomationEngineIntegration
import os

# デモ用テストファイルを作成
# ... (main.py の if __name__ == "__main__": 内のコードを参照)

detector = FlakkyTestDetector(db_path='flaky_test_db.sqlite')
engine_integration = TestAutomationEngineIntegration(detector, test_suite_path="./tests/test_flaky_suite.py")
engine_integration.run_daily_test_suite()
```

## API仕様

### `class FlakkyTestDetector` (main.py)

*   `__init__(self, db_path: str = 'test_history.db', config: Optional[Dict[str, Any]] = None)`
    *   コンストラクタ。データベースパスと設定を受け取ります。
*   `_execute_pytest_command(self, test_path: str, options: Optional[List[str]] = None) -> Dict[str, Any]`
    *   pytestコマンドを実行し、JSONレポートをパースして結果を返します。（内部メソッド）
*   `record_test_run_results(self, test_run_data: Dict[str, Any])`
    *   `_execute_pytest_command` から返されたテスト実行結果をDBに記録します。
*   `detect_flaky_tests_history_based(self) -> List[Dict[str, Any]]`
    *   テスト実行履歴に基づいてフラッキーテストを検出します。
*   `detect_flaky_tests_rerun_based(self, test_path: str = None) -> List[Dict[str, Any]]`
    *   特定のテストまたはスイートを複数回実行し、フラッキーテストを検出します。
*   `propose_fix_strategies(self, flaky_test_id: str) -> Dict[str, Any]`
    *   フラッキーテストに対する修正戦略のリストを提案します。
*   `apply_suggested_fix(self, flaky_test_id: str, strategy_type: str, test_file_path: Optional[str] = None) -> bool`
    *   提案された修正戦略を（推奨として）適用します。
*   `get_flaky_tests_status(self) -> List[Dict[str, Any]]`
    *   現在トラッキングされているフラッキーテストのステータスを取得します。

### `class TestHistoryManager` (utils.py)

*   `__init__(self, db_path: str = 'test_history.db')`
    *   コンストラクタ。データベースパスを受け取ります。
*   `save_test_run(self, test_id: str, result: str, duration: float, timestamp: Optional[datetime.datetime] = None, details: Optional[str] = None)`
    *   単一のテスト実行結果をDBに保存します。
*   `get_test_history(self, test_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]`
    *   特定のテストIDの実行履歴を取得します。
*   `get_all_test_ids(self) -> List[str]`
    *   DBに記録されている全てのユニークなテストIDを取得します。
*   `save_flaky_test(self, test_id: str, reason: str, status: str = 'detected', fix_suggestion: Optional[Dict[str, Any]] = None)`
    *   フラッキーテストの情報をDBに保存または更新します。
*   `mark_flaky_test_status(self, test_id: str, status: str, reason: str = "")`
    *   フラッキーテストのステータスを更新します。
*   `get_flaky_tests_status(self) -> List[Dict[str, Any]]`
    *   DBに記録されている全てのフラッキーテストのステータスを取得します。

### `utils.py` のヘルパー関数

*   `analyze_test_stability(history: List[Dict[str, Any]]) -> Dict[str, Any]`
    *   テスト履歴から安定性指標を計算します。
*   `generate_pytest_rerun_options(num_reruns: int = 3, reruns_delay: int = 0) -> List[str]`
    *   `pytest-rerunfailures` プラグイン用のコマンドラインオプションを生成します。
*   `generate_sleep_suggestion(test_id: str) -> Dict[str, str]`
    *   テストコードへの待機時間挿入に関する提案を生成します。

## CI/CDパイプラインとの連携方法

本Flaky Test Detectorは、既存のCI/CDパイプラインにシームレスに統合されるように設計されています。

1.  **テスト実行フェーズ**:
    *   CI/CDパイプラインがテストを実行する際、`FlakkyTestDetector` を利用して各テストの実行結果を記録します。具体的には、CI/CDスクリプト内で`FlakkyTestDetector`を初期化し、`_execute_pytest_command`を呼び出してテストを実行させ、その結果を`record_test_run_results`に渡します。
2.  **フラッキーテスト検出フェーズ**:
    *   テストスイート全体の実行後、または定期的なCI/CDジョブとして、`detector.detect_flaky_tests_history_based()` と `detector.detect_flaky_tests_rerun_based()` を実行します。
    *   検出されたフラッキーテストは内部データベースに記録され、これによりフラッキーテストの傾向や状態を追跡できます。
3.  **レポートと通知フェーズ**:
    *   検出されたフラッキーテストの情報は、CI/CDの実行結果レポートに含められます。
    *   検出されたテストに対して、`detector.propose_fix_strategies()` を実行し、その結果を開発者へ通知（Slack、Jiraなどの連携ツール経由）します。
4.  **自動修正提案・適用フェーズ**:
    *   CI/CDパイプラインは、自動適用が可能な修正（例: `pytest-rerunfailures` の設定変更）について、`detector.apply_suggested_fix()` メソッドからの推奨事項を基に、自動的に設定ファイルを更新したり、開発者へのプルリクエストを生成したりすることを検討できます。これにより、手動での介入を最小限に抑えつつ、テスト品質を向上させることが可能になります。
5.  **ダッシュボード連携**:
    *   データベースに蓄積されたフラッキーテストの履歴とステータスは、Grafanaや自作のダッシュボードツールと連携させることで、テストスイート全体の健全性やフラッキーテストの長期的な傾向を可視化できます。

## 貢献

本プロジェクトへの貢献を歓迎します。バグ報告、機能提案、コードの改善など、お気軽にお寄せください。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細についてはLICENSEファイルを参照してください。