/**
 * 依存関係可視化ダッシュボード JavaScript
 * 
 * 機能:
 * - APIからデータ取得
 * - 統計情報の表示
 * - D3.jsによる依存関係グラフ描画
 * - 影響範囲検索
 * 
 * 作成理由:
 * APIから取得したデータをインタラクティブに可視化し、
 * 開発者が依存関係を直感的に理解できるようにするため
 */

const API_BASE = 'http://localhost:5001';

// グローバル変数
let graphData = null;
let svg = null;
let zoom = null;

/**
 * ページ読み込み時の初期化
 */
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 ダッシュボード初期化中...');
    
    // イベントリスナー設定
    document.getElementById('refresh-btn').addEventListener('click', loadAllData);
    document.getElementById('zoom-in-btn').addEventListener('click', () => zoomGraph(1.2));
    document.getElementById('zoom-out-btn').addEventListener('click', () => zoomGraph(0.8));
    document.getElementById('reset-btn').addEventListener('click', resetGraph);
    document.getElementById('search-btn').addEventListener('click', searchImpact);
    
    // Enterキーで検索
    document.getElementById('search-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchImpact();
    });
    
    // 初回データ読み込み
    await loadAllData();
});

/**
 * 全データを読み込む
 */
async function loadAllData() {
    try {
        // ステータス更新
        updateStatus('読み込み中...', 'loading');
        
        // 並列でデータ取得
        const [healthData, statsData, nodesData, edgesData] = await Promise.all([
            fetchAPI('/api/health'),
            fetchAPI('/api/stats'),
            fetchAPI('/api/nodes'),
            fetchAPI('/api/edges')
        ]);
        
        // 統計情報更新
        updateStats(statsData);
        
        // Top 10モジュール表示
        displayTopModules(statsData.top_depended_modules);
        
        // グラフ描画
        graphData = prepareGraphData(nodesData, edgesData, statsData);
        drawGraph(graphData);
        
        // ステータス更新
        updateStatus('オンライン', 'online');
        updateTimestamp(healthData.timestamp);
        
        console.log('✅ データ読み込み完了');
        
    } catch (error) {
        console.error('❌ データ読み込みエラー:', error);
        updateStatus('エラー', 'error');
    }
}

/**
 * API呼び出し
 */
async function fetchAPI(endpoint) {
    const response = await fetch(`${API_BASE}${endpoint}`);
    if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
    }
    return await response.json();
}

/**
 * 統計情報を更新
 */
function updateStats(stats) {
    document.getElementById('total-modules').textContent = stats.total_modules.toLocaleString();
    document.getElementById('total-dependencies').textContent = stats.total_dependencies.toLocaleString();
    document.getElementById('high-impact').textContent = stats.dependency_stats.high_impact;
    document.getElementById('medium-impact').textContent = stats.dependency_stats.medium_impact;
    document.getElementById('low-impact').textContent = stats.dependency_stats.low_impact;
}

/**
 * Top 10モジュールを表示
 */
function displayTopModules(modules) {
    const container = document.getElementById('top-modules-list');
    container.innerHTML = modules.map((item, index) => `
        <div class="module-item">
            <span class="module-rank">${index + 1}.</span>
            <span class="module-name">${item[0]}</span>
            <span class="module-count">${item[1]}回参照</span>
        </div>
    `).join('');
}

/**
 * グラフデータを準備（上位50モジュールのみ）
 */
function prepareGraphData(nodesData, edgesData, statsData) {
    // Top 50モジュールを取得
    const top50Modules = statsData.top_depended_modules.slice(0, 50).map(item => item[0]);
    
    // Top 50に関連するノードのみフィルタ
    const filteredNodes = nodesData.nodes.filter(node => 
        top50Modules.includes(node.id) || node.import_count > 0
    ).slice(0, 100); // 最大100ノード
    
    const nodeIds = new Set(filteredNodes.map(n => n.id));
    
    // 関連するエッジのみフィルタ
    const filteredEdges = edgesData.edges.filter(edge =>
        nodeIds.has(edge.source) && nodeIds.has(edge.target)
    );
    
    return {
        nodes: filteredNodes,
        edges: filteredEdges
    };
}

/**
 * D3.jsでグラフを描画
 */
function drawGraph(data) {
    const container = document.getElementById('graph-container');
    container.innerHTML = ''; // クリア
    
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    // SVG作成
    svg = d3.select('#graph-container')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // ズーム設定
    zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });
    
    svg.call(zoom);
    
    const g = svg.append('g');
    
    // 力学シミュレーション
    const simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink(data.edges).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(30));
    
    // エッジ描画
    const link = g.append('g')
        .selectAll('line')
        .data(data.edges)
        .join('line')
        .attr('stroke', '#94a3b8')
        .attr('stroke-width', 1)
        .attr('stroke-opacity', 0.6);
    
    // ノード描画
    const node = g.append('g')
        .selectAll('circle')
        .data(data.nodes)
        .join('circle')
        .attr('r', d => Math.min(5 + d.import_count * 0.5, 20))
        .attr('fill', d => {
            if (d.import_count >= 5) return '#ef4444';
            if (d.import_count >= 2) return '#f59e0b';
            return '#10b981';
        })
        .attr('stroke', '#fff')
        .attr('stroke-width', 2)
        .call(drag(simulation));
    
    // ツールチップ
    node.append('title')
        .text(d => `${d.label}\nインポート数: ${d.import_count}`);
    
    // ラベル
    const label = g.append('g')
        .selectAll('text')
        .data(data.nodes.filter(d => d.import_count > 3))
        .join('text')
        .text(d => d.label)
        .attr('font-size', 10)
        .attr('dx', 15)
        .attr('dy', 4);
    
    // シミュレーション更新
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        label
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });
}

/**
 * ドラッグ処理
 */
function drag(simulation) {
    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }
    
    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }
    
    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }
    
    return d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended);
}

/**
 * グラフのズーム
 */
function zoomGraph(factor) {
    svg.transition()
        .duration(300)
        .call(zoom.scaleBy, factor);
}

/**
 * グラフのリセット
 */
function resetGraph() {
    svg.transition()
        .duration(750)
        .call(zoom.transform, d3.zoomIdentity);
}

/**
 * 影響範囲検索
 */
async function searchImpact() {
    const query = document.getElementById('search-input').value.trim();
    if (!query) return;
    
    const resultsContainer = document.getElementById('search-results');
    resultsContainer.innerHTML = '<p>検索中...</p>';
    
    try {
        // ファイルパスを推測して検索
        const possiblePaths = [
            `tools/${query}.py`,
            `agents/${query}.py`,
            `core_agents/${query}.py`,
            `${query}.py`
        ];
        
        for (const path of possiblePaths) {
            try {
                const data = await fetchAPI(`/api/impact/${path}`);
                if (data.exists) {
                    displaySearchResults(data);
                    return;
                }
            } catch (e) {
                continue;
            }
        }
        
        resultsContainer.innerHTML = '<p>⚠️ ファイルが見つかりませんでした</p>';
        
    } catch (error) {
        resultsContainer.innerHTML = `<p>❌ エラー: ${error.message}</p>`;
    }
}

/**
 * 検索結果を表示
 */
function displaySearchResults(data) {
    const container = document.getElementById('search-results');
    
    const impactClass = data.impact_level === 'high' ? 'high-impact' :
                       data.impact_level === 'medium' ? 'medium-impact' : 'low-impact';
    
    container.innerHTML = `
        <div class="result-card ${impactClass}">
            <h3>📄 ${data.file}</h3>
            <p><strong>影響レベル:</strong> ${data.impact_description}</p>
            <p><strong>このファイルに依存:</strong> ${data.direct_dependents_count}個</p>
            <p><strong>このファイルが依存:</strong> ${data.dependencies_count}個</p>
            ${data.direct_dependents.length > 0 ? `
                <details>
                    <summary>依存しているファイル (${data.direct_dependents.length}個)</summary>
                    <ul>
                        ${data.direct_dependents.slice(0, 10).map(dep => 
                            `<li><code>${dep.file}</code></li>`
                        ).join('')}
                    </ul>
                </details>
            ` : ''}
        </div>
    `;
}

/**
 * ステータス更新
 */
function updateStatus(text, status) {
    const statusEl = document.getElementById('status');
    statusEl.textContent = text;
    statusEl.className = `status-badge ${status}`;
}

/**
 * タイムスタンプ更新
 */
function updateTimestamp(timestamp) {
    const date = new Date(timestamp);
    document.getElementById('timestamp').textContent = 
        `更新: ${date.toLocaleString('ja-JP')}`;
}

console.log('✅ ダッシュボードスクリプト読み込み完了');
