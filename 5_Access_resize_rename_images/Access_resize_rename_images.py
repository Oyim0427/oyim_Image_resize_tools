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

# 画像処理パラメータ
target_size = (980, 550)  # 新しいキャンパスサイズ
background_color = (255, 255, 255)  # 背景は白

# フォルダが存在しない場合、作成する
os.makedirs(temp_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# ファイル名がAccess_で始まるかどうかをチェックする関数
def is_access_filename(filename):
    """ファイル名がAccess_で始まるかどうかをチェック"""
    return filename.startswith("Access_")

# ファイル名から施設IDを抽出する関数
def extract_facility_id(filename):
    """ファイル名から施設IDを抽出する"""
    numbers = re.findall(r'\d+', filename)
    if numbers:
        # 最初に見つかった数字を施設IDとして使用
        return numbers[0]
    # デフォルト値として "000" を返す
    return "000"

# トリミング関数
def trim(image, bg_color=(255,255,255)):
    """背景以外を自動トリミング"""
    bg = Image.new(image.mode, image.size, bg_color)
    diff = ImageChops.difference(image, bg)
    bbox = diff.getbbox()
    if bbox:
        return image.crop(bbox)
    else:
        return image  # 内容がなければトリミングしない

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

# 0_input_imagesフォルダの中に画像があるか確認
input_files = scan_directory(input_folder)
if not input_files:
    print("処理する画像がありません。0_input_imagesに画像を配置してください。")
    sys.exit(1)

print(f"{len(input_files)} 個の画像ファイルが見つかりました。")
print("画像のトリミングとリサイズを開始...")

processed_files = {}  # 処理したファイルと施設IDを記録
keep_original_names = {}  # 元の名前を保持するファイル

for file_path, filename, relative_path in input_files:
    try:
        img = Image.open(file_path).convert("RGB")

        # Access_で始まるファイル名かどうかをチェック
        is_access = is_access_filename(filename)

        # 内容エリアを自動トリミング
        trimmed = trim(img)
        
        # アスペクト比を保持してリサイズ
        w, h = trimmed.size
        
        # 全ての画像をアスペクト比を保持したままリサイズ
        # 980x550の比率を保つように調整
        target_ratio = target_size[0] / target_size[1]  # 980/550 = 約1.78
        img_ratio = w / h
        
        # 画像のアスペクト比に応じて適切にリサイズ
        if img_ratio > target_ratio:  # 画像が横長の場合
            new_w = target_size[0]
            new_h = int(new_w / img_ratio)
        else:  # 画像が縦長の場合
            new_h = target_size[1]
            new_w = int(new_h * img_ratio)
            
        # 高さが500~650pxの範囲内の場合は、そのアスペクト比を尊重
        if 500 <= h <= 650:
            print(f"画像 {relative_path} の高さは {h}px で、範囲内 (500-650px) です。アスペクト比を保持します。")
        
        # リサイズ実行
        resized = trimmed.resize((new_w, new_h), RESAMPLING_FILTER)

        # 背景画像を作成し、中央に貼り付け
        background = Image.new("RGB", target_size, background_color)
        x = (target_size[0] - new_w) // 2
        y = (target_size[1] - new_h) // 2
        background.paste(resized, (x, y))

        # 出力先のディレクトリ構造を維持
        rel_dir = os.path.dirname(relative_path)
        if rel_dir:
            rel_temp_dir = os.path.join(temp_folder, rel_dir)
            os.makedirs(rel_temp_dir, exist_ok=True)
        else:
            rel_temp_dir = temp_folder

        # 処理した画像を一時フォルダに保存（元のファイル名を変更しない）
        temp_filename = os.path.splitext(filename)[0] + ".webp"
        temp_path = os.path.join(rel_temp_dir, temp_filename)
        background.save(temp_path, "WEBP", quality=100, lossless=True)
        
        # ファイル名から施設IDを抽出
        facility_id = extract_facility_id(filename)
        facility_id = str(facility_id).zfill(3)  # 施設ID（3桁）
        
        # 処理したファイル情報を記録
        if is_access:
            keep_original_names[relative_path] = True
            print(f"⭕️トリミング＋リサイズ完了 (名前保持): {relative_path} -> {os.path.join(os.path.dirname(relative_path), temp_filename)}")
        else:
            processed_files[relative_path] = facility_id
            print(f"⭕️トリミング＋リサイズ完了: {relative_path} -> {os.path.join(os.path.dirname(relative_path), temp_filename)}")
    except Exception as e:
        print(f"エラー: ファイル {relative_path} の処理中にエラーが発生しました: {e}")
        continue

print("全画像の処理が完了、出力処理へ...")

# 名前を変更してoutput_imagesに出力
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
        
        # Access_で始まる場合は元のファイル名を変更しない
        found = False
        for orig_path in keep_original_names.keys():
            orig_filename = os.path.basename(orig_path)
            orig_basename = os.path.splitext(orig_filename)[0]
            current_basename = os.path.splitext(filename)[0]
            
            if orig_basename == current_basename:
                dst = os.path.join(full_output_dir, filename)
                shutil.copy2(src, dst)
                print(f"出力完了 (元の名前を変更しない): {current_rel_path}")
                found = True
                break
                
        if found:
            continue
            
        # 対応する施設ID情報を検索
        found = False
        for orig_path in processed_files.keys():
            orig_filename = os.path.basename(orig_path)
            orig_basename = os.path.splitext(orig_filename)[0]
            current_basename = os.path.splitext(filename)[0]
            
            if orig_basename == current_basename:
                # 新しいファイル名を生成
                facility_id = processed_files[orig_path]
                new_filename = f"Access_{facility_id}_01.webp"
                
                dst = os.path.join(full_output_dir, new_filename)
                shutil.copy2(src, dst)
                print(f"出力完了: {current_rel_path} -> {os.path.join(rel_output_dir, new_filename) if rel_output_dir else new_filename}")
                found = True
                break
        
        if not found:
            print(f"警告: {current_rel_path} の施設ID情報がありません。スキップします。")

print(f"⭕️全{len(input_files)}個の画像の処理が完了し、2_output_imagesに出力しました！")
