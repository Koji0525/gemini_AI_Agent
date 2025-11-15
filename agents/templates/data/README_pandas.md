# データ処理パイプライン

**タスクID**: {task_id}  
**説明**: {description}  
**生成日時**: {timestamp}

---

## 🚀 使い方
```python
from processor import DataProcessor

# 初期化
processor = DataProcessor("input.csv", "output.csv")

# データ読み込み
processor.load_data()

# クリーニング
processor.clean_data(drop_na=True)

# 変換
processor.transform([
    {{'type': 'rename', 'columns': {{'old': 'new'}}}},
])

# 保存
processor.save()
```

## 📦 requirements.txt
```txt
pandas==2.1.0
numpy==1.24.0
openpyxl==3.1.0
```
