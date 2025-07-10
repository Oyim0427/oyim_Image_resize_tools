# -*- coding: utf-8 -*-
import os
import sys
import shutil
import re
from PIL import Image

# Check for proper resampling filter based on PIL version
try:
    # For newer Pillow versions (9.0+)
    RESAMPLING_FILTER = Image.Resampling.LANCZOS
except AttributeError:
    try:
        # For Pillow 8.x and older
        RESAMPLING_FILTER = Image.LANCZOS
    except AttributeError:
        # Fallback to BICUBIC which should be available in all versions
        RESAMPLING_FILTER = Image.BICUBIC

# フォルダ設定
input_folder = "0_input_images"
temp_folder = "1_temp_images"
output_folder = "2_output_images"

# --- フォルダを先にクリア ---
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

# 1_temp_imagesと2_output_imagesをクリア
for folder in [temp_folder, output_folder]:
    clear_folder(folder)

# --- ここまで ---

target_width = 960  # 目標の幅
target_height = 540  # 目標の高さ（16:9）
target_ratio = target_width / target_height  # 16:9 ≈ 1.778
min_height = 500  # 最小許容高さ
max_height = 650  # 最大許容高さ

# フォルダが存在しない場合、作成する
os.makedirs(temp_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

def is_product_filename(filename):
    """ファイル名がProduct_で始まるかどうかをチェック"""
    return filename.startswith("Product_")

def extract_info(filename):
    """ファイル名から番号と文字列を抽出する"""
    # "Product_CIRQ-156_01.webp" のようなパターンを特別に処理
    product_match = re.search(r'Product_([A-Za-z]+)-(\d+)_', filename)
    if product_match:
        letters = product_match.group(1).upper()
        number = product_match.group(2)
        return letters, number
    
    # "Product_XXX" のパターンを処理
    product_prefix_match = re.search(r'Product_([A-Za-z]+)', filename)
    if product_prefix_match:
        letters = product_prefix_match.group(1).upper()
        # 数字を抽出
        numbers = re.findall(r'\d+', filename)
        number = numbers[-1] if numbers else "0000"
        return letters, number
    
    # "CTRG-2415.webp" のようなパターンを処理
    dash_match = re.search(r'([A-Za-z]+)-(\d+)', filename)
    if dash_match:
        letters = dash_match.group(1).upper()
        number = dash_match.group(2)
        return letters, number
    
    # ファイル名から数字を抽出
    numbers = re.findall(r'\d+', filename)
    number = numbers[-1] if numbers else "0000"
    
    # ファイル名から拡張子を除いた部分
    basename = os.path.splitext(filename)[0]
    
    # ファイル名が数字のみで構成されている場合
    if basename.isdigit():
        # 数字のみの場合はCTRGを使用
        return "CTRG", number
    
    # ファイル名から文字列を抽出
    letters_match = re.search(r'[A-Za-z]{2,}', filename)
    if letters_match:
        letters = letters_match.group(0).upper()
    else:
        # 見つからない場合は、ファイル拡張子を使用
        ext_match = re.search(r'\.([A-Za-z0-9]+)$', filename)
        if ext_match and ext_match.group(1).upper() not in ["WEBP", "JPG", "JPEG", "PNG"]:
            letters = ext_match.group(1).upper()
        else:
            # デフォルトはCTRGを使用
            letters = "CTRG"
    
    return letters, number

def process_image(img):
    """画像を処理する（リサイズ、必要に応じてトリミング）"""
    original_width, original_height = img.size
    original_ratio = original_width / original_height

    # まず960pxに合わせてリサイズ
    new_width = target_width
    new_height = int(target_width / original_ratio)
    img = img.resize((new_width, new_height), RESAMPLING_FILTER)

    # 高さが500-650pxの範囲内の場合、トリミングしない
    if min_height <= new_height <= max_height:
        return img

    # 範囲外の場合、16:9比率にトリミング
    if original_ratio > target_ratio:
        # 画像が16:9より横長の場合
        crop_width = int(target_height * target_ratio)
        img = img.resize((int(crop_width * (new_width/target_width)), target_height), RESAMPLING_FILTER)
        left = (img.width - target_width) // 2
        img = img.crop((left, 0, left + target_width, target_height))
    else:
        # 画像が16:9より縦長の場合
        top = (new_height - target_height) // 2
        img = img.crop((0, top, target_width, top + target_height))

    return img

def scan_directory(dir_path, relative_path=""):
    """ディレクトリを再帰的にスキャンして画像ファイルを見つける"""
    image_files = []
    
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        
        # 相対パスを構築（出力時のディレクトリ構造を維持するため）
        item_relative_path = os.path.join(relative_path, item) if relative_path else item
        
        if os.path.isdir(item_path):
            # サブディレクトリの場合は再帰的に処理
            sub_files = scan_directory(item_path, item_relative_path)
            image_files.extend(sub_files)
        elif item.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            # 画像ファイルの場合はリストに追加
            image_files.append((item_path, item, item_relative_path))
    
    return image_files

# ステップ1: サイズ調整してtemp_imagesに保存
print("画像のリサイズとトリミングを開始...")
processed_files = {}  # 処理したファイルと元のファイル名を記録

# 入力フォルダを再帰的にスキャン
image_files = scan_directory(input_folder)
print(f"{len(image_files)} 個の画像ファイルが見つかりました。")

for file_path, filename, relative_path in image_files:
    # Product_で始まるファイル名かどうかをチェック
    is_product = is_product_filename(filename)

    try:
        img = Image.open(file_path).convert("RGB")
        print(f"読み込み: {relative_path} ({img.width}x{img.height})")

    # 画像処理実行
    processed = process_image(img)

        # 出力先のディレクトリ構造を維持
        rel_dir = os.path.dirname(relative_path)
        if rel_dir:
            rel_temp_dir = os.path.join(temp_folder, rel_dir)
            os.makedirs(rel_temp_dir, exist_ok=True)
        else:
            rel_temp_dir = temp_folder

    if is_product:
        # Product_で始まる場合は元のファイル名を変更しない（拡張子のみwebpに変更）
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}.webp"
            output_path = os.path.join(rel_temp_dir, output_filename)
        processed.save(output_path, "WEBP", quality=100, lossless=True)
            processed_files[relative_path] = True  # 元のファイル名を保持するフラグ
            print(f"⭕️処理完了 (名前変更しない): {relative_path} -> {os.path.join(os.path.dirname(relative_path), output_filename)} ({processed.width}x{processed.height})")
    else:
        # ファイル名から情報を抽出
        letters, number = extract_info(filename)
        # 新しいファイル名を生成
        output_filename = f"Product_{letters}_{number.zfill(4)}.webp"
            output_path = os.path.join(rel_temp_dir, output_filename)
        processed.save(output_path, "WEBP", quality=100, lossless=True)
            processed_files[relative_path] = False  # 元のファイル名を保持しないフラグ
            print(f"⭕️処理完了: {relative_path} -> {os.path.join(os.path.dirname(relative_path), output_filename)} ({processed.width}x{processed.height})")
    except Exception as e:
        print(f"エラー: ファイル {relative_path} の処理中にエラーが発生しました: {e}")
        continue

print("全画像の処理が完了、出力処理へ...")

# ステップ2: output_imagesに出力
for root, dirs, files in os.walk(temp_folder):
    # temp_folder からの相対パスを取得
    rel_path = os.path.relpath(root, temp_folder) if root != temp_folder else ""
    
    for filename in files:
    if not filename.lower().endswith(".webp"):
        continue
        
        # 現在のファイルの相対パス
        if rel_path == "":
            current_rel_path = filename
        else:
            current_rel_path = os.path.join(rel_path, filename)
        
        src = os.path.join(root, filename)
        
        # 出力先のディレクトリ構造を維持
        rel_output_dir = os.path.dirname(current_rel_path)
        if rel_output_dir:
            full_output_dir = os.path.join(output_folder, rel_output_dir)
            os.makedirs(full_output_dir, exist_ok=True)
        else:
            full_output_dir = output_folder
        
        dst = os.path.join(full_output_dir, filename)
    shutil.copy2(src, dst)
    
        # 対応する元のファイルを検索
        found = False
        for orig_path, keep_original in processed_files.items():
            orig_filename = os.path.basename(orig_path)
            orig_basename = os.path.splitext(orig_filename)[0]
            current_basename = os.path.splitext(filename)[0]
            
            if current_basename.startswith(orig_basename) or orig_basename.startswith(current_basename):
                if keep_original:
                    print(f"出力完了 (元の名前を変更しない): {current_rel_path}")
    else:
                    print(f"出力完了: {current_rel_path}")
                found = True
                break
        
        if not found:
            print(f"出力完了: {current_rel_path}")

print("⭕️全画像の処理が完了し、2_output_imagesに出力しました！") 