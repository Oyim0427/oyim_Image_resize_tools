#!/bin/bash
# スクリプトのディレクトリに切り替え
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# プロジェクトのルートディレクトリを特定
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 仮想環境のPythonインタープリタへのパス
VENV_PYTHON="$PROJECT_ROOT/venv/bin/python"

while true; do
  # Python 実行
  echo "😎 3:2比率（900x600）に画像をリサイズし、WebP形式で出力します..."
  "$VENV_PYTHON" "$SCRIPT_DIR/3:2_resize_images.py"
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