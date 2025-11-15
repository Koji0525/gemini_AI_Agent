# 🛡️ 再発防止ガイドライン

## 📋 問題のまとめ

### 発生した問題
1. ❌ pm_tasksに新規タスクが追加されない
2. ❌ ナレッジ蓄積でメソッド名エラー
3. ✅ task_execution_logへの記録は成功

### 真因
1. **タスク追加ロジックの不足**
   - 「初回タスク生成」と「追加タスク生成」を区別していない
   - pendingがない場合の追加タスク生成機能が未実装

2. **APIの不一致**
   - `add_knowledge_entry`という存在しないメソッドを呼び出し
   - 正しくは`add_knowledge`

---

## 🔧 ツールによる再発防止

### 1. API検証ツール
```bash
# メソッド名の確認
python3 tools/api_validator.py
```

**使用タイミング:**
- 新しいAPIを使う前
- エラーが発生した時
- コードレビュー時

### 2. タスク管理フロー
```python
# ✅ 正しいフロー
tasks = engine.generate_additional_tasks(goal_id)
if tasks:
    engine.save_tasks_to_sheet(tasks)
```

**ポイント:**
- 進捗に応じた追加タスク生成
- pendingの有無確認
- 重複防止チェック

### 3. ナレッジ蓄積の正しい方法
```python
# ✅ 正しい
knowledge_manager.add_knowledge(
    title='タイトル',
    content='内容',
    category='カテゴリ',
    tags='タグ'
)

# ❌ 間違い
knowledge_manager.add_knowledge_entry(...)  # メソッド不存在
```

---

## 📝 運用ルールの見直し

### ルール1: API使用前の確認
**必須アクション:**
1. `python3 tools/api_validator.py`でメソッド確認
2. シグネチャと引数の確認
3. 使用例の参照

### ルール2: タスク生成の段階的アプローチ
**フロー:**
```
1. 初回: 調査・設計・実装の3タスク
2. 40-60%: テストタスク追加
3. 60-90%: 品質改善タスク追加
4. 90%以上: ドキュメントタスク追加
```

### ルール3: 3層の確認
**すべての操作で確認:**
1. ✅ task_execution_logに記録
2. ✅ pm_tasksのステータス更新
3. ✅ ナレッジ蓄積

### ルール4: エラー時の即座対応
**2回同じエラー → なぜなぜ分析**
- 10層の真因追求
- 他システムの成功事例調査
- 抜本的対策の立案

---

## 🎯 設計の改善

### 改善1: 動的タスク管理
```python
class TaskManager:
    def should_add_tasks(self, goal_id):
        """タスク追加が必要か判定"""
        existing = self.get_tasks(goal_id)
        pending_count = sum(1 for t in existing if t.status == 'pending')
        progress = self.calculate_progress(goal_id)
        
        # pendingがなく、進捗が特定範囲 → 追加
        return pending_count == 0 and progress in [40-60, 60-90, 90-100]
```

### 改善2: API統一インターフェース
```python
class APIWrapper:
    """API呼び出しの統一インターフェース"""
    
    def validate_method(self, obj, method_name):
        """メソッド存在確認"""
        if not hasattr(obj, method_name):
            raise AttributeError(f"{method_name}は存在しません")
    
    def call_with_validation(self, obj, method_name, *args, **kwargs):
        """検証付き呼び出し"""
        self.validate_method(obj, method_name)
        return getattr(obj, method_name)(*args, **kwargs)
```

### 改善3: 自動テスト
```bash
# CI/CDで自動実行
pytest tests/test_task_flow.py
pytest tests/test_knowledge_api.py
```

---

## 📊 モニタリング

### 定期確認項目
- [ ] pendingタスク数
- [ ] 新規タスク追加数
- [ ] ナレッジ蓄積数
- [ ] エラー発生数

### アラート条件
- 🚨 pendingが0で48時間経過
- 🚨 同じエラーが2回発生
- 🚨 ナレッジ蓄積が24時間なし

---

## 🔄 改善サイクル
```
1. 問題発生
   ↓
2. なぜなぜ分析（10層）
   ↓
3. 真因特定
   ↓
4. 対策実施（ツール + 運用）
   ↓
5. ドキュメント更新
   ↓
6. 定期レビュー
```

---

## ✅ チェックリスト

### コーディング時
- [ ] API検証ツールでメソッド確認
- [ ] 引数とシグネチャの確認
- [ ] エラーハンドリングの実装

### デプロイ前
- [ ] 3層確認（ログ・ステータス・ナレッジ）
- [ ] 手動テスト実行
- [ ] ドキュメント更新

### 運用中
- [ ] 日次: ダッシュボード確認
- [ ] 週次: タスク追加状況確認
- [ ] 月次: システム全体レビュー

---

**このガイドラインに従うことで、同様の問題の再発を防止できます。**
