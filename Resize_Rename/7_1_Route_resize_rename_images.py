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
    input_folder = os.path.join(base_dir, "0_input_images")
    temp_folder = os.path.join(base_dir, "1_temp_images")
    output_folder = os.path.join(base_dir, "2_output_images")
else:
    # 実行ファイルのあるディレクトリを取得
    if getattr(sys, 'frozen', False):
        # ビルドされた実行ファイルの場合
        executable_dir = os.path.dirname(sys.executable)
    else:
        # Pythonスクリプトの場合
        executable_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 複数の可能なディレクトリパスを試し、Image_HRER!を優先的に探す
    possible_paths = [
        os.path.join(executable_dir, "Image_HRER!"),  # 実行ファイルのあるディレクトリのImage_HRER!
        "Image_HRER!",  # カレントディレクトリのImage_HRER!
        os.path.join(os.getcwd(), "Image_HRER!"),  # 作業ディレクトリのImage_HRER!
        ".",  # カレントディレクトリ
    ]
    
    base_dir = None
    for path in possible_paths:
        if os.path.exists(os.path.join(path, "0_input_images")):
            base_dir = path
            break
    
    # それでも見つからない場合、実行ファイルのあるディレクトリから上位ディレクトリを探索
    if base_dir is None:
        current_dir = executable_dir
        while current_dir != "/" and base_dir is None:
            test_path = os.path.join(current_dir, "Image_HRER!")
            if os.path.exists(os.path.join(test_path, "0_input_images")):
                base_dir = test_path
                break
            current_dir = os.path.dirname(current_dir)
    
    # それでも見つからない場合、実行ファイルのあるディレクトリを使用
    if base_dir is None:
        base_dir = executable_dir
        print(f"⚠️  警告: Image_HRER!ディレクトリが見つかりませんでした。実行ファイルのあるディレクトリを使用します: {base_dir}")
    
    input_folder = os.path.join(base_dir, "0_input_images")
    temp_folder = os.path.join(base_dir, "1_temp_images")
    output_folder = os.path.join(base_dir, "2_output_images")

# 使用するディレクトリパスを表示
print(f"📁 入力ディレクトリ: {os.path.abspath(input_folder)}")
print(f"📁 一時ディレクトリ: {os.path.abspath(temp_folder)}")
print(f"📁 出力ディレクトリ: {os.path.abspath(output_folder)}")
print()

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

target_width = 960  # 目標の幅を960に変更
target_height = 720  # 目標の高さを720に変更
min_height = 650  # 最小許容高さ
max_height = 800  # 最大許容高さ

# コマンド引数を入力（施設IDとルート番号）
if len(sys.argv) < 3:
    print("=" * 50)
    print("🖼️  Route 画像処理ツール")
    print("=" * 50)
    print("施設番号とルート番号を入力してください（例: 施設番号: 123, ルート番号: 1）")
    print("注意: 画像を 0_input_images ディレクトリに入れておいてください")
    print()
    
    # 対話式で施設番号を入力（空欄の場合はデフォルト000を使用）
    while True:
        try:
            facility_input = input("施設番号を入力してください: ").strip()
            if facility_input:
                if facility_input.isdigit():
                    facility_id = facility_input  # 元の入力を保持
                    break
                else:
                    print("❌ 有効な数字を入力してください！")
            else:
                facility_id = "000"
                print("施設番号が入力されていません。デフォルト000で続行します…")
                break
        except (EOFError, KeyboardInterrupt):
            print("\nプログラムを終了します")
            sys.exit(0)
    
    # 対話式でルート番号を入力（空欄の場合はデフォルト00を使用）
    while True:
        try:
            route_input = input("ルート番号を入力してください: ").strip()
            if route_input:
                if route_input.isdigit():
                    route_number = route_input  # 元の入力を保持
                    break
                else:
                    print("❌ 有効な数字を入力してください！")
            else:
                route_number = "00"
                print("ルート番号が入力されていません。デフォルト00で続行します…")
                break
        except (EOFError, KeyboardInterrupt):
            print("\nプログラムを終了します")
            sys.exit(0)
    
    print(f"✅ 施設番号が設定されました: {facility_id}")
    print(f"✅ ルート番号が設定されました: {route_number}")
    print()
else:
    facility_id = str(sys.argv[1])  # 元の入力を保持
    route_number = str(sys.argv[2])  # 元の入力を保持

# 施設IDとルート番号のフォーマット（元の入力を保持し、3桁に強制しない）

# フォルダが存在しない場合、作成する
os.makedirs(temp_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

def is_route_filename(filename):
    """ファイル名がRoute_で始まるかどうかをチェック"""
    return filename.startswith("Route_")

def extract_number(filename):
    """ファイル名から番号を抽出する"""
    numbers = re.findall(r'\d+', filename)
    if numbers:
        return numbers[-1]
    return "00"

def trim_white_borders(img, bg_color=(255, 255, 255), threshold=235):
    """空白の境界を自動的にトリミングする（しきい値を設定可能）"""
    # グレースケールに変換
    img_gray = img.convert('L')
    
    # しきい値より明るいピクセルをマスク
    mask = Image.eval(img_gray, lambda x: 0 if x >= threshold else 255)
    
    # 実際のコンテンツの境界を取得
    bbox = mask.getbbox()
    
    if bbox:
        # 余白を追加せずに直接トリミング
        return img.crop(bbox)
    else:
        return img  # 内容がなければトリミングしない

def process_image(img):
    """画像を処理する（空白の境界をトリミングし、アスペクト比を維持しながらリサイズ）"""
    original_width, original_height = img.size
    
    if original_width <= 0 or original_height <= 0:
        print(f"警告: 画像サイズが無効です ({original_width}x{original_height})。スキップします。")
        return img
    
    # 空白の境界をトリミング
    trimmed_img = trim_white_borders(img, threshold=235)
    print(f"トリミング: {original_width}x{original_height} -> {trimmed_img.width}x{trimmed_img.height}")
    
    # トリミング後のサイズ
    trimmed_width, trimmed_height = trimmed_img.size
    
    if trimmed_width <= 0 or trimmed_height <= 0:
        print("警告: トリミング後のサイズが無効です。元の画像を使用します。")
        trimmed_img = img
        trimmed_width, trimmed_height = original_width, original_height
        
    trimmed_ratio = float(trimmed_width) / float(trimmed_height) if trimmed_height > 0 else 1.0
    target_ratio = float(target_width) / float(target_height)  # 960/720 = 1.33
    
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
        
        # 高さが650-800pxの範囲内の場合
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

while True:
    # ステップ1: サイズ調整してtemp_imagesに保存
    print("画像のリサイズとトリミングを開始します...")
    processed_files = {}  # 処理したファイルと抽出された番号を記録
    keep_original_names = {}  # 元の名前を保持するファイル

    # 入力フォルダを再帰的にスキャン
    image_files = scan_directory(input_folder)
    print(f"{len(image_files)} 個の画像ファイルが見つかりました。")

    for file_path, filename, relative_path in image_files:
        # Route_で始まるファイル名かどうかをチェック
        is_route = is_route_filename(filename)
        
        try:
            img = Image.open(file_path).convert("RGB")
            
            print(f"読み込み: {relative_path} ({img.width}x{img.height})")
            
            # 画像処理実行
            processed = process_image(img)
            
            # ファイル名から番号を抽出して保存
            number = extract_number(filename)
            processed_files[relative_path] = number
            
            # Route_で始まる場合は元の名前を保持
            if is_route:
                keep_original_names[relative_path] = True
            
            # 元のファイル名を保持したまま、WebP形式に変換
            base_name = os.path.splitext(filename)[0]
            temp_filename = f"{base_name}.webp"
            
            # 出力先のディレクトリ構造を維持
            rel_dir = os.path.dirname(relative_path)
            if rel_dir:
                rel_temp_dir = os.path.join(temp_folder, rel_dir)
                os.makedirs(rel_temp_dir, exist_ok=True)
                output_path = os.path.join(rel_temp_dir, temp_filename)
            else:
                output_path = os.path.join(temp_folder, temp_filename)
            
            # 画質を100%に設定して保存（無圧縮）
            processed.save(output_path, "WEBP", quality=100, lossless=True)
            
            if is_route:
                print(f"⭕️処理完了（名前を変更しません）: {relative_path} -> {os.path.join(os.path.dirname(relative_path), temp_filename)} ({processed.width}x{processed.height})")
            else:
                print(f"⭕️処理完了: {relative_path} -> {os.path.join(os.path.dirname(relative_path), temp_filename)} ({processed.width}x{processed.height})")
        except Exception as e:
            print(f"エラー: ファイル {relative_path} の処理中にエラーが発生しました: {e}")
            continue

    print("全画像の処理が完了しました。名前の変更と出力処理に進みます...")

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
            found = False
            
            # 対応する元のファイル名を検索
            for orig_path in processed_files.keys():
                orig_filename = os.path.basename(orig_path)
                orig_basename = os.path.splitext(orig_filename)[0]
                current_basename = os.path.splitext(filename)[0]
                
                if orig_basename == current_basename:
                    # 出力先のディレクトリ構造を維持
                    rel_output_dir = os.path.dirname(current_rel_path)
                    if rel_output_dir:
                        full_output_dir = os.path.join(output_folder, rel_output_dir)
                        os.makedirs(full_output_dir, exist_ok=True)
                    else:
                        full_output_dir = output_folder
                    
                    # 元の名前を保持するかどうか確認
                    if orig_path in keep_original_names:
                        # 元の名前を変更しない（拡張子のみwebpに変更）
                        dst = os.path.join(full_output_dir, filename)
                        shutil.copy2(src, dst)
                        print(f"出力完了（元の名前を変更しません）: {current_rel_path}")
                        found = True
                        break
                    
                    # 対応する番号を見つける
                    number = processed_files[orig_path]
                    
                    # 新しいファイル名を生成
                    new_filename = f"Route_{facility_id}_{route_number}_{number.zfill(2)}.webp"
                    
                    dst = os.path.join(full_output_dir, new_filename)
                    shutil.copy2(src, dst)
                    print(f"出力完了: {current_rel_path} -> {os.path.join(rel_output_dir, new_filename) if rel_output_dir else new_filename}")
                    found = True
                    break
            
            if not found:
                print(f"警告: {current_rel_path} に対応する元のファイル名が見つかりませんでした。")

    print("⭕️全画像の処理が完了し、2_output_imagesに出力しました！")

    # 続けて実行しますか？（続行時は施設番号とルート番号を再入力。空欄または無効な場合はデフォルト0000）
    while True:
        try:
            user_input = input("続けて実行しますか？（y/n）: ").strip().lower()
            if user_input in ['y', 'yes', 'はい', '続行']:
                print("🔄 処理を再開します...")
                # 出力ディレクトリをクリア
                for folder in [temp_folder, output_folder]:
                    clear_folder(folder)
                # 施設番号を再入力
                while True:
                    try:
                        rein_fac = input("施設番号を入力してください: ").strip()
                        if rein_fac and rein_fac.isdigit():
                            facility_id = rein_fac
                            break
                        else:
                            facility_id = "000"
                            print("有効な数字が入力されていません。デフォルト施設番号000で続行します…")
                            break
                    except (EOFError, KeyboardInterrupt):
                        print("\nプログラムを終了します")
                        sys.exit(0)
                # ルート番号を再入力
                while True:
                    try:
                        rein_route = input("ルート番号を入力してください: ").strip()
                        if rein_route and rein_route.isdigit():
                            route_number = rein_route
                            break
                        else:
                            route_number = "00"
                            print("有効な数字が入力されていません。デフォルトルート番号00で続行します…")
                            break
                    except (EOFError, KeyboardInterrupt):
                        print("\nプログラムを終了します")
                        sys.exit(0)
                # 再処理 - メインループに戻る
                break
            elif user_input in ['n', 'no', 'いいえ', '終了', 'やめる']:
                print("👋 プログラムを終了します。ご利用ありがとうございました！")
                sys.exit(0)
            else:
                print("❌ y または n を入力してください")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 プログラムを終了します。ご利用ありがとうございました！")
            sys.exit(0) 