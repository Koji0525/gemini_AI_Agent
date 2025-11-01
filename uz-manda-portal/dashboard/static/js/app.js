class Dashboard {
    constructor() {
        this.ws = null;
        this.init();
    }
    
    init() {
        this.connectWebSocket();
        this.setupEventListeners();
        this.loadStats();
        
        // 定期的に統計を更新
        setInterval(() => this.loadStats(), 10000);
    }
    
    connectWebSocket() {
        try {
            this.ws = new WebSocket(`ws://${window.location.host}/ws`);
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.updateStats(data.data);
            };
        } catch (e) {
            console.error('WebSocket error:', e);
        }
    }
    
    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            this.updateStats(stats);
        } catch (e) {
            console.error('Stats load error:', e);
        }
    }
    
    updateStats(stats) {
        // システム統計を更新
        if (stats.cpu_usage !== undefined) {
            document.getElementById('cpu-usage').textContent = stats.cpu_usage.toFixed(1) + '%';
            document.getElementById('memory-usage').textContent = stats.memory_usage.toFixed(1) + '%';
            document.getElementById('disk-usage').textContent = stats.disk_usage.toFixed(1) + '%';
        }
        
        // AIシステム状態
        if (stats.ai_system) {
            document.getElementById('ai-status').textContent = stats.ai_system.status;
            document.getElementById('ai-message').textContent = stats.ai_system.message;
        }
        
        // WordPress状態
        if (stats.wordpress_status) {
            document.getElementById('wp-status').textContent = stats.wordpress_status.status;
        }
        
        // 開発サイクル
        document.getElementById('dev-cycles').textContent = stats.development_cycles || 0;
        
        // タイムスタンプ
        document.getElementById('timestamp').textContent = stats.timestamp;
    }
    
    setupEventListeners() {
        document.getElementById('start-ai-btn').addEventListener('click', () => {
            this.startAISystem();
        });
        
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.loadStats();
        });
    }
    
    async startAISystem() {
        const btn = document.getElementById('start-ai-btn');
        btn.disabled = true;
        btn.textContent = '起動中...';
        
        try {
            const response = await fetch('/api/start_ai');
            const result = await response.json();
            alert(result.message);
        } catch (e) {
            alert('起動エラー: ' + e.message);
        } finally {
            btn.disabled = false;
            btn.textContent = 'AIシステム起動';
        }
    }
}

// ダッシュボード初期化
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});
