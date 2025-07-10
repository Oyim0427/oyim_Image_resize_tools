#!/bin/bash
# スクリプトのディレクトリに切り替え
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

while true; do
  # 会场番号を手動で入力
  read -p "😎会場IDを入力してください（例：1234）: " NUMBER

  # Python 実行 - 使用系统Python
  /usr/bin/python3 "$SCRIPT_DIR/Layout_resize_rename_images.py" "$NUMBER" "$SCRIPT_DIR"
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