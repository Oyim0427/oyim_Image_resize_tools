#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ビルドスクリプト：すべてのPythonツールをスタンドアロン実行ファイルにパッケージ化
使い方：python build_standalone.py
"""

import os
import subprocess
import sys
import shutil
import time
from pathlib import Path

def install_pyinstaller():
    """PyInstallerをインストール"""
    try:
        import PyInstaller
        print("✓ PyInstallerはすでにインストールされています")
        return True
    except ImportError:
        print("PyInstallerをインストール中...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstallerのインストールに成功しました")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ PyInstallerのインストールに失敗しました: {e}")
            return False

def build_executable(script_path, output_name, index, total):
    """単一の実行ファイルをビルド"""
    print(f"[{index}/{total}] ビルド中: {script_path}")
    
    # PyInstallerコマンド
    cmd = [
        "pyinstaller",
        "--onefile",  # 単一ファイル
        "--noconsole",  # コンソールウィンドウなし
        "--name", output_name,
        "--distpath", "dist",
        "--workpath", "build",
        "--specpath", "build",
        "--clean",  # 一時ファイルをクリーン
        script_path
    ]
    
    start_time = time.time()
    
    try:
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        build_time = time.time() - start_time
        
        # 出力ファイルを確認
        output_file = os.path.join("dist", output_name)
        if os.path.exists(output_file):
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"✓ {output_name} のビルドに成功しました ({size_mb:.1f} MB, {build_time:.1f}s)")
            return True
        else:
            print(f"✗ {output_name} のビルドに失敗しました: 出力ファイルが存在しません")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ {output_name} のビルドに失敗しました: {e}")
        return False

def main():
    """メインビルド処理"""
    print("=" * 60)
    print("           🖼️  画像処理ツール スタンドアロン実行ファイルビルダー 🖼️")
    print("=" * 60)
    print()
    
    # PyInstallerのインストールを確認
    if not install_pyinstaller():
        print("❌ PyInstallerのインストールに失敗したため、ビルドを中止します")
        return
    
    # 出力ディレクトリを作成
    os.makedirs("dist", exist_ok=True)
    os.makedirs("build", exist_ok=True)
    
    # パッケージ化するPythonスクリプト一覧
    scripts_to_build = [
        ("1_Facility_resize_rename_images/Facility_resize_rename_images.py", "Facility_Resizer"),
        ("2_ServiceResource_resize_rename_images/ServiceResource_resize_rename_images.py", "ServiceResource_Resizer"),
        ("3_FloorMap_resize_rename_images/FloorMap_resize_rename_images.py", "FloorMap_Resizer"),
        ("4_Layout_resize_rename_images/Layout_resize_rename_images.py", "Layout_Resizer"),
        ("5_Access_resize_rename_images/Access_resize_rename_images.py", "Access_Resizer"),
        ("6_Product_resize_rename_images/Product_singlefood_resize_rename_images.py", "Product_SingleFood_Resizer"),
        ("6_Product_resize_rename_images/Product_banner_resize_rename_images.py", "Product_Banner_Resizer"),
        ("7_Route_resize_rename_images/Route_resize_rename_images.py", "Route_Resizer"),
        ("9_900x600(3:2)_resize/3:2_resize_images.py", "3_2_Resizer"),
        ("10_960x540(16:9)_resize/16:9_resize_images.py", "16_9_Resizer"),
        ("11_960x720(4:3)_resize/4:3_resize_images.py", "4_3_Resizer"),
        ("12_(1:1)_resize/1:1_resize_images.py", "1_1_Resizer"),
    ]
    
    # 存在するスクリプトのみ抽出
    existing_scripts = [(path, name) for path, name in scripts_to_build if os.path.exists(path)]
    
    if not existing_scripts:
        print("❌ Pythonスクリプトが見つかりませんでした")
        return
    
    print(f"{len(existing_scripts)} 個のスクリプトが見つかりました。ビルドを開始します...")
    print()
    
    # すべてのスクリプトをビルド
    success_count = 0
    total_scripts = len(existing_scripts)
    
    for i, (script_path, output_name) in enumerate(existing_scripts, 1):
        if build_executable(script_path, output_name, i, total_scripts):
            success_count += 1
    
    print()
    print("=" * 60)
    print(f"ビルド完了！成功: {success_count}/{total_scripts}")
    print("=" * 60)
    
    if success_count > 0:
        print(f"出力ディレクトリ: dist/")
        
        # デプロイパッケージを作成
        create_deployment_package()
        
        print("\n🎉 ビルド成功！次のことができます：")
        print("1. dist/ ディレクトリ内の実行ファイルを他の環境にコピーして使用")
        print("2. または Image_Resize_Tools_Standalone/ デプロイパッケージを利用")
    else:
        print("❌ すべてのビルドが失敗しました。エラーメッセージを確認してください")

def create_deployment_package():
    """デプロイパッケージを作成"""
    print("\nデプロイパッケージを作成中...")
    
    # デプロイディレクトリ作成
    deploy_dir = "Image_Resize_Tools_Standalone"
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    os.makedirs(deploy_dir)
    
    # 実行ファイルをコピー
    if os.path.exists("dist"):
        for file in os.listdir("dist"):
            if file.endswith(".exe") or not file.endswith("."):  # WindowsとUnixの実行ファイル
                shutil.copy2(os.path.join("dist", file), deploy_dir)
    
    # スタータースクリプトをコピー
    copy_starter_scripts(deploy_dir)
    
    # ユーザーマニュアルをコピー
    if os.path.exists("★User_manual.xlsx"):
        shutil.copy2("★User_manual.xlsx", deploy_dir)
    
    # README作成
    create_readme(deploy_dir)
    
    # 使い方ガイド作成
    create_usage_guide(deploy_dir)
    
    print(f"✓ デプロイパッケージが作成されました: {deploy_dir}/")

def copy_starter_scripts(deploy_dir):
    """スタータースクリプトをコピー"""
    scripts_dir = os.path.join(deploy_dir, "起動スクリプト")
    os.makedirs(scripts_dir, exist_ok=True)
    
    # すべての.shファイルをコピー
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".sh"):
                # 相対パスを作成
                rel_path = os.path.relpath(root, ".")
                target_dir = os.path.join(scripts_dir, rel_path)
                os.makedirs(target_dir, exist_ok=True)
                shutil.copy2(os.path.join(root, file), target_dir)

def create_readme(deploy_dir):
    """READMEファイルを作成"""
    readme_content = """# 画像処理ツール - スタンドアロン版

## 説明
これは画像処理ツールのスタンドアロンバージョンで、Python環境をインストールせずに利用できます。

## 使い方
1. フォルダ全体をターゲット環境にコピーしてください
2. 対応する実行ファイルをダブルクリックして起動
3. または起動スクリプト（.shファイル）を利用

## ツール一覧
- Facility_Resizer: 施設画像処理
- ServiceResource_Resizer: サービスリソース画像処理
- FloorMap_Resizer: フロアマップ画像処理
- Layout_Resizer: レイアウト画像処理
- Access_Resizer: アクセス画像処理
- Product_SingleFood_Resizer: 商品（単品）画像処理
- Product_Banner_Resizer: 商品バナー画像処理
- Route_Resizer: ルート画像処理
- 3_2_Resizer: 3:2比率画像処理
- 16_9_Resizer: 16:9比率画像処理
- 4_3_Resizer: 4:3比率画像処理
- 1_1_Resizer: 1:1比率画像処理

## 注意事項
- 初回起動時は数秒かかる場合があります
- 十分なディスク空き容量を確保してください
- Windows、macOS、Linuxに対応

## サポート
ご不明な点は、元のプロジェクトドキュメントをご参照ください。
"""
    
    with open(os.path.join(deploy_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

def create_usage_guide(deploy_dir):
    """使い方ガイドを作成"""
    usage_content = """# 使い方

## クイックスタート

### Windowsユーザー
1. 実行ファイル（.exe）をダブルクリックして起動
2. 指示に従ってパラメータを入力

### macOS/Linuxユーザー
1. ターミナルで実行ファイルを起動
2. または起動スクリプトを利用

## 詳細な利用手順

### 1. 施設画像処理
- 実行: Facility_Resizer
- 入力: 施設IDと画像番号
- 出力: Facility_XXX_image_N.webp

### 2. サービスリソース画像処理
- 実行: ServiceResource_Resizer
- 入力: サービスリソースID
- 出力: ServiceResource_XXXX_N.webp

### 3. フロアマップ画像処理
- 実行: FloorMap_Resizer
- 入力: フロアIDとエリア番号
- 出力: FloorMap_XX_XX_N.webp

### 4. ルート画像処理
- 実行: Route_Resizer
- 入力: 施設IDとルート番号
- 出力: Route_XXX_X_XXX_NN.webp

### 5. 比率調整ツール
- 3:2比率: 3_2_Resizer
- 16:9比率: 16_9_Resizer
- 4:3比率: 4_3_Resizer
- 1:1比率: 1_1_Resizer

## 入出力ディレクトリ
- 入力画像: 0_input_images/
- 一時ファイル: 1_temp_images/
- 出力画像: 2_output_images/

## トラブルシューティング
1. 入力ディレクトリに画像ファイルがあるか確認してください
2. 出力ディレクトリの権限を確認してください
3. 初回起動時は少し待つ必要があります
"""
    
    with open(os.path.join(deploy_dir, "使い方.md"), "w", encoding="utf-8") as f:
        f.write(usage_content)

if __name__ == "__main__":
    main()
