#!/bin/bash
# WordPress完全自動デプロイ - ワンコマンド版

echo "🚀 WordPress完全自動デプロイ開始"
echo ""

# Python依存関係インストール
pip install -q requests paramiko 2>/dev/null || true

# デプロイ実行
python3 deploy_system/AUTO_DEPLOY_MASTER.py

echo ""
echo "✅ 完了！"
