# Python 3.11の軽量版を使用
FROM python:3.11-slim

# borgbackupのインストール
RUN apt update && apt install -y borgbackup

# 作業ディレクトリを設定
WORKDIR /app
COPY . .

# Pythonの依存関係をコピーしてインストール
RUN pip install --no-cache-dir -r requirements.txt


# ボットを起動
CMD ["python", "mincraft_backuper.py"]
