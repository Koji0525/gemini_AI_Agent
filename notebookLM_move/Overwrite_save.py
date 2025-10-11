import os
import shutil
from pathlib import Path

def copy_py_files(source_folders, destination_folder):
    """
    指定された複数のフォルダから.pyファイルをコピーする
    （サブフォルダは検索しない、同じ名前のファイルは上書き）
    
    Args:
        source_folders (list): コピー元フォルダのパスリスト
        destination_folder (str): コピー先フォルダのパス
    """
    # コピー先フォルダが存在しない場合は作成
    dest_path = Path(destination_folder)
    dest_path.mkdir(parents=True, exist_ok=True)
    
    copied_files = []
    
    for source_folder in source_folders:
        source_path = Path(source_folder)
        
        # コピー元フォルダが存在するか確認
        if not source_path.exists():
            print(f"警告: フォルダが存在しません - {source_folder}")
            continue
            
        print(f"\n{source_folder} から.pyファイルを検索中...")
        
        # サブフォルダは検索せず、直下の.pyファイルのみを対象
        for py_file in source_path.glob("*.py"):
            try:
                # コピー先のパスを生成
                destination_file = dest_path / py_file.name
                
                # ファイルをコピー（上書き）
                shutil.copy2(py_file, destination_file)
                copied_files.append(str(destination_file))
                
                if destination_file.exists():
                    print(f"✓ 上書き完了: {py_file.name}")
                else:
                    print(f"✓ コピー完了: {py_file.name}")
                
            except Exception as e:
                print(f"✗ エラー: {py_file} のコピーに失敗 - {e}")
    
    return copied_files

def main():
    # コピー元フォルダのリスト
    source_folders = [
        r"C:\Users\color\Documents\gemini_AI_Agent",
        r"C:\Users\color\Documents\gemini_AI_Agent\wordpress",
        r"C:\Users\color\Documents\gemini_AI_Agent\task_executor",
        r"C:\Users\color\Documents\gemini_AI_Agent\wordpress\wp_dev",
        r"C:\Users\color\Documents\gemini_AI_Agent\fix_agents",
        r"C:\Users\color\Documents\gemini_AI_Agent\data_models",
        r"C:\Users\color\Documents\gemini_AI_Agent\agents",
    ]
    
    # コピー先フォルダ
    destination_folder = r"C:\Users\color\Documents\gemini_AI_Agent\notebookLM"
    
    print("=== .pyファイルコピープログラム ===")
    print(f"コピー元: {source_folders}")
    print(f"コピー先: {destination_folder}")
    print("※同じ名前のファイルは上書きされます")
    print("※サブフォルダは検索しません")
    print("-" * 50)
    
    # ファイルコピーを実行
    copied_files = copy_py_files(source_folders, destination_folder)
    
    print("\n" + "=" * 50)
    print("コピー完了！")
    print(f"合計 {len(copied_files)} 個の.pyファイルを処理しました")
    
    # 重複を除いたファイルの一覧を表示
    if copied_files:
        unique_files = set(os.path.basename(f) for f in copied_files)
        print(f"\nコピーしたファイル ({len(unique_files)}個):")
        for file in sorted(unique_files):
            print(f"  - {file}")

if __name__ == "__main__":
    main()