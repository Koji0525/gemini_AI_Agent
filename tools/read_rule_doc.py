#!/usr/bin/env python3
"""
ルールドキュメント読み込みツール

AIが簡単にドキュメントを読めるようにする
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from dotenv import load_dotenv
load_dotenv('.env')

from tools.sheets_manager import GoogleSheetsManager

def read_rule_doc(rule_id: str = None, section: str = None):
    """
    ルールドキュメントを読み込む
    
    Args:
        rule_id: ルールID（例: R013）
        section: セクション名（例: architecture）
    """
    
    doc_path = Path('docs/DEVELOPMENT_RULES.md')
    
    if not doc_path.exists():
        print("❌ docs/DEVELOPMENT_RULES.md が存在しません")
        return
    
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ルールIDから検索
    if rule_id:
        sheets = GoogleSheetsManager(
            spreadsheet_id=os.getenv("SPREADSHEET_ID"),
            service_account_file="configuration/service_account.json"
        )
        
        spreadsheet = sheets.gc.open_by_key(os.getenv("SPREADSHEET_ID"))
        rules_sheet = spreadsheet.worksheet('dev_rules')
        
        all_data = rules_sheet.get_all_values()
        
        for row in all_data[1:]:
            if row[0] == rule_id:
                category = row[1]
                summary = row[2]
                
                print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"[{rule_id}] {summary}")
                print(f"カテゴリ: {category}")
                print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print()
                
                # カテゴリに対応するセクションを表示
                section = category
                break
    
    # セクション指定がある場合
    if section:
        # セクション見出しを探す
        lines = content.split('\n')
        in_section = False
        section_content = []
        
        for line in lines:
            if f"#{section}" in line.lower() or section.lower() in line.lower():
                in_section = True
            
            if in_section:
                section_content.append(line)
                
                # 次のメインセクション（## ）で終了
                if line.startswith('## ') and len(section_content) > 1:
                    # 最後の行は除外（次のセクションの見出し）
                    section_content = section_content[:-1]
                    break
        
        if section_content:
            print('\n'.join(section_content))
        else:
            print(f"⚠️  セクション '{section}' が見つかりません")
    else:
        # 全体を表示
        print(content)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ルールドキュメント読み込み')
    parser.add_argument('--rule-id', help='ルールID（例: R013）')
    parser.add_argument('--section', help='セクション名（例: architecture）')
    parser.add_argument('--all', action='store_true', help='全体を表示')
    
    args = parser.parse_args()
    
    if args.all:
        read_rule_doc()
    else:
        read_rule_doc(args.rule_id, args.section)
