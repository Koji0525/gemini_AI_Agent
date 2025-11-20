# 24時間自律稼働システム 統合テストスイート

## 概要

このプロジェクトは、24時間自律稼働システム (Autonomous System) の主要な10機能 (F1-F10) が正しく連携し、期待通りに動作することを保証するための統合テストスイートです。
システムの安定稼働と信頼性維持を目的としており、以下の主要な側面をカバーします。

-   **機能テスト**: F1 (ゴール分解) から F10 (健全性チェック) までの各機能の存在、初期化、および基本動作の確認。
-   **連携テスト**: ナレッジシステム (F4) と Google Sheets 連携といった外部システムとのインタラクションの確認。
-   **レポーティング**: テスト実行結果の詳細なJSONレポートを生成し、システムの状態を一目で把握できるようにします。

このスイートは、`unittest`フレームワークを利用して構築されており、既存のテストファイル (`tests/system_protection/test_core_functions.py` など) を動的にロードして実行します。テスト結果は、成功率、機能ごとのステータス、および詳細なテスト結果を含む統合レポートとして出力されます。

## 主要機能 (F1-F10)

自律稼働システムを構成する主要な機能群です。

-   **F1: ゴール分解 (Goal Decomposition)**: 高レベルな目標を達成可能なサブゴールやタスクに分解する機能。
-   **F2: 計画策定 (Planning)**: 分解されたゴールに基づき、具体的な実行計画を生成する機能。
-   **F3: 実行管理 (Execution Management)**: 策定された計画に従い、タスクの実行を管理し、進行状況を追跡する機能。
-   **F4: ナレッジシステム (Knowledge System)**: システムが学習した知識、設定、履歴などを保存・管理し、必要に応じて参照する機能。
-   **F5: モニタリング (Monitoring)**: システムの内部状態、外部環境、タスク実行状況などを継続的に監視する機能。
-   **F6: 異常検知 (Anomaly Detection)**: モニタリングデータから異常なパターンや予期せぬ挙動を検知する機能。
-   **F7: 自己回復 (Self-Healing)**: 異常が検知された際に、自動的に問題を診断し、修正または回復措置を講じる機能。
-   **F8: 学習・適応 (Learning and Adaptation)**: 過去の経験やフィードバックに基づき、システムの振る舞いやパフォーマンスを改善するために学習し、適応する機能。
-   **F9: 人間との協調 (Human Collaboration)**: 人間オペレーターとの効率的な情報交換、意思決定支援、およびタスク連携を可能にする機能。
-   **F10: 健全性チェック (Health Check)**: システム全体の健全性を定期的にチェックし、潜在的な問題を早期に特定する機能。

## インストール

このテストスイートはPython 3.8以降で動作します。追加のライブラリは`unittest`が標準ライブラリであるため、基本的に不要です。

1.  **Pythonのインストール**:
    お使いのシステムにPython 3.8以上がインストールされていることを確認してください。

2.  **プロジェクトのクローン**:
    ```bash
    git clone <リポジトリURL>
    cd <プロジェクトディレクトリ>
    ```

3.  **依存関係**:
    特にありません。必要であれば`requirements.txt`を作成し、`pip install -r requirements.txt`でインストールします。

## 設定 (`config.json`)

テストランナーは、`config.json`ファイルから設定を読み込みます。このファイルをプロジェクトのルートディレクトリに配置してください。

**`config.json`の例**:

```json
{
    "log_settings": {
        "log_file": "integration_test.log",
        "log_level": "INFO"
    },
    "test_settings": {
        "test_suite_path": "tests/system_protection",
        "report_output_dir": "reports"
    },
    "google_sheets": {
        "test_sheet_id": "YOUR_TEST_SHEET_ID_HERE",
        "api_key_path": "path/to/your/google_sheets_api_key.json"
    }
}
```

-   `log_settings.log_file`: ログファイルの名前。
-   `log_settings.log_level`: ロギングレベル (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)。
-   `test_settings.test_suite_path`: テストケースが配置されているディレクトリ、または単一のテストファイルのパス。デフォルトは `tests/system_protection`。
-   `test_settings.report_output_dir`: 生成されるレポートファイルの出力先ディレクトリ。
-   `google_sheets.test_sheet_id`: Google Sheets連携テストで使用するテスト用のシートID。モックのため、実際には使用されませんが、設定ファイルに含めることを推奨します。
-   `google_sheets.api_key_path`: Google Sheets APIキーのパス (モックでは使用されません)。

## 使用方法

### 1. テストファイルの準備

`config.json`で指定した`test_suite_path` (デフォルト: `tests/system_protection`) ディレクトリ内に、`unittest.TestCase`を継承したテストファイル (`test_*.py`の命名規則推奨) を作成します。

**`tests/system_protection/test_core_functions.py` の例**:

```python
import unittest
import time

class TestF1GoalDecomposition(unittest.TestCase):
    """F1: ゴール分解機能のテスト"""
    def setUp(self):
        # 各テストメソッド実行前に初期化処理
        pass

    def test_f1_initialization(self):
        """F1機能の初期化が正常に行われることを確認"""
        print("Executing F1 initialization test...")
        self.assertTrue(True, "F1 初期化が成功しました")

    def test_f1_basic_decomposition(self):
        """F1機能が基本的なゴール分解を実行できることを確認"""
        print("Executing F1 basic decomposition test...")
        # 実際にはここでゴール分解ロジックを呼び出し、結果をアサート
        self.assertIsNotNone("sub_goal_list", "サブゴールリストが生成されました")
        time.sleep(0.1) # 処理時間のシミュレーション

class TestF4KnowledgeSystemCore(unittest.TestCase):
    """F4: ナレッジシステム機能のコアテスト"""
    def test_f4_initialization(self):
        """F4機能の初期化が正常に行われることを確認"""
        print("Executing F4 initialization test...")
        self.assertTrue(True, "F4 初期化が成功しました")

    def test_f4_data_consistency(self):
        """F4機能がデータの一貫性を維持できることを確認"""
        print("Executing F4 data consistency test...")
        # 実際にはMockKnowledgeSystemなどを使用して、データのCRUD操作と整合性をテスト
        self.assertEqual("read_data", "expected_data", "データの一貫性が保たれています")

class TestF10HealthCheck(unittest.TestCase):
    """F10: 健全性チェック機能のテスト"""
    def test_f10_system_heartbeat(self):
        """F10機能がシステムハートビートを正常に報告できることを確認"""
        print("Executing F10 system heartbeat test...")
        self.assertTrue(True, "システムハートビートが正常です")

    # F2, F3, F5-F9 のテストも同様に追加してください
```

### 2. テストの実行

プロジェクトのルートディレクトリで以下のコマンドを実行します。

```bash
python main.py
```

実行後、`reports`ディレクトリにタイムスタンプ付きのJSON形式のテスト結果レポートが生成されます。
また、コンソールと`integration_test.log`ファイルに実行ログが出力されます。

## API仕様

### `IntegrationTestRunner` クラス

`main.py` にて定義される、統合テストを実行するための主要なクラスです。

#### `__init__(self, test_suite_path: str, config: dict, report_dir: str = "reports")`

-   **説明**: `IntegrationTestRunner` のコンストラクタ。
-   **引数**:
    -   `test_suite_path` (str): テストケースを含むディレクトリまたはファイルのパス。
    -   `config` (dict): システム設定を含む辞書。`utils.load_config()` でロードされた設定オブジェクト。
    -   `report_dir` (str): テスト結果レポートを保存するディレクトリ。デフォルトは `"reports"`。
-   **例外**:
    -   `FileNotFoundError`: `test_suite_path` が存在しない場合。

#### `run_all_tests(self) -> bool`

-   **説明**: 全ての統合テストを実行し、テストの発見、実行、ナレッジシステム/Google Sheets連携の確認、レポート生成、成功基準の評価までの一連のプロセスを実行します。
-   **戻り値**: 全ての成功基準を満たした場合は `True`、それ以外は `False`。
-   **内部処理**:
    -   `_discover_tests()`: `unittest` を使用してテストケースを発見。
    -   `_execute_tests()`: 発見されたテストケースを実行。
    -   `_test_knowledge_system()`: ナレッジシステム (F4) の読み書きテスト。
    -   `_test_google_sheets_integration()`: Google Sheets 連携の動作確認。
    -   `_generate_report()`: テスト結果をJSON形式でレポート出力。
    -   `_evaluate_success_criteria()`: 定義された成功基準を評価。

## テスト結果レポートの構造

生成されるJSONレポートファイルは以下の構造を持ちます。

```json
{
    "summary": {
        "total_tests": 10,
        "ran": 8,
        "failures": 1,
        "errors": 0,
        "skipped": 1,
        "success_rate": 87.5,
        "knowledge_system_test_status": "PASSED",
        "google_sheets_integration_status": "PASSED",
        "start_time": "2023-10-27T10:30:00.000000",
        "end_time": "2023-10-27T10:30:15.500000",
        "duration_seconds": 15.5
    },
    "detailed_results": [
        {
            "test_id": "TestF1GoalDecomposition.test_f1_initialization",
            "status": "PASSED",
            "message": "F1 初期化が成功しました",
            "type": "FUNCTIONAL_TEST"
        },
        {
            "test_id": "TestF1GoalDecomposition.test_f1_basic_decomposition",
            "status": "FAILED",
            "message": "AssertionError: サブゴールリストが生成されました",
            "type": "FUNCTIONAL_TEST"
        },
        {
            "test_id": "knowledge_system_read_write_test",
            "status": "PASSED",
            "message": "F4ナレッジシステムの読み書きが正常に動作しました。",
            "type": "INTEGRATION_TEST"
        },
        {
            "test_id": "google_sheets_integration_test",
            "status": "PASSED",
            "message": "Google Sheets連携が正常に動作しました。",
            "type": "INTEGRATION_TEST"
        }
    ],
    "function_status": {
        "F1": "FAILED",
        "F2": "PASSED",
        "F3": "NOT_TESTED",
        "F4": "PASSED",
        "F5": "PASSED",
        "F6": "SKIPPED",
        "F7": "PASSED",
        "F8": "PASSED",
        "F9": "PASSED",
        "F10": "PASSED"
    },
    "test_runner_output": "...", # unittest.TextTestRunnerのコンソール出力全体
    "error_message": null # 発生した場合のみ
}
```

## 成功基準

統合テストの成功は、以下の基準を満たすことで判断されます。

-   **全テストで85%以上の成功率を達成**: 実行された全てのテストケース（機能テスト、ナレッジシステム、Google Sheets連携）において、成功したテストの割合が85%以上であること。
-   **F1-F10の全機能が正常に初期化される**: 各機能（F1からF10）に対応するテストが実行され、その初期化または基本動作テストが全て成功すること。レポートの `function_status` フィールドで確認されます。
-   **ナレッジシステムが正常に動作する**: F4ナレッジシステムに対する読み書きテストが成功すること。レポートの `summary.knowledge_system_test_status` フィールドで確認されます。
-   **テスト結果レポートが生成される**: テスト実行後に、JSON形式の統合テスト結果レポートファイルが指定されたディレクトリに生成されること。

---

**タスクID**: 7_統合テスト実行_221738_01
**タスク説明**: F1-F10の統合テストを実行し、全機能が正常に動作することを確認する。【目的】24時間自律稼働システムの全機能が正しく連携し、期待通りに動作することを保証する。【作業内容】1. tests/system_protection/test_core_functions.pyを実行2. F1（ゴール分解）からF10（健全性チェック）まで全機能をテスト3. 各機能の存在確認、初期化確認、基本動作確認を実施4. ナレッジシステム（F4）の読み書きテスト5. Google Sheets連携の動作確認【成功基準】・全テストで85%以上の成功率を達成・F1-F10の全機能が正常に初期化される・ナレッジシステムが正常に動作する・テスト結果レポートが生成される【コンテキスト】システム保護テストスイートを使用。各機能の最新実装状態を反映。