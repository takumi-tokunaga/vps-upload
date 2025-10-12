# Python 3.11の軽量版を使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app
COPY . .

# Pythonの依存関係をコピーしてインストール
RUN pip install --no-cache-dir -r requirements.txt


# ボットを起動
CMD ["uvicorn", "sugercraft.asgi:application", "--host", "0.0.0.0", "--port", "8000"]