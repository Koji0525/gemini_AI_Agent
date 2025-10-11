#!/usr/bin/env python3
import os
from pathlib import Path
from config_hybrid import HybridFixConfig

# .envファイルを手動で読み込む
env_file = Path(".env")
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

config = HybridFixConfig()
print("=" * 50)
print("🔧 ハイブリッド修正システム設定")
print("=" * 50)
print(f"✅ Run mode: {config.run_mode}")
print(f"✅ Default strategy: {config.default_strategy}")
print(f"✅ Cloud provider: {config.cloud_provider}")
print(f"✅ OpenAI API key: {'設定済み' if os.getenv('OPENAI_API_KEY') else '未設定'}")
print(f"✅ Use local AI: {config.use_local_ai}")
print("=" * 50)
