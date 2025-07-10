# -*- coding: utf-8 -*-
import os
import sys
import shutil
import re
from PIL import Image, ImageChops

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

target_width = 900  # 目標の幅
target_height = 600  # 目標の高さ（3:2）
min_height = 550  # 最小許容高さ
max_height = 650  # 最大許容高さ

# フォルダが存在しない場合、作成する
os.makedirs(temp_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

def is_entrance_filename(filename):
    """ファイル名がEntrance_で始まるかどうかをチェック"""
    return filename.startswith("Entrance_")

def extract_facility_id(filename):
    """ファイル名から施設IDを抽出する"""
    numbers = re.findall(r'\d+', filename)
    if numbers:
        # 最初に見つかった数字を施設IDとして使用
        return numbers[0]
    # デフォルト値として "000" を返す
    return "000"

def trim_white_borders(img, bg_color=(255, 255, 255), threshold=235):
    """空白の境界を自動的にトリミングする（しきい値を設定可能）"""
    # グレースケールに変換
    img_gray = img.convert('L')
    
    # しきい値より明るいピクセルをマスク
    mask = Image.eval(img_gray, lambda x: 0 if x >= threshold else 255)
    
    # 実際のコンテンツの境界を取得
    bbox = mask.getbbox()
    
    if bbox:
        # 少し余白を追加せずに直接トリミング
        return img.crop(bbox)
    else:
        return img  # 内容がなければトリミングしない

def process_image(img):
    """画像を処理する（空白の境界をトリミングし、アスペクト比を維持しながらリサイズ）"""
    original_width, original_height = img.size
    
    if original_width <= 0 or original_height <= 0:
        print(f"警告: 画像サイズが無効です ({original_width}x{original_height})。スキップします。")
        return img
    
    # 空白の境界をトリミング（しきい値を調整可能）
    trimmed_img = trim_white_borders(img, threshold=235)
    print(f"トリミング: {original_width}x{original_height} -> {trimmed_img.width}x{trimmed_img.height}")
    
    # トリミング後のサイズ
    trimmed_width, trimmed_height = trimmed_img.size
    
    if trimmed_width <= 0 or trimmed_height <= 0:
        print("警告: トリミング後のサイズが無効です。元の画像を使用します。")
        trimmed_img = img
        trimmed_width, trimmed_height = original_width, original_height
        
    trimmed_ratio = float(trimmed_width) / float(trimmed_height) if trimmed_height > 0 else 1.5  # デフォルトは3:2比率
    target_ratio = float(target_width) / float(target_height)  # 3:2 = 1.5
    
    # アスペクト比を維持しながらリサイズ
    if trimmed_ratio > target_ratio:
        # 画像が目標比率より横長の場合
        new_height = target_height
        new_width = int(new_height * trimmed_ratio)
        resized_img = trimmed_img.resize((new_width, new_height), RESAMPLING_FILTER)
        
        # 中央部分を切り取る
        crop_left = (new_width - target_width) // 2
        final_img = resized_img.crop((crop_left, 0, crop_left + target_width, target_height))
    else:
        # 画像が目標比率より縦長の場合
        new_width = target_width
        new_height = int(new_width / trimmed_ratio)
        
        # 高さが550-650pxの範囲内の場合
        if min_height <= new_height <= max_height:
            # ちょうど目標の幅にリサイズ
            final_img = trimmed_img.resize((target_width, new_height), RESAMPLING_FILTER)
        else:
            # 目標の幅にリサイズしてから中央部分を切り取る
            resized_img = trimmed_img.resize((new_width, new_height), RESAMPLING_FILTER)
            crop_top = (new_height - target_height) // 2
            final_img = resized_img.crop((0, crop_top, target_width, crop_top + target_height))
    
    return final_img

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
processed_files = {}  # 処理したファイルと抽出された施設IDを記録
keep_original_names = {}  # 元の名前を保持するファイル

# 入力フォルダを再帰的にスキャン
image_files = scan_directory(input_folder)
print(f"{len(image_files)} 個の画像ファイルが見つかりました。")

for file_path, filename, relative_path in image_files:
    # Entrance_で始まるファイル名かどうかをチェック
    is_entrance = is_entrance_filename(filename)

    try:
        img = Image.open(file_path).convert("RGB")
        
        print(f"読み込み: {relative_path} ({img.width}x{img.height})")
        
        # ファイル名から施設IDを抽出
        facility_id = extract_facility_id(filename)
        facility_id = str(facility_id).zfill(3)  # 施設ID（3桁）
        processed_files[relative_path] = facility_id
        
        # Entrance_で始まる場合は元の名前を保持
        if is_entrance:
            keep_original_names[relative_path] = True
        
        # 画像処理実行
        processed = process_image(img)

        # 出力先のディレクトリ構造を維持
        rel_dir = os.path.dirname(relative_path)
        if rel_dir:
            rel_temp_dir = os.path.join(temp_folder, rel_dir)
            os.makedirs(rel_temp_dir, exist_ok=True)
        else:
            rel_temp_dir = temp_folder

        # 元のファイル名を保持したまま、WebP形式に変換
        base_name = os.path.splitext(filename)[0]
        temp_filename = f"{base_name}.webp"
        output_path = os.path.join(rel_temp_dir, temp_filename)
        
        # 画質を100%に設定して保存
        processed.save(output_path, "WEBP", quality=100, lossless=True)
        
        if is_entrance:
            print(f"⭕️処理完了 (名前変更しない): {relative_path} -> {os.path.join(os.path.dirname(relative_path), temp_filename)} ({processed.width}x{processed.height})")
        else:
            print(f"⭕️処理完了: {relative_path} -> {os.path.join(os.path.dirname(relative_path), temp_filename)} ({processed.width}x{processed.height})")
    except Exception as e:
        print(f"エラー: ファイル {relative_path} の処理中にエラーが発生しました: {e}")
        continue

print("全画像の処理が完了、名前の変更と出力処理へ...")

# ステップ2: 名前を変更してoutput_imagesに出力
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
        
        # 元の名前を保持するかどうか確認
        found = False
        for orig_path in keep_original_names.keys():
            orig_filename = os.path.basename(orig_path)
            orig_basename = os.path.splitext(orig_filename)[0]
            current_basename = os.path.splitext(filename)[0]
            
            if orig_basename == current_basename:
                # 元の名前を変更しない（拡張子のみwebpに変更）
                dst = os.path.join(full_output_dir, filename)
                shutil.copy2(src, dst)
                print(f"出力完了 (元の名前を変更しない): {current_rel_path}")
                found = True
                break
                
        if found:
            continue
            
        # 対応する施設IDを検索
        found = False
        for orig_path in processed_files.keys():
            orig_filename = os.path.basename(orig_path)
            orig_basename = os.path.splitext(orig_filename)[0]
            current_basename = os.path.splitext(filename)[0]
            
            if orig_basename == current_basename:
                # 対応する施設IDを見つける
                facility_id = processed_files[orig_path]
                
                # 新しいファイル名を生成
                new_filename = f"Entrance_{facility_id}_01.webp"
                
                dst = os.path.join(full_output_dir, new_filename)
                shutil.copy2(src, dst)
                print(f"出力完了: {current_rel_path} -> {os.path.join(rel_output_dir, new_filename) if rel_output_dir else new_filename}")
                found = True
                break
        
        if not found:
            print(f"警告: {current_rel_path} に対応する元のファイル名が見つかりませんでした。")

print("⭕️全画像の処理が完了し、2_output_imagesに出力しました！")
