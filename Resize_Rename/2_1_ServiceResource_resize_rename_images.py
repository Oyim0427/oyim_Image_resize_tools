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
if len(sys.argv) > 2:
    base_dir = sys.argv[2]
    input_folder = os.path.join(base_dir, "0_input_images")
    temp_folder = os.path.join(base_dir, "1_temp_images")
    output_folder = os.path.join(base_dir, "2_output_images")
else:
    # 実行ファイルのディレクトリを取得
    if getattr(sys, 'frozen', False):
        # ビルドされた実行ファイルの場合
        executable_dir = os.path.dirname(sys.executable)
    else:
        # Pythonスクリプトの場合
        executable_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 複数のパスを試し、Image_HRER!を優先的に探す
    possible_paths = [
        os.path.join(executable_dir, "Image_HRER!"),  # 実行ファイルのディレクトリ内Image_HRER!
        "Image_HRER!",  # カレントディレクトリのImage_HRER!
        os.path.join(os.getcwd(), "Image_HRER!"),  # 作業ディレクトリのImage_HRER!
        ".",  # カレントディレクトリ
    ]
    
    base_dir = None
    for path in possible_paths:
        if os.path.exists(os.path.join(path, "0_input_images")):
            base_dir = path
            break
    
    # まだ見つからない場合、実行ファイルのディレクトリから上位ディレクトリを探索
    if base_dir is None:
        current_dir = executable_dir
        while current_dir != "/" and base_dir is None:
            test_path = os.path.join(current_dir, "Image_HRER!")
            if os.path.exists(os.path.join(test_path, "0_input_images")):
                base_dir = test_path
                break
            current_dir = os.path.dirname(current_dir)
    
    # それでも見つからない場合、実行ファイルのディレクトリを使用
    if base_dir is None:
        base_dir = executable_dir
        print(f"⚠️  警告: Image_HRER!ディレクトリが見つかりませんでした。実行ファイルのディレクトリを使用します: {base_dir}")
    
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

target_width = 900  # 目標の幅
target_height = 600  # 目標の高さ
target_ratio = target_width / target_height  # 3:2 = 1.5
min_height = 550  # 最小許容高さ
max_height = 650  # 最大許容高さ

# コマンド引数を入力（会場ID）
if len(sys.argv) < 2:
    print("=" * 50)
    print("🖼️  ServiceResource 画像処理ツール")
    print("=" * 50)
    print("会場番号を入力してください（例: 7、12、123、1234）")
    print("注意: 画像を 0_input_images ディレクトリに入れてください")
    print()
    
    # 対話式入力（空入力可、全てのファイルがServiceResource_で始まる場合はそのまま続行）
    while True:
        try:
            user_input = input("会場番号を入力してください: ").strip()
            if user_input:
                # 入力が数字かどうかを検証
                if user_input.isdigit():
                    venue_id = user_input  # 元の入力を保持
                    break
                else:
                    print("❌ 有効な数字を入力してください！")
            else:
                # 空入力時、入力ディレクトリ内が全てServiceResource_で始まるか確認
                def _all_prefixed():
                    def _scan(dir_path):
                        for item in os.listdir(dir_path):
                            item_path = os.path.join(dir_path, item)
                            if os.path.isdir(item_path):
                                if not _scan(item_path):
                                    return False
                            elif item.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                                if not item.startswith("ServiceResource_"):
                                    return False
                        return True
                    return _scan(input_folder)

                if _all_prefixed():
                    print("全ての画像名がServiceResource_で始まっていることを検出しました。元の名前を保持して続行します…")
                    venue_id = "0000"  # プレースホルダー、ServiceResource_接頭辞ファイルのリネームには使われません
                    break
                else:
                    print("❌ 会場番号が入力されておらず、ServiceResource_で始まらないファイルが存在するため続行できません。")
        except (EOFError, KeyboardInterrupt):
            print("\nプログラムを終了しました")
            sys.exit(0)
    
    print(f"✅ 会場番号が設定されました: {venue_id}")
    print()
else:
    venue_id = str(sys.argv[1])  # 元の入力を保持

# 会場IDのフォーマット（元の入力を保持、4桁に強制しない）

# フォルダが存在しない場合、作成する
os.makedirs(temp_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

def extract_number(filename):
    """ファイル名から番号を抽出する"""
    numbers = re.findall(r'\d+', filename)
    if numbers:
        return numbers[-1]
    return None

def is_serviceresource_filename(filename):
    """ファイル名がServiceResource_で始まるかどうかをチェック"""
    return filename.startswith("ServiceResource_")

def process_image(img):
    """画像を処理する（リサイズ、必要に応じてトリミング）"""
    original_width, original_height = img.size
    
    if original_width <= 0 or original_height <= 0:
        print(f"警告: 画像サイズが無効です ({original_width}x{original_height})。スキップします。")
        return img
        
    original_ratio = float(original_width) / float(original_height)  

    # まず900pxに合わせてリサイズ
    new_width = target_width
    new_height = int(target_width / original_ratio) if original_ratio > 0 else target_height
    
    if new_height <= 0:
        new_height = target_height
        
    img = img.resize((new_width, new_height), RESAMPLING_FILTER)

    # 高さが550-650pxの範囲内の場合、トリミングしない
    if min_height <= new_height <= max_height:
        return img

    # 範囲外の場合、3:2比率にトリミング
    if original_ratio > target_ratio:
        # 画像が3:2より横長の場合
        crop_width = int(target_height * target_ratio)
        img = img.resize((int(crop_width * (new_width/target_width)), target_height), RESAMPLING_FILTER)
        left = (img.width - target_width) // 2
        img = img.crop((left, 0, left + target_width, target_height))
    else:
        # 画像が3:2より縦長の場合
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

# メイン処理ループ
while True:
    # ステップ1: サイズ調整してtemp_imagesに保存
    print("画像のリサイズとトリミングを開始します...")
    processed_files = {}  # 処理したファイルと抽出された番号を記録
    keep_original_names = {}  # 元の名前を保持するファイル

    # 入力フォルダを再帰的にスキャン
    image_files = scan_directory(input_folder)
    print(f"{len(image_files)} 個の画像ファイルが見つかりました。")

    for file_path, filename, relative_path in image_files:
        # ServiceResource_で始まるファイル名かどうかをチェック
        is_serviceresource = is_serviceresource_filename(filename)
        
        # ファイル名から番号を抽出して保存
        number = extract_number(filename)
        if number is None and not is_serviceresource:
            print(f"警告: {relative_path} から番号を抽出できませんでした。スキップします。")
            continue

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

            # 元のファイル名を保持したまま、WebP形式で保存
            base_name = os.path.splitext(filename)[0]
            temp_filename = f"{base_name}.webp"
            output_path = os.path.join(rel_temp_dir, temp_filename)
            processed.save(output_path, "WEBP", quality=100, lossless=True)
            
            # 処理したファイル情報を記録
            if is_serviceresource:
                keep_original_names[relative_path] = True
                print(f"⭕️処理完了（名前を変更しません）: {relative_path} -> {os.path.join(os.path.dirname(relative_path), temp_filename)} ({processed.width}x{processed.height})")
            else:
                processed_files[relative_path] = number
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
            
            # 出力先のディレクトリ構造を維持
            rel_output_dir = os.path.dirname(current_rel_path)
            if rel_output_dir:
                full_output_dir = os.path.join(output_folder, rel_output_dir)
                os.makedirs(full_output_dir, exist_ok=True)
            else:
                full_output_dir = output_folder
            
            # ServiceResource_で始まるファイル名の場合は元の名前を保持
            found = False
            for orig_path in keep_original_names.keys():
                orig_filename = os.path.basename(orig_path)
                orig_basename = os.path.splitext(orig_filename)[0]
                current_basename = os.path.splitext(filename)[0]
                
                if orig_basename == current_basename:
                    dst = os.path.join(full_output_dir, filename)
                    shutil.copy2(src, dst)
                    print(f"出力完了（元の名前を保持）: {current_rel_path}")
                    found = True
                    break
                    
            if found:
                continue
            
            # 対応する番号情報を検索
            found = False
            for orig_path in processed_files.keys():
                orig_filename = os.path.basename(orig_path)
                orig_basename = os.path.splitext(orig_filename)[0]
                current_basename = os.path.splitext(filename)[0]
                
                if orig_basename == current_basename:
                    # 新しいファイル名を生成
                    number = processed_files[orig_path]
                    new_filename = f"ServiceResource_{venue_id}_{number}.webp"
                    
                    dst = os.path.join(full_output_dir, new_filename)
                    shutil.copy2(src, dst)
                    print(f"出力完了: {current_rel_path} -> {os.path.join(rel_output_dir, new_filename) if rel_output_dir else new_filename}")
                    found = True
                    break
            
            if not found:
                print(f"警告: {current_rel_path} の番号情報がありません。スキップします。")

    print("⭕️全画像の処理が完了し、2_output_imagesに出力しました！")

    # 続けて実行しますか？（続行時は会場番号を再入力、空または無効時はデフォルト0000）
    while True:
        try:
            user_input = input("続けて実行しますか？（y/n）: ").strip().lower()
            if user_input in ['y', 'yes', 'はい', '続行']:
                print("🔄 処理を再開します...")
                # 出力ディレクトリをクリア
                for folder in [temp_folder, output_folder]:
                    clear_folder(folder)
                # 会場番号を再入力
                while True:
                    try:
                        rein = input("会場番号を入力してください: ").strip()
                        if rein and rein.isdigit():
                            venue_id = rein
                            break
                        else:
                            venue_id = "0000"
                            print("有効な数字が入力されなかったため、デフォルト会場番号0000で続行します…")
                            break
                    except (EOFError, KeyboardInterrupt):
                        print("\nプログラムを終了しました")
                        sys.exit(0)
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
