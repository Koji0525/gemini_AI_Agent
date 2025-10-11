import os
import shutil
from pathlib import Path

def copy_py_files(source_folders, destination_folder):
    """
    指定された複数のフォルダから.pyファイルをコピーする
    （サブフォルダは検索しない）
    
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
                # コピー先のパスを生成（同じ名前の場合は連番を付ける）
                destination_file = dest_path / py_file.name
                
                # 同じ名前のファイルが既に存在する場合は番号を付ける
                if destination_file.exists():
                    base_name = py_file.stem
                    extension = py_file.suffix
                    counter = 1
                    
                    while destination_file.exists():
                        destination_file = dest_path / f"{base_name}_{counter}{extension}"
                        counter += 1
                
                # ファイルをコピー
                shutil.copy2(py_file, destination_file)
                copied_files.append(str(destination_file))
                print(f"✓ コピー完了: {py_file.name} → {os.path.basename(destination_file)}")
                
            except Exception as e:
                print(f"✗ エラー: {py_file} のコピーに失敗 - {e}")
    
    return copied_files

def main():
    # コピー元フォルダのリスト
    source_folders = [
        r"C:\Users\color\Documents\gemini_AI_Agent",
        r"C:\Users\color\Documents\gemini_AI_Agent\wordpress"
    ]
    
    # コピー先フォルダ
    destination_folder = r"C:\Users\color\Documents\gemini_AI_Agent\notebookLM"
    
    print("=== .pyファイルコピープログラム ===")
    print(f"コピー元: {source_folders}")
    print(f"コピー先: {destination_folder}")
    print("※サブフォルダは検索しません")
    print("-" * 50)
    
    # ファイルコピーを実行
    copied_files = copy_py_files(source_folders, destination_folder)
    
    print("\n" + "=" * 50)
    print("コピー完了！")
    print(f"合計 {len(copied_files)} 個の.pyファイルをコピーしました")
    
    # コピーしたファイルの一覧を表示
    if copied_files:
        print("\nコピーしたファイル:")
        for file in copied_files:
            print(f"  - {os.path.basename(file)}")
    else:
        print("コピーする.pyファイルが見つかりませんでした")

if __name__ == "__main__":
    main()