"""
厳格な品質評価器
実用化レベルを正確に判定
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class StrictQualityEvaluator:
    """厳格な品質評価器"""
    
    # 品質基準の定義
    MIN_LINES_FOR_PASS = 300  # 合格最低行数
    MIN_LINES_FOR_GOOD = 500  # 良好の最低行数
    MIN_SIZE_BYTES = 5000     # 合格最低バイト数
    
    def __init__(self):
        self.evaluation_results = []
        
    def evaluate_task_output(self, task_id: str, output_dir: str) -> Dict[str, Any]:
        """タスク成果物を厳格に評価"""
        print(f"\n{'=' * 80}")
        print(f"🔍 厳格品質評価: {task_id}")
        print('=' * 80)
        
        # 成果物の存在確認
        if not os.path.exists(output_dir):
            print(f"❌ 成果物ディレクトリが存在しません: {output_dir}")
            return self._create_failure_result(task_id, "成果物なし")
        
        # ファイル情報の収集
        files_info = self._collect_files_info(output_dir)
        
        if not files_info:
            print(f"❌ 成果物ファイルが見つかりません")
            return self._create_failure_result(task_id, "ファイルなし")
        
        # 詳細評価
        evaluation = self._evaluate_files(files_info)
        
        # 総合スコアの計算
        final_score = self._calculate_final_score(evaluation)
        
        # 実用性判定
        usability = self._judge_usability(evaluation, final_score)
        
        # 結果の表示
        self._print_evaluation_result(evaluation, final_score, usability)
        
        return {
            'task_id': task_id,
            'score': final_score,
            'usability': usability,
            'evaluation': evaluation,
            'pass': final_score >= 7.0
        }
    
    def _collect_files_info(self, output_dir: str) -> List[Dict[str, Any]]:
        """ファイル情報を収集"""
        files_info = []
        
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                # ファイルサイズ
                size_bytes = os.path.getsize(file_path)
                
                # 行数（テキストファイルのみ）
                lines = 0
                if file.endswith(('.py', '.md', '.txt', '.sh', '.yaml', '.json')):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = len(f.readlines())
                    except:
                        pass
                
                files_info.append({
                    'path': file_path,
                    'name': file,
                    'size_bytes': size_bytes,
                    'lines': lines
                })
        
        return files_info
    
    def _evaluate_files(self, files_info: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ファイルを評価"""
        total_lines = sum(f['lines'] for f in files_info)
        total_bytes = sum(f['size_bytes'] for f in files_info)
        file_count = len(files_info)
        
        # 実装ファイルの確認
        code_files = [f for f in files_info if f['name'].endswith(('.py', '.sh'))]
        doc_files = [f for f in files_info if f['name'].endswith(('.md', '.txt'))]
        
        has_readme = any(f['name'].lower() == 'readme.md' for f in files_info)
        has_code = len(code_files) > 0
        
        return {
            'total_lines': total_lines,
            'total_bytes': total_bytes,
            'file_count': file_count,
            'code_files': len(code_files),
            'doc_files': len(doc_files),
            'has_readme': has_readme,
            'has_code': has_code,
            'files_info': files_info
        }
    
    def _calculate_final_score(self, evaluation: Dict[str, Any]) -> float:
        """最終スコアを計算（10点満点）"""
        score = 0.0
        
        # 1. 行数評価（最大4点）
        total_lines = evaluation['total_lines']
        if total_lines >= 500:
            score += 4.0
        elif total_lines >= 300:
            score += 3.0
        elif total_lines >= 150:
            score += 2.0
        elif total_lines >= 50:
            score += 1.0
        else:
            score += 0.0  # 50行未満は0点
        
        # 2. サイズ評価（最大2点）
        total_bytes = evaluation['total_bytes']
        if total_bytes >= 10000:
            score += 2.0
        elif total_bytes >= 5000:
            score += 1.5
        elif total_bytes >= 1000:
            score += 1.0
        elif total_bytes >= 500:
            score += 0.5
        else:
            score += 0.0
        
        # 3. ファイル構成評価（最大2点）
        if evaluation['has_readme']:
            score += 0.5
        if evaluation['has_code']:
            score += 0.5
        if evaluation['file_count'] >= 3:
            score += 0.5
        if evaluation['code_files'] >= 1 and evaluation['doc_files'] >= 1:
            score += 0.5
        
        # 4. 実装の充実度（最大2点）
        if evaluation['code_files'] >= 2:
            score += 1.0
        elif evaluation['code_files'] >= 1:
            score += 0.5
        
        if evaluation['doc_files'] >= 2:
            score += 1.0
        elif evaluation['doc_files'] >= 1:
            score += 0.5
        
        return min(score, 10.0)
    
    def _judge_usability(self, evaluation: Dict[str, Any], score: float) -> str:
        """実用性を判定"""
        total_lines = evaluation['total_lines']
        total_bytes = evaluation['total_bytes']
        has_code = evaluation['has_code']
        
        # 実用化レベル（7点以上）
        if score >= 7.0 and total_lines >= 300 and has_code:
            return "実用化レベル"
        
        # 基本機能あり（5-7点）
        elif score >= 5.0 and total_lines >= 150:
            return "基本機能あり（要改善）"
        
        # プロトタイプレベル（3-5点）
        elif score >= 3.0 and total_lines >= 50:
            return "プロトタイプレベル"
        
        # 使用不可（3点未満）
        else:
            return "使用不可"
    
    def _create_failure_result(self, task_id: str, reason: str) -> Dict[str, Any]:
        """失敗結果を作成"""
        return {
            'task_id': task_id,
            'score': 0.0,
            'usability': '使用不可',
            'reason': reason,
            'pass': False
        }
    
    def _print_evaluation_result(self, evaluation: Dict[str, Any], score: float, usability: str):
        """評価結果を表示"""
        print("\n【成果物の詳細】")
        print(f"  総行数: {evaluation['total_lines']}行")
        print(f"  総サイズ: {evaluation['total_bytes']}バイト")
        print(f"  ファイル数: {evaluation['file_count']}個")
        print(f"  コードファイル: {evaluation['code_files']}個")
        print(f"  ドキュメント: {evaluation['doc_files']}個")
        print(f"  README: {'あり' if evaluation['has_readme'] else 'なし'}")
        
        print("\n【評価結果】")
        print(f"  総合スコア: {score:.1f}/10点")
        print(f"  実用性: {usability}")
        print(f"  合否: {'✅ 合格' if score >= 7.0 else '❌ 不合格'}")
        
        print("\n【判定基準】")
        print("  10点: 優秀（500行以上、完全な実装）")
        print("  7-9点: 実用化レベル（300行以上、基本機能完備）")
        print("  5-6点: 基本機能あり（150行以上、要改善）")
        print("  3-4点: プロトタイプレベル（50行以上）")
        print("  0-2点: 使用不可（50行未満または成果物なし）")
        
        # ファイル詳細
        if evaluation.get('files_info'):
            print("\n【ファイル詳細】")
            for file_info in evaluation['files_info'][:10]:  # 最大10ファイル
                print(f"  - {file_info['name']}: {file_info['lines']}行, {file_info['size_bytes']}バイト")

def main():
    """テスト実行"""
    evaluator = StrictQualityEvaluator()
    
    # テスト対象
    test_dirs = [
        "agent_outputs/implementation/6_進捗可視化ダッシュボード拡張_DORAメトリクス表示機能実装_05_20251119_114144",
        "agent_outputs/implementation/6_進捗可視化ダッシュボード拡張_DORAメトリクス表示機能実装_05_20251119_145633"
    ]
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            result = evaluator.evaluate_task_output("test_task", test_dir)
            print()

if __name__ == "__main__":
    main()

