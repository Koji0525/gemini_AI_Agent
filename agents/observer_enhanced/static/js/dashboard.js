/**
 * 依存関係可視化ダッシュボード JavaScript
 * 
 * 修正内容:
 * - 検索機能改善: モジュール名→ファイルパス自動変換
 * - 日本時間（JST）表示
 * - 更新ボタンUI改善
 */

const API_BASE = window.location.origin;

let graphData = null;
let svg = null;
let zoom = null;

function debugLog(message, data = null) {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${message}`, data || '');
}

// 日本時間（JST）フォーマット
function formatJST(isoString) {
    const date = new Date(isoString);
    const jstDate = new Date(date.getTime() + (9 * 60 * 60 * 1000));
    const year = jstDate.getUTCFullYear();
    const month = String(jstDate.getUTCMonth() + 1).padStart(2, '0');
    const day = String(jstDate.getUTCDate()).padStart(2, '0');
    const hour = String(jstDate.getUTCHours()).padStart(2, '0');
    const minute = String(jstDate.getUTCMinutes()).padStart(2, '0');
    const second = String(jstDate.getUTCSeconds()).padStart(2, '0');
    return `${year}/${month}/${day} ${hour}:${minute}:${second}`;
}

document.addEventListener('DOMContentLoaded', async () => {
    debugLog('🚀 ダッシュボード初期化開始');
    
    document.getElementById('refresh-btn').addEventListener('click', loadAllData);
    document.getElementById('zoom-in-btn').addEventListener('click', () => zoomGraph(1.2));
    document.getElementById('zoom-out-btn').addEventListener('click', () => zoomGraph(0.8));
    document.getElementById('reset-btn').addEventListener('click', resetGraph);
    document.getElementById('search-btn').addEventListener('click', searchImpact);
    
    document.getElementById('search-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchImpact();
    });
    
    await loadAllData();
});

async function loadAllData() {
    try {
        updateStatus('読み込み中...', 'loading');
        debugLog('📡 データ取得開始');
        
        const [healthData, statsData, nodesData, edgesData] = await Promise.all([
            fetchAPI('/api/health'),
            fetchAPI('/api/stats'),
            fetchAPI('/api/nodes'),
            fetchAPI('/api/edges')
        ]);
        
        debugLog('✅ 全データ取得成功');
        
        updateStats(statsData);
        displayTopModules(statsData.top_depended_modules || []);
        
        graphData = prepareGraphData(nodesData, edgesData, statsData);
        drawGraph(graphData);
        
        updateStatus('オンライン', 'online');
        updateTimestamp(healthData.timestamp);
        
        debugLog('✅ ダッシュボード更新完了');
        
    } catch (error) {
        console.error('❌ データ読み込みエラー:', error);
        updateStatus('エラー', 'error');
        showError(`データ取得エラー: ${error.message}`);
    }
}

async function fetchAPI(endpoint) {
    const url = `${API_BASE}${endpoint}`;
    debugLog(`📡 API呼び出し: ${url}`);
    
    const response = await fetch(url);
    debugLog(`📥 レスポンス: ${response.status}`, url);
    
    if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
}

function updateStats(stats) {
    const safeValue = (val, defaultVal = 0) => val ?? defaultVal;
    
    document.getElementById('total-modules').textContent = 
        safeValue(stats?.total_modules, 0).toLocaleString();
    document.getElementById('total-dependencies').textContent = 
        safeValue(stats?.total_dependencies, 0).toLocaleString();
    
    const depStats = stats?.dependency_stats || {};
    document.getElementById('high-impact').textContent = safeValue(depStats.high_impact, 0);
    document.getElementById('medium-impact').textContent = safeValue(depStats.medium_impact, 0);
    document.getElementById('low-impact').textContent = safeValue(depStats.low_impact, 0);
}

function displayTopModules(modules) {
    const container = document.getElementById('top-modules-list');
    
    if (!modules || modules.length === 0) {
        container.innerHTML = '<p>データがありません</p>';
        return;
    }
    
    container.innerHTML = modules.map((item, index) => {
        const moduleName = item[0];
        const count = item[1];
        
        return `
        <div class="module-item" onclick="searchModuleByName('${moduleName}')" style="cursor: pointer;" title="クリックして影響範囲を検索">
            <span class="module-rank">${index + 1}.</span>
            <span class="module-name">${moduleName}</span>
            <span class="module-count">${count}回参照</span>
        </div>
    `}).join('');
}

// モジュール名をクリックして検索
window.searchModuleByName = function(moduleName) {
    debugLog('🔍 モジュール名から検索:', moduleName);
    document.getElementById('search-input').value = moduleName;
    searchImpact();
}

function prepareGraphData(nodesData, edgesData, statsData) {
    const topModules = (statsData?.top_depended_modules || [])
        .slice(0, 50)
        .map(item => item[0]);
    
    const nodes = (nodesData?.nodes || [])
        .filter(node => topModules.includes(node.id) || node.import_count > 0)
        .slice(0, 100);
    
    const nodeIds = new Set(nodes.map(n => n.id));
    
    const edges = (edgesData?.edges || [])
        .filter(edge => nodeIds.has(edge.source) && nodeIds.has(edge.target));
    
    return { nodes, edges };
}

function drawGraph(data) {
    debugLog('🎨 グラフ描画開始');
    
    const container = document.getElementById('graph-container');
    container.innerHTML = '';
    
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    svg = d3.select('#graph-container')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });
    
    svg.call(zoom);
    
    const g = svg.append('g');
    
    const simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink(data.edges).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(30));
    
    const link = g.append('g')
        .selectAll('line')
        .data(data.edges)
        .join('line')
        .attr('stroke', '#94a3b8')
        .attr('stroke-width', 1)
        .attr('stroke-opacity', 0.6);
    
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
    
    node.append('title')
        .text(d => `${d.label}\nインポート数: ${d.import_count}`);
    
    const label = g.append('g')
        .selectAll('text')
        .data(data.nodes.filter(d => d.import_count > 3))
        .join('text')
        .text(d => d.label)
        .attr('font-size', 10)
        .attr('dx', 15)
        .attr('dy', 4);
    
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

function zoomGraph(factor) {
    if (svg && zoom) {
        svg.transition().duration(300).call(zoom.scaleBy, factor);
    }
}

function resetGraph() {
    if (svg && zoom) {
        svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
    }
}

async function searchImpact() {
    const query = document.getElementById('search-input').value.trim();
    if (!query) return;
    
    const resultsContainer = document.getElementById('search-results');
    resultsContainer.innerHTML = '<p>🔍 検索中...</p>';
    
    debugLog('🔍 検索開始:', query);
    
    try {
        // モジュール名（ドット区切り）をファイルパス（スラッシュ区切り）に変換
        const moduleToPath = query.replace(/\./g, '/');
        
        // 複数のパスパターンを試行
        const possiblePaths = [
            `${moduleToPath}.py`,              // tools.sheets_manager → tools/sheets_manager.py
            `${query}.py`,                      // そのまま.py追加
            `tools/${query}.py`,               // tools配下
            `agents/${query}.py`,              // agents配下
            `core_agents/${query}.py`,         // core_agents配下
            `${moduleToPath}`,                 // 拡張子なし
        ];
        
        debugLog('🔍 試行パス:', possiblePaths);
        
        for (const path of possiblePaths) {
            try {
                const data = await fetchAPI(`/api/impact/${path}`);
                debugLog(`✅ 見つかりました: ${path}`, data);
                
                if (data.exists) {
                    displaySearchResults(data);
                    return;
                }
            } catch (e) {
                debugLog(`❌ 見つかりません: ${path}`);
                continue;
            }
        }
        
        resultsContainer.innerHTML = `
            <p>⚠️ ファイルが見つかりませんでした</p>
            <p style="font-size: 0.9em; color: #666;">
                検索: "${query}"<br>
                試行したパス:<br>
                ${possiblePaths.map(p => `• ${p}`).join('<br>')}
            </p>
        `;
        
    } catch (error) {
        resultsContainer.innerHTML = `<p>❌ エラー: ${error.message}</p>`;
    }
}

function displaySearchResults(data) {
    const container = document.getElementById('search-results');
    
    const impactClass = data.impact_level === 'high' ? 'high-impact' :
                       data.impact_level === 'medium' ? 'medium-impact' : 'low-impact';
    
    container.innerHTML = `
        <div class="result-card ${impactClass}">
            <h3>📄 ${data.file}</h3>
            <p><strong>影響レベル:</strong> ${data.impact_description}</p>
            <p><strong>このファイルに依存:</strong> ${data.direct_dependents_count}個のファイル</p>
            <p><strong>このファイルが依存:</strong> ${data.dependencies_count}個のファイル</p>
            ${data.direct_dependents && data.direct_dependents.length > 0 ? `
                <details open>
                    <summary><strong>このファイルに依存しているファイル (${data.direct_dependents.length}個)</strong></summary>
                    <ul style="max-height: 300px; overflow-y: auto;">
                        ${data.direct_dependents.slice(0, 20).map(dep => 
                            `<li><code>${dep.file || dep}</code></li>`
                        ).join('')}
                        ${data.direct_dependents.length > 20 ? 
                            `<li><em>...他 ${data.direct_dependents.length - 20}個</em></li>` : ''}
                    </ul>
                </details>
            ` : '<p><em>他のファイルからの依存はありません</em></p>'}
            ${data.dependencies && data.dependencies.length > 0 ? `
                <details>
                    <summary><strong>このファイルが依存しているモジュール (${data.dependencies.length}個)</strong></summary>
                    <ul style="max-height: 300px; overflow-y: auto;">
                        ${data.dependencies.slice(0, 20).map(dep => 
                            `<li><code>${dep}</code></li>`
                        ).join('')}
                        ${data.dependencies.length > 20 ? 
                            `<li><em>...他 ${data.dependencies.length - 20}個</em></li>` : ''}
                    </ul>
                </details>
            ` : ''}
        </div>
    `;
}

function updateStatus(text, status) {
    const statusEl = document.getElementById('status');
    statusEl.textContent = text;
    statusEl.className = `status-badge ${status}`;
}

function updateTimestamp(timestamp) {
    const jstTime = formatJST(timestamp);
    document.getElementById('timestamp').textContent = `更新: ${jstTime} (JST)`;
}

function showError(message) {
    const container = document.getElementById('top-modules-list');
    container.innerHTML = `
        <div style="padding: 20px; background: #fee; border-radius: 8px; color: #c00;">
            <h3>⚠️ エラーが発生しました</h3>
            <p>${message}</p>
            <button onclick="location.reload()" style="margin-top: 10px; padding: 10px 20px; cursor: pointer;">
                🔄 再読み込み
            </button>
        </div>
    `;
}

debugLog('✅ ダッシュボードスクリプト読み込み完了');
