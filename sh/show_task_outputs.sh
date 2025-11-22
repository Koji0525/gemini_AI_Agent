#!/bin/bash
# タスク実行結果を表示

TASK_ID=$1

if [ -z "$TASK_ID" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 最近のタスク実行結果"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # 最新の成果物を表示
    echo "【最新の成果物（上位10件）】"
    find agent_outputs -type d -name "*_*_*" | sort -r | head -10 | while read dir; do
        echo ""
        echo "📂 $(basename $dir)"
        echo "   パス: $dir"
        echo "   ファイル数: $(find $dir -type f | wc -l)"
        echo "   合計サイズ: $(du -sh $dir | cut -f1)"
        
        # 中身をプレビュー
        echo "   📄 ファイル:"
        find $dir -type f | head -5 | while read file; do
            echo "      - $(basename $file) ($(wc -l < $file 2>/dev/null || echo 0)行)"
        done
    done
    
    echo ""
    echo "【最新の実行ログ（上位5件）】"
    ls -lt agent_outputs/auto_logs/*.txt 2>/dev/null | head -5 | while read line; do
        file=$(echo $line | awk '{print $NF}')
        echo "  📝 $(basename $file)"
    done
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "使い方:"
    echo "  特定タスクの詳細: bash sh/show_task_outputs.sh [タスクID]"
    echo "  例: bash sh/show_task_outputs.sh 7_フラッキーテスト検出設計_122119_03"
    echo ""
    
else
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 タスク実行結果: $TASK_ID"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # タスクIDの先頭部分を抽出（例: 7_フラッキーテスト → 7）
    TASK_NUM=$(echo $TASK_ID | cut -d'_' -f1)
    
    # 成果物ディレクトリを検索
    echo "【成果物ディレクトリ】"
    find agent_outputs -type d -name "${TASK_NUM}_*" | while read dir; do
        echo ""
        echo "📂 $(basename $dir)"
        echo "   パス: $dir"
        echo ""
        
        # ファイル一覧
        echo "   【ファイル一覧】"
        find $dir -type f | while read file; do
            size=$(wc -l < $file 2>/dev/null || echo "バイナリ")
            echo "      📄 $(basename $file) - ${size}行"
        done
        
        # README.mdがあれば表示
        if [ -f "$dir/README.md" ]; then
            echo ""
            echo "   【README.md】"
            head -20 "$dir/README.md" | sed 's/^/      /'
        fi
    done
    
    # 実行ログを検索
    echo ""
    echo "【実行ログ】"
    find agent_outputs/auto_logs -name "${TASK_NUM}_*.txt" | sort -r | head -3 | while read log; do
        echo ""
        echo "📝 $(basename $log)"
        echo ""
        cat $log | sed 's/^/   /'
    done
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

