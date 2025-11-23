/**
 * 依存関係可視化ダッシュボード JavaScript (修正版2)
 * サーバーからJSTで受信するため、変換不要
 */

const API_BASE = window.location.origin;

function debugLog(message, data = null) {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${message}`, data || '');
}

// サーバーから受信したISO形式の時刻をそのまま表示
function formatJST(isoString) {
    try {
        const date = new Date(isoString);
        
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hour = String(date.getHours()).padStart(2, '0');
        const minute = String(date.getMinutes()).padStart(2, '0');
        const second = String(date.getSeconds()).padStart(2, '0');
        
        return `${year}/${month}/${day} ${hour}:${minute}:${second}`;
    } catch (e) {
        console.error('時刻変換エラー:', e);
        return '--';
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    debugLog('🚀 ダッシュボード初期化開始');
    
    document.getElementById('refresh-btn').addEventListener('click', loadAllData);
    document.getElementById('search-btn').addEventListener('click', searchImpact);
    document.getElementById('risk-search-btn').addEventListener('click', searchRiskScore);
    
    document.getElementById('search-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchImpact();
    });
    
    document.getElementById('risk-search-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchRiskScore();
    });
    
    await loadAllData();
});

async function loadAllData() {
    try {
        updateStatus('読み込み中...', 'loading');
        debugLog('📡 データ取得開始');
        
        const [healthData, statsData] = await Promise.all([
            fetchAPI('/api/health'),
            fetchAPI('/api/stats')
        ]);
        
        const [hiddenDeps, cycles, breakingChanges] = await Promise.all([
            fetchAPI('/api/hidden-dependencies/summary'),
            fetchAPI('/api/cycles'),
            fetchAPI('/api/breaking-changes')
        ]);
        
        debugLog('✅ 全データ取得成功', {
            health: healthData.status,
            timestamp: healthData.timestamp
        });
        
        updateStats(statsData);
        displayTopModules(statsData.top_depended_modules || []);
        displayHiddenDependencies(hiddenDeps);
        displayCircularDependencies(cycles);
        displayBreakingChanges(breakingChanges);
        
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
    const response = await fetch(url);
    
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
            <span class="module-count">${count}回参照 ⚠️</span>
        </div>
    `}).join('');
}

window.searchModuleByName = function(moduleName) {
    debugLog('🔍 モジュール名から検索:', moduleName);
    document.getElementById('search-input').value = moduleName;
    searchImpact();
}

function displayHiddenDependencies(data) {
    const stats = data.statistics || {};
    
    document.getElementById('hidden-deps-badge').textContent = 
        `${stats.files_with_hidden_deps || 0}ファイル`;
    document.getElementById('env-vars-count').textContent = 
        `${stats.unique_env_vars || 0}個`;
    document.getElementById('file-ops-count').textContent = 
        `${stats.unique_files_accessed || 0}個`;
    document.getElementById('commands-count').textContent = 
        `${stats.unique_commands || 0}個`;
    
    const topEnvVars = data.top_env_vars || [];
    const envVarsList = document.getElementById('top-env-vars');
    envVarsList.innerHTML = topEnvVars.slice(0, 5).map(item => 
        `<li><span>${item.name}</span><span>${item.count}回</span></li>`
    ).join('');
}

function displayCircularDependencies(data) {
    const stats = data.statistics || {};
    const totalCycles = stats.total_cycles || 0;
    
    document.getElementById('cycles-badge').textContent = `${totalCycles}個`;
    
    const statusDiv = document.getElementById('cycles-status');
    const listDiv = document.getElementById('cycles-list');
    
    if (totalCycles === 0) {
        statusDiv.className = 'status-message';
        statusDiv.innerHTML = '<span class="status-icon">✅</span><span>循環依存なし（健全）</span>';
        listDiv.innerHTML = '';
    } else {
        statusDiv.className = 'status-message warning';
        statusDiv.innerHTML = `<span class="status-icon">⚠️</span><span>${totalCycles}個の循環依存を検出</span>`;
    }
}

function displayBreakingChanges(data) {
    const stats = data.statistics || {};
    const totalChanges = stats.total_changes || 0;
    
    document.getElementById('breaking-badge').textContent = `${totalChanges}個`;
    
    const statusDiv = document.getElementById('breaking-status');
    
    if (totalChanges === 0) {
        statusDiv.className = 'status-message';
        statusDiv.innerHTML = '<span class="status-icon">✅</span><span>最近の破壊的変更なし</span>';
    } else {
        statusDiv.className = 'status-message warning';
        statusDiv.innerHTML = `<span class="status-icon">⚠️</span><span>${totalChanges}個の破壊的変更を検出</span>`;
    }
}

async function searchRiskScore() {
    const query = document.getElementById('risk-search-input').value.trim();
    if (!query) {
        alert('ファイルパスを入力してください');
        return;
    }
    
    const resultsContainer = document.getElementById('risk-result');
    resultsContainer.innerHTML = '<p>🔍 分析中...</p>';
    
    try {
        const data = await fetchAPI(`/api/risk-score/${encodeURIComponent(query)}`);
        
        if (!data.exists) {
            resultsContainer.innerHTML = '<p>⚠️ ファイルが見つかりませんでした</p>';
            return;
        }
        
        const riskClass = data.risk_level;
        const levelEmoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢',
            'minimal': '🔵'
        }[riskClass] || '⚪';
        
        resultsContainer.innerHTML = `
            <div class="risk-card ${riskClass}">
                <h4>${data.file}</h4>
                <div class="risk-score">${levelEmoji} ${data.risk_score}/100</div>
                <div class="risk-level">リスクレベル: ${data.risk_level.toUpperCase()}</div>
                
                <div class="risk-factors">
                    <h4>リスク要因:</h4>
                    ${Object.entries(data.risk_factors || {}).filter(([k,v]) => v > 0).map(([key, value]) => 
                        `<div class="risk-factor"><span>${key}</span><span>${value}点</span></div>`
                    ).join('')}
                </div>
                
                <div class="recommendations">
                    <h4>推奨事項:</h4>
                    <ul>
                        ${(data.recommendations || []).map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    } catch (error) {
        resultsContainer.innerHTML = `<p>❌ エラー: ${error.message}</p>`;
    }
}

async function searchImpact() {
    const query = document.getElementById('search-input').value.trim();
    if (!query) {
        alert('モジュール名を入力してください');
        return;
    }
    
    const resultsContainer = document.getElementById('search-results');
    resultsContainer.innerHTML = '<p>🔍 検索中...</p>';
    
    try {
        const moduleToPath = query.replace(/\./g, '/');
        const possiblePaths = [
            `${moduleToPath}.py`,
            `${query}.py`,
        ];
        
        for (const path of possiblePaths) {
            try {
                const data = await fetchAPI(`/api/impact/${encodeURIComponent(path)}`);
                
                if (data.exists) {
                    displaySearchResults(data);
                    return;
                }
            } catch (e) {
                continue;
            }
        }
        
        resultsContainer.innerHTML = `<p>⚠️ ファイルが見つかりませんでした</p>`;
        
    } catch (error) {
        resultsContainer.innerHTML = `<p>❌ エラー: ${error.message}</p>`;
    }
}

function displaySearchResults(data) {
    const container = document.getElementById('search-results');
    
    const impactClass = data.impact_level === 'high' ? 'high-impact' :
                       data.impact_level === 'medium' ? 'medium-impact' : 'low-impact';
    
    const note = data.direct_dependents_count !== data.file_info?.import_count ? 
        `<p style="color: #f80; font-size: 0.9em;">⚠️ 注意: 統計データ(${data.file_info?.import_count || 'N/A'})と実際の依存数(${data.direct_dependents_count})に差があります</p>` : '';
    
    container.innerHTML = `
        <div class="result-card ${impactClass}">
            <h3>📄 ${data.file}</h3>
            <p><strong>影響レベル:</strong> ${data.impact_description}</p>
            <p><strong>実際の依存ファイル数:</strong> ${data.direct_dependents_count}個</p>
            ${note}
            ${data.direct_dependents && data.direct_dependents.length > 0 ? `
                <details open>
                    <summary><strong>依存しているファイル一覧 (${data.direct_dependents.length}個)</strong></summary>
                    <ul style="max-height: 300px; overflow-y: auto;">
                        ${data.direct_dependents.slice(0, 30).map(dep => 
                            `<li><code>${dep.file || dep}</code></li>`
                        ).join('')}
                        ${data.direct_dependents.length > 30 ? 
                            `<li><em>...他 ${data.direct_dependents.length - 30}個</em></li>` : ''}
                    </ul>
                </details>
            ` : '<p><em>他のファイルからの依存はありません</em></p>'}
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
    console.log('⏰ サーバータイムスタンプ:', timestamp, '→ 表示:', jstTime);
}

function showError(message) {
    const container = document.getElementById('top-modules-list');
    container.innerHTML = `
        <div style="padding: 20px; background: #fee; border-radius: 8px; color: #c00;">
            <h3>⚠️ エラーが発生しました</h3>
            <p>${message}</p>
        </div>
    `;
}
