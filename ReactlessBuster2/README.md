# ReactlessBuster2

Discordサーバーの非アクティブメンバーを自動監視・管理するボット

## 機能

- サーバーメンバーのアクティビティを自動監視
- 非アクティブメンバーへの自動警告
- 一定期間後の自動キック機能
- Google Spreadsheetへのデータエクスポート
- SQLiteデータベースでのデータ管理

## セットアップ

### 方法1: Docker を使用（推奨）

#### 前提条件
- Docker Desktop for Windows
- Docker Compose

#### セットアップ手順

1. **Dockerセットアップスクリプトを実行**
```bash
scripts\docker-setup.bat
```

2. **環境変数を設定**
`.env`ファイルを編集して必要な値を設定

3. **Google APIキーファイルを配置**
`credentials/`フォルダにGoogle APIキーファイルを配置

4. **Dockerイメージをビルド**
```bash
scripts\docker-build.bat
```

5. **コンテナを起動**
```bash
scripts\docker-run.bat
```

#### Docker管理コマンド

```bash
# 管理ツールを起動
scripts\docker-manage.bat

# 手動でのコマンド例
docker-compose logs -f      # ログ表示
docker-compose down         # 停止
docker-compose restart      # 再起動
docker-compose ps           # 状態確認
```

### 方法2: 従来のPython環境

### 方法2: 従来のPython環境

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example`をコピーして`.env`ファイルを作成し、必要な値を設定してください。

```bash
cp .env.example .env
```

設定が必要な項目：
- `DISCORD_TOKEN`: Discordボットのトークン
- `GOOGLE_API_KEY_FILE`: Google APIサービスアカウントキーファイルのパス
- その他の設定は必要に応じて調整

### 3. データベースの初期化

```bash
python -m utils.database_init
```

### 4. ボットの起動

```bash
python bot.py
```

## ディレクトリ構造

```
ReactlessBuster2/
├── bot.py                 # メインボットファイル
├── config.py             # 設定管理
├── requirements.txt      # Python依存関係
├── pyproject.toml        # プロジェクト設定
├── .env.example         # 環境変数テンプレート
├── .gitignore           # Git無視ファイル
├── README.md            # このファイル
├── cogs/                # ボット機能モジュール
│   ├── __init__.py      # パッケージ初期化
│   ├── database.py      # データベース操作
│   └── monitor.py       # メンバー監視機能
├── credentials/         # 機密ファイル（Gitで除外）
│   └── *.json          # Google APIキーなど
├── db/                  # データベースファイル
│   └── members.db
├── scripts/             # ユーティリティスクリプト
│   ├── setup.bat       # 自動セットアップ
│   └── run.bat         # ボット起動
└── utils/               # ユーティリティ関数
    ├── __init__.py          # パッケージ初期化
    ├── activity_tracker.py  # アクティビティ追跡
    ├── database_init.py     # データベース初期化
    ├── exporter.py          # データエクスポート
    ├── logger.py            # ログ機能
    ├── server_cacher.py     # サーバーデータキャッシュ
    └── sync_to_django.py    # Django連携（オプション）
```

## 使用方法

ボットは自動的に以下の処理を実行します：

1. 毎日定時にサーバーメンバーのアクティビティをチェック
2. 非アクティブ日数が閾値を超えたメンバーに警告
3. 警告後、猶予期間を過ぎてもアクティビティがないメンバーをキック
4. 全データをGoogle SpreadsheetとSQLiteデータベースに保存

## 注意事項

- Google APIキーファイルは絶対にGitリポジトリにコミットしないでください
- `.env`ファイルも機密情報を含むため、共有しないでください
- 本番環境では適切な権限設定を行ってください

## ライセンス

このプロジェクトは個人利用を想定しています。

## Docker の利点

- **環境の統一**: 開発・本番環境の一致
- **依存関係の分離**: システムのPython環境に影響なし
- **簡単なデプロイ**: どの環境でも同じように動作
- **リソース制限**: メモリ・CPU使用量の制御
- **ログ管理**: 構造化されたログ出力
- **自動再起動**: コンテナの自動回復

## トラブルシューティング

### Docker関連
- **ポート競合**: 他のサービスとのポート競合を確認
- **メモリ不足**: `docker-compose.yml`のメモリ制限を調整
- **ボリューム問題**: `docker volume prune`でボリュームをクリーンアップ

### ボット関連
- **トークンエラー**: `.env`ファイルのDISCORD_TOKENを確認
- **権限エラー**: ボットの権限設定を確認
- **APIキーエラー**: Google APIキーファイルのパスを確認
