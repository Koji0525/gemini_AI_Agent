#!/bin/bash
# Geminiモデル確認と修正

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Geminiモデル確認と修正"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: 利用可能なモデルを確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: 利用可能なGeminiモデルを確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << 'PYCHECK'
import os
import sys

try:
    import google.generativeai as genai
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEYが設定されていません")
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    
    print("📋 利用可能なGeminiモデル（generateContent対応）:")
    print("")
    
    models = list(genai.list_models())
    
    content_models = [
        m for m in models 
        if 'generateContent' in m.supported_generation_methods
    ]
    
    if content_models:
        flash_models = []
        pro_models = []
        other_models = []
        
        for model in content_models:
            name = model.name
            if 'flash' in name.lower():
                flash_models.append(model)
            elif 'pro' in name.lower():
                pro_models.append(model)
            else:
                other_models.append(model)
        
        if flash_models:
            print("🚀 Flash モデル（高速）:")
            for m in flash_models:
                print(f"  ✅ {m.name}")
                print(f"     {m.display_name}")
                if '2.5' in m.name or '2.0' in m.name:
                    print(f"     ⭐ 推奨: 最新版")
                print("")
        
        if pro_models:
            print("💎 Pro モデル（高性能）:")
            for m in pro_models:
                print(f"  ✅ {m.name}")
                print(f"     {m.display_name}")
                print("")
        
        if other_models:
            print("📦 その他のモデル:")
            for m in other_models:
                print(f"  ✅ {m.name}")
                print("")
        
        # 推奨モデルを特定
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🎯 推奨モデル:")
        print("")
        
        # 2.5-flashを探す
        model_25_flash = next((m for m in flash_models if '2.5' in m.name and 'flash' in m.name.lower()), None)
        if model_25_flash:
            print(f"  1. {model_25_flash.name} ⭐⭐⭐")
            print(f"     理由: 最新のFlashモデル、高速で安定")
            print("")
        
        # 2.0-flashを探す
        model_20_flash = next((m for m in flash_models if '2.0' in m.name and 'flash' in m.name.lower()), None)
        if model_20_flash:
            print(f"  2. {model_20_flash.name} ⭐⭐")
            print(f"     理由: 新しいFlashモデル")
            print("")
        
        # 1.5-flashを探す
        model_15_flash = next((m for m in flash_models if '1.5' in m.name and 'flash' in m.name.lower()), None)
        if model_15_flash:
            print(f"  3. {model_15_flash.name} ⭐")
            print(f"     理由: 安定版Flashモデル")
            print("")
        
    else:
        print("⚠️  generateContentをサポートするモデルが見つかりません")
        print("")
        print("全モデル一覧:")
        for m in models[:20]:
            print(f"  - {m.name}")
        
except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()

PYCHECK

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: 既存システムで使用されているモデルを確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: 既存システムのモデル名を確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📂 agents/配下のGenerativeModel使用箇所:"
grep -r "GenerativeModel" agents/ --include="*.py" 2>/dev/null | grep -v "backup" | head -10

echo ""
echo "📂 tools/配下のGenerativeModel使用箇所:"
grep -r "GenerativeModel" tools/ --include="*.py" 2>/dev/null | grep -v "backup" | head -10

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: 正しいモデル名を自動検出して修正
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: モデル名の自動検出"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Pythonで最適なモデルを検出
RECOMMENDED_MODEL=$(python3 << 'PYDETECT'
import os
import sys

try:
    import google.generativeai as genai
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    
    models = list(genai.list_models())
    
    content_models = [
        m for m in models 
        if 'generateContent' in m.supported_generation_methods
    ]
    
    # 優先順位: 2.5-flash > 2.0-flash > 1.5-flash
    for priority in ['2.5', '2.0', '1.5', '1.0']:
        for model in content_models:
            name = model.name
            if priority in name and 'flash' in name.lower():
                print(name)
                sys.exit(0)
    
    # Flashが見つからない場合はProを探す
    for priority in ['2.5', '2.0', '1.5', '1.0']:
        for model in content_models:
            name = model.name
            if priority in name and 'pro' in name.lower():
                print(name)
                sys.exit(0)
    
    # それでも見つからない場合は最初のモデル
    if content_models:
        print(content_models[0].name)
    
except Exception as e:
    sys.exit(1)

PYDETECT
)

if [ -n "$RECOMMENDED_MODEL" ]; then
    echo "✅ 推奨モデルを検出: $RECOMMENDED_MODEL"
else
    echo "❌ モデル検出失敗"
    exit 1
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: TaskExecutorEnhanced v2を修正
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: TaskExecutorEnhanced v2の修正"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 既存ファイルをバックアップ
cp agents/task_executor_enhanced_v2.py "agents/task_executor_enhanced_v2.py.backup_${NOW_JST}" 2>/dev/null

# モデル名を置き換え
sed -i "s|GEMINI_MODEL = '.*'|GEMINI_MODEL = '$RECOMMENDED_MODEL'|g" agents/task_executor_enhanced_v2.py

echo "✅ モデル名を修正: $RECOMMENDED_MODEL"

# 確認
echo ""
echo "📝 修正後の内容:"
grep "GEMINI_MODEL = " agents/task_executor_enhanced_v2.py | head -1

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 5: F1エージェントなど既存システムのモデル名も確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: 既存エージェントの統一推奨"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > "MD/${NOW_JST}_GEMINI_MODEL_FIX_COMPLETE.md" << DOC
# Geminiモデル名修正完了

## 検出されたモデル
推奨モデル: \`$RECOMMENDED_MODEL\`

## 修正内容

### TaskExecutorEnhanced v2
- ✅ モデル名を \`$RECOMMENDED_MODEL\` に変更
- ✅ 自動検出により最新の利用可能モデルを使用

## 既存システムとの統一

既存のF1エージェントなどでも同じモデルを使用することを推奨します。

### 確認方法
\`\`\`bash
# 既存システムのモデル名を確認
grep -r "GenerativeModel" agents/ tools/ --include="*.py" | grep -v backup
\`\`\`

### 統一推奨
すべてのエージェントで \`$RECOMMENDED_MODEL\` を使用することで、
動作の一貫性が保たれます。

## テスト実行
\`\`\`bash
bash sh/start_pending_tasks_with_quality.sh 1
\`\`\`

DOC

echo "✅ マニュアル作成: MD/${NOW_JST}_GEMINI_MODEL_FIX_COMPLETE.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Geminiモデル確認と修正完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 検出結果:"
echo "  推奨モデル: $RECOMMENDED_MODEL"
echo ""
echo "🔧 修正完了:"
echo "  TaskExecutorEnhanced v2 → $RECOMMENDED_MODEL"
echo ""
echo "🧪 テスト実行:"
echo "  bash sh/start_pending_tasks_with_quality.sh 1"
echo ""
echo "📖 詳細:"
echo "  cat MD/${NOW_JST}_GEMINI_MODEL_FIX_COMPLETE.md"
echo ""

# 自動テスト
read -p "今すぐ修正版でタスクを実行しますか？ [Y/n] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🧪 修正版でタスク実行テスト"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    bash sh/start_pending_tasks_with_quality.sh 1
fi

