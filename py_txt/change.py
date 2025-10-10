import os
import glob

def change_extension_to_txt(folder_path, skip_confirmation=False):
    """
    指定したフォルダ内のすべての.pyファイルを.txtに変換する
    
    Args:
        folder_path (str): 処理対象のフォルダパス
        skip_confirmation (bool): 確認をスキップする場合はTrue
    """
    # フォルダ内のすべての.pyファイルを検索
    pattern = os.path.join(folder_path, "*.py")
    py_files = glob.glob(pattern)
    
    if not py_files:
        print(f"{folder_path} 内に.pyファイルが見つかりませんでした。")
        return
    
    print(f"見つかった.pyファイル: {len(py_files)}個")
    
    # 確認（スキップ可能）
    if not skip_confirmation:
        print("以下のファイルが処理対象です:")
        for py_file in py_files:
            print(f"  - {os.path.basename(py_file)}")
        
        confirm = input("続行しますか？ (y/N): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            print("処理をキャンセルしました。")
            return
    
    # ファイル名変更の実行
    for i, py_file in enumerate(py_files, 1):
        base_name = os.path.splitext(py_file)[0]
        txt_file = base_name + ".txt"
        
        try:
            os.rename(py_file, txt_file)
            print(f"{i}/{len(py_files)} 変更完了: {os.path.basename(py_file)} -> {os.path.basename(txt_file)}")
        except Exception as e:
            print(f"エラー: {py_file} の処理中に問題が発生しました - {str(e)}")

if __name__ == "__main__":
    # 指定されたパス
    target_folder = r"C:\Users\color\Documents\gemini_AI_Agent\notebookLM"
    
    if not os.path.exists(target_folder):
        print("指定されたフォルダが存在しません。")
        print(f"パス: {target_folder}")
    else:
        print(f"処理対象フォルダ: {target_folder}")
        
        # 確認をスキップしたい場合は、以下の行のコメントを外してTrueを設定
        # change_extension_to_txt(target_folder, skip_confirmation=True)
        
        # 通常実行（確認あり）
        change_extension_to_txt(target_folder)