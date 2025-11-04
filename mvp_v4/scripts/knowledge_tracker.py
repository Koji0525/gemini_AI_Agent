"""
ナレッジ成功率の自動追跡
"""
import json
from datetime import datetime

class KnowledgeTracker:
    """ナレッジの使用状況と成功率を追跡"""
    
    def __init__(self, kb_file='mvp_v4/knowledge/learned/conversation_knowledge_v3.json'):
        self.kb_file = kb_file
        self.usage_log_file = 'mvp_v4/knowledge/learned/usage_log.json'
    
    def record_usage(self, knowledge_id, success=True):
        """
        ナレッジ使用を記録
        
        使い方:
        tracker = KnowledgeTracker()
        tracker.record_usage("CONV_20251104_012824", success=True)
        """
        # 使用ログ読み込み
        try:
            with open(self.usage_log_file, 'r') as f:
                usage_log = json.load(f)
        except FileNotFoundError:
            usage_log = {}
        
        # 記録追加
        if knowledge_id not in usage_log:
            usage_log[knowledge_id] = {
                "total_uses": 0,
                "successes": 0,
                "failures": 0,
                "history": []
            }
        
        usage_log[knowledge_id]["total_uses"] += 1
        if success:
            usage_log[knowledge_id]["successes"] += 1
        else:
            usage_log[knowledge_id]["failures"] += 1
        
        usage_log[knowledge_id]["history"].append({
            "timestamp": datetime.now().isoformat(),
            "success": success
        })
        
        # 保存
        with open(self.usage_log_file, 'w') as f:
            json.dump(usage_log, f, indent=2, ensure_ascii=False)
        
        # 成功率計算
        total = usage_log[knowledge_id]["total_uses"]
        success_count = usage_log[knowledge_id]["successes"]
        actual_rate = success_count / total if total > 0 else 0
        
        print(f"✅ 使用記録: {knowledge_id}")
        print(f"   実績成功率: {actual_rate*100:.0f}% ({success_count}/{total}回)")
        
        return actual_rate
    
    def update_success_rate(self, knowledge_id):
        """ナレッジベースの成功率を実績に基づいて更新"""
        try:
            with open(self.usage_log_file, 'r') as f:
                usage_log = json.load(f)
        except FileNotFoundError:
            print("⚠️ 使用ログが見つかりません")
            return
        
        if knowledge_id not in usage_log:
            print("⚠️ このナレッジの使用記録がありません")
            return
        
        # 実績成功率を計算
        total = usage_log[knowledge_id]["total_uses"]
        successes = usage_log[knowledge_id]["successes"]
        actual_rate = successes / total if total > 0 else 0
        
        # 最低5回の使用実績がある場合のみ更新
        if total < 5:
            print(f"⚠️ 使用回数が少ないため更新しません（{total}/5回）")
            return
        
        # ナレッジベース更新
        with open(self.kb_file, 'r') as f:
            data = json.load(f)
        
        updated = False
        for kb in data['knowledge_base']:
            if kb.get('id') == knowledge_id:
                old_rate = kb.get('success_rate', 0)
                kb['success_rate'] = actual_rate
                kb['success_rate_source'] = 'measured'  # 実測値
                kb['total_uses'] = total
                updated = True
                
                print(f"✅ 成功率更新: {old_rate*100:.0f}% → {actual_rate*100:.0f}%")
                break
        
        if updated:
            with open(self.kb_file, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # テスト
    tracker = KnowledgeTracker()
    
    # 使用例1: 成功
    tracker.record_usage("TEST_001", success=True)
    
    # 使用例2: 失敗
    tracker.record_usage("TEST_001", success=False)
    
    # 使用例3: 成功
    tracker.record_usage("TEST_001", success=True)
    
    print("\n実績に基づく更新:")
    tracker.update_success_rate("TEST_001")
