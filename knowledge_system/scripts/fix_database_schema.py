#!/usr/bin/env python3
import os
import sqlite3


def fix_database_schema():
    db_path = "../database/knowledge.db"
    if not os.path.exists(db_path):
        print(f"❌ データベースファイルが見つかりません: {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 現在のスキーマを確認
        cursor.execute("PRAGMA table_info(knowledge_entries)")
        columns = cursor.fetchall()
        print("📋 現在のスキーマ:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - NULL: {col[3]}, Default: {col[4]}")

        # scenarioカラムが必須か確認
        scenario_col = [col for col in columns if col[1] == "scenario"]
        if scenario_col:
            print("✅ scenarioカラムが見つかりました")
            # scenarioカラムにデフォルト値を設定
            try:
                cursor.execute(
                    "ALTER TABLE knowledge_entries ADD COLUMN scenario_temp TEXT DEFAULT 'general'"
                )
                cursor.execute(
                    "UPDATE knowledge_entries SET scenario_temp = scenario WHERE scenario IS NOT NULL"
                )
                cursor.execute("ALTER TABLE knowledge_entries DROP COLUMN scenario")
                cursor.execute(
                    "ALTER TABLE knowledge_entries RENAME COLUMN scenario_temp TO scenario"
                )
                print("✅ scenarioカラムにデフォルト値を設定しました")
            except Exception as e:
                print(f"⚠️  scenarioカラム修正中にエラー: {e}")

        conn.commit()
        conn.close()
        print("✅ データベーススキーマ修正完了")
        return True

    except Exception as e:
        print(f"❌ データベース修正失敗: {e}")
        return False


if __name__ == "__main__":
    fix_database_schema()
