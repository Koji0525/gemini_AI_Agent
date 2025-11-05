#!/usr/bin/env python3
"""
RAG自動起動スクリプト - 完全重複防止版
"""
import os
import sys
import time
import fcntl


def main():
    # ロックファイル方式で重複起動防止
    lock_file = "/tmp/rag_auto_start.lock"
    try:
        lock_fd = open(lock_file, "w")
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        # 既に他のプロセスが実行中
        return True

    start_time = time.time()

    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from rag_engine_persistent_v2 import get_rag_engine_v2

        rag_engine = get_rag_engine_v2(["mvp_v4/knowledge/learned/conversation_knowledge_v3.json"])
        load_time = time.time() - start_time

        # 1秒以上かかった場合のみ表示
        if load_time >= 1.0:
            stats = rag_engine.get_stats()
            print(f"🚀 RAG v2起動: {load_time:.2f}秒 ({stats['count']}件)")

        return True

    except Exception as e:
        print(f"❌ RAG起動エラー: {e}")
        return False
    finally:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_fd.close()
            os.unlink(lock_file)
        except:
            pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
