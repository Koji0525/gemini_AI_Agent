# 🛡️ インポートパターンガイド（再発防止策）

## 📊 問題の経緯

### 発生した問題
- `SheetsManager` のインポートエラーが3回以上繰り返された
- 原因: 実際のクラス名とインポートパスの誤認識

### 根本原因
1. **実際のクラス名**: `GoogleSheetsManager`（`SheetsManager` ではない）
2. **実際の場所**: `tools.sheets_manager`（`core_agents` ではない）
3. **既存コードを確認しなかった**: 動作しているファイルを見れば即解決だった

---

## ✅ 正しいインポートパターン（必ず従うこと）

### 基本原則
**新しいファイルを作成する前に、必ず既存の動作しているファイルを確認する**
```bash
# 正しいインポートパターンを確認
grep -r "from.*sheets_manager import" scripts/*.py | head -5
```

### 主要モジュールの正しいインポート

| モジュール | 正しいインポート | 誤ったインポート |
|-----------|----------------|-----------------|
| **GoogleSheetsManager** | `from tools.sheets_manager import GoogleSheetsManager` | `from core_agents.sheets_manager import SheetsManager` |
| **config_loader** | `from configuration.config_loader import get_config` | `from configuration.config_loader import load_config` |
| **ErrorClassifier** | `from agents.self_healing.utils.error_classifier import ErrorClassifier` | `from agents.self_healing.error_classifier import ErrorClassifier` |
| **RetryManager** | `from agents.self_healing.retry_manager import RetryManager` | `from core_agents.error_recovery.retry_manager import RetryManager` |

---

## 🔍 確認手順（新規ファイル作成時）

### STEP 1: 既存の成功パターンを確認
```bash
# 類似機能のファイルを検索
find scripts/ -name "*.py" -exec grep -l "同じ機能のキーワード" {} \;

# インポート文を抽出
head -30 <見つかったファイル> | grep "import"
```

### STEP 2: インポートパターンをコピー
- **完全に同じパターン**を使用
- 推測や創造はしない

### STEP 3: 動作確認
```bash
# インポートテスト
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from <モジュール> import <クラス>
print("✅ インポート成功")
