"""バッチデータ処理テンプレート"""
import pandas as pd
import numpy as np
import os
import json
import logging
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_processing.log'),
        logging.StreamHandler()
    ]
)

class BatchDataProcessor:
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.processed_count = 0
        self.error_count = 0
    
    def load_config(self, config_file):
        """設定ファイル読み込み"""
        default_config = {
            'input_dir': 'input',
            'output_dir': 'output',
            'archive_dir': 'archive',
            'processing_rules': {
                'required_columns': ['id', 'timestamp'],
                'date_format': '%Y-%m-%d',
                'chunk_size': 1000
            },
            'notification': {
                'enabled': False,
                'email': 'admin@example.com'
            }
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        # ディレクトリ作成
        for dir_name in [default_config['input_dir'], 
                        default_config['output_dir'], 
                        default_config['archive_dir']]:
            os.makedirs(dir_name, exist_ok=True)
        
        return default_config
    
    def find_input_files(self, pattern='*.csv'):
        """入力ファイル検索"""
        input_dir = self.config['input_dir']
        files = []
        
        for file in os.listdir(input_dir):
            if file.endswith('.csv') or file.endswith('.xlsx'):
                files.append(os.path.join(input_dir, file))
        
        logging.info(f"📁 入力ファイル検出: {len(files)}件")
        return files
    
    def validate_data(self, df, filename):
        """データ検証"""
        rules = self.config['processing_rules']
        required_cols = rules.get('required_columns', [])
        
        # 必須カラムチェック
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logging.warning(f"⚠️  {filename}: 必須カラム不足 - {missing_cols}")
            return False
        
        # データ型チェック
        if 'timestamp' in df.columns:
            try:
                pd.to_datetime(df['timestamp'])
            except:
                logging.warning(f"⚠️  {filename}: タイムスタンプ形式不正")
                return False
        
        logging.info(f"✅ {filename}: データ検証成功")
        return True
    
    def process_file(self, file_path):
        """ファイル処理"""
        try:
            logging.info(f"🔧 処理開始: {file_path}")
            
            # ファイル読み込み
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                logging.error(f"❌ 未対応ファイル形式: {file_path}")
                return False
            
            # データ検証
            if not self.validate_data(df, os.path.basename(file_path)):
                self.error_count += 1
                return False
            
            # データ処理（サンプル処理）
            processed_df = self.apply_processing_rules(df)
            
            # 出力ファイル保存
            output_file = self.save_processed_file(processed_df, file_path)
            
            # 入力ファイルをアーカイブ
            self.archive_file(file_path)
            
            self.processed_count += 1
            logging.info(f"✅ 処理完了: {output_file}")
            return True
            
        except Exception as e:
            logging.error(f"❌ 処理エラー {file_path}: {e}")
            self.error_count += 1
            return False
    
    def apply_processing_rules(self, df):
        """処理ルール適用"""
        # サンプル処理ルール
        processed_df = df.copy()
        
        # 1. タイムスタンプ変換
        if 'timestamp' in processed_df.columns:
            processed_df['timestamp'] = pd.to_datetime(processed_df['timestamp'])
        
        # 2. 数値データのクリーニング
        numeric_cols = processed_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            processed_df[col] = processed_df[col].fillna(0)
        
        # 3. テキストデータのクリーニング
        text_cols = processed_df.select_dtypes(include=['object']).columns
        for col in text_cols:
            processed_df[col] = processed_df[col].fillna('').str.strip()
        
        return processed_df
    
    def save_processed_file(self, df, original_path):
        """処理済みファイル保存"""
        filename = os.path.basename(original_path)
        name, ext = os.path.splitext(filename)
        
        output_dir = self.config['output_dir']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f"{name}_processed_{timestamp}{ext}")
        
        if output_file.endswith('.csv'):
            df.to_csv(output_file, index=False)
        else:
            df.to_excel(output_file, index=False)
        
        return output_file
    
    def archive_file(self, file_path):
        """ファイルアーカイブ"""
        filename = os.path.basename(file_path)
        archive_dir = self.config['archive_dir']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        archived_file = os.path.join(archive_dir, f"{timestamp}_{filename}")
        os.rename(file_path, archived_file)
    
    def send_notification(self):
        """通知送信"""
        if not self.config['notification']['enabled']:
            return
        
        try:
            # メール通知（設定が必要）
            msg = MIMEMultipart()
            msg['Subject'] = f"バッチ処理完了 - {datetime.now().strftime('%Y-%m-%d')}"
            msg['From'] = 'batch@system.com'
            msg['To'] = self.config['notification']['email']
            
            body = f"""
バッチ処理が完了しました。

処理結果:
- 処理ファイル数: {self.processed_count}
- エラー数: {self.error_count}
- 実行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            msg.attach(MIMEText(body, 'plain'))
            
            # 実際のメール送信は環境に合わせて実装
            logging.info("📧 通知メール準備完了")
            
        except Exception as e:
            logging.error(f"❌ 通知送信エラー: {e}")
    
    def run(self):
        """バッチ処理実行"""
        logging.info("🚀 バッチ処理開始")
        start_time = datetime.now()
        
        # 入力ファイル検索
        files = self.find_input_files()
        
        if not files:
            logging.info("📭 処理対象ファイルなし")
            return True
        
        # ファイル処理
        for file_path in files:
            self.process_file(file_path)
        
        # 結果集計
        end_time = datetime.now()
        duration = end_time - start_time
        
        logging.info(f"📊 バッチ処理完了")
        logging.info(f"  処理ファイル数: {self.processed_count}")
        logging.info(f"  エラー数: {self.error_count}")
        logging.info(f"  処理時間: {duration}")
        
        # 通知送信
        self.send_notification()
        
        return self.error_count == 0

def main():
    """メイン実行関数"""
    processor = BatchDataProcessor()
    
    try:
        success = processor.run()
        if success:
            print("🎉 バッチ処理正常終了")
        else:
            print("⚠️  バッチ処理完了（エラーあり）")
        
        return success
        
    except Exception as e:
        logging.error(f"❌ バッチ処理異常終了: {e}")
        return False

if __name__ == "__main__":
    main()
