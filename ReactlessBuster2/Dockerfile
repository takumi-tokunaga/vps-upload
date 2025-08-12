# Python 3.11の軽量版を使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージの更新と必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# アプリケーションコードをコピー
COPY . .

# Pythonの依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# データベースとログ用のボリュームポイントを作成
VOLUME ["/app/db", "/app/logs"]

# 環境変数を設定
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# ボットを起動
CMD ["python", "./app/bot.py"]
