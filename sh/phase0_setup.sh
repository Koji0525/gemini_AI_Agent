#!/bin/bash
# Phase 0: 事前準備実装

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Phase 0: 事前準備開始"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

START_TIME=$(date +%s)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# P0-T001: プロジェクト構造作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "⬜ P0-T001: プロジェクト構造作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# メインディレクトリ
mkdir -p agents/observer_enhanced
mkdir -p agents/observer_enhanced/web
mkdir -p agents/observer_enhanced/web/static/js
mkdir -p agents/observer_enhanced/web/static/css

# ログディレクトリ
mkdir -p logs

# 設定ディレクトリ
mkdir -p config

# テストディレクトリ
mkdir -p tests/observer_enhanced
mkdir -p tests/integration
mkdir -p tests/performance

# バックアップディレクトリ
mkdir -p backups

echo "✅ ディレクトリ構造作成完了"
tree -L 3 agents/observer_enhanced 2>/dev/null || find agents/observer_enhanced -type d

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# P0-T002: 依存関係インストール
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "⬜ P0-T002: 依存関係インストール"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cat > requirements_observer.txt << 'REQ'
# Enhanced Observer System Dependencies
# Phase 0 Setup

# 既存依存関係（確認のみ）
google-api-python-client>=2.0.0
google-auth>=2.0.0
google-auth-oauthlib>=0.5.0
google-auth-httplib2>=0.1.0

# 新規依存関係
networkx>=3.0          # グラフ処理
flask>=3.0.0           # Web API
flask-cors>=4.0.0      # CORS対応
flask-socketio>=5.3.0  # WebSocket
python-socketio>=5.10.0
pytz>=2024.1           # タイムゾーン（既に一部で使用）
pyyaml>=6.0            # 設定ファイル
pytest>=8.0.0          # テスト（既存）
pytest-cov>=4.1.0      # カバレッジ
pytest-asyncio>=0.23.0 # 非同期テスト
REQ

echo "📦 依存関係リスト作成完了"
cat requirements_observer.txt

echo ""
echo "📥 依存関係インストール中..."

pip install -r requirements_observer.txt --break-system-packages --quiet

echo "✅ 依存関係インストール完了"

# バージョン確認
python3 << PYTHON
import sys
print("\n📊 インストール済みパッケージ:")
print(f"  networkx: {__import__('networkx').__version__}")
print(f"  flask: {__import__('flask').__version__}")
print(f"  pytz: {__import__('pytz').__version__}")
print(f"  yaml: {__import__('yaml').__version__}")
print(f"  pytest: {__import__('pytest').__version__}")
PYTHON

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# P0-T003: 設定ファイル作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "⬜ P0-T003: 設定ファイル作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cat > config/observer_config.yaml << 'YAML'
# Enhanced Observer System Configuration
# Version: 1.0
# Created: 2025-11-22

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# System Paths
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
paths:
  project_root: "/workspaces/gemini_AI_Agent"
  logs_dir: "logs"
  config_dir: "config"
  backups_dir: "backups"
  
  # データベース
  traces_db: "logs/traces.db"
  graph_db: "logs/graph.json"
  
  # 既存システム（読み取り専用）
  existing_agents: "agents"
  existing_tools: "tools"
  existing_tests: "tests"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Static Analysis Layer (Layer 1)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
static_analysis:
  # スキャン対象
  scan_patterns:
    - "agents/**/*.py"
    - "tools/**/*.py"
    - "!tests/**"
    - "!backups/**"
  
  # パフォーマンス設定
  max_file_size_mb: 5
  scan_timeout_seconds: 180  # 3分
  
  # グラフ設定
  max_nodes: 200
  max_edges: 1000
  
  # キャッシュ
  cache_enabled: true
  cache_ttl_seconds: 300  # 5分

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Dynamic Tracing Layer (Layer 2)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
dynamic_tracing:
  # トレース設定
  enabled: true
  trace_all_agents: true
  trace_tools: true
  
  # パフォーマンス
  max_overhead_ms: 5
  
  # データ保持
  retention_days: 30
  auto_cleanup: true
  
  # ログレベル
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Graph Control Layer (Layer 3)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
graph_control:
  # 影響範囲分析
  impact_analysis_depth: 3  # 3階層
  
  # スコアリング
  importance_weights:
    agents: 3.0
    tools: 2.0
    tests: 1.0
  
  # グラフアルゴリズム
  layout_algorithm: "force_directed"  # force_directed, hierarchical
  
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Orchestration Layer (Layer 0)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
orchestration:
  # 診断サイクル
  diagnostic_interval_minutes: 10
  
  # ヘルスチェック
  health_check:
    enabled: true
    
    # 評価項目と配点
    scoring:
      test_success_rate: 30  # テスト成功率
      agent_alive_rate: 25   # エージェント生存率
      api_response_time: 15  # API応答時間
      error_rate: 15         # エラー発生率
      resource_usage: 10     # リソース使用率
      knowledge_usage: 5     # ナレッジ活用率
    
    # 閾値
    thresholds:
      test_success_rate_min: 84.3  # 絶対に下回らない
      grade_warning: 70            # C以下で警告
      grade_critical: 60           # D以下でアラート
  
  # アラート
  alerts:
    enabled: true
    channels:
      - "log"
      - "file"
    
    # アラートレベル
    levels:
      low: 70
      medium: 60
      high: 50
      critical: 40

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Web Dashboard
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
dashboard:
  # サーバー設定
  host: "0.0.0.0"
  port: 5001
  debug: false
  
  # WebSocket
  websocket_enabled: true
  update_interval_seconds: 5
  
  # パフォーマンス
  max_concurrent_sessions: 10
  response_timeout_seconds: 3
  
  # セキュリティ
  cors_enabled: true
  allowed_origins:
    - "http://localhost:*"
    - "https://*.github.dev"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Testing
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
testing:
  # 既存テスト保護
  existing_tests:
    min_success_rate: 84.3
    rollback_on_failure: true
  
  # 新規テスト
  new_tests:
    target_success_rate: 95.0
    min_coverage: 80.0
  
  # パフォーマンステスト
  performance:
    dashboard_load_max_seconds: 3
    graph_render_max_seconds: 3
    static_scan_max_seconds: 180
    trace_query_max_seconds: 1
    health_check_max_seconds: 10

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Logging
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
  # ファイル出力
  file:
    enabled: true
    path: "logs/observer.log"
    max_bytes: 10485760  # 10MB
    backup_count: 5
  
  # コンソール出力
  console:
    enabled: true
    colorize: true

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Feature Flags
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
features:
  static_analysis: true
  dynamic_tracing: true
  graph_control: true
  orchestration: true
  web_dashboard: true
  
  # 実験的機能
  experimental:
    auto_healing: false
    predictive_analysis: false

YAML

echo "✅ 設定ファイル作成完了"
wc -l config/observer_config.yaml

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# P0-T004: ベーステスト環境構築
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "⬜ P0-T004: ベーステスト環境構築"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# pytest設定
cat > tests/observer_enhanced/pytest.ini << 'INI'
[pytest]
minversion = 8.0
testpaths = tests/observer_enhanced
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=agents/observer_enhanced
    --cov-report=html
    --cov-report=term-missing

markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    slow: Slow running tests
INI

# __init__.py作成
cat > tests/observer_enhanced/__init__.py << 'PYTHON'
"""
Enhanced Observer System Tests
"""
PYTHON

# conftest.py（テスト共通設定）
cat > tests/observer_enhanced/conftest.py << 'PYTHON'
"""
pytest設定・フィクスチャ
"""

import pytest
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

@pytest.fixture
def project_root():
    """プロジェクトルートパス"""
    return Path('/workspaces/gemini_AI_Agent')

@pytest.fixture
def config_path():
    """設定ファイルパス"""
    return Path('/workspaces/gemini_AI_Agent/config/observer_config.yaml')

@pytest.fixture
def sample_python_file(tmp_path):
    """テスト用Pythonファイル"""
    file_path = tmp_path / "sample.py"
    file_path.write_text("""
import sys
import os
from pathlib import Path

class SampleClass:
    def method(self):
        pass
""")
    return file_path
PYTHON

echo "✅ テスト環境構築完了"

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# P0-T005: 既存システムバックアップ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "⬜ P0-T005: 既存システムバックアップ"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backups/system_backup_${BACKUP_DATE}.tar.gz"

# 既存システムファイルをバックアップ
tar -czf "$BACKUP_FILE" \
  agents/pm_agent.py \
  agents/task_executor.py \
  agents/review_agent.py \
  agents/automation/ \
  agents/system_observer/ \
  tools/knowledge_manager.py \
  tools/sheets_manager.py \
  tools/observability_manager.py \
  tools/file_version_manager.py \
  tools/api_validator.py \
  tools/integrated_diagnostics.py \
  tests/ \
  2>/dev/null

if [ -f "$BACKUP_FILE" ]; then
    echo "✅ バックアップ作成完了"
    ls -lh "$BACKUP_FILE"
    
    # バックアップ内容確認
    echo ""
    echo "📦 バックアップ内容:"
    tar -tzf "$BACKUP_FILE" | head -20
    
    # ファイル数カウント
    FILE_COUNT=$(tar -tzf "$BACKUP_FILE" | wc -l)
    echo ""
    echo "📊 バックアップファイル数: ${FILE_COUNT}個"
else
    echo "❌ バックアップ失敗"
    exit 1
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Phase 0 完了判定
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Phase 0 完了判定"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# チェックリスト
CHECKS_PASSED=0
CHECKS_TOTAL=5

echo "1. ディレクトリ構造"
if [ -d "agents/observer_enhanced" ]; then
    echo "   ✅ agents/observer_enhanced 存在"
    ((CHECKS_PASSED++))
else
    echo "   ❌ agents/observer_enhanced 不在"
fi

echo "2. 依存関係"
if python3 -c "import networkx, flask, pytz, yaml" 2>/dev/null; then
    echo "   ✅ 全パッケージインストール済み"
    ((CHECKS_PASSED++))
else
    echo "   ❌ パッケージ不足"
fi

echo "3. 設定ファイル"
if [ -f "config/observer_config.yaml" ]; then
    echo "   ✅ observer_config.yaml 存在"
    ((CHECKS_PASSED++))
else
    echo "   ❌ 設定ファイル不在"
fi

echo "4. テスト環境"
if [ -f "tests/observer_enhanced/conftest.py" ]; then
    echo "   ✅ テスト環境構築済み"
    ((CHECKS_PASSED++))
else
    echo "   ❌ テスト環境未構築"
fi

echo "5. バックアップ"
if [ -f "$BACKUP_FILE" ]; then
    echo "   ✅ バックアップ作成済み"
    ((CHECKS_PASSED++))
else
    echo "   ❌ バックアップ未作成"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $CHECKS_PASSED -eq $CHECKS_TOTAL ]; then
    echo "✅ Phase 0 完了: ${CHECKS_PASSED}/${CHECKS_TOTAL}"
    echo ""
    
    # 所要時間
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    MINUTES=$((DURATION / 60))
    SECONDS=$((DURATION % 60))
    
    echo "⏱️  所要時間: ${MINUTES}分${SECONDS}秒"
    echo ""
    
    # ロードマップ更新指示
    echo "📝 次のステップ:"
    echo "   1. ロードマップのチェックシート更新"
    echo "      Phase 0のすべてのタスクを ⬜ → ✅ に変更"
    echo ""
    echo "   2. Git commit"
    echo "      git add ."
    echo "      git commit -m 'Phase 0 Complete: Setup (5/5 tasks)'"
    echo ""
    echo "   3. Phase 1開始"
    echo "      bash sh/phase1_static_analysis.sh"
    echo ""
else
    echo "❌ Phase 0 未完了: ${CHECKS_PASSED}/${CHECKS_TOTAL}"
    echo "   上記のエラーを修正してください"
    exit 1
fi

