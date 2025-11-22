"""
フォルダ名フォーマッター
{parent_goal_id}_{task_id}_{task_name}_{timestamp}_{jst_datetime}
例: 7_7_24時間稼働最終確認_032337_04_251122_1231
"""

from datetime import datetime
import pytz

def format_folder_name(
    parent_goal_id: str,
    task_id: str,
    task_name: str,
    sequence_number: int = 1
) -> str:
    """
    フォルダ名をフォーマット
    
    Args:
        parent_goal_id: 親ゴールID（例: "7"）
        task_id: タスクID（例: "7"）
        task_name: タスク名（例: "24時間稼働最終確認"）
        sequence_number: 連番（例: 4）
    
    Returns:
        folder_name: 例: "7_7_24時間稼働最終確認_032337_04_251122_1231"
    """
    
    # 日本時間取得
    jst = pytz.timezone('Asia/Tokyo')
    now_jst = datetime.now(jst)
    
    # タイムスタンプ（時分秒）
    timestamp_hms = now_jst.strftime('%H%M%S')
    
    # 日本時間（年月日時分）
    jst_datetime = now_jst.strftime('%y%m%d_%H%M')
    
    # 連番（2桁）
    seq = str(sequence_number).zfill(2)
    
    # タスク名をクリーンアップ
    clean_task_name = task_name.strip().replace(' ', '_')
    
    # フォルダ名構築
    folder_name = f"{parent_goal_id}_{task_id}_{clean_task_name}_{timestamp_hms}_{seq}_{jst_datetime}"
    
    return folder_name

def parse_task_info_from_sheet(row: dict) -> dict:
    """
    Google Sheetsの行からタスク情報を抽出
    
    Args:
        row: Sheetsの行データ
    
    Returns:
        task_info: {
            'parent_goal_id': str,
            'task_id': str,
            'task_name': str
        }
    """
    
    # parent_goal_id（例: "7"）
    parent_goal_id = str(row.get('parent_goal_id', '0'))
    
    # task_id（例: "7"）
    task_id = str(row.get('task_id', '0'))
    
    # task_name（例: "24時間稼働最終確認"）
    task_name = row.get('task_name', row.get('title', 'unknown_task'))
    
    return {
        'parent_goal_id': parent_goal_id,
        'task_id': task_id,
        'task_name': task_name
    }

# 使用例
if __name__ == '__main__':
    # テスト
    folder_name = format_folder_name(
        parent_goal_id='7',
        task_id='7',
        task_name='24時間稼働最終確認',
        sequence_number=4
    )
    
    print(f"フォルダ名: {folder_name}")
    # 例: 7_7_24時間稼働最終確認_123456_04_251122_1231

