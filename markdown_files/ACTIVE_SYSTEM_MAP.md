# 🎯 アクティブシステム構成図

📅 生成日時: 1760249726.1022046

## 🚀 メインエントリーポイント

### integrated_system_with_review.py
- **ステータス**: ⚠️ エラーあり
- **説明**: メインの統合システム（WordPressとレビュー連携）
- **優先度**: HIGH
- **使用状況**: ⚠️ 未使用

### run_multi_agent.py
- **ステータス**: ✅ 動作中
- **説明**: マルチエージェント実行システム
- **優先度**: HIGH
- **使用状況**: ✓ 使用中

### test_tasks.py
- **ステータス**: ✅ テスト完了
- **説明**: 基本システムテスト
- **優先度**: MEDIUM
- **使用状況**: ✓ 使用中

### test_tasks_practical.py
- **ステータス**: ✅ 実践テスト完了
- **説明**: WordPress/Sheets実践テスト
- **優先度**: MEDIUM
- **使用状況**: ✓ 使用中


## 🔧 コアモジュール構成

### Browser

- ✓ `browser_controller.py` (使用中)
- ✓ `browser_lifecycle.py` (使用中)
- ✓ `browser_ai_chat_agent.py` (使用中)
- ✓ `browser_wp_session_manager.py` (使用中)
- ✓ `brower_cookie_and_session.py` (使用中)

### WordPress

- ✓ `wordpress/wp_post_creator.py` 
- ✓ `wordpress/wp_post_editor.py` 
- ✓ `wordpress/wp_auth.py` 
- ✓ `wordpress/wp_agent.py` 

### Sheets

- ✓ `sheets_manager.py` (使用中)

### Review

- ✓ `review_agent.py` (使用中)
- ✓ `review_agent_prompts.py` (使用中)

### Agents

- ✓ `pm_agent.py` (使用中)
- ✓ `dev_agent.py` (使用中)
- ✓ `design_agent.py` (使用中)
- ✓ `content_writer_agent.py` 

### Config

- ✓ `config_utils.py` (使用中)
- ✓ `config_hybrid.py` (使用中)


## ⚠️ 既知の問題

### 1. ブラウザ初期化エラー
- **エラー**: `'NoneType' object has no attribute 'goto'`
- **場所**: WordPressエグゼキューター
- **原因**: ブラウザコントローラーが未初期化

### 2. レビューAIエラー
- **エラー**: `'NoneType' object has no attribute 'send_prompt'`
- **場所**: レビューエージェント
- **原因**: ブラウザコントローラーとの連携不備


## 📝 次のアクション

1. ✅ バックアップファイルの整理（安全な削除）
2. 🔧 ブラウザ初期化の統一
3. 🐛 エラーハンドリングの強化
4. 🧪 integrated_system_with_review.py の修正
