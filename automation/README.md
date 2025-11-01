# WordPress自動化システム

## 📁 ディレクトリ構造
```
automation/
├── tests/              # テストスクリプト
├── pipelines/          # 自動化パイプライン
├── config/             # 設定ファイル
├── logs/               # 実行ログ
└── docs/               # ドキュメント
```

## 🚀 クイックスタート

### 1. コンポーネントテスト
```bash
python3 automation/tests/test_components.py
```

### 2. WordPress自動化実行
```bash
python3 automation/pipelines/wordpress_automation.py
```

### 3. 24時間自動化（GitHub Actions）
```bash
# .github/workflows/に設定ファイルあり
```

## 📊 システム構成

- **WPAutoConfigAgent**: functions.php自動更新
- **WPDataPopulator**: 企業データ自動登録
- **BrowserController**: ブラウザ自動操作
- **TaskExecutor**: タスク実行管理
- **FeedbackGenerator**: 改善提案生成
