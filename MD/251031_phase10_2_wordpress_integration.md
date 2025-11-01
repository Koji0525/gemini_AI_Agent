# Phase 10.2: WordPress連携強化 - 実装計画

**開始日時**: 2025-10-31 21:30
**目標期間**: 1-2日
**優先度**: HIGH

---

## 🎯 目標

WordPress専門エージェントを復活させ、Task Executorとの完全連携を確立。
pm_tasksからWordPressタスクが実際に実行できる状態にする。

---

## 📊 現状の課題

### 1. WordPress専門エージェントの問題
```
❌ インポートエラー
❌ モジュールパスの不整合
❌ 汎用エージェント（Gemini）で代替
```

### 2. 認証情報の問題
```
❌ wp_url, wp_user, wp_pass の読み込み失敗
❌ 設定シートからの取得に問題
```

### 3. ルーティングの問題
```
❌ WordPressタスクが専門エージェントに振り分けられない
❌ Task Executorのルーティングロジック未完成
```

---

## 🔧 実装ステップ

### Step 1: WordPress専門エージェントの診断と修正
```bash
# 1.1 エージェントファイルの存在確認
wordpress/wp_dev/
├── cpt_agent.py          # カスタム投稿タイプ
├── acf_agent.py          # カスタムフィールド
├── taxonomy_agent.py     # カテゴリー・タグ
└── __init__.py

# 1.2 インポートエラーの修正
- モジュールパスの統一
- 依存関係の解決
- クラス名の整合性確認

# 1.3 テスト実行
python3 -c "from wordpress.wp_dev.cpt_agent import WordPressCPTAgent"
```

### Step 2: WordPress認証情報の確実な設定
```python
# configuration/wp_config_loader.py
class WordPressConfigLoader:
    """WordPress設定の確実な読み込み"""
    
    def load_config(self):
        # 優先順位:
        # 1. 環境変数 (.env)
        # 2. 設定シート (configuration_db)
        # 3. デフォルト値
        
        wp_config = {
            'wp_url': os.getenv('WP_URL') or self._load_from_sheet('wp_url'),
            'wp_user': os.getenv('WP_USER') or self._load_from_sheet('wp_user'),
            'wp_pass': os.getenv('WP_PASS') or self._load_from_sheet('wp_pass'),
        }
        
        return wp_config
```

### Step 3: Task Executorへの統合
```python
# scripts/task_executor_wordpress.py
class WordPressTaskExecutor:
    """WordPress専門タスク実行エンジン"""
    
    def __init__(self):
        self.wp_agents = {
            'wordpress_cpt': WordPressCPTAgent(),
            'wordpress_acf': WordPressACFAgent(),
            'wordpress_taxonomy': WordPressTaxonomyAgent(),
        }
    
    def execute_wp_task(self, task):
        """WordPressタスクを実行"""
        agent_type = task.get('required_role')
        
        if agent_type in self.wp_agents:
            agent = self.wp_agents[agent_type]
            result = agent.execute(task)
            return result
        else:
            # フォールバック
            return self.execute_generic_task(task)
```

### Step 4: pm_tasksとの連携
```python
# tools/pm_tasks_wp_integration.py
class PMTasksWordPressIntegration:
    """pm_tasksからWordPressタスクを実行"""
    
    def run_pending_wp_tasks(self):
        # 1. pm_tasksからpending かつ WordPress関連を取得
        tasks = self.get_pending_wp_tasks()
        
        # 2. 各タスクを実行
        for task in tasks:
            # ステータス更新: pending → in_progress
            self.update_task_status(task, 'in_progress')
            
            # WordPress専門エージェントで実行
            result = self.wp_executor.execute_wp_task(task)
            
            # 結果に応じてステータス更新
            if result['success']:
                self.update_task_status(task, 'completed')
            else:
                self.update_task_status(task, 'failed')
```

---

## 📈 期待効果

| 指標 | 現在 | 目標 |
|------|------|------|
| WordPress専門エージェント稼働率 | 0% | 100% |
| WordPressタスク成功率 | 未実行 | 80%+ |
| 汎用エージェントへのフォールバック率 | 100% | 20% |
| 認証成功率 | 不明 | 95%+ |

---

## 🧪 テスト項目

1. ✅ WordPress専門エージェントのインポート成功
2. ✅ WordPress認証情報の読み込み成功
3. ✅ カスタム投稿タイプの作成テスト
4. ✅ カスタムフィールドの設定テスト
5. ✅ pm_tasksからのタスク実行テスト

---

## 🚧 リスクと対策

| リスク | 対策 |
|--------|------|
| WordPress REST API認証失敗 | Application Passwords の設定手順ドキュメント化 |
| エージェントのバグ | 段階的テスト、ドライランモード実装 |
| pm_tasks更新失敗 | ロールバック機能の実装 |

