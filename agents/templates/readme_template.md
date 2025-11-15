# GitHub開発効率化ツール

**タスクID**: {task_id}  
**説明**: {description}

## 特徴

- 🤖 AIコード生成
- 📝 自動コミット
- 🔍 コードレビュー

## インストール
```bash
pip install -r requirements.txt
```

## 使い方

### コード生成
```bash
python cli.py generate --type feature -d "認証機能"
```

### コミット支援
```bash
git add .
python cli.py commit --auto
```

### コードレビュー
```bash
python cli.py review -f main.py
```
