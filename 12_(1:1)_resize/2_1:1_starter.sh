#!/bin/bash
# スクリプトのディレクトリに切り替え
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

while true; do
  # ユーザーに画像サイズを入力してもらう
  read -p "画像サイズを入力してください（例: 960）: " image_size
  
  # 入力が数字かどうか確認
  if ! [[ "$image_size" =~ ^[0-9]+$ ]]; then
    echo "エラー: 数字を入力してください"
    continue
  fi
  
  # Python 実行
  echo "😎 1:1比率（${image_size}x${image_size}）に画像をリサイズします..."
  python3 "$SCRIPT_DIR/1:1_resize_images.py" "$image_size"
  
  if [ $? -eq 0 ]; then
    echo "🥳完了しました。"
  else
    echo "😢失敗しました。"
  fi

  read -p "もう一度実行しますか？ (y/n): " yn
  case $yn in
    [Yy]* ) continue;;
    * ) echo "終了します。"; break;;
  esac
done 