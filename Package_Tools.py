#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画像処理ツールパッケージャー - PyInstallerスタンドアロン実行ファイル版
使い方: python package_tools.py
"""

import os
import sys
import subprocess

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
    print("1. 🚀 すべてのツールをスタンドアロン実行ファイルとしてビルド")
    print("   - メリット：完全に独立、Python環境不要")
    print("   - デメリット：ファイルサイズが大きい、初回起動が遅い")
    print()
    print("2. 🔧 PyInstaller依存関係のインストール/アップデート")
    print()
    print("3. 📁 出力ディレクトリを確認")
    print()
    print("0. ❌ 終了")
    print()

def install_dependencies():
    """依存関係をインストール"""
    print("PyInstallerをインストール中...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller"])
        print("✓ PyInstallerのインストール/アップデートに成功しました！")
    except subprocess.CalledProcessError as e:
        print(f"✗ PyInstallerのインストールに失敗しました: {e}")
        return False
    
    return True

def run_pyinstaller_build():
    """PyInstallerビルドを実行"""
    print("PyInstallerビルドを開始します...")
    
    # PyInstallerがインストールされているか確認
    try:
        import PyInstaller
        print("✓ PyInstallerはインストール済みです")
    except ImportError:
        print("PyInstallerがインストールされていません。インストールします...")
        if not install_dependencies():
            return
    
    try:
        subprocess.check_call([sys.executable, "build_standalone.py"])
        print("\n✓ PyInstallerビルドが完了しました！")
        print("\n出力ファイルの場所：")
        print("- 実行ファイル: dist/ ディレクトリ")
        print("- 配布パッケージ: Image_Resize_Tools_Standalone/ ディレクトリ")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ PyInstallerビルドに失敗しました: {e}")

def show_output_directories():
    """出力ディレクトリを表示"""
    print("出力ディレクトリ情報：")
    print()
    
    if os.path.exists("dist"):
        print("📁 dist/ ディレクトリ (実行ファイル):")
        files = os.listdir("dist")
        if files:
            for file in files:
                size = os.path.getsize(os.path.join("dist", file))
                size_mb = size / (1024 * 1024)
                print(f"   - {file} ({size_mb:.1f} MB)")
        else:
            print("   (空)")
    else:
        print("📁 dist/ ディレクトリが存在しません")
    
    print()
    
    if os.path.exists("Image_Resize_Tools_Standalone"):
        print("📁 Image_Resize_Tools_Standalone/ ディレクトリ (配布パッケージ):")
        files = os.listdir("Image_Resize_Tools_Standalone")
        if files:
            for file in files:
                print(f"   - {file}")
        else:
            print("   (空)")
    else:
        print("📁 Image_Resize_Tools_Standalone/ ディレクトリが存在しません")
    
    print()
    print("💡 ヒント：ビルド完了後、Image_Resize_Tools_Standalone/ ディレクトリを")
    print("   他の環境にコピーして、そのまま利用できます（Pythonのインストール不要）")

def main():
    """メイン関数"""
    while True:
        print_banner()
        print_menu()
        
        try:
            choice = input("選択してください (0-3): ").strip()
            
            if choice == "0":
                print("\n👋 ではまた！")
                break
            elif choice == "1":
                print("\n🚀 スタンドアロン実行ファイルのビルドを開始します...")
                run_pyinstaller_build()
            elif choice == "2":
                print("\n🔧 依存関係をインストール/アップデートします...")
                install_dependencies()
            elif choice == "3":
                print("\n📁 出力ディレクトリを表示します...")
                show_output_directories()
            else:
                print("\n❌ 無効な選択です。0～3を入力してください。")
            
            if choice in ["1", "2", "3"]:
                input("\nEnterキーを押して続行...")
                
        except KeyboardInterrupt:
            print("\n\n👋 ユーザーによる中断、ではまた！")
            break
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            input("Enterキーを押して続行...")

if __name__ == "__main__":
    main()
