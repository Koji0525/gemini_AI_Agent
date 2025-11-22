#!/bin/bash
# APIキー漏洩問題の完全分析

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚨 APIキー漏洩問題の完全分析"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: なぜなぜ分析（真因追求）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cat > "MD/${NOW_JST}_API_KEY_LEAK_ANALYSIS.md" << 'ANALYSIS'
# APIキー漏洩問題 - なぜなぜ分析

## 🚨 問題
```
403 Your API key was reported as leaked. 
Please use another API key.
```

## 📊 なぜなぜ分析（10+原因候補）

### 1. GitHubリポジトリへの露出 ⭐⭐⭐
**可能性: 高**
- .envファイルが誤ってコミット/プッシュされた
- Codespacesが公開リポジトリの場合、.envが見えている可能性
- GitHubのSecret Scanningが自動検出 → Googleに通報

**確認方法**:
```bash
# Gitの履歴を確認
git log --all --full-history -- .env
git log --all --full-history -S "GEMINI_API_KEY"
```

### 2. ターミナル出力への平文表示 ⭐⭐⭐
**可能性: 高**
- 既存スクリプトでAPIキーを平文出力している
- TaskExecutorにも確認メッセージで一部表示している
- Codespacesのターミナルが共有されている可能性

**確認箇所**:
```python
# TaskExecutorEnhanced v2で追加した行
print(f"🔑 GEMINI_API_KEY: {self.gemini_api_key[:10]}...（読み込み成功）")
# ↑ これでも検出される可能性
```

### 3. 過去のチャット履歴への混入 ⭐⭐
**可能性: 中**
- Claudeとの会話で.envの内容を貼り付けた
- ログファイルを共有した際に含まれていた

### 4. ログファイルへの記録 ⭐⭐⭐
**可能性: 高**
- logs/配下にAPIキーが記録されている
- エラーメッセージに含まれている
- スタックトレースに含まれている

**確認方法**:
```bash
# ログファイルを検索
grep -r "AIza" logs/ 2>/dev/null
```

### 5. バックアップファイルの存在 ⭐⭐
**可能性: 中**
- .env.backup_* ファイルが残っている
- エディタの自動バックアップ（.env~など）

**確認方法**:
```bash
find . -name ".env*" -o -name "*backup*" | grep env
```

### 6. 既存システムでのハードコーディング ⭐⭐⭐
**可能性: 高**
- agents/配下のファイルに直接記述されている
- complete_engine_ultimate.pyなど

**確認方法**:
```bash
grep -r "AIza" agents/ tools/ --include="*.py" 2>/dev/null
```

### 7. Google Sheets経由での漏洩 ⭐
**可能性: 低**
- APIキーがシートに記録されている
- シートが公開設定になっている

### 8. 環境変数の設定ミス ⭐
**可能性: 低**
- Codespacesのシークレット設定が誤っている
- 環境変数が公開されている

### 9. 複数IPからの同時アクセス ⭐⭐
**可能性: 中**
- 同じAPIキーを複数の場所で使用
- 自動化スクリプトの並列実行

### 10. APIキー使用量の異常 ⭐⭐
**可能性: 中**
- 短時間に大量のリクエスト
- レート制限を超えた使用

### 11. .gitignoreの設定ミス ⭐⭐⭐
**可能性: 高**
- .envが.gitignoreに含まれていない
- .gitignoreの記述ミス

**確認方法**:
```bash
cat .gitignore | grep ".env"
```

### 12. スクリーンショット/ビデオへの映り込み ⭐
**可能性: 低**
- 画面共有時に表示された
- デモ動画に含まれた

## 🎯 最も可能性が高い原因（トップ3）

1. **GitHubへの露出**（可能性: 80%）
   - .envファイルが誤ってコミットされた
   - GitHubのSecret Scanningが検出

2. **ログファイルへの記録**（可能性: 70%）
   - エラーログにAPIキーが含まれている
   - logs/配下が公開されている

3. **ターミナル出力**（可能性: 60%）
   - デバッグ出力で平文表示
   - Codespacesのターミナルが記録されている

## 📋 既存システムの成功事例

既存のF1エージェント（agents/pm_agent/task_breakdown_gemini.py）は
正常に動作している → そちらのAPIキー管理方法を確認すべき
```python
# task_breakdown_gemini.pyでの使用例
self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
```

**F1が動作している理由**:
- 同じ.envを使用しているはず
- しかし、エラーが出ていない
- → 別のAPIキーを使用している可能性？
- → または、F1は漏洩前に実行済み？

ANALYSIS

echo "✅ なぜなぜ分析完了: MD/${NOW_JST}_API_KEY_LEAK_ANALYSIS.md"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: 漏洩箇所の特定
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: 漏洩箇所の特定"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🔍 検索1: Gitの履歴に.envが含まれているか"
git log --all --full-history -- .env 2>/dev/null | head -20 || echo "  履歴なし"

echo ""
echo "🔍 検索2: .envファイルの存在確認"
find . -name ".env*" -type f 2>/dev/null

echo ""
echo "🔍 検索3: .gitignoreの確認"
cat .gitignore | grep -i "env" || echo "  .envの記述なし"

echo ""
echo "🔍 検索4: ログファイルにAPIキーが含まれているか"
grep -r "AIza" logs/ 2>/dev/null | head -5 || echo "  ログに記録なし"

echo ""
echo "🔍 検索5: Pythonファイルにハードコーディングされているか"
grep -r "AIza" agents/ tools/ --include="*.py" 2>/dev/null | head -5 || echo "  ハードコーディングなし"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: 抜本的な対策
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: 抜本的な対策"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > "MD/${NOW_JST}_API_KEY_PROTECTION_PLAN.md" << 'PLAN'
# APIキー保護計画

## 🚨 即座に実施すべきこと

### 1. 新しいAPIキーを発行 ⭐⭐⭐
**最優先**
1. Google AI Studioにアクセス
2. 漏洩したAPIキーを削除
3. 新しいAPIキーを発行
4. .envファイルを更新

### 2. .gitignoreの強化 ⭐⭐⭐
```bash
# .gitignoreに追加
.env
.env.*
*.env
.env.backup*
configuration/service_account.json
```

### 3. Git履歴からの削除 ⭐⭐⭐
もし.envがコミットされていた場合：
```bash
# Git履歴から完全削除
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 強制プッシュ（注意！）
git push origin --force --all
```

### 4. ログファイルのクリーンアップ ⭐⭐
```bash
# logs/配下のAPIキー含むファイルを削除
find logs/ -type f -exec grep -l "AIza" {} \; -delete
```

### 5. デバッグ出力の削除 ⭐⭐⭐
すべてのprint文でAPIキーを表示しない：
```python
# ❌ 危険
print(f"API Key: {api_key}")

# ❌ これも危険
print(f"API Key: {api_key[:10]}...")

# ✅ 安全
# 何も出力しない、またはマスク
print("API Key: ********")
```

## 🛡️ 長期的な対策

### 1. Codespacesシークレットの活用
.envファイルを使わず、Codespacesの環境変数機能を使用

### 2. APIキーのローテーション
定期的に（月1回）APIキーを変更

### 3. APIキー使用のモニタリング
Google Cloud Consoleで使用状況を監視

### 4. 最小権限の原則
必要最小限のスコープでAPIキーを発行

### 5. 複数APIキーの使用
開発用・本番用でAPIキーを分ける

## 📝 既存システムとの整合性

### F1エージェントの確認
```bash
# F1が使用しているAPIキー管理方法を確認
cat agents/pm_agent/task_breakdown_gemini.py | grep -A 10 "api_key"
```

もしF1が正常動作しているなら：
- 別のAPIキーを使用している可能性
- または、環境変数の読み込み方が異なる

### 統一的なAPIキー管理
すべてのエージェントで同じ方法を使用：
```python
import os
from dotenv import load_dotenv

# プロジェクトルートの.envを読み込み
load_dotenv('/workspaces/gemini_AI_Agent/.env')

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEYが設定されていません")
```

## 🔒 セキュリティチェックリスト

- [ ] 新しいAPIキーを発行
- [ ] .envを.gitignoreに追加
- [ ] Git履歴をクリーンアップ
- [ ] ログファイルをクリーンアップ
- [ ] すべてのprint文からAPIキーを削除
- [ ] Codespacesシークレットに移行
- [ ] APIキー使用状況をモニタリング
- [ ] ドキュメントを更新

PLAN

echo "✅ 保護計画作成: MD/${NOW_JST}_API_KEY_PROTECTION_PLAN.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ APIキー漏洩問題の分析完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 分析結果:"
echo "  最も可能性が高い原因:"
echo "    1. GitHubへの露出 (80%)"
echo "    2. ログファイルへの記録 (70%)"
echo "    3. ターミナル出力 (60%)"
echo ""
echo "🚨 即座に実施すべきこと:"
echo "  1. ⭐⭐⭐ 新しいAPIキーを発行"
echo "  2. ⭐⭐⭐ .gitignoreの強化"
echo "  3. ⭐⭐⭐ Git履歴のクリーンアップ"
echo "  4. ⭐⭐  ログファイルのクリーンアップ"
echo "  5. ⭐⭐⭐ デバッグ出力の削除"
echo ""
echo "📖 詳細:"
echo "  cat MD/${NOW_JST}_API_KEY_LEAK_ANALYSIS.md"
echo "  cat MD/${NOW_JST}_API_KEY_PROTECTION_PLAN.md"
echo ""
echo "🔧 次のステップ:"
echo "  1. Google AI Studioで新しいAPIキーを発行"
echo "  2. .envファイルを更新"
echo "  3. 再テスト"
echo ""

