import os
import sys
import shutil
from PIL import Image

# フォルダ設定
if len(sys.argv) > 1:
    base_dir = sys.argv[1]
    input_folder = os.path.join(base_dir, "0_input_images")
    output_folder = os.path.join(base_dir, "2_output_images")
else:
    # 実行ファイルのディレクトリを取得
    if getattr(sys, 'frozen', False):
        # ビルドされた実行ファイルの場合
        executable_dir = os.path.dirname(sys.executable)
    else:
        # Pythonスクリプトの場合
        executable_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 複数のパス候補を試す。Image_HRER!を優先的に探す
    possible_paths = [
        os.path.join(executable_dir, "Image_HRER!"),  # 実行ファイルのディレクトリ内
        "Image_HRER!",  # カレントディレクトリ
        os.path.join(os.getcwd(), "Image_HRER!"),  # 作業ディレクトリ
        ".",  # カレントディレクトリ
    ]
    
    base_dir = None
    for path in possible_paths:
        if os.path.exists(os.path.join(path, "0_input_images")):
            base_dir = path
            break
    
    # まだ見つからない場合は、実行ファイルのディレクトリから上位ディレクトリを探索
    if base_dir is None:
        current_dir = executable_dir
        while current_dir != "/" and base_dir is None:
            test_path = os.path.join(current_dir, "Image_HRER!")
            if os.path.exists(os.path.join(test_path, "0_input_images")):
                base_dir = test_path
                break
            current_dir = os.path.dirname(current_dir)
    
    # それでも見つからなければ、実行ファイルのディレクトリを使用
    if base_dir is None:
        base_dir = executable_dir
        print(f"⚠️  警告: Image_HRER!ディレクトリが見つかりません。実行ファイルのディレクトリを使用します: {base_dir}")
    
    input_folder = os.path.join(base_dir, "0_input_images")
    output_folder = os.path.join(base_dir, "2_output_images")

# 使用するディレクトリパスを表示
print("=" * 50)
print("🖼️  16:9 比率画像処理ツール")
print("=" * 50)
print(f"📁 入力ディレクトリ: {os.path.abspath(input_folder)}")
print(f"📁 出力ディレクトリ: {os.path.abspath(output_folder)}")
print("注意: 画像を 0_input_images フォルダに入れてください")
print()

# --- フォルダを先にクリア ---
folders_to_clear = [output_folder]

def clear_folder(folder_path):
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'{file_path} の削除に失敗しました。理由: {e}')

# 2_output_imagesをクリア
for folder in folders_to_clear:
    clear_folder(folder)

# --- ここまで ---

target_width = 960  # 目標の幅
target_height = 540  # 目標の高さ（16:9）
target_ratio = target_width / target_height  # 16:9 ≈ 1.778

# フォルダが存在しない場合、作成する
os.makedirs(output_folder, exist_ok=True)

def process_image(img):
    """画像を処理する（リサイズ、トリミング）"""
    original_width, original_height = img.size
    original_ratio = original_width / original_height

    if original_ratio > target_ratio:
        # 画像が16:9より横長の場合
        # 高さを540pxに合わせる
        new_height = target_height
        new_width = int(new_height * original_ratio)
        img = img.resize((new_width, new_height), Image.LANCZOS)
        # 中央から切り取り
        left = (new_width - target_width) // 2
        img = img.crop((left, 0, left + target_width, target_height))
    else:
        # 画像が16:9より縦長の場合
        # 幅を960pxに合わせる
        new_width = target_width
        new_height = int(new_width / original_ratio)
        img = img.resize((new_width, new_height), Image.LANCZOS)
        # 中央から切り取り
        top = (new_height - target_height) // 2
        img = img.crop((0, top, target_width, top + target_height))

    return img

def process_files_in_directory(input_dir, output_dir, relative_path=""):
    """指定されたディレクトリ内のファイルを処理（サブディレクトリも含む）"""
    current_input_dir = os.path.join(input_dir, relative_path)
    current_output_dir = os.path.join(output_dir, relative_path)
    
    # 出力ディレクトリが存在しない場合は作成
    os.makedirs(current_output_dir, exist_ok=True)
    
    # ディレクトリ内のファイルとサブディレクトリを処理
    for item in os.listdir(current_input_dir):
        item_path = os.path.join(current_input_dir, item)
        
        # サブディレクトリの場合は再帰的に処理
        if os.path.isdir(item_path):
            new_relative_path = os.path.join(relative_path, item)
            process_files_in_directory(input_dir, output_dir, new_relative_path)
        
        # 画像ファイルの場合は処理
        elif item.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            try:
                img = Image.open(item_path).convert("RGB")

                # 画像処理実行
                processed = process_image(img)

                # WebP形式で保存
                base_name = os.path.splitext(item)[0]
                output_filename = f"{base_name}.webp"
                output_path = os.path.join(current_output_dir, output_filename)
                
                # 画質を100%に設定して保存（無圧縮）
                processed.save(output_path, "WEBP", quality=100, lossless=True)
                print(f"⭕️処理完了: {os.path.join(relative_path, item)} -> {os.path.join(relative_path, output_filename)} ({processed.width}x{processed.height})")
            except Exception as e:
                print(f"エラー: ファイル {os.path.join(relative_path, item)} の処理中にエラーが発生しました: {e}")

while True:
    # 画像処理を実行
    print("画像のリサイズとトリミングを開始します...")
    process_files_in_directory(input_folder, output_folder)
    print("⭕️全画像の処理が完了し、WebP形式で2_output_imagesに出力しました！")

    # 続けて実行するか確認
    while True:
        try:
            user_input = input("続けて実行しますか？（y/n）: ").strip().lower()
            if user_input in ['y', 'yes', 'はい', '続ける']:
                print("🔄 再処理を開始します...")
                # 出力ディレクトリをクリア
                for folder in folders_to_clear:
                    clear_folder(folder)
                # 再処理 - メインループに戻る
                break
            elif user_input in ['n', 'no', 'いいえ', 'やめる', '終了']:
                print("👋 プログラムを終了します。ご利用ありがとうございました！")
                sys.exit(0)
            else:
                print("❌ y または n を入力してください")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 プログラムを終了します。ご利用ありがとうございました！")
            sys.exit(0)
