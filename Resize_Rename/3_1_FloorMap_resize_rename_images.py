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
    # 実行ファイルのディレクトリを取得
    if getattr(sys, 'frozen', False):
        # ビルドされた実行ファイルの場合
        executable_dir = os.path.dirname(sys.executable)
    else:
        # Pythonスクリプトの場合
        executable_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 複数のパスを試行、Image_HRER!を優先
    possible_paths = [
        os.path.join(executable_dir, "Image_HRER!"),  # 実行ファイルディレクトリのImage_HRER!
        "Image_HRER!",  # カレントディレクトリのImage_HRER!
        os.path.join(os.getcwd(), "Image_HRER!"),  # 作業ディレクトリのImage_HRER!
        ".",  # カレントディレクトリ
    ]
    
    base_dir = None
    for path in possible_paths:
        if os.path.exists(os.path.join(path, "0_input_images")):
            base_dir = path
            break
    
    # まだ見つからない場合、実行ファイルディレクトリから上位ディレクトリを探索
    if base_dir is None:
        current_dir = executable_dir
        while current_dir != "/" and base_dir is None:
            test_path = os.path.join(current_dir, "Image_HRER!")
            if os.path.exists(os.path.join(test_path, "0_input_images")):
                base_dir = test_path
                break
            current_dir = os.path.dirname(current_dir)
    
    # それでも見つからない場合、実行ファイルディレクトリを使用
    if base_dir is None:
        base_dir = executable_dir
        print(f"⚠️  警告: Image_HRER!ディレクトリが見つかりませんでした。実行ファイルのディレクトリを使用します: {base_dir}")
    
    input_folder = os.path.join(base_dir, "0_input_images")
    temp_folder = os.path.join(base_dir, "1_temp_images")
    output_folder = os.path.join(base_dir, "2_output_images")

# 使用ディレクトリパスを表示
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

target_size = (750, 750)  # キャンパスサイズを750x750に変更
background_color = (255, 255, 255)  # 背景は白
content_target_size = 720  # 内容エリアの最大辺を720にリサイズ

# コマンド引数を入力（施設ID）
if len(sys.argv) < 2:
    print("=" * 50)
    print("🖼️  FloorMap 画像処理ツール")
    print("=" * 50)
    print("施設番号を入力してください（例: 7、12、123、1234）")
    print("注意: 画像は 0_input_images フォルダに入れてください")
    print("画像上の数字は階数になります。数字が正しいかご確認ください")
    print()
    
    # 対話式入力（空欄の場合はデフォルトID 000を使用）
    while True:
        try:
            user_input = input("施設番号を入力してください: ").strip()
            if user_input:
                if user_input.isdigit():
                    facility_id = user_input
                    break
                else:
                    print("❌ 有効な数字を入力してください！")
            else:
                facility_id = "000"
                print("施設番号が未入力のため、デフォルト000で続行します…")
                break
        except (EOFError, KeyboardInterrupt):
            print("\nプログラムを終了します")
            sys.exit(0)
    
    print(f"✅ 施設番号が設定されました: {facility_id}")
    print()
else:
    facility_id = str(sys.argv[1])  # 入力値をそのまま使用

# 施設IDのフォーマット（入力値をそのまま使用、3桁固定しない）

# フォルダが存在しない場合、作成する
os.makedirs(temp_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

def extract_floor_number(filename):
    """ファイル名から階数を抽出する"""
    numbers = re.findall(r'\d+', filename)
    if numbers:
        return numbers[-1]
    return None

def is_floormap_filename(filename):
    """ファイル名がFloorMap_で始まるかどうかをチェック"""
    return filename.startswith("FloorMap_")

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

while True:
    # ステップ1: サイズ調整してtemp_imagesに保存
    print("画像のトリミングとリサイズを開始します...")
    processed_files = {}  # 処理したファイルと階数を記録
    keep_original_names = {}  # 元の名前を保持するファイル

    # 入力フォルダを再帰的にスキャン
    image_files = scan_directory(input_folder)
    print(f"{len(image_files)} 個の画像ファイルが見つかりました。")

    for file_path, filename, relative_path in image_files:
        # FloorMap_で始まるファイル名かどうかをチェック
        is_floormap = is_floormap_filename(filename)
        floor_number = extract_floor_number(filename)
        if floor_number is None and not is_floormap:
            print(f"警告: {relative_path} から階数を抽出できませんでした。スキップします。")
            continue

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

            # 元のファイル名を維持して拡張子だけwebpに変更
            base_name = os.path.splitext(filename)[0]
            temp_filename = f"{base_name}.webp"
            temp_path = os.path.join(rel_temp_dir, temp_filename)
            background.save(temp_path, "WEBP", quality=100, lossless=True)

            # 処理したファイル情報を記録
            if is_floormap:
                keep_original_names[relative_path] = True
                print(f"⭕️トリミング＋リサイズ完了 (名前保持): {relative_path} -> {os.path.join(os.path.dirname(relative_path), temp_filename)}")
            else:
                processed_files[relative_path] = floor_number
                print(f"⭕️トリミング＋リサイズ完了: {relative_path} -> {os.path.join(os.path.dirname(relative_path), temp_filename)}")
        except Exception as e:
            print(f"エラー: ファイル {relative_path} の処理中にエラーが発生しました: {e}")
            continue


    print("全画像のトリミングとリサイズが完了し、出力処理に進みます...")

    # ステップ2: output_imagesに出力（ここで名前を変更）
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
        
            # FloorMap_で始まるファイル名の場合は元の名前を変更しない
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
            
            # 対応する階数情報を検索
            found = False
            for orig_path in processed_files.keys():
                orig_filename = os.path.basename(orig_path)
                orig_basename = os.path.splitext(orig_filename)[0]
                current_basename = os.path.splitext(filename)[0]
                
                if orig_basename == current_basename:
                    # 新しいファイル名を生成
                    floor_number = processed_files[orig_path]
                    new_filename = f"FloorMap_{facility_id}_a{floor_number}_1.webp"
                    
                    dst = os.path.join(full_output_dir, new_filename)
                    shutil.copy2(src, dst)
                    print(f"出力完了: {current_rel_path} -> {os.path.join(rel_output_dir, new_filename) if rel_output_dir else new_filename}")
                    found = True
                    break
            
            if not found:
                print(f"警告: {current_rel_path} の階数情報がありません。スキップします。")

    print("⭕️全画像のトリミング・リサイズ処理が完了し、2_output_imagesに出力しました！")

    # 続けて実行しますか？（続行時は施設番号を再入力、空欄や無効時はデフォルト0000）
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
                        rein = input("施設番号を入力してください: ").strip()
                        if rein and rein.isdigit():
                            facility_id = rein
                            break
                        else:
                            facility_id = "000"
                            print("有効な数字が未入力のため、デフォルト施設番号000で続行します…")
                            break
                    except (EOFError, KeyboardInterrupt):
                        print("\nプログラムを終了します")
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
