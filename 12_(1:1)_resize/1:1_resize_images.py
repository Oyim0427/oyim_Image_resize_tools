import os
import sys
import shutil
from PIL import Image

# フォルダ設定
input_folder = "0_input_images"
output_folder = "2_output_images"

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

# コマンド引数を入力（画像サイズ）
if len(sys.argv) < 2:
    print("使い方: 1:1_resize_images.py 画像サイズ")
    print("例: 1:1_resize_images.py 960")
    print("出力例: 960x960のWebP画像")
    sys.exit(1)

try:
    target_size = int(sys.argv[1])
    if target_size <= 0:
        raise ValueError("画像サイズは正の整数である必要があります")
except ValueError as e:
    print(f"エラー: {e}")
    print("使い方: 1:1_resize_images.py 画像サイズ")
    print("例: 1:1_resize_images.py 960")
    sys.exit(1)

target_width = target_size  # 目標の幅
target_height = target_size  # 目標の高さ（1:1）

print(f"画像サイズ: {target_width}x{target_height}（1:1比率）")
print("長辺を維持し、短辺を拡張して正方形にします（画像内容は完全に保持されます）")

# フォルダが存在しない場合、作成する
os.makedirs(output_folder, exist_ok=True)

def process_image(img):
    """画像を処理する（長辺を維持し、短辺を拡張して正方形にする）"""
    original_width, original_height = img.size
    
    # 長辺のサイズを決定
    if original_width >= original_height:
        # 横長の画像
        aspect_ratio = target_size / original_width
        new_width = target_size
        new_height = int(original_height * aspect_ratio)
    else:
        # 縦長の画像
        aspect_ratio = target_size / original_height
        new_height = target_size
        new_width = int(original_width * aspect_ratio)
    
    # リサイズ
    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # 正方形のキャンバスを作成（白背景）
    square_img = Image.new("RGB", (target_size, target_size), (255, 255, 255))
    
    # リサイズした画像を中央に配置
    paste_x = (target_size - new_width) // 2
    paste_y = (target_size - new_height) // 2
    square_img.paste(resized_img, (paste_x, paste_y))

    return square_img

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

# 画像処理を実行
print("画像のリサイズと正方形化を開始...")
process_files_in_directory(input_folder, output_folder)
print(f"⭕️全画像の処理が完了し、{target_width}x{target_height}のWebP形式で2_output_imagesに出力しました！")