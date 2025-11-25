# 🎯 Orchestrator バージョン管理

## 📌 最新版（使用推奨）

**v51_complete.py** ← 👈 **常にこれを使用**
```bash
# 方法1: シンボリックリンク経由（推奨）
python3 scripts/integrated_orchestrator_latest.py

# 方法2: 直接指定
python3 scripts/integrated_orchestrator_v51_complete.py
```

## 📊 バージョン履歴

| バージョン | ステータス | 特徴 | 使用 |
|-----------|----------|------|------|
| **v51_complete.py** | ✅ **安定版** | 全機能実装、完全版 | ✅ 推奨 |
| v31_core.py | ⚠️ 非推奨 | コア機能のみ | ❌ 使用禁止 |

## 🚀 使用方法

### 基本的な実行
```bash
cd /workspaces/gemini_AI_Agent

# デフォルト実行
python3 scripts/integrated_orchestrator_latest.py
```

### オプション付き実行
```bash
# テストモード（60秒実行）
python3 scripts/integrated_orchestrator_latest.py --mode test --duration 60

# 本番モード（継続実行）
python3 scripts/integrated_orchestrator_latest.py --mode production

# ドライラン（シミュレーション）
python3 scripts/integrated_orchestrator_latest.py --dry-run
```

## ⚠️ 注意事項

### 古いバージョンを使用しない
```bash
# ❌ これは使わない
python3 scripts/integrated/integrated_orchestrator_v31_core.py

# ✅ これを使う
python3 scripts/integrated_orchestrator_latest.py
```

### 理由

- v31は古いAPIを使用
- メソッド不足（例: `run_continuous_cycle` がない）
- バグ修正が反映されていない

## 🔍 バージョン確認方法

### 利用可能なすべてのバージョンをリスト
```bash
ls -lt scripts/integrated_orchestrator*.py
```

### 最新版の確認
```bash
ls -la scripts/integrated_orchestrator_latest.py
```

### コード内バージョン情報
```bash
grep -n "__version__" scripts/integrated_orchestrator_v51_complete.py
```

## 📝 更新履歴

- **2025-11-25**: v51_complete.py を最新安定版として確定
- **2025-11-25**: シンボリックリンク `integrated_orchestrator_latest.py` 導入
- **2025-11-25**: v31_core.py を非推奨化

## 🆘 トラブルシューティング

### エラー: `AttributeError: 'IntegratedOrchestratorV31Core' object has no attribute 'run_continuous_cycle'`

**原因**: 古いv31を使用している

**解決策**:
```bash
# v51に切り替える
python3 scripts/integrated_orchestrator_latest.py
```

### エラー: `ModuleNotFoundError`

**原因**: 依存パッケージが不足

**解決策**:
```bash
pip install -r requirements.txt --break-system-packages
```

## 📚 関連ドキュメント

- [統合要件定義書](/mnt/project/____統合要件定義書_v4_0_-_完全版.txt)
- [ロードマップ](/mnt/project/___統合システム実装ロードマップ_v4_1.txt)
- [運用ルール](/mnt/project/_運用ルール.txt)

---

**最終更新**: 2025-11-25  
**管理者**: AI Development System

