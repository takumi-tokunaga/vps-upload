# Python 3.11の軽量版を使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app
COPY . .

# Pythonの依存関係をコピーしてインストール
RUN pip install --no-cache-dir -r requirements.txt


# ASGIサーバー（daphne）で起動
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "sugercraft.asgi:application"]