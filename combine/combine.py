import os
import glob

def combine_py_files(directory_path, output_file="combine.txt"):
    """
    指定したディレクトリ内のすべての.pyファイルを結合し、
    ファイル名を先頭に付けたテキストファイルを作成する
    """
    # 指定ディレクトリ内のすべての.pyファイルを検索
    py_files = glob.glob(os.path.join(directory_path, "*.py"))
    
    # ファイル名でソート
    py_files.sort()
    
    with open(os.path.join(directory_path, output_file), "w", encoding="utf-8") as outfile:
        for py_file in py_files:
            # ファイル名のみを取得
            filename = os.path.basename(py_file)
            
            # ファイル名を区切りとして書き込み
            outfile.write(f"#{filename}\n")
            
            try:
                # ファイル内容を読み込んで書き込み
                with open(py_file, "r", encoding="utf-8") as infile:
                    content = infile.read()
                    outfile.write(content)
                    
                # ファイル間に空行を追加（最後のファイル以外）
                if py_file != py_files[-1]:
                    outfile.write("\n\n")
                    
            except Exception as e:
                print(f"エラー: {filename} の読み込み中に問題が発生しました - {e}")
    
    print(f"完了: {len(py_files)}個の.pyファイルを {output_file} に結合しました")

# 使用例
if __name__ == "__main__":
    target_directory = r"C:\Users\color\Documents\gemini_AI_Agent\notebookLM"
    
    # 指定ディレクトリが存在するか確認
    if os.path.exists(target_directory):
        combine_py_files(target_directory)
    else:
        print(f"エラー: ディレクトリ {target_directory} が見つかりません")