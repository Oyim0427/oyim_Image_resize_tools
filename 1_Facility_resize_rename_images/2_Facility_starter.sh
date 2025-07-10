#!/bin/bash
# スクリプトのディレクトリに切り替え
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

while true; do
  # 施設IDを入力
  read -p "😎施設IDを入力してください（例：123）: " FACILITY_ID

  # Python 実行
  python3 "$SCRIPT_DIR/Facility_resize_rename_images.py" "$FACILITY_ID"
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