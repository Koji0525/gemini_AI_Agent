# Gemini AI 自律エージェントシステム - プロジェクト構造

## 📊 整理サマリー

### 整理前
- 約89ファイルがルートディレクトリに散在
- 依存関係が不明確
- メンテナンス困難

### 整理後
- **総ファイル数: 165個**
- **7つの主要パッケージに分類**
- **インポートパス自動修正: 85ファイル**
- **構文エラー: 0個**

---

## 📁 新しいプロジェクト構造

gemini_AI_Agent/
│
├── 🎯 メインエントリーポイント (ルート)
│   ├── autonomous_system.py          # 自律実行システム
│   ├── main_hybrid_fix.py            # ハイブリッド修正
│   └── safe_wordpress_executor.py    # 安全なWP実行
│
├── 🌐 browser_control/               # ブラウザ制御 (7ファイル)
│   ├── browser_controller.py         # メインコントローラー
│   ├── browser_ai_chat_agent.py      # AI対話
│   ├── safe_browser_manager.py       # 安全な管理
│   └── ...
│
├── 🤖 core_agents/                   # コアエージェント (14ファイル)
│   ├── pm_agent.py                   # プロジェクトマネージャー
│   ├── dev_agent.py                  # 開発エージェント
│   ├── review_agent.py               # レビューエージェント
│   ├── fixed_review_agent.py         # 修正版レビュー
│   └── ...
│
├── ⚙️ configuration/                 # 設定管理 (3ファイル)
│   ├── config_hybrid.py              # ハイブリッド設定
│   ├── config_utils.py               # 設定ユーティリティ
│   └── check_config.py               # 設定チェック
│
├── 🛠️ tools/                         # ユーティリティ (6ファイル)
│   ├── sheets_manager.py             # Googleシート連携
│   ├── cloud_storage_manager.py      # クラウドストレージ
│   └── error_handler_enhanced.py     # エラーハンドリング
│
├── 📜 scripts/                       # 実行スクリプト (6ファイル)
│   ├── run_multi_agent.py            # マルチエージェント実行
│   ├── task_executor.py              # タスク実行
│   └── main_automator.py             # 自動化メイン
│
├── 🧪 test/                          # テストコード (17ファイル)
│   ├── test_full_integration.py      # 完全統合テスト
│   ├── test_tasks.py                 # タスクテスト
│   └── ...
│
├── 📦 archive/                       # アーカイブ (22ファイル)
│   └── (古いバージョン、POCコード)
│
├── 🔧 agents/                        # メタエージェント (8ファイル)
├── 🐛 fix_agents/                    # 修正エージェント (12ファイル)
├── ⚡ task_executor/                 # タスク実行 (7ファイル)
└── 🌐 wordpress/                     # WordPress専用 (15ファイル)

---

## 🚀 使用方法

### 1. 自律システムの起動
```bash
# 完全な自律実行（テスト → 修正 → マルチエージェント → 修正）
python autonomous_system.py

# テストのみ実行
python autonomous_system.py --test-only

# マルチエージェントのみ実行
python autonomous_system.py --agent-only



📝 重要な更新内容
インポートパスの変更
整理前:
pythonfrom browser_controller import BrowserController
from pm_agent import PMAgent
from config_utils import setup_logging
整理後:
pythonfrom browser_control.browser_controller import BrowserController
from core_agents.pm_agent import PMAgent
from configuration.config_utils import setup_logging
ファイルパスの変更

test_tasks.py → test/test_tasks.py
run_multi_agent.py → scripts/run_multi_agent.py
(他75ファイルが移動)


✅ 検証結果

✅ 構文チェック: 104/104ファイル合格
✅ インポートテスト: 4/4モジュール成功
✅ ファイル移動: 75ファイル完了
✅ パス更新: 85ファイル完了
✅ 不足ファイル: 0個


🎯 次のステップ

環境変数の設定 (.env ファイル)

GEMINI_API_KEY
OPENAI_API_KEY
その他必要な設定


依存パッケージのインストール

 pip install -r requirements.txt

初回テスト実行

 python test/test_full_integration.py

自律システムの起動

python autonomous_system.py

📅 最終更新: 2025-10-12
👨‍💻 整理完了
