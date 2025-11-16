#!/usr/bin/env python3
"""
会話ナレッジシステム v2.0 セットアップスクリプト
"""
import os


def create_extractor_v2():
    """conversation_to_knowledge_v2.py 作成"""

    code = '''"""
会話ナレッジ抽出システム v2.0
品質チェック・重複排除・自動整理機能付き
"""
import json
import re
import hashlib
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class KnowledgeQualityScore:
    """ナレッジ品質スコア"""
    completeness: float
    specificity: float
    clarity: float
    usefulness: float
    total: float
    
    def is_high_quality(self) -> bool:
        return self.total >= 7.0

class ConversationKnowledgeExtractorV2:
    """会話からナレッジを抽出（v2.0）"""
    
    def __init__(self):
        self.extracted_knowledge = []
        self.knowledge_hashes = set()
    
    def extract_from_format(self, text: str) -> Optional[Dict]:
        """標準フォーマットから抽出"""
        knowledge = {
            "id": f"CONV_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "task_type": "general",
            "scenario": "",
            "best_practice": "",
            "code_example": "",
            "success_rate": 0.0,
            "avg_execution_time": 0.0,
            "conditions": [],
            "avoid_patterns": [],
            "error_fixes": {},
            "created_at": datetime.now().isoformat()
        }
        
        # 何が起きた
        what_patterns = [
            r'何が起きた[：:]\\\\\s*(.+?)(?=\\\n|原因|狙い|###|$)',
            r'### 何が起きた\\\n(.+?)(?=\\\n###|$)',
        ]
        
        for pattern in what_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                knowledge["scenario"] = match.group(1).strip()
                break
        
        # 原因
        cause_patterns = [
            r'原因[：:]\\\\\s*(.+?)(?=\\\n|狙い|###|$)',
            r'### 原因\\\n(.+?)(?=\\\n###|$)',
        ]
        
        for pattern in cause_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                knowledge["avoid_patterns"] = [match.group(1).strip()]
                break
        
        # 狙い
        goal_patterns = [
            r'狙い[：:]\\\\\s*(.+?)(?=\\\n###|$)',
            r'### 狙い.*?\\\n(.+?)(?=\\\n###|$)',
        ]
        
        for pattern in goal_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                knowledge["best_practice"] = match.group(1).strip()
                break
        
        # コード例
        code_match = re.search(r'```(?:bash|python|javascript)?\\\n(.+?)\\\n```', text, re.DOTALL)
        if code_match:
            knowledge["code_example"] = code_match.group(1).strip()
        
        # 成功率
        success_match = re.search(r'成功率[：:]\\\\\s*(\\\d+)%', text)
        if success_match:
            knowledge["success_rate"] = float(success_match.group(1)) / 100
        
        # タスクタイプ自動推定
        knowledge["task_type"] = self._infer_task_type(knowledge)
        
        # エラー修正方法
        if "Error" in knowledge["scenario"]:
            error_type = re.search(r'(\\\w+Error)', knowledge["scenario"])
            if error_type and knowledge["best_practice"]:
                knowledge["error_fixes"][error_type.group(1)] = knowledge["best_practice"]
        
        return knowledge if knowledge["scenario"] else None
    
    def _infer_task_type(self, knowledge: Dict) -> str:
        """タスクタイプを自動推定"""
        scenario = knowledge.get("scenario", "").lower()
        
        type_keywords = {
            "wordpress": ["wordpress", "wp_", "記事投稿"],
            "design": ["デザイン", "ワイヤーフレーム", "figma"],
            "troubleshooting": ["error", "エラー", "解決"],
            "api": ["api", "認証", "トークン"],
            "database": ["データベース", "sql", "mysql"],
        }
        
        for task_type, keywords in type_keywords.items():
            if any(kw in scenario for kw in keywords):
                return task_type
        
        return "general"
    
    def calculate_quality_score(self, knowledge: Dict) -> KnowledgeQualityScore:
        """ナレッジ品質スコア算出"""
        # 1. 完全性（0-3点）
        completeness = 0.0
        if knowledge.get('scenario'):
            completeness += 1.5
        if knowledge.get('best_practice'):
            completeness += 1.5
        if knowledge.get('code_example'):
            completeness = 3.0
        
        # 2. 具体性（0-3点）
        specificity = 0.0
        if knowledge.get('code_example'):
            specificity += 1.5
        if knowledge.get('success_rate', 0) > 0:
            specificity += 1.0
        if re.search(r'\\\d+', knowledge.get('best_practice', '')):
            specificity += 0.5
        
        # 3. 明確性（0-2点）
        clarity = 2.0
        ambiguous = ['なんか', 'たぶん', 'なんとなく']
        text = f"{knowledge.get('scenario', '')} {knowledge.get('best_practice', '')}"
        for word in ambiguous:
            if word in text:
                clarity -= 0.5
        clarity = max(0, clarity)
        
        # 4. 有用性（0-2点）
        usefulness = 0.0
        if knowledge.get('code_example'):
            usefulness += 1.0
        if knowledge.get('error_fixes'):
            usefulness += 1.0
        
        total = completeness + specificity + clarity + usefulness
        
        return KnowledgeQualityScore(
            completeness=completeness,
            specificity=specificity,
            clarity=clarity,
            usefulness=usefulness,
            total=round(total, 1)
        )
    
    def check_duplicate(self, knowledge: Dict) -> bool:
        """重複チェック"""
        content = f"{knowledge.get('scenario', '')}{knowledge.get('best_practice', '')}"
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        if content_hash in self.knowledge_hashes:
            return True
        
        self.knowledge_hashes.add(content_hash)
        return False
    
    def save_knowledge(self, knowledge: Dict, output_file: str = "mvp_v4/knowledge/learned/conversation_knowledge_v2.json"):
        """品質チェック付きでナレッジ保存"""
        import os
        
        quality = self.calculate_quality_score(knowledge)
        knowledge["quality_score"] = quality.total
        
        print(f"\\n📊 品質スコア: {quality.total}/10")
        print(f"  - 完全性: {quality.completeness}/3")
        print(f"  - 具体性: {quality.specificity}/3")
        print(f"  - 明確性: {quality.clarity}/2")
        print(f"  - 有用性: {quality.usefulness}/2")
        
        if not quality.is_high_quality():
            print(f"⚠️ 品質基準未達（7点以上必要）")
            return False
        
        if self.check_duplicate(knowledge):
            print(f"⚠️ 重複ナレッジ検出")
            return False
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"knowledge_base": []}
        
        data["knowledge_base"].append(knowledge)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 高品質ナレッジ保存完了")
        print(f"   ID: {knowledge['id']}")
        print(f"   タイプ: {knowledge['task_type']}")
        
        return True

if __name__ == "__main__":
    print("\\n" + "="*70)
    print("🧪 会話ナレッジ抽出システム v2.0 テスト")
    print("="*70)
    
    extractor = ConversationKnowledgeExtractorV2()
    
    # テスト: 高品質ナレッジ
    test_text = """
何が起きた: ChromaDBのインデックス構築時にメモリ不足エラー
原因: ドキュメント数が1万件を超えるとRAM 2GBでは不足
狙い: バッチサイズを1000件ごとに分割してインデックス構築
成功率: 95%
    """
    
    kb = extractor.extract_from_format(test_text)
    if kb:
        extractor.save_knowledge(kb)
    
    print("\\n✅ テスト完了")
'''

    os.makedirs("mvp_v4/scripts", exist_ok=True)
    with open("mvp_v4/scripts/conversation_to_knowledge_v2.py", "w", encoding="utf-8") as f:
        f.write(code)

    print("✅ conversation_to_knowledge_v2.py 作成完了")


def create_templates():
    """テンプレートファイル作成"""

    template = """# 🤖 Claude用ナレッジ登録プロンプト

## 📋 基本的な使い方

Claudeに以下のように依頼してください：
```
このエラー/タスクの解決方法を、以下のフォーマットで出力してください：

何が起きた: （1行で明確に）
原因: （具体的に）
狙い: （解決方法を実行可能な形で）
成功率: XX%
```

## 💡 出力例
```
何が起きた: ModuleNotFoundError: No module named 'llama_index.vector_stores'
原因: LlamaIndex v0.10以降でモジュールが分離された
狙い: pip install llama-index-vector-stores-chroma で個別インストール
成功率: 100%
```
"""

    os.makedirs("mvp_v4/templates", exist_ok=True)
    with open("mvp_v4/templates/CLAUDE_PROMPT_SIMPLE.md", "w", encoding="utf-8") as f:
        f.write(template)

    print("✅ Claude用テンプレート作成完了")


def main():
    print("\n" + "=" * 70)
    print("🚀 会話ナレッジシステム v2.0 セットアップ")
    print("=" * 70 + "\n")

    create_extractor_v2()
    create_templates()

    print("\n" + "=" * 70)
    print("✅ セットアップ完了！")
    print("=" * 70)
    print("\n【使い方】\n")
    print("1. Claudeに依頼:")
    print("   cat mvp_v4/templates/CLAUDE_PROMPT_SIMPLE.md")
    print("\n2. ナレッジ抽出テスト:")
    print("   python3 mvp_v4/scripts/conversation_to_knowledge_v2.py")
    print("\n3. 実際の使用:")
    print("   python3 << 'EOF'")
    print(
        "from mvp_v4.scripts.conversation_to_knowledge_v2 import ConversationKnowledgeExtractorV2"
    )
    print("")
    print("text = '''")
    print("何が起きた: （Claudeの出力を貼り付け）")
    print("原因: ...")
    print("狙い: ...")
    print("'''")
    print("")
    print("extractor = ConversationKnowledgeExtractorV2()")
    print("kb = extractor.extract_from_format(text)")
    print("if kb:")
    print("    extractor.save_knowledge(kb)")
    print("EOF")
    print("")


if __name__ == "__main__":
    main()
