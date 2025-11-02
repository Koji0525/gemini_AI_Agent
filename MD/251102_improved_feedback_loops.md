# 🔄 改善後のフィードバックループ（v2.0）

## 🎉 **新機能**
- ✅ タスク完了→次タスク自動生成
- ✅ エラー→自動修復提案
- ✅ シート統合（重複削除）

---

## 📊 改善後のシステム構成
```mermaid
graph TB
    subgraph "入力層"
        A[GitHub Actions] --> B[pm_task_queue]
        B --> C[PM Agent]
        C --> D[project_goal]
    end
    
    subgraph "タスク分解層"
        D --> E[PM Agent<br/>タスク分解]
        E --> F[pm_tasks]
    end
    
    subgraph "実行層 ✨NEW"
        F --> G[Task Coordinator v02]
        G --> H{タスク種別判定}
        H -->|Workflow| I[WorkflowExecutor]
        H -->|Content| J[ContentExecutor]
        H -->|CLI| K[CLIExecutor]
        
        I --> L[task_execution_log]
        J --> L
        K --> L
        
        L --> TCH[TaskCompletionHandler ✨NEW]
        TCH --> TCH_EVAL{目標達成?}
        TCH_EVAL -->|No| TCH_GEN[次タスク生成]
        TCH_GEN --> F
        TCH_EVAL -->|Yes| TCH_DONE[完了]
    end
    
    subgraph "自己修復層 ✨ENHANCED"
        G --> M{エラー?}
        M -->|Yes| ACF[AutoCodeFixer ✨NEW]
        ACF --> KB_SEARCH[KnowledgeBase検索]
        KB_SEARCH --> DSS[DecisionSupportSystem]
        DSS --> FIX_GEN[修正コード生成]
        FIX_GEN --> FIX_APPLY[修正提案]
        FIX_APPLY --> O[retry_log]
        O --> G
        
        FIX_APPLY -->|成功| KB_SAVE[KnowledgeBase保存]
    end
    
    subgraph "学習層"
        L --> Q[SelfLearningPipeline]
        O --> Q
        Q --> R[PatternExtractor]
        R --> S[knowledge_base]
        S --> DSS
    end
    
    subgraph "人間介入層"
        T[GitHub Issues] --> U[HumanInteractionAgent]
        U -->|stop/resume| G
    end
    
    style TCH fill:#ffe1e1
    style ACF fill:#ffe1e1
    style FIX_GEN fill:#ffe1e1
```

---

## �� 改善された各ループ

### **Loop 1: タスク実行ループ（✨改善）**
```mermaid
sequenceDiagram
    participant PM as PM Agent
    participant Tasks as pm_tasks
    participant TC as Task Coordinator v02
    participant TCH as TaskCompletionHandler
    participant Log as task_execution_log
    
    PM->>Tasks: タスク登録
    TC->>Tasks: タスク取得（pending）
    TC->>TC: 実行
    TC->>Log: 結果記録
    TC->>TCH: タスク完了通知 ✨NEW
    
    TCH->>TCH: 進捗評価
    alt 目標未達成
        TCH->>TCH: 次タスク生成 ✨NEW
        TCH->>Tasks: 新タスク追加 ✨NEW
    else 目標達成
        TCH->>TCH: 完了
    end
    
    TC->>Tasks: ステータス更新
```

**✅ 改善点:**
- タスク完了後に**自動で次のタスクを生成**
- 目標達成度を**自動評価**

---

### **Loop 2: 自己修復ループ（✨大幅改善）**
```mermaid
sequenceDiagram
    participant TC as Task Coordinator v02
    participant ACF as AutoCodeFixer ✨NEW
    participant KB as KnowledgeBase
    participant DSS as DecisionSupportSystem
    
    TC->>TC: エラー発生
    TC->>ACF: 自動修復依頼 ✨NEW
    ACF->>KB: 類似事例検索 ✨NEW
    KB-->>ACF: 過去の成功パターン
    ACF->>DSS: 修正戦略取得
    DSS-->>ACF: 推奨戦略
    ACF->>ACF: 修正コード生成 ✨NEW
    ACF->>TC: 修正提案 ✨NEW
    
    alt 修正成功
        ACF->>KB: 修正パターン保存 ✨NEW
    end
```

**✅ 改善点:**
- エラー発生時に**修正コードを自動生成**
- 成功パターンを**KnowledgeBaseに自動保存**

---

### **Loop 3: 学習ループ（既存）**
```mermaid
sequenceDiagram
    participant Cron as GitHub Actions<br/>（6時間ごと）
    participant SLP as SelfLearningPipeline
    participant Logs as task_execution_log<br/>retry_log
    participant KB as knowledge_base
    
    Cron->>SLP: 定期実行
    SLP->>Logs: ログ取得
    SLP->>SLP: パターン抽出
    SLP->>KB: パターン保存
    Note over KB: 次回のDSS判断に使用
```

---

## 📊 改善効果

| 項目 | 改善前 | 改善後 | 効果 |
|------|--------|--------|------|
| タスク完了後 | 何もしない | 次タスク自動生成 | **自律性向上** |
| エラー時 | ログのみ | 修正コード提案 | **自己修復能力獲得** |
| シート管理 | 重複あり | 統合済み | **保守性向上** |
| ナレッジ活用 | 参照のみ | 自動蓄積 | **学習能力向上** |

---

## 🎯 残りの改善タスク

| タスク | 優先度 | 状態 |
|--------|--------|------|
| Loop 4: 目標→タスク追加 | P0 | ✅ 完了 |
| Loop 5: エラー→修正適用 | P0 | ✅ 完了（提案まで） |
| シート統合 | P1 | ✅ 完了 |
| DSSの実戦投入 | P1 | ✅ 完了 |
| 学習のリアルタイム化 | P2 | ⏳ 未着手 |
| 修正コードの自動適用 | P2 | ⏳ 未着手 |

---

## 📈 次のステップ

1. **テスト実行** → 実際の動作確認
2. **v24との統合** → Orchestratorに組み込み
3. **24時間稼働テスト** → 本番運用開始

