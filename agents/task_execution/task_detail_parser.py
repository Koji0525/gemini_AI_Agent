#!/usr/bin/env python3
"""
pm_tasksシートから詳細情報を抽出
① 目的 ② タスク概要 ③ 成功基準 ④ コンテキスト情報
"""
import re
from typing import Dict, Any


class TaskDetailParser:
    """タスク詳細情報パーサー"""
    
    @staticmethod
    def parse_description(description: str) -> Dict[str, Any]:
        """
        説明文から詳細情報を抽出
        
        想定フォーマット:
        ① 目的：... ② タスク概要：... ③ 成功基準：... ④ コンテキスト情報：...
        """
        details = {
            'raw_description': description,
            'purpose': '',
            'overview': '',
            'success_criteria': '',
            'context': '',
            'has_details': False
        }
        
        # ①〜④のマーカーで分割
        patterns = {
            'purpose': r'①\s*目的[：:]\s*([^②]+)',
            'overview': r'②\s*タスク概要[：:]\s*([^③]+)',
            'success_criteria': r'③\s*成功基準[：:]\s*([^④]+)',
            'context': r'④\s*コンテキスト情報[：:]\s*(.+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, description)
            if match:
                details[key] = match.group(1).strip()
                details['has_details'] = True
        
        return details
    
    @staticmethod
    def parse_success_criteria(criteria_text: str) -> Dict[str, Any]:
        """
        成功基準を構造化
        
        例: "全247テストが成功、カバレッジ84.3%以上維持、テスト実行時間5分以内"
        """
        criteria = {
            'raw': criteria_text,
            'items': []
        }
        
        # カンマ、句点で分割
        items = re.split(r'[、,，]', criteria_text)
        criteria['items'] = [item.strip() for item in items if item.strip()]
        
        # 数値目標を抽出
        criteria['numeric_targets'] = {}
        
        # テスト数
        test_count_match = re.search(r'(\d+)\s*テスト', criteria_text)
        if test_count_match:
            criteria['numeric_targets']['test_count'] = int(test_count_match.group(1))
        
        # カバレッジ
        coverage_match = re.search(r'(\d+\.?\d*)\s*%', criteria_text)
        if coverage_match:
            criteria['numeric_targets']['coverage'] = float(coverage_match.group(1))
        
        # 時間
        time_match = re.search(r'(\d+)\s*分', criteria_text)
        if time_match:
            criteria['numeric_targets']['time_minutes'] = int(time_match.group(1))
        
        return criteria
    
    @staticmethod
    def parse_context(context_text: str) -> Dict[str, Any]:
        """
        コンテキスト情報を構造化
        
        例: "Python 3.10、pytest、既存テストスイート（tests/）、カバレッジレポート（coverage.xml）"
        """
        context = {
            'raw': context_text,
            'technologies': [],
            'files': [],
            'directories': []
        }
        
        # 技術スタック
        tech_keywords = ['python', 'pytest', 'nodejs', 'react', 'docker', 'kubernetes']
        for tech in tech_keywords:
            if tech.lower() in context_text.lower():
                # バージョン情報も抽出
                version_match = re.search(rf'{tech}\s+(\d+\.?\d*\.?\d*)', context_text, re.IGNORECASE)
                if version_match:
                    context['technologies'].append(f"{tech} {version_match.group(1)}")
                else:
                    context['technologies'].append(tech)
        
        # ファイル名抽出（括弧内）
        file_matches = re.findall(r'\(([^)]+\.\w+)\)', context_text)
        context['files'].extend(file_matches)
        
        # ディレクトリ抽出
        dir_matches = re.findall(r'\(([^)]+/)\)', context_text)
        context['directories'].extend(dir_matches)
        
        return context


if __name__ == '__main__':
    # テスト
    test_desc = "① 目的：既存システムの健全性を確保し、新機能開発の基盤を固める ② タスク概要：既存の247テストをすべて実行し、84.3%以上のカバレッジを確認する ③ 成功基準：全247テストが成功、カバレッジ84.3%以上維持、テスト実行時間5分以内 ④ コンテキスト情報：Python 3.10、pytest、既存テストスイート（tests/）、カバレッジレポート（coverage.xml）"
    
    parser = TaskDetailParser()
    details = parser.parse_description(test_desc)
    
    print("詳細情報:")
    print(f"  目的: {details['purpose']}")
    print(f"  概要: {details['overview']}")
    print(f"  成功基準: {details['success_criteria']}")
    print(f"  コンテキスト: {details['context']}")
    
    criteria = parser.parse_success_criteria(details['success_criteria'])
    print(f"\n成功基準（構造化）:")
    print(f"  項目: {criteria['items']}")
    print(f"  数値目標: {criteria['numeric_targets']}")
    
    context = parser.parse_context(details['context'])
    print(f"\nコンテキスト（構造化）:")
    print(f"  技術: {context['technologies']}")
    print(f"  ファイル: {context['files']}")
    print(f"  ディレクトリ: {context['directories']}")
