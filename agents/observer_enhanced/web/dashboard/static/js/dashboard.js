// ==============================================================
// ダッシュボード JavaScript
// ==============================================================

const API_BASE = 'http://localhost:8000/api';

// ページロード時に実行
document.addEventListener('DOMContentLoaded', function() {
    loadOverviewStats();
    loadDuplicates();
});

// 概要統計をロード
async function loadOverviewStats() {
    try {
        const response = await fetch(`${API_BASE}/dependencies`);
        const data = await response.json();
        
        document.getElementById('total-files').textContent = data.nodes.length;
        
        // 重複ファイル数を取得
        const dupResponse = await fetch(`${API_BASE}/duplicates`);
        const dupData = await dupResponse.json();
        document.getElementById('duplicate-count').textContent = dupData.total_duplicates;
        
    } catch (error) {
        console.error('統計データの読み込みエラー:', error);
    }
}

// 重複ファイルをロード
async function loadDuplicates() {
    try {
        const response = await fetch(`${API_BASE}/duplicates`);
        const data = await response.json();
        
        const container = document.getElementById('duplicates-content');
        container.innerHTML = '';
        
        if (data.groups.length === 0) {
            container.innerHTML = '<p class="text-success">✅ 重複ファイルは見つかりませんでした</p>';
            return;
        }
        
        data.groups.forEach(group => {
            const card = document.createElement('div');
            card.className = 'card mb-3';
            card.innerHTML = `
                <div class="card-header bg-warning">
                    <strong>${group.base_name}</strong> (${group.count}ファイル)
                </div>
                <div class="card-body">
                    <p><strong>推奨:</strong> <code>${group.recommended}</code></p>
                    <p><strong>削除候補:</strong></p>
                    <ul>
                        ${group.delete_candidates.map(f => `<li><code>${f}</code></li>`).join('')}
                    </ul>
                </div>
            `;
            container.appendChild(card);
        });
        
    } catch (error) {
        console.error('重複ファイルの読み込みエラー:', error);
        document.getElementById('duplicates-content').innerHTML = 
            '<p class="text-danger">⚠️ データ読み込みエラー</p>';
    }
}

// 影響範囲を分析
async function analyzeImpact() {
    const filePath = document.getElementById('impact-file-input').value;
    const resultDiv = document.getElementById('impact-result');
    
    if (!filePath) {
        alert('ファイルパスを入力してください');
        return;
    }
    
    resultDiv.innerHTML = '<p class="text-muted">分析中...</p>';
    
    try {
        const response = await fetch(`${API_BASE}/impact/${encodeURIComponent(filePath)}`);
        const data = await response.json();
        
        if (data.error) {
            resultDiv.innerHTML = `<p class="text-danger">⚠️ ${data.error}</p>`;
            return;
        }
        
        resultDiv.innerHTML = `
            <div class="alert alert-info">
                <h5>📊 影響範囲分析結果</h5>
                <p><strong>対象ファイル:</strong> ${data.target_file}</p>
                <p><strong>総影響ファイル数:</strong> ${data.total_impact_count}個</p>
                
                <h6 class="mt-3">直接影響 (1階層)</h6>
                <ul>
                    ${data.direct_impact.slice(0, 10).map(f => `<li><code>${f}</code></li>`).join('')}
                </ul>
                
                ${data.recommended_tests && data.recommended_tests.length > 0 ? `
                    <h6 class="mt-3">推奨テスト</h6>
                    <ul>
                        ${data.recommended_tests.map(t => 
                            `<li><code>${t.file}</code> - ${t.reason}</li>`
                        ).join('')}
                    </ul>
                ` : ''}
            </div>
        `;
        
    } catch (error) {
        console.error('影響範囲分析エラー:', error);
        resultDiv.innerHTML = '<p class="text-danger">⚠️ 分析エラー</p>';
    }
}

// ファイルを検索
function searchFiles() {
    const query = document.getElementById('file-search-input').value.toLowerCase();
    const resultsDiv = document.getElementById('search-results');
    
    if (query.length < 2) {
        resultsDiv.innerHTML = '';
        return;
    }
    
    // 簡易実装: 後でAPI化
    resultsDiv.innerHTML = '<p class="text-muted">検索機能は次のフェーズで実装予定です</p>';
}
