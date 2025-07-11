#!/bin/bash
# スクリプトのディレクトリに切り替え
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# プロジェクトのルートディレクトリを特定
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 仮想環境のPythonインタープリタへのパス
VENV_PYTHON="$PROJECT_ROOT/venv/bin/python"

while true; do
  # 施設IDを入力
  read -p "😎施設IDを入力してください（例：123）: " facility_id
  
  # 施設IDを3桁に変換
  facility_id=$(printf "%03d" $facility_id)
  
  # ルート番号を入力
  read -p "😎ルート番号を入力してください（1,2,3,4など）: " route_number
  
  # Pythonスクリプトを実行 - 使用虚拟环境Python
  "$VENV_PYTHON" "$SCRIPT_DIR/Route_resize_rename_images.py" "$facility_id" "$route_number"
  
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