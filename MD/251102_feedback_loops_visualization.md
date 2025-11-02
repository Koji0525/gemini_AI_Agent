# 🔄 既存フィードバックループの全体像

## 📊 現在のシステム構成
```mermaid
graph TB
    subgraph "入力層"
        A[GitHub Actions<br/>目標入力] --> B[pm_task_queue]
        B --> C[PM Agent]
        C --> D[project_goal]
    end
    
    subgraph "タスク分解層"
        D --> E[PM Agent<br/>タスク分解]
        E --> F[pm_tasks]
    end
    
    subgraph "実行層"
        F --> G[Task Coordinator]
        G --> H{タスク種別判定}
        H -->|Workflow| I[WorkflowExecutor]
        H -->|Content| J[ContentExecutor]
        H -->|CLI| K[CLIExecutor]
        
        I --> L[task_execution_log]
        J --> L
        K --> L
    end
    
    subgraph "自己修復層"
        L --> M{エラー?}
        M -->|Yes| N[RetryManager]
        N --> O[retry_history]
        O --> P[DecisionSupportSystem]
        P -->|修正戦略| G
    end
    
    subgraph "学習層"
        L --> Q[SelfLearningPipeline]
        O --> Q
        Q --> R[PatternExtractor]
        R --> S[knowledge_base]
        S --> P
    end
    
    subgraph "人間介入層"
        T[GitHub Issues] --> U[HumanInteractionAgent]
        U -->|stop/resume| G
    end
    
    style A fill:#e1f5ff
    style D fill:#ffe1e1
    style F fill:#fff4e1
    style L fill:#e1ffe1
    style S fill:#f0e1ff
```

## 🔍 各ループの詳細

### **Loop 1: タスク実行ループ（既存）**
```mermaid
sequenceDiagram
    participant PM as PM Agent
    participant Tasks as pm_tasks
    participant TC as Task Coordinator
    participant Log as task_execution_log
    
    PM->>Tasks: タスク登録
    TC->>Tasks: タスク取得（pending）
    TC->>TC: 実行
    TC->>Log: 結果記録
    TC->>Tasks: ステータス更新（completed/failed）
```

**問題点:**
- ❌ タスク完了後の**次のタスク生成**がない
- ❌ タスク間の依存関係が不明確

---

### **Loop 2: 自己修復ループ（部分実装）**
```mermaid
sequenceDiagram
    participant TC as Task Coordinator
    participant RM as RetryManager
    participant DSS as DecisionSupportSystem
    participant KB as KnowledgeBase
    
    TC->>TC: エラー発生
    TC->>RM: リトライ依頼
    RM->>DSS: 修正戦略取得
    DSS->>KB: 類似事例検索
    KB-->>DSS: 過去の成功パターン
    DSS-->>RM: 推奨戦略
    RM->>TC: 修正適用→再実行
```

**問題点:**
- ⚠️ DecisionSupportSystemが**実際に使われていない**
- ❌ KnowledgeBaseの検索結果が**実行に反映されない**

---

### **Loop 3: 学習ループ（自動実行なし）**
```mermaid
sequenceDiagram
    participant Cron as GitHub Actions<br/>（6時間ごと）
    participant SLP as SelfLearningPipeline
    participant Logs as task_execution_log<br/>retry_history
    participant KB as knowledge_base
    
    Cron->>SLP: 定期実行
    SLP->>Logs: ログ取得
    SLP->>SLP: パターン抽出
    SLP->>KB: パターン保存
    Note over KB: 次回のDSS判断に使用
```

**問題点:**
- ❌ 学習結果が**即座に反映されない**
- ❌ 学習→適用のループが**6時間遅延**

---

## ❌ **不足しているループ**

### **Loop 4: 目標→タスク追加ループ（未実装）**
```mermaid
graph LR
    A[タスク完了] --> B{目標達成?}
    B -->|No| C[PM Agent<br/>追加タスク生成]
    C --> D[pm_tasks追加]
    D --> A
    B -->|Yes| E[次の目標へ]
```

**現状:** タスクが完了しても、**次に何をすべきか自動判断しない**

---

### **Loop 5: エラー→修正コード生成ループ（未実装）**
```mermaid
graph LR
    A[エラー検出] --> B[DecisionSupportSystem]
    B --> C[修正コード生成]
    C --> D[自動適用]
    D --> E[再実行]
    E -->|成功| F[knowledge_base更新]
    E -->|失敗| A
```

**現状:** エラーを検出しても、**修正コードを生成・適用しない**

---

## 📋 改善が必要な箇所

| 箇所 | 現状 | 理想 | 優先度 |
|------|------|------|--------|
| タスク完了後 | 何もしない | 次のタスク自動生成 | �� 高 |
| エラー時 | ログのみ | 修正コード自動適用 | 🔴 高 |
| 学習 | 6時間遅延 | リアルタイム反映 | 🟡 中 |
| 目標達成判定 | 手動 | 自動判定→次の目標 | 🟢 低 |
| エージェント追加 | 手動 | 必要性を自動判断 | 🟢 低 |
