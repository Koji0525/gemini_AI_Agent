# WordPress設定確認システム

## 📋 概要

WordPress環境の設定を自動的に確認し、Quality Scoreを算出してGoogle Sheetsに記録するシステム。

**実装日**: 2025-10-28  
**バージョン**: v1.0  
**Quality Score**: 9/10 (合格)

---

## 🚀 使い方

### 基本的な実行方法
```bash
# 統合システムの実行
python3 scripts/config_validation_system.py
```

### Phase 1のみ実行（設定確認のみ）
```bash
# Phase 1単体の実行
python3 scripts/config_validator.py
```

---

## 📊 機能

### Phase 1: 基本的な設定確認
- ✅ WordPress接続テスト
- ✅ REST API利用可能性確認
- ✅ サイト情報取得（投稿タイプ、プラグイン、テーマ）
- ✅ エージェント状態確認
- ✅ 重要モジュール確認

### Phase 2: ログ記録
- ✅ Quality Score自動計算（1-10点、合格ライン7点）
- ✅ task_execution_logシートへの記録
- ✅ status判定（completed/warning/failed）

### Phase 3: レポート生成
- ✅ Markdownレポート自動生成
- ✅ `logs/`ディレクトリに保存
- ✅ 詳細な確認結果を記載

---

## 📈 Quality Score基準

| スコア | 判定 | 説明 |
|--------|------|------|
| 10点 | 完璧 | すべての機能が正常動作 |
| 9点 | ほぼ完璧 | 一部オプション機能に制限 |
| 8点 | 良好 | 主要機能は正常 |
| **7点** | **合格** | **基本機能が使用可能** |
| 6点以下 | 不合格 | 設定の確認が必要 |

### 減点項目
- WordPress接続失敗: -8点
- REST API利用不可: -5点
- REST API制限あり: -3点
- サイト情報取得失敗: -2点
- 主要エージェント未実装: -1点/個
- 重要モジュール利用不可: -1点/個

---

## 🔧 システム構成

### ファイル構成
```
scripts/
├── config_validation_system.py  # 統合システム（Phase 1-3）
└── config_validator.py          # Phase 1単体

logs/
└── config_validation_report_YYYYMMDD_HHMMSS.md  # 生成されるレポート
```

### 必要な環境変数（.env）
```bash
# WordPress設定
WP_URL=https://your-site.com
WP_USER=your-username
WP_PASS=your-password

# Google Sheets設定
SPREADSHEET_ID=your-spreadsheet-id
GOOGLE_SERVICE_ACCOUNT_FILE=configuration/service_account.json
```

---

## 📝 出力例

### コンソール出力
```
================================================================================
🚀 Phase 1: 基本的な設定確認を開始します
================================================================================

📡 WordPress接続テスト
✅ WordPress接続成功 (Status: 200)

📊 サイト情報取得
✅ REST API利用可能
   📝 投稿タイプ: 14個

🤖 エージェント状態確認
   ✅ wp_design_generator
   ✅ wp_orchestrator

================================================================================
📊 Phase 2: ログ記録を開始
================================================================================

✅ Quality Score: 9/10
📝 Status: completed

================================================================================
🎉 全Phase完了!
Quality Score: 9/10
================================================================================
```

### Markdownレポート（例）
```markdown
# WordPress設定確認レポート

**実行日時**: 2025-10-28 15:19:20
**Quality Score**: 9/10

---

## 1. WordPress接続テスト
✅ **成功** - https://uzbek-ma.com

## 2. REST API
✅ **利用可能**

## 3. サイト情報
- 投稿タイプ: 14個

## 総合判定
🎉 **合格** - システムは基本的な動作が可能です
```

---

## �� 運用フロー

1. **定期実行**: cron等で定期的に実行し、システム状態を監視
2. **ログ確認**: Google Sheetsの`task_execution_log`シートで履歴確認
3. **レポート確認**: `logs/`ディレクトリのMarkdownファイルで詳細確認
4. **問題対応**: Quality Score 7点未満の場合、設定を確認

---

## �� トラブルシューティング

### WordPress接続失敗
- `.env`ファイルの`WP_URL`, `WP_USER`, `WP_PASS`を確認
- WordPressサイトが稼働しているか確認

### REST API利用不可
- WordPress REST APIが有効になっているか確認
- プラグインでREST APIが無効化されていないか確認

### Google Sheetsエラー
- `GOOGLE_SERVICE_ACCOUNT_FILE`のパスを確認
- サービスアカウントにスプレッドシートの編集権限があるか確認

---

## 📚 関連ドキュメント

- 運用ルール: `1761662500265_pasted-content-1761662500264.txt`
- ログ記録仕様: `1761662524252_pasted-content-1761662524252.txt`
- プロジェクトREADME: `README.md`

---

**作成日**: 2025-10-28  
**最終更新**: 2025-10-28  
**バージョン**: 1.0
