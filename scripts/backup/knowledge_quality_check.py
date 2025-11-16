#!/usr/bin/env python3
"""
ナレッジ品質チェックシステム
悪いデータがナレッジベースに混入していないかを検出
"""
import os
import re
import ast
import json
from pathlib import Path
import sqlite3

class KnowledgeQualityAuditor:
    def __init__(self):
        self.issues = []
        self.banned_patterns = [
            (r'def \\[0-9]', "正規表現後方参照"),
            (r'[🤖🚀🔍📊📋✅❌⚠️🔧🎯🎉]', "絵文字"),
            (r'""".*?""",', "三重引用符後のカンマ"),
            (r'from, import,', "不正なimport構文"),
            (r'SyntaxError', "エラーメッセージ"),
            (r'IndentationError', "インデントエラー"),
        ]
    
    def check_python_files(self, directory):
        """Pythonファイルの品質チェック"""
        print(f"🔍 {directory} のPythonファイルをチェック中...")
        
        for py_file in Path(directory).rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 構文チェック
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    self.issues.append(f"❌ {py_file}: 構文エラー - {e}")
                    continue
                
                # 禁止パターンチェック
                for pattern, description in self.banned_patterns:
                    if re.search(pattern, content):
                        self.issues.append(f"⚠️ {py_file}: {description}を検出")
                
            except Exception as e:
                self.issues.append(f"❌ {py_file}: 読み込みエラー - {e}")
    
    def check_json_files(self, directory):
        """JSONファイルの品質チェック"""
        print(f"🔍 {directory} のJSONファイルをチェック中...")
        
        for json_file in Path(directory).rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json.load(f)  # JSONとして読み込み可能かチェック
            except json.JSONDecodeError as e:
                self.issues.append(f"❌ {json_file}: JSON形式エラー - {e}")
            except Exception as e:
                self.issues.append(f"❌ {json_file}: 読み込みエラー - {e}")
    
    def check_sqlite_databases(self, directory):
        """SQLiteデータベースのチェック"""
        print(f"🔍 {directory} のデータベースファイルをチェック中...")
        
        for db_file in Path(directory).rglob("*.db"):
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # テーブル一覧を取得
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                # 各テーブルの整合性チェック
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table[0]} LIMIT 1")
                    except sqlite3.Error as e:
                        self.issues.append(f"❌ {db_file}.{table[0]}: テーブル整合性エラー - {e}")
                
                conn.close()
                
            except Exception as e:
                self.issues.append(f"❌ {db_file}: データベース接続エラー - {e}")
    
    def check_knowledge_integrity(self):
        """ナレッジベース全体の整合性チェック"""
        print("🎯 ナレッジベース全体の整合性チェックを開始...")
        
        check_targets = [
            "/workspaces/gemini_AI_Agent/knowledge_system",
            "/workspaces/gemini_AI_Agent/agents/templates", 
            "/workspaces/gemini_AI_Agent/agent_outputs",
            "/workspaces/gemini_AI_Agent/tools"
        ]
        
        for target in check_targets:
            if os.path.exists(target):
                self.check_python_files(target)
                self.check_json_files(target)
                self.check_sqlite_databases(target)
    
    def generate_report(self):
        """検査レポートの生成"""
        print("\\n" + "="*60)
        print("📊 ナレッジ品質検査レポート")
        print("="*60)
        
        if not self.issues:
            print("🎉 素晴らしい！問題は見つかりませんでした")
            return True
        else:
            print(f"⚠️ {len(self.issues)} 個の問題を検出:")
            for issue in self.issues:
                print(f"  {issue}")
            
            # レポートをファイルに保存
            report_file = Path("/workspaces/gemini_AI_Agent/backups/quality_audit_report.txt")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("ナレッジ品質検査レポート\\n")
                f.write("="*50 + "\\n")
                for issue in self.issues:
                    f.write(issue + "\\n")
            
            print(f"\\n📄 詳細レポート: {report_file}")
            return False

if __name__ == "__main__":
    auditor = KnowledgeQualityAuditor()
    auditor.check_knowledge_integrity()
    is_clean = auditor.generate_report()
    
    exit(0 if is_clean else 1)
