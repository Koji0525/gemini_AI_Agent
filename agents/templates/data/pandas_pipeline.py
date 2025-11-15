#!/usr/bin/env python3
"""
データ処理パイプライン

タスクID: {task_id}
説明: {description}
生成日時: {timestamp}
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
import logging

# ロガー設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataProcessor:
    """データ処理パイプライン
    
    CSV/Excel/JSONデータの読み込み、クリーニング、変換、保存を行う
    """
    
    def __init__(self, input_path: str, output_path: Optional[str] = None):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path) if output_path else None
        self.df: Optional[pd.DataFrame] = None
        self.stats: Dict = {{}}
    
    def load_data(self) -> pd.DataFrame:
        """データ読み込み
        
        対応形式: CSV, Excel, JSON, Parquet
        """
        logger.info(f"Loading data from {{self.input_path}}")
        
        suffix = self.input_path.suffix.lower()
        
        try:
            if suffix == '.csv':
                self.df = pd.read_csv(self.input_path)
            elif suffix in ['.xlsx', '.xls']:
                self.df = pd.read_excel(self.input_path)
            elif suffix == '.json':
                self.df = pd.read_json(self.input_path)
            elif suffix == '.parquet':
                self.df = pd.read_parquet(self.input_path)
            else:
                raise ValueError(f"Unsupported file format: {{suffix}}")
            
            self.stats['original_rows'] = len(self.df)
            self.stats['original_columns'] = len(self.df.columns)
            
            logger.info(f"Loaded {{len(self.df)}} rows, {{len(self.df.columns)}} columns")
            return self.df
            
        except Exception as e:
            logger.error(f"Error loading data: {{e}}")
            raise
    
    def clean_data(self, 
                   drop_na: bool = True,
                   drop_duplicates: bool = True,
                   fill_na: Optional[Dict] = None) -> pd.DataFrame:
        """データクリーニング
        
        Args:
            drop_na: 欠損値を含む行を削除
            drop_duplicates: 重複行を削除
            fill_na: 欠損値を埋める値（列名: 値）
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        logger.info("Cleaning data...")
        
        # 欠損値処理
        if drop_na:
            before = len(self.df)
            self.df = self.df.dropna()
            logger.info(f"Dropped {{before - len(self.df)}} rows with NA values")
        
        if fill_na:
            self.df = self.df.fillna(fill_na)
            logger.info(f"Filled NA values: {{fill_na}}")
        
        # 重複削除
        if drop_duplicates:
            before = len(self.df)
            self.df = self.df.drop_duplicates()
            logger.info(f"Dropped {{before - len(self.df)}} duplicate rows")
        
        self.stats['cleaned_rows'] = len(self.df)
        
        return self.df
    
    def transform(self, operations: List[Dict]) -> pd.DataFrame:
        """データ変換
        
        Args:
            operations: 変換操作のリスト
                例: [
                    {{'type': 'rename', 'columns': {{'old': 'new'}}}},
                    {{'type': 'convert', 'column': 'date', 'to': 'datetime'}},
                    {{'type': 'filter', 'column': 'value', 'condition': '> 0'}}
                ]
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        logger.info(f"Applying {{len(operations)}} transformations...")
        
        for op in operations:
            op_type = op.get('type')
            
            if op_type == 'rename':
                self.df = self.df.rename(columns=op['columns'])
                logger.info(f"Renamed columns: {{op['columns']}}")
            
            elif op_type == 'convert':
                col = op['column']
                to_type = op['to']
                
                if to_type == 'datetime':
                    self.df[col] = pd.to_datetime(self.df[col])
                elif to_type == 'numeric':
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                
                logger.info(f"Converted {{col}} to {{to_type}}")
            
            elif op_type == 'filter':
                col = op['column']
                condition = op['condition']
                self.df = self.df.query(f"{{col}} {{condition}}")
                logger.info(f"Filtered: {{col}} {{condition}}")
        
        return self.df
    
    def analyze(self) -> Dict:
        """基本統計分析"""
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        analysis = {{
            'shape': self.df.shape,
            'columns': self.df.columns.tolist(),
            'dtypes': self.df.dtypes.to_dict(),
            'missing_values': self.df.isnull().sum().to_dict(),
            'summary_stats': self.df.describe().to_dict()
        }}
        
        logger.info("Analysis completed")
        return analysis
    
    def save(self, output_path: Optional[str] = None, format: str = 'csv'):
        """データ保存
        
        Args:
            output_path: 出力先パス（Noneの場合は初期化時のパス使用）
            format: 保存形式（csv, excel, json, parquet）
        """
        if self.df is None:
            raise ValueError("No data to save")
        
        path = Path(output_path) if output_path else self.output_path
        
        if path is None:
            raise ValueError("No output path specified")
        
        logger.info(f"Saving data to {{path}}")
        
        if format == 'csv':
            self.df.to_csv(path, index=False)
        elif format == 'excel':
            self.df.to_excel(path, index=False)
        elif format == 'json':
            self.df.to_json(path, orient='records', indent=2)
        elif format == 'parquet':
            self.df.to_parquet(path, index=False)
        
        logger.info(f"Saved {{len(self.df)}} rows to {{path}}")
    
    def get_stats(self) -> Dict:
        """処理統計取得"""
        return self.stats


# ========================================
# 使用例
# ========================================

if __name__ == "__main__":
    # 基本的な使い方
    processor = DataProcessor("input.csv", "output.csv")
    
    # データ読み込み
    processor.load_data()
    
    # クリーニング
    processor.clean_data(drop_na=True, drop_duplicates=True)
    
    # 変換
    processor.transform([
        {{'type': 'rename', 'columns': {{'old_name': 'new_name'}}}},
        {{'type': 'convert', 'column': 'date', 'to': 'datetime'}}
    ])
    
    # 分析
    analysis = processor.analyze()
    print(analysis)
    
    # 保存
    processor.save()
    
    # 統計表示
    print(processor.get_stats())
