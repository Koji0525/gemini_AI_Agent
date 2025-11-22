"""
拡張APIエンドポイント

このモジュールは、Phase 8で追加された拡張機能のAPIを提供します。
既存のapi_endpoints.pyは変更せず、新規ファイルとして実装。
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.observer_enhanced.hidden_dependency_detector import HiddenDependencyDetector
from agents.observer_enhanced.change_impact_analyzer import ChangeImpactAnalyzer
from agents.observer_enhanced.code_intelligence import CodeIntelligence
from agents.observer_enhanced.breaking_change_detector import BreakingChangeDetector

app = Flask(__name__)
CORS(app)

# 各エンジンの初期化
hidden_detector = HiddenDependencyDetector()
impact_analyzer = ChangeImpactAnalyzer()
code_intel = CodeIntelligence()
breaking_detector = BreakingChangeDetector()


@app.route('/api/hidden-dependencies', methods=['GET'])
def get_hidden_dependencies():
    """隠れた依存関係を取得"""
    try:
        results = hidden_detector.scan_project()
        return jsonify({
            'total': len(results),
            'file_io': len([r for r in results if r['type'] == 'file_io']),
            'env_vars': len([r for r in results if r['type'] == 'env_var']),
            'external_commands': len([r for r in results if r['type'] == 'external_command']),
            'details': results[:10]  # 最初の10件のみ
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/change-impact', methods=['GET'])
def get_change_impact():
    """変更影響範囲を取得"""
    try:
        file_path = request.args.get('file')
        if file_path:
            impact = impact_analyzer.analyze_file_change(file_path)
        else:
            # 最新のGit変更を自動検出
            impact = impact_analyzer.analyze_recent_changes()
        
        return jsonify(impact)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/code-search', methods=['GET'])
def search_code():
    """セマンティックコード検索"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'クエリが必要です'}), 400
        
        results = code_intel.search(query, top_k=10)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/breaking-changes', methods=['GET'])
def detect_breaking_changes():
    """破壊的変更を検出"""
    try:
        file_path = request.args.get('file')
        if not file_path:
            return jsonify({'error': 'ファイルパスが必要です'}), 400
        
        changes = breaking_detector.detect(file_path)
        return jsonify({
            'has_breaking_changes': len(changes) > 0,
            'changes': changes
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health-extended', methods=['GET'])
def get_extended_health():
    """拡張ヘルスチェック（全機能統合）"""
    try:
        # 既存のヘルスチェック
        from agents.observer_enhanced.health_checker import HealthChecker
        health_checker = HealthChecker()
        base_health = health_checker.calculate_score()
        
        # 拡張情報を追加
        hidden_deps = hidden_detector.scan_project()
        
        return jsonify({
            **base_health,
            'extended': {
                'hidden_dependencies': len(hidden_deps),
                'code_search_available': code_intel.is_ready(),
                'breaking_change_detector_active': True
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("🚀 拡張APIサーバー起動中...")
    print("   ポート: 5002")
    print("   エンドポイント:")
    print("   - /api/hidden-dependencies")
    print("   - /api/change-impact")
    print("   - /api/code-search")
    print("   - /api/breaking-changes")
    print("   - /api/health-extended")
    
    app.run(host='0.0.0.0', port=5002, debug=True)
