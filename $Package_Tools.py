#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画像処理ツールパッケージャー - PyInstallerスタンドアロン実行ファイル版
使い方: python3 $Package_Tools.py
"""

import os
import sys
import subprocess
import shutil
import time
import stat

# 常に現在のスクリプトのディレクトリをプロジェクトルートとすることで、作業ディレクトリの違いによるスクリプトの見失いを防ぐ
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def auto_set_executable_permission():
    """スクリプトの実行権限を自動で設定する"""
    script_path = os.path.abspath(__file__)
    try:
        # 現在の権限を確認
        current_mode = os.stat(script_path).st_mode
        if not (current_mode & stat.S_IXUSR):  # ユーザー実行権限がない場合
            # 実行権限を追加
            os.chmod(script_path, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            print(f"✓ 実行権限を自動で設定しました: {script_path}")
            print("これで直接実行できます: ./$Package_Tools.py")
            print()
    except Exception as e:
        print(f"⚠️ 実行権限を設定できませんでした: {e}")
        print("手動で実行してください: chmod +x $Package_Tools.py")
        print()

def print_banner():
    """バナーを表示"""
    print("=" * 60)
    print("           🖼️  画像処理ツールパッケージャー 🖼️")
    print("=" * 60)
    print()

def print_menu():
    """メニューを表示"""
    print("PyInstallerスタンドアロン実行ファイルパッケージ案")
    print()
    print("1. 🔧 PyInstaller依存関係のインストール/アップデート")
    print()
    print("2. 🚀 すべてのツールをスタンドアロン実行ファイルとしてビルド")
    print("   - メリット：完全に独立、Python環境不要")
    print("   - デメリット：ファイルサイズが大きい、初回起動が遅い")
    print()
    print("3. 📁 出力ディレクトリを表示")
    print()
    print("0. ❌ 終了")
    print()

def setup_virtual_environment():
    """仮想環境をセットアップ"""
    venv_dir = os.path.join(PROJECT_ROOT, "venv_package")
    
    if not os.path.exists(venv_dir):
        print("仮想環境を作成中...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
            print("✓ 仮想環境の作成に成功しました")
        except subprocess.CalledProcessError as e:
            print(f"✗ 仮想環境の作成に失敗しました: {e}")
            return None
    
    # 仮想環境内のPythonパスを取得
    if sys.platform == "win32":
        python_path = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        python_path = os.path.join(venv_dir, "bin", "python")
    
    if not os.path.exists(python_path):
        print(f"✗ 仮想環境のPythonパスが存在しません: {python_path}")
        return None
    
    return python_path

def install_dependencies():
    """依存関係をインストール"""
    print("PyInstallerをインストール中...")
    
    # 仮想環境をセットアップ
    venv_python = setup_virtual_environment()
    if not venv_python:
        return False
    
    try:
        # pipをアップグレード
        subprocess.check_call([venv_python, "-m", "pip", "install", "--upgrade", "pip"])
        # PyInstallerとPillow（ランタイム依存）をインストール
        subprocess.check_call([venv_python, "-m", "pip", "install", "--upgrade", "pyinstaller", "pillow"])
        print("✓ 依存関係のインストール/アップデート成功！（PyInstaller, Pillow）")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ PyInstallerのインストールに失敗しました: {e}")
        return False

def build_executable(venv_python, script_path, output_name, index, total):
    """単一の実行ファイルをビルド"""
    print(f"[{index}/{total}] ビルド中: {script_path}")
    
    # PyInstallerコマンド
    cmd = [
        venv_python, "-m", "PyInstaller",
        "--onefile",  # 単一ファイル
        "--console",  # コンソールウィンドウあり（macOS互換）
        "--name", output_name,
        "--distpath", os.path.join(PROJECT_ROOT, "dist"),
        "--workpath", os.path.join(PROJECT_ROOT, "build"),
        "--specpath", os.path.join(PROJECT_ROOT, "build"),
        "--clean",  # 一時ファイルをクリーン
        script_path
    ]
    
    start_time = time.time()
    
    try:
        # 詳細な出力を表示して問題を診断
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
        build_time = time.time() - start_time
        
        if result.returncode == 0:
            # 出力ファイルを確認（Windowsは .exe）
            expected_name = output_name + (".exe" if sys.platform == "win32" else "")
            output_file = os.path.join(PROJECT_ROOT, "dist", expected_name)
            if os.path.exists(output_file):
                size_mb = os.path.getsize(output_file) / (1024 * 1024)
                print(f"✓ {expected_name} ビルド成功 ({size_mb:.1f} MB, {build_time:.1f}s)")
                return True
            else:
                print(f"✗ {output_name} ビルド失敗: 出力ファイルが存在しません")
                return False
        else:
            print(f"✗ {output_name} ビルド失敗:")
            print(f"  エラーメッセージ: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ {output_name} ビルド失敗: {e}")
        return False

def run_pyinstaller_build():
    """PyInstallerビルドを実行"""
    print("PyInstallerビルドを開始します...")
    
    # 仮想環境をセットアップ
    venv_python = setup_virtual_environment()
    if not venv_python:
        print("❌ 仮想環境をセットアップできません")
        return
    
    # PyInstallerがインストールされているか確認
    try:
        subprocess.check_call([venv_python, "-c", "import PyInstaller"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✓ PyInstallerはインストール済みです")
    except subprocess.CalledProcessError:
        print("PyInstallerがインストールされていません。インストール中...")
        if not install_dependencies():
            return
    
    # Pillowがビルド環境に存在するか確認（画像処理のため）
    try:
        subprocess.check_call([venv_python, "-c", "import PIL"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✓ Pillow はインストール済みです")
    except subprocess.CalledProcessError:
        print("Pillow がインストールされていません。インストール中...")
        try:
            subprocess.check_call([venv_python, "-m", "pip", "install", "--upgrade", "pillow"])
            print("✓ Pillow のインストールに成功しました")
        except subprocess.CalledProcessError as e:
            print(f"✗ Pillow のインストールに失敗しました: {e}")
            return
    
    # 出力ディレクトリを作成
    os.makedirs(os.path.join(PROJECT_ROOT, "dist"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_ROOT, "build"), exist_ok=True)
    
    # パッケージ化するPythonスクリプト一覧
    scripts_to_build = [
        ("Resize_Rename/1_1_Facility_resize_rename_images.py", "1_Facility_Resizer"),
        ("Resize_Rename/2_1_ServiceResource_resize_rename_images.py", "2_ServiceResource_Resizer"),
        ("Resize_Rename/3_1_FloorMap_resize_rename_images.py", "3_FloorMap_Resizer"),
        ("Resize_Rename/4_1_Layout_resize_rename_images.py", "4_Layout_Resizer"),
        ("Resize_Rename/5_1_Access_resize_rename_images.py", "5_Access_Resizer"),
        ("Resize_Rename/6_1_1_Product_banner_resize_rename_images.py", "6_1_Product_Banner_Resizer"),
        ("Resize_Rename/6_2_1_Product_singlefood_resize_rename_images.py", "6_2_Product_SingleFood_Resizer"),
        ("Resize_Rename/7_1_Route_resize_rename_images.py", "7_Route_Resizer"),
        ("Resize/10_1_32_resize_images.py", "10_3_2_Resizer"),
        ("Resize/11_1_169_resize_images.py", "11_16_9_Resizer"),
        ("Resize/12_1_43_resize_images.py", "12_4_3_Resizer"),
        ("Resize/13_1_11_resize_images.py", "13_1_1_Resizer"),
    ]
    
    # 存在するスクリプトのみフィルタ（絶対パスで確認）
    existing_scripts = []
    for rel_path, name in scripts_to_build:
        abs_path = os.path.join(PROJECT_ROOT, rel_path)
        if os.path.exists(abs_path):
            existing_scripts.append((abs_path, name))
    
    if not existing_scripts:
        print("❌ Pythonスクリプトファイルが見つかりません")
        return
    
    print(f"{len(existing_scripts)} 個のスクリプトファイルが見つかりました。ビルドを開始します...")
    print()
    
    # すべてのスクリプトをビルド
    success_count = 0
    total_scripts = len(existing_scripts)
    
    for i, (script_path, output_name) in enumerate(existing_scripts, 1):
        if build_executable(venv_python, script_path, output_name, i, total_scripts):
            success_count += 1
    
    print()
    print("=" * 60)
    print(f"ビルド完了！成功: {success_count}/{total_scripts}")
    print("=" * 60)
    
    if success_count > 0:
        print(f"出力ディレクトリ: {os.path.join(PROJECT_ROOT, 'dist')}/")
        
        # デプロイパッケージを作成
        create_deployment_package()
        
        print("\n🎉 ビルド成功！これで：")
        print("$Image_Resize_Tools_Application/ デプロイパッケージを他の環境にコピーして利用できます")
    else:
        print("❌ すべてのビルドが失敗しました。エラーメッセージを確認してください")

def create_deployment_package():
    """デプロイパッケージを作成"""
    print("\nデプロイパッケージを作成中...")
    
    # デプロイディレクトリを作成
    deploy_dir = os.path.join(PROJECT_ROOT, "$Image_Resize_Tools_Application")
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    os.makedirs(deploy_dir)
    
    # 実行ファイルをコピー
    dist_dir = os.path.join(PROJECT_ROOT, "dist")
    if os.path.exists(dist_dir):
        for file in os.listdir(dist_dir):
            file_path = os.path.join(dist_dir, file)
            
            # 実行ファイルの種類ごとに処理
            if file.endswith(".exe"):  # Windows
                shutil.copy2(file_path, deploy_dir)
            elif file.endswith(".app"):  # macOSアプリケーションパッケージ
                shutil.copytree(file_path, os.path.join(deploy_dir, file))
            elif not file.endswith(".") and os.path.isfile(file_path):  # Unix実行ファイル
                shutil.copy2(file_path, deploy_dir)
    
    # 使い方ガイドを作成
    create_usage_guide(deploy_dir)
    
    # Image_HRER!ディレクトリを作成（デプロイパッケージ用）
    create_image_hrer_dirs(os.path.join(deploy_dir, "Image_HRER!"))
    
    print(f"✓ デプロイパッケージが作成されました: {deploy_dir}/")



def create_readme(deploy_dir):
    """READMEファイルを作成"""
    readme_content = """# 🖼️ 画像処理ツール - スタンドアロン版

## 📖 説明
これは画像処理ツールのスタンドアロン版で、Python 環境をインストールせずに利用できます。各ツールは実行ファイルとしてパッケージされており、ダブルクリックで起動できます。

## 🚀 クイックスタート
1. フォルダ一式をターゲット環境へコピー
2. 画像を `Image_HRER!/0_input_images/` ディレクトリに配置
3. 対応する実行ファイルをダブルクリック（例: `Facility_Resizer`）
4. 画面の指示に従ってパラメータを入力
5. `Image_HRER!/2_output_images/` で結果を確認

## 🛠️ ツール分類

### 🏢 業務画像処理
- Facility_Resizer: 施設画像処理
- ServiceResource_Resizer: サービスリソース画像処理
- FloorMap_Resizer: フロアマップ画像処理
- Layout_Resizer: レイアウト画像処理
- Access_Resizer: アクセス画像処理
- Route_Resizer: ルート画像処理

### 🍽️ 製品画像処理
- Product_SingleFood_Resizer: 製品単品画像処理
- Product_Banner_Resizer: 製品バナー画像処理

### 📐 比率調整ツール
- 3_2_Resizer: 3:2 比率の画像処理
- 16_9_Resizer: 16:9 比率の画像処理
- 4_3_Resizer: 4:3 比率の画像処理
- 1_1_Resizer: 1:1 比率の画像処理

## 📁 ディレクトリ構成
```
$Image_Resize_Tools_Application/
├── Image_HRER!/
│   ├── 0_input_images/    ← 入力画像を配置
│   ├── 1_temp_images/     ← 一時ファイル
│   └── 2_output_images/   ← 出力画像

├── 各種_Resizer            ← 実行ファイル
├── 使用方法.md             ← 詳細な使い方
└── $User_manual.xlsx       ← ユーザーマニュアル
```

## ⚠️ 注意事項
- 初回起動には数秒かかる場合があります
- 十分なディスク容量を確保してください
- Windows/macOS/Linux をサポート
- まずは `使用方法.md` をお読みください

## 📞 サポート
詳細な使い方は `使用方法.md` を参照してください
"""
    
    with open(os.path.join(deploy_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

def create_usage_guide(deploy_dir):
    """使用ガイドを作成"""
    usage_content = """# 🖼️ 画像処理ツール 使用方法

## 🚀 はじめに（クイックスタート）

### 方法1：実行ファイルを直接起動（推奨）
1. 画像を `Image_HRER!/0_input_images/` に配置
2. 対応する実行ファイルをダブルクリック（例: `Facility_Resizer`）
3. 画面の指示に従ってパラメータを入力
4. `Image_HRER!/2_output_images/` で結果を確認


## 📋 ツール一覧

### 🏢 業務画像処理ツール
- Facility_Resizer: 施設画像処理
- ServiceResource_Resizer: サービスリソース画像処理
- FloorMap_Resizer: フロアマップ画像処理
- Layout_Resizer: レイアウト画像処理
- Access_Resizer: アクセス画像処理
- Route_Resizer: ルート画像処理

### 🍽️ 製品画像処理ツール
- Product_SingleFood_Resizer: 製品単品画像処理
- Product_Banner_Resizer: 製品バナー画像処理

### 📐 比率調整ツール
- 3_2_Resizer: 3:2 比率の画像処理
- 16_9_Resizer: 16:9 比率の画像処理
- 4_3_Resizer: 4:3 比率の画像処理
- 1_1_Resizer: 1:1 比率の画像処理

## 📁 ディレクトリ構成
```
$Image_Resize_Tools_Application/
├── Image_HRER!/
│   ├── 0_input_images/    ← 入力画像を配置
│   ├── 1_temp_images/     ← 一時ファイル（自動生成）
│   └── 2_output_images/   ← 出力画像

├── 各種_Resizer            ← 実行ファイル
└── 使用方法.md             ← 本ファイル
```

## 💡 使い方のヒント
1. 初めての方は「方法1（直接起動）」がおすすめです
2. 複数画像は一括で入力ディレクトリに入れて処理できます
3. 対応形式: jpg, png, webp などの一般的な画像形式
4. 出力形式: 既定で webp（高品質かつサイズが小さい）

## 🔧 よくある質問
- 画像が表示されない: `Image_HRER!/0_input_images/` に配置されているか確認
- 反応がない: 初回起動は数秒かかる場合があります
- 権限エラー: 出力ディレクトリへの書き込み権限を確認

## 📞 サポート
不明点は `$User_manual.xlsx`（ユーザーマニュアル）をご確認ください
"""
    
    with open(os.path.join(deploy_dir, "使用説明書.md"), "w", encoding="utf-8") as f:
        f.write(usage_content)

def show_output_directories():
    """出力ディレクトリを表示"""
    print("出力ディレクトリ情報：")
    print()
    
    dist_dir = os.path.join(PROJECT_ROOT, "dist")
    if os.path.exists(dist_dir):
        print("📁 dist/ ディレクトリ（実行ファイル）:")
        files = os.listdir(dist_dir)
        if files:
            for file in files:
                size = os.path.getsize(os.path.join(dist_dir, file))
                size_mb = size / (1024 * 1024)
                print(f"   - {file}（{size_mb:.1f} MB）")
        else:
            print("   （空）")
    else:
        print("📁 dist/ ディレクトリは存在しません")
    
    print()
    
    deploy_dir = os.path.join(PROJECT_ROOT, "$Image_Resize_Tools_Application")
    if os.path.exists(deploy_dir):
        print("📁 $Image_Resize_Tools_Application/ ディレクトリ（配布パッケージ）:")
        files = os.listdir(deploy_dir)
        if files:
            for file in files:
                print(f"   - {file}")
        else:
            print("   （空）")
    else:
        print("📁 $Image_Resize_Tools_Application/ ディレクトリは存在しません")
    
    print()
    print("💡 ヒント：ビルド完了後、$Image_Resize_Tools_Application/ フォルダを")
    print("   他の環境へコピーするだけで利用できます（Python のインストール不要）")

def create_image_hrer_dirs(image_hrer_root: str):
    """Image_HRER! のディレクトリ構成を作成: 0_input_images/ 1_temp_images/ 2_output_images/"""
    os.makedirs(image_hrer_root, exist_ok=True)
    for sub in ["0_input_images", "1_temp_images", "2_output_images"]:
        os.makedirs(os.path.join(image_hrer_root, sub), exist_ok=True)

def safe_replace_with_symlink(link_path: str, target_path: str):
    """link_path を target_path を指すシンボリックリンクに置き換え、元をバックアップする"""
    # 既に存在しシンボリックリンクの場合は削除して再作成
    if os.path.islink(link_path):
        try:
            os.unlink(link_path)
        except OSError:
            pass
    elif os.path.exists(link_path):
        # 既存のディレクトリ/ファイルをバックアップ
        backup_path = link_path + ".bak"
        idx = 1
        while os.path.exists(backup_path):
            backup_path = link_path + f".bak{idx}"
            idx += 1
        try:
            os.rename(link_path, backup_path)
            print(f"バックアップ済み: {link_path} -> {backup_path}")
        except OSError as e:
            print(f"⚠️ バックアップできませんでした {link_path}: {e}")
    # シンボリックリンクを作成
    try:
        os.symlink(target_path, link_path)
        print(f"リンク作成: {link_path} -> {target_path}")
    except OSError as e:
        print(f"⚠️ シンボリックリンクの作成に失敗しました {link_path} -> {target_path}: {e}")

def link_all_tools_to_image_hrer():
    """全ツールのディレクトリに Image_HRER! へのシンボリックリンクを作成"""
    image_hrer_root = os.path.join(PROJECT_ROOT, "Image_HRER!")
    create_image_hrer_dirs(image_hrer_root)
    
    tool_dirs = [
        os.path.dirname(p) for p, _ in [
            ("Resize_Rename/1_1_Facility_resize_rename_images.py", "Facility_Resizer"),
            ("Resize_Rename/2_1_ServiceResource_resize_rename_images.py", "ServiceResource_Resizer"),
            ("Resize_Rename/3_1_FloorMap_resize_rename_images.py", "FloorMap_Resizer"),
            ("Resize_Rename/4_1_Layout_resize_rename_images.py", "Layout_Resizer"),
            ("Resize_Rename/5_1_Access_resize_rename_images.py", "Access_Resizer"),
            ("Resize_Rename/6_1_1_Product_banner_resize_rename_images.py", "Product_Banner_Resizer"),
            ("Resize_Rename/6_2_1_Product_singlefood_resize_rename_images.py", "Product_SingleFood_Resizer"),
            ("Resize_Rename/7_1_Route_resize_rename_images.py", "Route_Resizer"),
            ("Resize/10_1_3:2_resize_images.py", "3_2_Resizer"),
            ("Resize/11_1_16:9_resize_images.py", "16_9_Resizer"),
            ("Resize/12_1_4:3_resize_images.py", "4_3_Resizer"),
            ("Resize/13_1_1:1_resize_images.py", "1_1_Resizer"),
        ]
    ]
    # 重複排除
    tool_dirs = sorted(set(tool_dirs))
    
    for rel_dir in tool_dirs:
        abs_dir = os.path.join(PROJECT_ROOT, rel_dir)
        if not os.path.isdir(abs_dir):
            continue
        for sub in ["0_input_images", "1_temp_images", "2_output_images"]:
            link_path = os.path.join(abs_dir, sub)
            target_path = os.path.join(image_hrer_root, sub)
            safe_replace_with_symlink(link_path, target_path)
    
    print("\n✓ Image_HRER! の設定が完了しました。画像は Image_HRER!/0_input_images/ にまとめて配置してください")

def main():
    """主函数"""
    auto_set_executable_permission()  # 実行権限を自動で設定する関数を呼び出す
    while True:
        print_banner()
        print_menu()
        
        try:
            choice = input("選択してください (0-3): ").strip()
            
            if choice == "0":
                print("\n👋 ではまた！")
                break
            elif choice == "1":
                print("\n🔧 依存関係をインストール/更新しています...")
                install_dependencies()
            elif choice == "2":
                print("\n🚀 スタンドアロン実行ファイルのビルドを開始します...")
                run_pyinstaller_build()
            elif choice == "3":
                print("\n📁 出力ディレクトリを表示します...")
                show_output_directories()
            else:
                print("\n❌ 無効な選択です。0-3 を入力してください")
            
            if choice in ["1", "2", "3"]:
                input("\nEnterキーで続行...")
                
        except KeyboardInterrupt:
            print("\n\n👋 ユーザーにより中断されました。ではまた！")
            break
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            input("Enterキーで続行...")

if __name__ == "__main__":
    main()
