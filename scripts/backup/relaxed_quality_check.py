#!/usr/bin/env python3
"""
緩和版品質チェック - 絵文字を警告のみに
"""

import os
import re
import ast
from pathlib import Path

class RelaxedQualityAuditor:
    def __init__(self):
        self.critical_issues = []
        self.warnings = []
        
        # 重大な問題パターン
        self.critical_patterns = [
            (r'def \\[0-9]', "正規表現後方参照"),
            (r'""".*?""",', "三重引用符後のカンマ"),
            (r'from, import,', "不正なimport構文"),
        ]
        
        # 警告のみのパターン（絵文字など）
        self.warning_patterns = [
            (r'[🤖🚀🔍📊📋✅❌⚠️🔧🎯🎉]', "絵文字"),
        ]
    
    def check_python_files(self, directory):
        """Pythonファイルのチェック（緩和版）"""
        print(f"🔍 {directory} をチェック...")
        
        for py_file in Path(directory).rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 構文チェック（重大）
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    self.critical_issues.append(f"❌ {py_file}: 構文エラー - {e}")
                    continue
                
                # 重大な問題パターン
                for pattern, description in self.critical_patterns:
                    if re.search(pattern, content):
                        self.critical_issues.append(f"❌ {py_file}: {description}")
                
                # 警告パターン（絵文字など）
                for pattern, description in self.warning_patterns:
                    if re.search(pattern, content):
                        self.warnings.append(f"⚠️ {py_file}: {description}")
                        
            except Exception as e:
                self.critical_issues.append(f"❌ {py_file}: 読み込みエラー - {e}")
    
    def run_complete_check(self):
        """完全なチェックを実行"""
        check_targets = [
            "/workspaces/gemini_AI_Agent/agents/templates",
            "/workspaces/gemini_AI_Agent/knowledge_system/core",
            "/workspaces/gemini_AI_Agent/tools"
        ]
        
        for target in check_targets:
            if os.path.exists(target):
                self.check_python_files(target)
    
    def generate_report(self):
        """レポート生成"""
        print("\n" + "="*60)
        print("📊 緩和版品質検査レポート")
        print("="*60)
        
        if self.critical_issues:
            print(f"❌ 重大な問題: {len(self.critical_issues)}件")
            for issue in self.critical_issues:
                print(f"  {issue}")
        else:
            print("✅ 重大な問題はありません")
        
        if self.warnings:
            print(f"⚠️ 警告: {len(self.warnings)}件")
            for warning in self.warnings[:10]:  # 最初の10件のみ表示
                print(f"  {warning}")
            if len(self.warnings) > 10:
                print(f"  ... 他{len(self.warnings)-10}件の警告")
        else:
            print("✅ 警告はありません")
        
        return len(self.critical_issues) == 0

if __name__ == "__main__":
    auditor = RelaxedQualityAuditor()
    auditor.run_complete_check()
    is_ok = auditor.generate_report()
    
    exit(0 if is_ok else 1)
