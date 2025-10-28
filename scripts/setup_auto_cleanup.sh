#!/bin/bash
echo "🔧 自動キャッシュクリーンアップ設定"

# Pythonプログラム実行用エイリアス
echo 'alias python-clean="./scripts/run_with_cache_cleanup.sh python"' >> ~/.bashrc
echo 'alias pytest-clean="./scripts/run_with_cache_cleanup.sh pytest"' >> ~/.bashrc
echo 'alias main-clean="./scripts/run_with_cache_cleanup.sh python main_automator.py"' >> ~/.bashrc

echo "✅ 設定完了"
echo "使用例:"
echo "  python-clean script.py     # キャッシュクリア後実行"
echo "  pytest-clean tests/        # キャッシュクリア後テスト"
echo "  main-clean                 # キャッシュクリア後メインプログラム"
