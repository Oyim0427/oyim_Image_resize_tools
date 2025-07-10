#!/bin/bash
# スクリプトのディレクトリに切り替え
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# 项目根目录（包含虚拟环境的目录）
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PYTHON="$PROJECT_ROOT/venv/bin/python"

while true; do
  # 施設IDを入力
  read -p "😎施設IDを入力してください（例：123）: " FACILITY_ID

  # 使用虚拟环境中的Python执行脚本
  "$VENV_PYTHON" "$SCRIPT_DIR/FloorMap_resize_rename_images.py" "$FACILITY_ID"
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