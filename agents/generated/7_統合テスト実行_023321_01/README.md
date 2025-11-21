# 24H Autonomous Agent System Integration Test Suite

## 概要

本プロジェクトは、24時間自律稼働システム (`24H Autonomous Agent System`) のF1-F10のコア機能が正しく連携し、期待通りに動作することを保証するための統合テストスイートです。このシステムは、ゴール分解から健全性チェックまで、多岐にわたる機能を持ち、それぞれが密接に連携することで自律的な運用を実現します。

このテストスイートは、システムの稼働前に全ての主要コンポーネントが正常に初期化され、基本的な動作を実行できることを確認します。また、ナレッジシステム（F4）のデータ永続性や、Google Sheetsなどの外部サービス連携（F7）の信頼性についても検証します。

### 目的
- 24時間自律稼働システムの全機能が正しく連携し、期待通りに動作することを保証する。
- システムの安定性と信頼性を高め、潜在的な問題を早期に特定する。

### 対象機能 (F1-F10)
システムは以下の主要機能から構成されます。
- **F1: ゴール分解 (Goal Decomposition)**: 高レベルな目標を、実行可能な小さなタスクに分解する機能。
- **F2: プランニングモジュール (Planning Module)**: 分解されたタスクを実行するための最適な計画を立案する機能。
- **F3: アクション実行エンジン (Action Execution Engine)**: 計画に基づき、実際のアクションを実行する機能。
- **F4: ナレッジシステム (Knowledge System)**: システムの知識ベースを管理し、情報の読み書きを行う機能。
- **F5: 自己監視エージェント (Self-Monitoring Agent)**: システム自身の状態、パフォーマンス、健全性をリアルタイムで監視する機能。
- **F6: 適応学習コンポーネント (Adaptive Learning Component)**: 過去の経験や監視結果に基づき、システムの動作を最適化し学習する機能。
- **F7: 外部サービス連携 (External Service Integration)**: Google Sheetsなどの外部APIやサービスとの連携を管理する機能。
- **F8: リソース管理 (Resource Management)**: コンピューティングリソース、メモリ、ストレージなどを効率的に管理する機能。
- **F9: ユーザーインターフェースレイヤー (User Interface Layer)**: ユーザーがシステムと対話するためのインターフェースを提供する機能。
- **F10: システム健全性チェック (System Health Check)**: システム全体の健全性を定期的に診断し、異常を報告する機能。

### コンテキスト
本テストスイートは、システムの各機能の最新実装状態を反映するように設計されており、システム保護テストスイートの一部として位置づけられます。実際のシステム構成を模倣したシミュレーションを通じて、機能間の連携を確認します。

## インストール

1.  **リポジトリのクローン:**
    ```bash
    git clone <repository_url>
    cd 24h-autonomous-system-integration-tests
    ```

2.  **Python環境のセットアップ:**
    Python 3.8以上のバージョンを推奨します。仮想環境の利用を強く推奨します。
    ```bash
    python -m venv venv
    source venv/bin/activate  # macOS/Linux
    # venv\Scripts\activate  # Windows
    ```

3.  **依存関係のインストール:**
    本プロジェクトは標準ライブラリのみを使用しており、追加の依存関係は`pip install`でインストールする必要はありません。将来的に`pytest`などのテストフレームワークを導入する場合は、`requirements.txt`に追記しインストールしてください。

## 使用方法

### テストの実行

統合テストを実行するには、`main.py`スクリプトを実行します。

```bash
python main.py
```

スクリプトは以下のステップを実行します。
1.  F1からF10までの各機能について、初期化確認と基本動作確認をシミュレートします。
2.  ナレッジシステム（F4）の読み書きテストを行います。
3.  Google Sheets連携（F7）の動作確認をシミュレートします。
4.  全てのテスト結果を集計し、詳細なレポートを`test_reports/`ディレクトリに生成します。

### 設定ファイル

`config/system_config.json`ファイルを作成することで、テストランナーの挙動をカスタマイズできます。ファイルが存在しない場合、システムはデフォルト設定を使用します。

**`config/system_config.json`の例:**
```json
{
    "system_name": "My Custom Autonomous Agent",
    "features": {
        "F1_Goal_Decomposition": "ゴール分解 (カスタム名)",
        "F2_Planning_Module": "計画モジュール (カスタム名)"
    },
    "overall_success_threshold": 0.90,
    "knowledge_system_path": "custom_data/knowledge.txt",
    "google_sheets_api_endpoint": "https://custom.googlesheets.api/v2/sheets",
    "log_dir": "my_test_logs"
}
```

## 成功基準

統合テストの成功は、以下の基準に基づいて判断されます。

-   **全テストで85%以上の成功率を達成:** `overall_success_threshold`で設定された割合（デフォルト85%）。
-   **F1-F10の全機能が正常に初期化される:** 各機能の初期化テストが成功すること。
-   **ナレッジシステムが正常に動作する:** ナレッジシステムの読み書きテストが成功すること。
-   **テスト結果レポートが生成される:** `test_reports/`ディレクトリに詳細なレポートファイルが作成されること。

テスト実行後、コンソール出力と生成されたレポートファイルを確認し、成功基準が満たされているか検証してください。レポートファイルには、各テストケースの詳細な結果、ステータス、実行時間、およびメッセージが含まれます。

## API仕様

### `main.py`

#### `class IntegrationTestRunner`
システムの統合テストをオーケストレーションするメインクラス。

##### `__init__(self, config_path: str = None)`
-   **引数**:
    -   `config_path` (str, オプション): カスタム設定ファイルへのパス。指定しない場合、デフォルト設定を使用。
-   **説明**: テストランナーを初期化し、システム設定、テスト対象機能リスト、成功閾値などを設定します。

##### `run_all_tests(self) -> Dict[str, Any]`
-   **引数**: なし
-   **戻り値**:
    -   `Dict[str, Any]`: テスト実行のサマリー（成功数、失敗数、成功率、全体ステータスなど）を含む辞書。
-   **説明**: F1-F10の全ての統合テストを実行します。これには、機能の初期化、基本動作、ナレッジシステムI/O、Google Sheets連携のテストが含まれます。テスト完了後、`generate_report`を呼び出してレポートを生成し、そのサマリーを返します。

##### `generate_report(self) -> Dict[str, Any]`
-   **引数**: なし
-   **戻り値**:
    -   `Dict[str, Any]`: テスト実行の最終サマリーと、生成されたレポートファイルのパスを含む辞書。
-   **説明**: 実行された全てのテスト結果に基づいて、詳細なレポートを生成し、指定されたログディレクトリにファイルとして保存します。コンソールにも主要なサマリーを出力します。

### `utils.py`

#### `class TestResult`
個々のテストケースの結果を保持するためのデータ構造。

##### `__init__(self, name: str, description: str, success: bool, message: str = "", status: str = "UNKNOWN", duration: float = 0.0)`
-   **引数**:
    -   `name` (str): テストケースの名前。
    -   `description` (str): テストケースの簡潔な説明。
    -   `success` (bool): テストが成功したかどうか。
    -   `message` (str, オプション): テスト結果に関する詳細メッセージ。
    -   `status` (str, オプション): テストのステータス ("SUCCESS", "FAILURE", "ERROR"など)。
    -   `duration` (float, オプション): テストの実行時間（秒）。

#### `class TestReporter`
複数の`TestResult`オブジェクトからテストレポートを生成するためのユーティリティクラス。

##### `__init__(self, results: List[TestResult])`
-   **引数**:
    -   `results` (List[TestResult]): 報告する`TestResult`オブジェクトのリスト。

##### `get_summary(self) -> Dict[str, Any]`
-   **引数**: なし
-   **戻り値**:
    -   `Dict[str, Any]`: テストの合計数、成功数、失敗数、成功率などを含むサマリー辞書。

##### `generate_full_report(self) -> str`
-   **引数**: なし
-   **戻り値**:
    -   `str`: 詳細なテスト結果を含む整形されたレポート文字列。

#### `load_system_config(config_path: str = "config/system_config.json") -> Dict[str, Any]`
-   **引数**:
    -   `config_path` (str, オプション): 設定ファイルへのパス。
-   **戻り値**:
    -   `Dict[str, Any]`: ロードされたシステム設定。ファイルが見つからないかエラーが発生した場合、デフォルト設定を返します。
-   **説明**: 指定されたパスからJSON形式のシステム設定を読み込みます。

#### `simulate_external_api_call(api_endpoint: str, method: str = "GET", payload: Dict[str, Any] = None, success_rate: float = 0.9) -> Dict[str, Any]`
-   **引数**:
    -   `api_endpoint` (str): 呼び出しをシミュレートするAPIエンドポイント。
    -   `method` (str, オプション): HTTPメソッド (例: "GET", "POST")。
    -   `payload` (Dict[str, Any], オプション): API呼び出しのペイロード。
    -   `success_rate` (float, オプション): シミュレートされた呼び出しが成功する確率（0.0から1.0）。
-   **戻り値**:
    -   `Dict[str, Any]`: シミュレートされたAPI呼び出しの結果（成功/失敗ステータス、メッセージなど）。
-   **説明**: ネットワーク遅延や成功/失敗の確率を考慮し、外部API呼び出しをシミュレートします。