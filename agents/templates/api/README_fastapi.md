# FastAPI RESTful API

**タスクID**: {task_id}  
**説明**: {description}  
**生成日時**: {timestamp}

---

## 🚀 クイックスタート
```bash
# 依存パッケージインストール
pip install -r requirements.txt

# アプリケーション起動
python main.py

# または uvicorn で起動
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📖 API ドキュメント

起動後、以下のURLでドキュメントを確認:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔌 エンドポイント

### ヘルスチェック
```bash
curl http://localhost:8000/health
```

### アイテム一覧
```bash
curl http://localhost:8000/items
```

### アイテム作成
```bash
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{{"name": "Test Item", "description": "Description"}}'
```

## 🧪 テスト
```bash
pytest tests/
```

## 📦 requirements.txt
```txt
fastapi==0.104.0
uvicorn[standard]==0.24.0
pydantic==2.4.0
python-multipart==0.0.6
```
