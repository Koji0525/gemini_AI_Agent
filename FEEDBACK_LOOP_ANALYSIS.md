# 🔄 フィードバックループ分析

## 現在の実装（v1.0.0-integrated）

### レベル1: 基本的な依存関係
```
動作フロー:

1. pm_tasksシートから依存関係を読み込み
   ┌─────────────────────────────────────┐
   │ task_id: 2                          │
   │ description: ACF設定作成            │
   │ dependencies: 1                     │ ← タスク1に依存
   └─────────────────────────────────────┘

2. task_execution_logから依存タスクの出力を検索
   ┌─────────────────────────────────────┐
   │ log_id: 90                          │
   │ task_id: 1                          │
   │ output_data: 📁 GitHub: agent_...  │
   └─────────────────────────────────────┘

3. GitHubファイルから完全な出力を読み込み
   agent_outputs/tasks/task_1_design_20251019.md
   ↓
   「ma_caseカスタム投稿タイプが必要...」（2976文字）

4. タスク2のプロンプトに含める
   「あなたはwp_acfの専門家です。
   
   【前提情報】
   前のタスクの出力:
   ma_caseカスタム投稿タイプが必要...
   
   上記を踏まえて実行してください。」
```

### コード実装箇所
```python
# get_dependency_output メソッド
async def get_dependency_output(self, dependency_task_id: int):
    # 1. Sheetsからログ検索
    for row in reversed(all_data[1:]):
        if str(row[1]) == str(dependency_task_id):
            # 2. GitHub参照取得
            github_path = extract_path(row[6])
            
            # 3. ファイル読み込み
            with open(full_path, "r") as f:
                content = f.read()
            
            return content  # 完全な出力を返す

# _execute_with_gemini メソッド
async def _execute_with_gemini(self, task, role, dependency_output):
    prompt = f"""あなたは{role}の専門家です。
    
    タスク: {task['description']}
    """
    
    if dependency_output:
        prompt += f"""
        【前提情報】
        前のタスクの出力:
        {dependency_output[:2000]}  # 最初の2000文字のみ
        """
```

---

## ✅ 動作している機能

### 1. 単一依存関係
```
タスク1（要件定義）
    ↓
タスク2（実装プラン）← タスク1の出力を参照
```

### 2. GitHub優先のストレージ
```
完全な出力 → GitHub保存（制限なし）
サマリー   → Sheets保存（検索用）
```

### 3. 自動ログ記録
```
task_execution_log に：
- タスクID
- エージェント
- ステータス
- 出力サマリー
- GitHub参照リンク
```

---

## ❌ 問題点と制限

### 問題1: 単純な線形依存のみ
```
現在:
タスクA → タスクB → タスクC
        (1つのみ)

できない:
タスクA ┐
タスクB ┼→ タスクD（複数の依存）
タスクC ┘

pm_tasks.dependencies は単一の値のみ
例: dependencies: 1
```

**影響**: 複雑なワークフローに対応できない

### 問題2: 依存タスクが失敗した場合
```
タスクA（失敗）
    ↓
タスクB ← 依存タスクの出力が存在しない
       → エラーまたは不完全な実行
```

**影響**: 連鎖的な失敗

### 問題3: 循環依存のチェックなし
```
タスクA → タスクB
    ↑         ↓
    └─────タスクC

無限ループの可能性
```

**影響**: システムハング

### 問題4: 出力の2000文字制限
```python
dependency_output[:2000]  # プロンプトに含めるのは2000文字のみ
```

**影響**: 長い要件定義の場合、重要な情報が失われる

### 問題5: 品質評価なし
```
タスク完了 → そのまま次へ
           (品質チェックなし)
```

**影響**: 低品質な出力が次のタスクに影響

### 問題6: 再実行メカニズムなし
```
タスク失敗 → ステータスが "failed"
           → 手動で修正が必要
```

**影響**: 自動復旧できない

### 問題7: ゴール達成度の測定なし
```
タスク完了 → ゴールにどれだけ近づいたか不明
```

**影響**: プロジェクト進捗が見えない

### 問題8: 学習メカニズムなし
```
同じミスを繰り返す可能性
```

**影響**: 効率が上がらない

---

## 🎯 改善提案（v1.1.0で実装予定）

### 改善1: 複数依存対応
```python
# pm_tasksシート
dependencies: "1,2,3"  # カンマ区切り

# 実装
dependency_ids = [int(id) for id in task['dependencies'].split(',')]
all_outputs = []
for dep_id in dependency_ids:
    output = await self.get_dependency_output(dep_id)
    all_outputs.append(output)

# プロンプトに統合
combined_output = "\n\n---\n\n".join(all_outputs)
```

### 改善2: 依存チェック
```python
async def validate_dependencies(self, task):
    """依存タスクが完了しているか確認"""
    dep_ids = self.parse_dependencies(task['dependencies'])
    
    for dep_id in dep_ids:
        dep_status = await self.get_task_status(dep_id)
        
        if dep_status != 'completed':
            raise DependencyNotReadyError(f"Task {dep_id} not completed")
```

### 改善3: 循環依存検出
```python
def detect_circular_dependency(self, task_id, dependencies, visited=None):
    """循環依存を検出"""
    if visited is None:
        visited = set()
    
    if task_id in visited:
        raise CircularDependencyError(f"Circular dependency detected: {task_id}")
    
    visited.add(task_id)
    
    for dep_id in dependencies:
        dep_dependencies = self.get_dependencies(dep_id)
        self.detect_circular_dependency(dep_id, dep_dependencies, visited)
```

### 改善4: スマート要約
```python
async def smart_summarize_dependency(self, full_output):
    """重要な情報を抽出"""
    
    # Geminiで要約
    summary_prompt = f"""
    以下の出力から、次のタスクに必要な重要情報のみを抽出してください。
    
    {full_output}
    
    重要情報（1000文字以内）:
    """
    
    summary = await self.browser.send_prompt(summary_prompt)
    return summary
```

### 改善5: 品質評価
```python
async def evaluate_quality(self, task_id, output):
    """出力品質を評価"""
    
    evaluation_prompt = f"""
    以下の出力を評価してください（1-10点）。
    
    タスク: {task['description']}
    出力: {output}
    
    評価基準:
    - 完成度
    - 正確性
    - 実用性
    
    点数と理由を回答してください。
    """
    
    evaluation = await self.browser.send_prompt(evaluation_prompt)
    
    # 7点未満は再実行
    if score < 7:
        await self.retry_task(task_id)
```

### 改善6: 自動再実行
```python
async def execute_with_retry(self, task, max_retries=3):
    """失敗時に自動再実行"""
    
    for attempt in range(max_retries):
        success, output, error = await self._execute_with_gemini(task)
        
        if success:
            return output
        
        print(f"⚠️  試行 {attempt + 1}/{max_retries} 失敗: {error}")
        
        # 待機時間を増やす
        await asyncio.sleep(10 * (attempt + 1))
    
    raise TaskExecutionError(f"Task {task['task_id']} failed after {max_retries} attempts")
```

### 改善7: ゴール達成度測定
```python
async def measure_goal_progress(self):
    """ゴール達成度を測定"""
    
    completed_tasks = self.get_completed_tasks()
    total_tasks = self.get_all_tasks()
    
    progress = len(completed_tasks) / len(total_tasks) * 100
    
    # Geminiで質的評価
    evaluation_prompt = f"""
    プロジェクトゴール:
    {self.project_goal}
    
    完了タスク:
    {completed_tasks}
    
    ゴールにどれだけ近づきましたか？（%）
    """
    
    goal_progress = await self.browser.send_prompt(evaluation_prompt)
    
    return {
        "quantitative": progress,
        "qualitative": goal_progress
    }
```

