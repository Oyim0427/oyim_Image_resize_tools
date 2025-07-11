#!/bin/bash
# スクリプトのディレクトリに切り替え
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# プロジェクトのルートディレクトリを特定
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 仮想環境のPythonインタープリタへのパス
VENV_PYTHON="$PROJECT_ROOT/venv/bin/python"

while true; do
  # 会場IDを入力
  read -p "😎会場IDを入力してください（例：1234）: " VENUE_ID

  # Python 実行 - 使用虚拟环境Python
  "$VENV_PYTHON" "$SCRIPT_DIR/ServiceResource_resize_rename_images.py" "$VENUE_ID"
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