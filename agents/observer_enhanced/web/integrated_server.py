# パフォーマンス最適化を適用
from agents.observer_enhanced.performance_optimizer import apply_all_optimizations
apply_all_optimizations()

"""
統合Webサーバー

既存APIエンドポイント（ポート5001）と
拡張APIエンドポイント（ポート5002）と
完全版ダッシュボードを1つのサーバーで提供

ポート: 5003
"""

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import sys
import os
from pathlib import Path

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.observer_enhanced.hidden_dependency_detector import HiddenDependencyDetector
from agents.observer_enhanced.change_impact_analyzer import ChangeImpactAnalyzer
from agents.observer_enhanced.code_intelligence import CodeIntelligence
from agents.observer_enhanced.breaking_change_detector import BreakingChangeDetector

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
CORS(app)

# 検出エンジン初期化
dependency_detector = HiddenDependencyDetector()
impact_analyzer = ChangeImpactAnalyzer()
code_search = CodeIntelligence()
breaking_detector = BreakingChangeDetector()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ダッシュボードUI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/')
def index():
    """完全版ダッシュボード"""
    return render_template('complete_dashboard.html')

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APIエンドポイント（拡張機能）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/health', methods=['GET'])
def health_check():
    """ヘルスチェック"""
    return jsonify({
        "status": "ok",
        "version": "2.0.0",
        "features": [
            "dependencies",
            "impact",
            "search",
            "breaking"
        ]
    })


@app.route('/api/dependencies/scan', methods=['POST'])
def scan_dependencies():
    """依存関係スキャン"""
    try:
        dependencies = dependency_detector.scan_project()
        report = dependency_detector.generate_report(dependencies)
        return jsonify({"status": "success", "data": report})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/search/code', methods=['POST'])
def search_code():
    """コード検索"""
    try:
        data = request.get_json()
        query = data.get('query')
        search_type = data.get('search_type', 'auto')
        max_results = data.get('max_results', 10)
        
        if not query:
            return jsonify({"status": "error", "message": "query required"}), 400
        
        results = code_search.search(query, search_type, max_results)
        
        response_data = [
            {
                "file_path": r.file_path,
                "line_number": r.line_number,
                "code_snippet": r.code_snippet,
                "similarity_score": r.similarity_score
            }
            for r in results
        ]
        
        return jsonify({"status": "success", "data": response_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/impact/analyze', methods=['POST'])
def analyze_impact():
    """変更影響分析"""
    try:
        data = request.get_json() or {}
        since = data.get('since', 'HEAD~1')
        
        impacts = impact_analyzer.analyze_all_changes(since=since)
        report = impact_analyzer.generate_report(impacts)
        
        return jsonify({"status": "success", "data": report})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/breaking/detect', methods=['POST'])
def detect_breaking():
    """破壊的変更検出"""
    try:
        data = request.get_json() or {}
        since = data.get('since', 'HEAD~1')
        
        changes = breaking_detector.detect_all_breaking_changes(since=since)
        
        response_data = [
            {
                "file_path": c.file_path,
                "change_type": c.change_type,
                "old_value": c.old_value,
                "new_value": c.new_value,
                "severity": c.severity
            }
            for c in changes
        ]
        
        return jsonify({"status": "success", "data": response_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# サーバー起動
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == '__main__':
    print("""
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🚀 Enhanced Observer - Integrated Server
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    Dashboard: http://0.0.0.0:5003/
    API Base:  http://0.0.0.0:5003/api/
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    app.run(host='0.0.0.0', port=5003, debug=False)
