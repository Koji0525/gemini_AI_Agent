# 🎯 Orchestrator バージョン管理（修正版）

## 📌 最新版（使用推奨）

**integrated_orchestrator.py** ← 👈 **これを使用**
```bash
# 方法1: シンボリックリンク経由（推奨）
python3 scripts/integrated_orchestrator_latest.py

# 方法2: 直接指定
python3 scripts/integrated_orchestrator.py
```

## 📊 重要な発見

### 分析結果（2025-11-25）

| ファイル | ステータス | 参照数 | サイズ | 備考 |
|---------|----------|-------|--------|------|
| **integrated_orchestrator.py** | ✅ **本流** | **15件** | 26K, 677行 | **これが最新版** |
| integrated/v31_core.py | ✅ 使用中 | 6件 | 32K, 813行 | 一部で使用 |
| v25_complete.py | ✅ 使用中 | 2件 | 24K, 632行 | レガシー |
| v51_complete.py | ❌ **未使用** | 0件 | 8.2K, 220行 | 誤認識 |
| 他24ファイル | ❌ 未使用 | 0件 | - | アーカイブ済み |

### 誤認識の経緯
```
当初の判断: v51が最新版と思われた
実際の調査: integrated_orchestrator.py が本流（15件で使用中）
結論: ファイル名のバージョン番号に惑わされた
```

## 🚀 使用方法

### 基本的な実行
```bash
cd /workspaces/gemini_AI_Agent

# 推奨方法
python3 scripts/integrated_orchestrator_latest.py
```

### 使用中のファイル（保持）

1. **integrated_orchestrator.py** - 本流（15件参照）
2. **integrated/v31_core.py** - サブシステム（6件参照）
3. **v25_complete.py** - レガシーシステム（2件参照）
4. 他5ファイル - 限定的使用

### アーカイブ済み（24ファイル）

- v51を含む未使用バージョン
- 復元可能: `archived_orchestrators_YYYYMMDD_HHMMSS/`

## 💡 教訓

### 学んだこと

1. **ファイル名のバージョン番号は信用できない**
   - v51 > v31 とは限らない
   - 実際の使用状況を調査すべき

2. **分析が重要**
   - プロジェクト全体でのimport/参照を確認
   - 使用頻度が真の「最新版」を示す

3. **正規版の重要性**
   - バージョン番号なしの `integrated_orchestrator.py` が本流
   - シンボリックリンクはこれを指すべき

## 🔧 今後のバージョン管理

### file_version_manager.py の使用
```bash
# 新バージョン作成
python3 tools/file_version_manager.py \
    scripts/integrated_orchestrator.py \
    "新機能追加"

# 自動で以下を実行:
# 1. バックアップ作成
# 2. 新バージョン生成
# 3. 重複チェック
```

### ルール

1. バージョン番号付きファイルは**実験用**
2. 正規版は `integrated_orchestrator.py`
3. 確定したら正規版にマージ
4. 古いバージョンは即座にアーカイブ

---

**最終更新**: 2025-11-25  
**管理者**: AI Development System  
**注意**: v51は未使用だったことが判明

