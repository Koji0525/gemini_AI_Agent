// ダッシュボードの機能
class Dashboard {
    constructor() {
        this.stats = {};
        this.ws = null;
        this.init();
    }

    init() {
        this.connectWebSocket();
        this.loadStats();
        this.setupEventListeners();
        
        // 5秒ごとに統計を更新
        setInterval(() => this.loadStats(), 5000);
    }

    connectWebSocket() {
        try {
            this.ws = new WebSocket(`ws://${window.location.host}/ws`);
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            this.ws.onclose = () => {
                console.log('WebSocket接続が閉じられました。5秒後に再接続します...');
                setTimeout(() => this.connectWebSocket(), 5000);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocketエラー:', error);
            };
        } catch (error) {
            console.error('WebSocket接続エラー:', error);
        }
    }

    handleWebSocketMessage(data) {
        if (data.type === 'stats') {
            this.updateStats(data.data);
        } else if (data.type === 'logs') {
            this.updateLogs(data.data);
        }
    }

    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            this.updateStats(stats);
        } catch (error) {
            console.error('統計データの取得に失敗しました:', error);
        }
    }

    updateStats(stats) {
        this.stats = stats;
        
        // 統計カードを更新
        document.getElementById('total-executions').textContent = stats.total_executions || 0;
        document.getElementById('success-rate').textContent = (stats.success_rate || 0).toFixed(1) + '%';
        document.getElementById('total-posts').textContent = stats.total_posts || 0;
        document.getElementById('avg-quality').textContent = (stats.avg_quality || 0).toFixed(1);
        
        // 最終実行時間を更新
        const lastExecution = document.getElementById('last-execution');
        if (lastExecution) {
            lastExecution.textContent = new Date().toLocaleString();
        }
    }

    updateLogs(logs) {
        const logsContainer = document.getElementById('logs');
        if (logsContainer && Array.isArray(logs)) {
            // 最新のログを上に表示
            const html = logs.slice(-20).reverse().map(log => {
                let logClass = 'log-info';
                if (log.includes('ERROR') || log.includes('❌')) logClass = 'log-error';
                if (log.includes('WARNING') || log.includes('⚠️')) logClass = 'log-warning';
                
                return `<div class="log-entry">
                    <span class="log-time">[${new Date().toLocaleTimeString()}]</span>
                    <span class="${logClass}">${this.escapeHtml(log)}</span>
                </div>`;
            }).join('');
            
            logsContainer.innerHTML = html;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    setupEventListeners() {
        // 手動実行ボタン
        const runBtn = document.getElementById('run-btn');
        if (runBtn) {
            runBtn.addEventListener('click', () => this.runManual());
        }

        // ログ更新ボタン
        const refreshLogsBtn = document.getElementById('refresh-logs-btn');
        if (refreshLogsBtn) {
            refreshLogsBtn.addEventListener('click', () => this.loadStats());
        }
    }

    async runManual() {
        const btn = document.getElementById('run-btn');
        const originalText = btn.textContent;
        
        try {
            btn.textContent = '実行中...';
            btn.disabled = true;

            const response = await fetch('/api/run', { method: 'POST' });
            const result = await response.json();
            
            alert(result.message || '実行が開始されました');
        } catch (error) {
            alert('実行中にエラーが発生しました: ' + error.message);
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    }
}

// ダッシュボードを初期化
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});
