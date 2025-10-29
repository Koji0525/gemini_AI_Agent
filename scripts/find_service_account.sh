#!/bin/bash

echo "================================================"
echo "🔍 サービスアカウントファイル検索"
echo "================================================"
echo ""

# .envから実際のファイル名を取得
echo "【.envの設定】"
grep -i "service" .env | grep -v "^#"
echo ""

# Google Cloud サービスアカウントの特徴を持つJSONを探す
echo "【JSONファイルの内容確認】"
echo ""

for json_file in *.json; do
    if [ -f "$json_file" ]; then
        # JSONファイルの中身をチェック
        if grep -q "private_key" "$json_file" 2>/dev/null && \
           grep -q "client_email" "$json_file" 2>/dev/null && \
           grep -q "project_id" "$json_file" 2>/dev/null; then
            echo "✅ サービスアカウント発見: $json_file"
            
            # 詳細情報
            client_email=$(grep -o '"client_email": "[^"]*"' "$json_file" | cut -d'"' -f4)
            project_id=$(grep -o '"project_id": "[^"]*"' "$json_file" | cut -d'"' -f4)
            
            echo "   client_email: $client_email"
            echo "   project_id: $project_id"
            echo ""
        fi
    fi
done

echo "================================================"
