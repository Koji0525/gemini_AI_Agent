"""
データ処理パイプライン

タスクID: {task_id}
説明: {description}
"""

import pandas as pd
import numpy as np
from pathlib import Path

class DataProcessor:
    def __init__(self, input_path: str):
        self.input_path = Path(input_path)
        self.df = None
    
    def load_data(self):
        self.df = pd.read_csv(self.input_path)
        print(f"Loaded {{len(self.df)}} rows")
    
    def clean_data(self):
        # 欠損値処理
        self.df = self.df.dropna()
        print(f"After cleaning: {{len(self.df)}} rows")
    
    def transform(self):
        # データ変換
        pass
    
    def save(self, output_path: str):
        self.df.to_csv(output_path, index=False)
        print(f"Saved to {{output_path}}")

if __name__ == "__main__":
    processor = DataProcessor("input.csv")
    processor.load_data()
    processor.clean_data()
    processor.save("output.csv")
