#!/usr/bin/env python3
"""ルール更新ヘルパー"""


def update_rule_interactive():
    """対話式ルール更新"""

    print("🔧 運用ルール更新")
    print()

    rule_id = input("ルールID (例: R001): ")
    field = input("変更項目 (summary/command/priority): ")
    new_value = input("新しい値: ")
    reason = input("変更理由: ")

    # シート更新（省略）
    # 履歴記録（省略）

    print(f"\n✅ {rule_id} の {field} を更新しました")
    print(f"   新しい値: {new_value}")
    print(f"   理由: {reason}")


if __name__ == "__main__":
    update_rule_interactive()
