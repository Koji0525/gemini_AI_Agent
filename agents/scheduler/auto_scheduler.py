"""
自動実行スケジューラー
定期的にシステムを実行し、学習サイクルを回す
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AutoScheduler:
    """自動実行スケジューラー"""
    
    def __init__(
        self,
        config_path: str = "config/schedules/schedule_config.json",
        log_dir: str = "logs/scheduler"
    ):
        self.config_path = Path(config_path)
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.schedules: Dict = {}
        self.running = False
        
    def load_config(self) -> None:
        """スケジュール設定を読み込み"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.schedules = json.load(f)
        else:
            # デフォルト設定
            self.schedules = {
                "learning_cycle": {
                    "interval_minutes": 60,
                    "enabled": True,
                    "command": "python3 scripts/run_learning_cycle.py"
                },
                "health_check": {
                    "interval_minutes": 30,
                    "enabled": True,
                    "command": "python3 scripts/health_check.py"
                },
                "backup": {
                    "interval_minutes": 1440,  # 24時間
                    "enabled": True,
                    "command": "python3 scripts/backup_system.py"
                }
            }
            self.save_config()
    
    def save_config(self) -> None:
        """設定を保存"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.schedules, f, indent=2, ensure_ascii=False)
    
    async def run_schedule(self, name: str, schedule: Dict) -> bool:
        """スケジュールを実行"""
        try:
            logger.info(f"📅 スケジュール実行: {name}")
            
            # コマンド実行
            proc = await asyncio.create_subprocess_shell(
                schedule["command"],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            # ログ保存
            log_file = self.log_dir / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"=== {name} 実行ログ ===\n")
                f.write(f"実行時刻: {datetime.now()}\n")
                f.write(f"コマンド: {schedule['command']}\n\n")
                f.write("=== STDOUT ===\n")
                f.write(stdout.decode('utf-8'))
                f.write("\n=== STDERR ===\n")
                f.write(stderr.decode('utf-8'))
            
            if proc.returncode == 0:
                logger.info(f"✅ {name} 実行成功")
                return True
            else:
                logger.error(f"❌ {name} 実行失敗 (code: {proc.returncode})")
                return False
                
        except Exception as e:
            logger.error(f"❌ {name} 実行エラー: {e}")
            return False
    
    async def run_forever(self) -> None:
        """スケジューラーを永続実行"""
        logger.info("🚀 自動スケジューラー起動")
        self.load_config()
        self.running = True
        
        # 各スケジュールの最終実行時刻
        last_run: Dict[str, datetime] = {}
        
        while self.running:
            try:
                now = datetime.now()
                
                for name, schedule in self.schedules.items():
                    if not schedule.get("enabled", False):
                        continue
                    
                    # 実行タイミングチェック
                    interval = timedelta(minutes=schedule["interval_minutes"])
                    last = last_run.get(name)
                    
                    if last is None or (now - last) >= interval:
                        success = await self.run_schedule(name, schedule)
                        if success:
                            last_run[name] = now
                
                # 1分待機
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"❌ スケジューラーエラー: {e}")
                await asyncio.sleep(60)
    
    def stop(self) -> None:
        """スケジューラーを停止"""
        logger.info("🛑 スケジューラー停止")
        self.running = False


async def main():
    """メイン実行"""
    scheduler = AutoScheduler()
    
    try:
        await scheduler.run_forever()
    except KeyboardInterrupt:
        logger.info("⚠️ 中断されました")
        scheduler.stop()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main())
