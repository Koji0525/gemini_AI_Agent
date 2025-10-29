# 📝 ドキュメント命名規則ガイド

**作成日**: 2025-10-29  
**最終更新**: 2025-10-29

---

## 📁 ファイル配置ルール

### すべてのMarkdownファイルは `/md` フォルダに配置
```
gemini_AI_Agent/
├── md/                    ← ここにすべてのMdファイル
│   ├── 251029_2203_PHASE3_COMPLETE.md
│   ├── 251029_2205_SESSION_COMPLETE.md
│   └── ...
├── docs/                  ← 廃止（.gitignoreに追加）
└── ...
```

---

## 📝 命名規則

### フォーマット
```
YYMMDD_HHMM_FEATURE.md
```

### 構成要素

| 要素 | 説明 | 例 |
|------|------|-----|
| `YYMMDD` | 年月日（2桁年 + 2桁月 + 2桁日） | `251029` |
| `HHMM` | 時分（24時間形式） | `2203` |
| `FEATURE` | 機能・内容の説明（大文字スネークケース） | `PHASE3_COMPLETE` |

---

## 📋 命名例

### ✅ 正しい例
```
251029_2203_PHASE3_COMPLETE.md
251029_2205_SESSION_COMPLETE.md
251029_2210_ROADMAP_NEXTGEN.md
251030_0900_PHASE4_KICKOFF.md
251030_1200_FEEDBACK_GENERATOR_IMPL.md
251101_1500_AB_TESTING_ENGINE.md
```

### ❌ 間違った例
```
phase3_complete.md                    ← 日時なし
2025-10-29-phase3.md                  ← フォーマット違い
PHASE3_COMPLETION_REPORT.md           ← 日時なし
session_complete_20251029.md          ← フォーマット違い
```

---

## 🎯 FEATUREの命名ガイド

### カテゴリ別の推奨FEATURE名

#### Phase完了系
```
PHASE1_COMPLETE
PHASE2_COMPLETE
PHASE3_COMPLETE
PHASE4_KICKOFF
PHASE4_PROGRESS
```

#### セッション系
```
SESSION_START
SESSION_PROGRESS
SESSION_COMPLETE
SESSION_SUMMARY
```

#### 機能実装系
```
FEATURE_[名前]_IMPL         # 実装
FEATURE_[名前]_TEST         # テスト
FEATURE_[名前]_DEPLOY       # デプロイ
FEATURE_[名前]_COMPLETE     # 完成
```

#### システム系
```
SYSTEM_DESIGN
SYSTEM_ARCHITECTURE
SYSTEM_ANALYSIS
SYSTEM_OPTIMIZATION
```

#### レポート系
```
REPORT_ANALYSIS
REPORT_PERFORMANCE
REPORT_QUALITY
REPORT_PROGRESS
```

#### ロードマップ系
```
ROADMAP_NEXTGEN
ROADMAP_PHASE4
ROADMAP_UPDATE
```

---

## 📚 実際の使用例

### Phase 3完了時（2025-10-29 22:03）
```bash
# 作成するファイル
md/251029_2203_PHASE3_COMPLETE.md
md/251029_2203_SESSION_COMPLETE.md
md/251029_2203_ANALYSIS_REPORT.md
```

### Phase 4開始時（2025-10-30 09:00）
```bash
# 作成するファイル
md/251030_0900_PHASE4_KICKOFF.md
md/251030_0900_FEEDBACK_SYSTEM_DESIGN.md
```

### 機能実装時（2025-10-30 14:30）
```bash
# 作成するファイル
md/251030_1430_INTELLIGENT_FEEDBACK_IMPL.md
md/251030_1500_AB_TESTING_ENGINE_IMPL.md
```

---

## 🔧 自動化スクリプト

### 新規ドキュメント作成ヘルパー
```bash
# create_doc.sh
#!/bin/bash

FEATURE=$1

if [ -z "$FEATURE" ]; then
    echo "使用方法: ./create_doc.sh FEATURE_NAME"
    exit 1
fi

TIMESTAMP=$(date +%y%m%d_%H%M)
FILENAME="md/${TIMESTAMP}_${FEATURE}.md"

cat > "$FILENAME" << EOF
# ${FEATURE}

**作成日**: $(date +%Y-%m-%d)  
**作成時刻**: $(date +%H:%M)

---

## 概要

[ここに概要を記載]

---

## 詳細

[ここに詳細を記載]

