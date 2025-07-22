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
if len(sys.argv) > 2:
    base_dir = sys.argv[2]
else:
    base_dir = "."
input_folder = os.path.join(base_dir, "0_input_images")
temp_folder = os.path.join(base_dir, "1_temp_images")
output_folder = os.path.join(base_dir, "2_output_images")

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

target_size = (750, 750)  # キャンパスサイズ
background_color = (255, 255, 255)  # 背景は白
content_target_size = 650  # 内容エリアの最大辺を650にリサイズ

# コマンド引数を入力（会場番号）
if len(sys.argv) < 2:
    print("使い方: resize_rename_images.py 番号（例: 7、12、123、1234）")
    sys.exit(1)
set_number = str(sys.argv[1]).zfill(4)  # 会場ID（4桁）
prefix = f"Layout_{set_number}_"

# フォルダが存在しない場合、作成する
os.makedirs(temp_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

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

# ステップ1: サイズ調整してtemp_imagesに保存
print("画像のトリミングとリサイズを開始...")

# 入力フォルダを再帰的にスキャン
image_files = scan_directory(input_folder)
print(f"{len(image_files)} 個の画像ファイルが見つかりました。")

for file_path, filename, relative_path in image_files:
    try:
        img = Image.open(file_path).convert("RGB")

        # 内容エリアを自動トリミング
        trimmed = trim(img)

        # 内容エリアをcontent_target_sizeにリサイズ
        w, h = trimmed.size
        scale = content_target_size / max(w, h)
        new_w, new_h = int(w * scale), int(h * scale)
        trimmed = trimmed.resize((new_w, new_h), RESAMPLING_FILTER)

        # 背景画像を作成し、中央に貼り付け
        background = Image.new("RGB", target_size, background_color)
        x = (target_size[0] - trimmed.width) // 2
        y = (target_size[1] - trimmed.height) // 2
        background.paste(trimmed, (x, y))

        # 出力先のディレクトリ構造を維持
        rel_dir = os.path.dirname(relative_path)
        if rel_dir:
            rel_temp_dir = os.path.join(temp_folder, rel_dir)
            os.makedirs(rel_temp_dir, exist_ok=True)
        else:
            rel_temp_dir = temp_folder

        # webp形式でtemp_imagesに保存
        output_filename = os.path.splitext(filename)[0] + ".webp"
        output_path = os.path.join(rel_temp_dir, output_filename)
        background.save(output_path, "WEBP", quality=100, lossless=True)
        print(f"⭕️トリミング＋リサイズ完了: {relative_path} -> {os.path.join(os.path.dirname(relative_path), output_filename)}")
    except Exception as e:
        print(f"エラー: ファイル {relative_path} の処理中にエラーが発生しました: {e}")
        continue

print("全画像のトリミングとリサイズが完了、リネーム処理へ...")

# ステップ2: リネームしてoutput_imagesに出力
def get_new_name(filename):
    # 既にLayout_で始まる場合はリネームしない
    if filename.startswith("Layout_"):
        return filename
    
    # すべての空白（半角・全角・ゼロ幅など）を除去
    name_for_check = re.sub(r'[\s\u3000\u200b]+', '', filename)
    
    # プロジェクター有のバリエーションをチェック
    has_projector = (
        # プロジェクター検出 - 特殊な文字の組み合わせも考慮
        "プロジェクター" in name_for_check or
        "プロジェクタ" in name_for_check or
        # 特殊な文字の組み合わせ検出 (プロジェクター)
        ("フ" in name_for_check and "ロ" in name_for_check and "シ" in name_for_check and "ェ" in name_for_check and "ク" in name_for_check and "タ" in name_for_check) or
        # スクプロ検出
        "スクプロ" in name_for_check or
        # 特殊な文字の組み合わせ検出 (スクプロ)
        ("スク" in name_for_check and "フ" in name_for_check and "ロ" in name_for_check) or
        # 英語表記
        "projector" in name_for_check.lower() or
        "pj" in name_for_check.lower() or
        re.search(r'pj[有あ]り', name_for_check.lower()) is not None or
        re.search(r'PJ[有あ]り', name_for_check) is not None or
        # 有の文字が含まれる場合も考慮
        ("有" in name_for_check and ("フ" in name_for_check or "ロ" in name_for_check or "シ" in name_for_check or "ェ" in name_for_check or "ク" in name_for_check or "タ" in name_for_check))
    )
    
    # 特定のパターンを最初にチェック
    if "スクール" in name_for_check and has_projector:
        return prefix + "10.webp"
    
    if ("コノ字" in name_for_check or "コの字" in name_for_check or "こノ字" in name_for_check or "この字" in name_for_check) and has_projector:
        return prefix + "13.webp"
    
    if ("T字島型" in name_for_check or "T字島" in name_for_check or "T字島形" in name_for_check or "T島型" in name_for_check) and has_projector:
        return prefix + "12.webp"
    
    if "シアター" in name_for_check and has_projector:
        return prefix + "9.webp"
    
    if ("島形" in name_for_check or "島型" in name_for_check) and has_projector:
        return prefix + "11.webp"
    
    # 一般のパターンをチェック
    if "T字島型" in name_for_check or "T字島" in name_for_check or "T字島形" in name_for_check or "T島型" in name_for_check:
        return prefix + "4.webp"
    if "コノ字" in name_for_check or "コの字" in name_for_check or "こノ字" in name_for_check or "この字" in name_for_check:
        return prefix + "8.webp"
    if "ロノ字" in name_for_check or "ロの字" in name_for_check:
        return prefix + "5.webp"
    if "正餐" in name_for_check or "着席" in name_for_check:
        return prefix + "6.webp"
    if "立食" in name_for_check:
        return prefix + "7.webp"
    if "スクール" in name_for_check:
        return prefix + "2.webp"
    if "シアター" in name_for_check:
        return prefix + "1.webp"
    if "島形" in name_for_check or "島型" in name_for_check:
        return prefix + "3.webp"
    return None

# WebP画像を新しい名前で最終フォルダに出力する
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
        
        new_name = get_new_name(filename)
        if new_name == filename:
            # 既にLayout_で始まる場合はそのままコピー
            dst = os.path.join(full_output_dir, filename)
            shutil.copy2(src, dst)
            print(f"{current_rel_path} -> {current_rel_path}（リネームせずコピー）")
        elif new_name:
            dst = os.path.join(full_output_dir, new_name)
            shutil.copy2(src, dst)
            print(f"{current_rel_path} -> {os.path.join(rel_output_dir, new_name) if rel_output_dir else new_name}")
        else:
            print(f"{current_rel_path} -> ルールとの不一致により、処理は行われませんでした。")

print("⭕️全画像のトリミング・リサイズ・リネーム処理が完了し、2_output_imagesに出力しました！")
