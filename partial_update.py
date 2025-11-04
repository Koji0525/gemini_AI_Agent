#!/bin/env python3
import sys

def update_file_section(filename, start_marker, end_marker, new_content):
    """ファイルの特定部分だけを更新"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    start_index = content.find(start_marker)
    end_index = content.find(end_marker, start_index)
    
    if start_index != -1 and end_index != -1:
        # 部分置換
        new_full_content = (content[:start_index] + 
                           start_marker + new_content + end_marker + 
                           content[end_index + len(end_marker):])
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_full_content)
        print(f"✅ {filename} の部分更新完了")
        return True
    else:
        print(f"❌ マーカーが見つかりません: {start_marker}")
        return False

# 使用例
if __name__ == "__main__":
    update_file_section(
        "autonomous_development_orchestrator.py",
        "# 2. オプションエージェントの初期化",
        "# 3. 開発サイクル実行",
        "\n            # ここに追加したいコード\n            print('部分更新成功')\n"
    )
