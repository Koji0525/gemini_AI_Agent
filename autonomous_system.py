#!/usr/bin/env python3
"""
自律型マルチエージェント実行&バグ修正システム

フロー:
1. test_tasks.py を実行
2. エラーが出たら main_hybrid_fix.py で自動修正
3. run_multi_agent.py を実行  
4. エラーが出たら main_hybrid_fix.py で自動修正
5. 自動的に繰り返し
"""

import subprocess
import sys
import time
import os
from pathlib import Path
from datetime import datetime
import json


class AutonomousAgentSystem:
    """自律型エージェントシステム"""
    
    def __init__(self, max_retry=3, auto_fix_enabled=True):
        self.max_retry = max_retry
        self.auto_fix_enabled = auto_fix_enabled
        self.log_file = Path(f"logs/autonomous_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.stats = {
            "tasks_executed": 0,
            "errors_found": 0,
            "auto_fixed": 0,
            "manual_required": 0,
            "total_runtime": 0
        }
    
    def log(self, message, level="INFO"):
        """ログを記録"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {message}"
        print(log_msg)
        
        with open(self.log_file, "a") as f:
            f.write(log_msg + "\n")
    
    def run_command(self, command, description=""):
        """コマンドを実行してエラーをチェック"""
        self.log(f"🚀 実行開始: {description or command}", "INFO")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5分タイムアウト
            )
            
            self.log(f"📊 終了コード: {result.returncode}", "DEBUG")
            
            if result.returncode == 0:
                self.log(f"✅ 成功: {description or command}", "SUCCESS")
                return {"success": True, "output": result.stdout, "error": None}
            else:
                self.log(f"❌ エラー検出: {description or command}", "ERROR")
                self.log(f"エラー内容:\n{result.stderr}", "ERROR")
                return {"success": False, "output": result.stdout, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            self.log(f"⏰ タイムアウト: {description or command}", "ERROR")
            return {"success": False, "output": "", "error": "Timeout"}
        except Exception as e:
            self.log(f"💥 例外発生: {str(e)}", "ERROR")
            return {"success": False, "output": "", "error": str(e)}
    
    def auto_fix_error(self, error_file, error_output):
        """エラーを自動修正"""
        if not self.auto_fix_enabled:
            self.log("⚠️ 自動修正が無効です", "WARN")
            return False
        
        self.log(f"🔧 自動修正を開始: {error_file}", "INFO")
        
        # main_hybrid_fix.py を実行
        fix_command = f"python3 main_hybrid_fix.py --file {error_file} --strategy CLOUD_ONLY"
        result = self.run_command(fix_command, f"ハイブリッド修正: {error_file}")
        
        if result["success"]:
            self.stats["auto_fixed"] += 1
            self.log(f"✅ 自動修正成功: {error_file}", "SUCCESS")
            return True
        else:
            self.stats["manual_required"] += 1
            self.log(f"❌ 自動修正失敗: {error_file}", "ERROR")
            return False
    
    def run_test_tasks(self):
        """test_tasks.py を実行"""
        self.log("=" * 60, "INFO")
        self.log("📝 STEP 1: test_tasks.py を実行", "INFO")
        self.log("=" * 60, "INFO")
        
        result = self.run_command("python3 test/test_tasks.py", "テストタスク実行")
        self.stats["tasks_executed"] += 1
        
        if not result["success"]:
            self.stats["errors_found"] += 1
            self.log("🔍 エラーを検出しました。自動修正を試みます...", "WARN")
            
            # エラーファイルを特定（簡易版）
            if "test/test_tasks.py" in result["error"]:
                if self.auto_fix_error("test/test_tasks.py", result["error"]):
                    # 再実行
                    self.log("🔄 修正後に再実行します...", "INFO")
                    return self.run_test_tasks()
                else:
                    return False
        
        return result["success"]
    
    def run_multi_agent(self):
        """run_multi_agent.py を実行"""
        self.log("=" * 60, "INFO")
        self.log("🤖 STEP 2: run_multi_agent.py を実行", "INFO")
        self.log("=" * 60, "INFO")
        
        result = self.run_command("python3 scripts/run_multi_agent.py", "マルチエージェント実行")
        self.stats["tasks_executed"] += 1
        
        if not result["success"]:
            self.stats["errors_found"] += 1
            self.log("🔍 エラーを検出しました。自動修正を試みます...", "WARN")
            
            # エラーファイルを特定
            if "scripts/run_multi_agent.py" in result["error"]:
                if self.auto_fix_error("scripts/run_multi_agent.py", result["error"]):
                    # 再実行
                    self.log("🔄 修正後に再実行します...", "INFO")
                    return self.run_multi_agent()
                else:
                    return False
        
        return result["success"]
    
    def run_full_cycle(self):
        """完全なサイクルを実行"""
        start_time = time.time()
        
        self.log("🌟 自律型エージェントシステム起動", "INFO")
        self.log(f"最大リトライ回数: {self.max_retry}", "INFO")
        self.log(f"自動修正: {'有効' if self.auto_fix_enabled else '無効'}", "INFO")
        
        retry_count = 0
        
        while retry_count < self.max_retry:
            self.log(f"\n{'='*60}", "INFO")
            self.log(f"🔄 サイクル {retry_count + 1}/{self.max_retry}", "INFO")
            self.log(f"{'='*60}\n", "INFO")
            
            # Step 1: test_tasks.py
            if not self.run_test_tasks():
                retry_count += 1
                self.log(f"⚠️ test_tasks.py が失敗しました（リトライ {retry_count}/{self.max_retry}）", "WARN")
                time.sleep(2)
                continue
            
            # Step 2: run_multi_agent.py
            if not self.run_multi_agent():
                retry_count += 1
                self.log(f"⚠️ run_multi_agent.py が失敗しました（リトライ {retry_count}/{self.max_retry}）", "WARN")
                time.sleep(2)
                continue
            
            # 両方成功
            self.log("🎉 すべてのタスクが成功しました！", "SUCCESS")
            break
        
        else:
            # max_retryに到達
            self.log("❌ 最大リトライ回数に到達しました。手動介入が必要です。", "ERROR")
        
        # 統計情報を表示
        elapsed_time = time.time() - start_time
        self.stats["total_runtime"] = elapsed_time
        
        self.log("\n" + "="*60, "INFO")
        self.log("📊 実行統計", "INFO")
        self.log("="*60, "INFO")
        self.log(f"実行タスク数: {self.stats['tasks_executed']}", "INFO")
        self.log(f"検出エラー数: {self.stats['errors_found']}", "INFO")
        self.log(f"自動修正成功: {self.stats['auto_fixed']}", "INFO")
        self.log(f"手動介入必要: {self.stats['manual_required']}", "INFO")
        self.log(f"総実行時間: {elapsed_time:.2f}秒", "INFO")
        self.log("="*60, "INFO")
        
        # 統計をJSONで保存
        stats_file = self.log_file.parent / f"stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, "w") as f:
            json.dump(self.stats, f, indent=2)
        
        self.log(f"📄 統計情報を保存: {stats_file}", "INFO")
        self.log(f"📄 ログファイル: {self.log_file}", "INFO")


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="自律型マルチエージェント実行&バグ修正システム")
    parser.add_argument("--max-retry", type=int, default=3, help="最大リトライ回数")
    parser.add_argument("--no-auto-fix", action="store_true", help="自動修正を無効化")
    parser.add_argument("--test-only", action="store_true", help="test_tasks.pyのみ実行")
    parser.add_argument("--agent-only", action="store_true", help="run_multi_agent.pyのみ実行")
    
    args = parser.parse_args()
    
    system = AutonomousAgentSystem(
        max_retry=args.max_retry,
        auto_fix_enabled=not args.no_auto_fix
    )
    
    if args.test_only:
        system.run_test_tasks()
    elif args.agent_only:
        system.run_multi_agent()
    else:
        system.run_full_cycle()


if __name__ == "__main__":
    main()