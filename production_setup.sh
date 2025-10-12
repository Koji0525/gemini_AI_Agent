#!/bin/bash
# 本番環境セットアップ

echo "🚀 本番環境セットアップ"
echo "=" * 70

# 1. systemdサービス作成（Linuxの場合）
cat > claude-agent.service << 'SERVICE'
[Unit]
Description=Claude Agent Daemon
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/gemini_AI_Agent
ExecStart=/usr/bin/python3 /path/to/gemini_AI_Agent/claude_agent_daemon.py --monitor --check 5 --interval 3600
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

echo "✅ systemdサービスファイル作成: claude-agent.service"
echo ""
echo "インストール方法:"
echo "  sudo cp claude-agent.service /etc/systemd/system/"
echo "  sudo systemctl enable claude-agent"
echo "  sudo systemctl start claude-agent"
echo ""

# 2. cronジョブ設定例
echo "⏰ cron設定例:"
echo "# 毎時実行"
echo "0 * * * * cd /path/to/gemini_AI_Agent && python3 claude_agent_daemon.py --once"
echo ""
echo "# 毎日午前9時実行"
echo "0 9 * * * cd /path/to/gemini_AI_Agent && python3 autonomous_system.py"
echo ""

# 3. nginx設定例
cat > nginx_claude.conf << 'NGINX'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
NGINX

echo "✅ nginx設定ファイル作成: nginx_claude.conf"
echo ""
echo "=" * 70
echo "✅ セットアップファイル準備完了"
