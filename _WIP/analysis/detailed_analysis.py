#!/usr/bin/env python3
"""
詳細調査: なぜこんなに多いのか？
初心者向け解説付き
"""

import os
from pathlib import Path

def detailed_analysis():
    print("🔍 詳細調査レポート")
    print("=" * 70)
    
    # 1. browser_data/ の正体
    print("\n" + "=" * 70)
    print("📂 1. browser_data/Default/Code Cache/js (509ファイル)")
    print("=" * 70)
    print("""
🎯 これは何？
→ Playwright（ブラウザ自動操作ツール）が作った**キャッシュファイル**

📝 詳しく説明:
あなたがブラウザでWebサイトを見る時、
・JavaScriptファイル
・画像
・CSSファイル
などをパソコンに保存（キャッシュ）します。
次に同じサイトを開くと速くなるためです。

Playwrightでブラウザを起動すると、
→ 自動的に browser_data/ フォルダが作られる
→ キャッシュファイルが大量に保存される

🚨 問題点:
・プログラムには**全く不要**
・509ファイルもある
・GitHub上でも不要
・毎回実行するたびに新しく作られる

✅ 結論: **完全に削除してOK！**

💡 対策:
1. 削除する
2. .gitignoreに追加（次から無視）
    """)
    
    # browser_data/の実際のファイルをサンプル表示
    print("\n📋 実際のファイル例:")
    cache_dir = Path("browser_data/Default/Code Cache/js")
    if cache_dir.exists():
        files = list(cache_dir.iterdir())[:5]
        for f in files:
            print(f"  - {f.name}")
        print(f"  ... 他{len(list(cache_dir.iterdir()))-5}個")
    
    # 2. ROOT直下152ファイルの正体
    print("\n" + "=" * 70)
    print("📂 2. ROOT直下 (152ファイル)")
    print("=" * 70)
    print("""
🎯 これは何？
→ プロジェクトのメインフォルダ（一番上のフォルダ）に
  ファイルが152個も散らばっている状態

📝 本来あるべき状態:
ROOT/
├── README.md（1個）
├── config.json（1個）
├── requirements.txt（1個）
├── scripts/（フォルダ）
├── core_agents/（フォルダ）
└── browser_control/（フォルダ）

👉 5-10個程度が理想

🚨 現状:
・Pythonスクリプト: 106個 ← 多すぎ！
・シェルスクリプト: 18個 ← 多すぎ！
・その他: 28個

📝 なぜこうなった？:
開発中に、
「とりあえずここに作ろう」
「テストファイルをここに」
「修正スクリプトをここに」
を繰り返した結果

✅ 結論: **大部分を整理すべき**

💡 対策:
1. テストスクリプト → _WIP/
2. 古いスクリプト → _ARCHIVE/
3. 本番で使うもの → scripts/
    """)
    
    # 実際のROOT直下ファイルをカテゴリ分類
    print("\n📋 ROOT直下のファイル分類:")
    root_files = [f for f in os.listdir('.') if os.path.isfile(f)]
    
    categories = {
        '�� テスト用': [],
        '🔧 修正用（一時）': [],
        '📊 分析用': [],
        '⚙️ 設定ファイル': [],
        '📝 ドキュメント': [],
        '❓ 不明': []
    }
    
    for f in root_files:
        if any(x in f for x in ['test', 'check', 'diagnose']):
            categories['🧪 テスト用'].append(f)
        elif any(x in f for x in ['fix', 'add_', 'organize']):
            categories['🔧 修正用（一時）'].append(f)
        elif any(x in f for x in ['analyze', 'compare', 'report']):
            categories['📊 分析用'].append(f)
        elif any(x in f for x in ['.json', '.yml', 'config']):
            categories['⚙️ 設定ファイル'].append(f)
        elif any(x in f for x in ['.md', 'README']):
            categories['📝 ドキュメント'].append(f)
        else:
            categories['❓ 不明'].append(f)
    
    for cat, files in categories.items():
        if files:
            print(f"\n  {cat} ({len(files)}個):")
            for f in files[:3]:
                print(f"    - {f}")
            if len(files) > 3:
                print(f"    ... 他{len(files)-3}個")
    
    # 3. no_extension 775ファイル
    print("\n" + "=" * 70)
    print("📂 3. no_extension (拡張子なし 775ファイル)")
    print("=" * 70)
    print("""
🎯 「拡張子なし」とは？
→ ファイル名に「.」がないファイル

�� 例:
・通常のファイル: document.txt ← 拡張子 .txt
・拡張子なし: document ← 拡張子なし

🤔 なぜこんなに多い？
→ ほとんどが browser_data/ のキャッシュファイル

📋 拡張子なしファイルの種類:
1. ブラウザキャッシュ（LevelDB等）
   → browser_data/内に大量にある
   → 数字だけの名前（000001, 000002等）
2. 設定ファイル（少数）
   → .gitignore, dockerfile 等
   → これは必要

✅ 結論: 
・ほとんどが**ブラウザキャッシュで不要**
・.gitignore等の設定ファイル数個だけ必要
    """)
    
    # 実際の no_extension ファイルの場所を調査
    print("\n📋 拡張子なしファイルの所在:")
    no_ext_locations = {}
    for root, dirs, files in os.walk('.'):
        if '.git' in root or 'node_modules' in root:
            continue
        for f in files:
            if '.' not in f:
                location = root.replace('./', '').split('/')[0] or 'ROOT'
                no_ext_locations[location] = no_ext_locations.get(location, 0) + 1
    
    for loc, count in sorted(no_ext_locations.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {count:4}個 : {loc}")
    
    # 4. ローカルブラウザデータの必要性
    print("\n" + "=" * 70)
    print("📂 4. ローカルブラウザデータは必要？")
    print("=" * 70)
    print("""
🎯 質問: GitHubに browser_data/ をアップロードすべき？

📝 答え: **絶対にNO！**

🤔 なぜ？

【ローカル（あなたのPC）】
browser_data/
├── セッション情報（ログイン状態）
├── Cookie（認証情報）
├── キャッシュ（速度向上）
└── 閲覧履歴

👉 ブラウザを起動するたびに**自動で作られる**
👉 あなたのPCでブラウザを動かすため**だけ**に必要

【GitHub（共有リポジトリ）】
❌ 他の人のセッション情報は不要
❌ 他の人のCookieは不要
❌ キャッシュは毎回違う
❌ 大量のファイルで容量を圧迫

✅ 結論:
・ローカルでは: 必要（自動生成されるから放置でOK）
・GitHubでは: **絶対に不要**（.gitignoreで除外）

💡 例え話:
あなたの部屋の「ゴミ箱」
・あなたの部屋では: 必要（ゴミを捨てる）
・友達の家に持っていく: 不要（意味不明）

browser_data/ = ゴミ箱みたいなもの
    """)
    
    # 5. まとめ
    print("\n" + "=" * 70)
    print("📊 まとめ")
    print("=" * 70)
    print("""
🗑️ 削除すべきファイル（安全）:
1. browser_data/ 全体（509+ファイル）
2. __pycache__/ 全フォルダ（45個の.pycファイル）
3. ROOT直下の一時スクリプト（約100個）
4. *.backup, *.old ファイル（28個）

📦 整理すべきファイル:
1. テストスクリプト → _WIP/
2. 分析スクリプト → _WIP/
3. 古いバックアップ → _ARCHIVE/

✅ 残すべきファイル:
1. core_agents/ (本番コード)
2. browser_control/ (本番コード)
3. scripts/ (本番コード)
4. README.md, config.json 等（設定）

📈 整理後の期待値:
・現在: 1378ファイル
・整理後: 約300ファイル（78%削減）
    """)

if __name__ == "__main__":
    detailed_analysis()
