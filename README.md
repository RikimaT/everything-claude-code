# 総合学習塾ブリッジ SNS 自動投稿システム

## 概要

彦根市稲枝の総合学習塾「ブリッジ」用の SNS 自動投稿システムです。以下の機能を提供します：

- 🔍 **リサーチエンジン** - HP・ブログ・SNS から塾長の投稿スタイルを自動学習
- 📝 **投稿生成エンジン** - Claude API で最適な投稿内容を自動生成
- ⏰ **時間最適化エンジン** - エンゲージメント分析で最適な投稿時間を計算
- 📅 **スケジューラー** - X・Threads・Instagram へ自動投稿

## セットアップ手順

### 1. API キーの取得・確認

#### ① X（Twitter）API

```bash
# X Developer Portal にログイン
# https://developer.x.com

# 手順：
# 1. Projects & Apps → Add App
# 2. User authentication settings を設定
#    - App permissions: Read and Write
#    - Callback URI: http://127.0.0.1:8976/oauth/callback
# 3. Keys and Tokens タブで以下を取得：
#    - API Key (OAuth 2.0 Client ID)
#    - API Secret
#    - Bearer Token
```

#### ② Meta API（Threads・Instagram）

```bash
# Meta Developers へログイン
# https://developers.meta.com

# 手順：
# 1. My Apps → Create App（Businessアプリ）
# 2. Threads Product を追加
# 3. Instagram Product を追加
# 4. Settings → Users and Permissions
#    - Access Token を生成
# 5. 必要な情報：
#    - Meta Access Token
#    - Meta Business ID
#    - Instagram Account ID
```

#### ③ Claude API

```bash
# Anthropic Console にログイン
# https://console.anthropic.com

# API Key を生成・コピー
```

### 2. 環境変数の設定

```bash
# .env ファイルを作成
cp .env.example .env

# .env を編集して API キーを記入
cat .env

# 必須項目：
# - X_OAUTH_CONSUMER_KEY
# - X_OAUTH_CONSUMER_SECRET
# - X_BEARER_TOKEN
# - META_ACCESS_TOKEN
# - META_BUSINESS_ID
# - INSTAGRAM_ACCOUNT_ID
# - CLAUDE_API_KEY
```

### 3. 依存関係のインストール

```bash
# Python 3.9 以上が必要
python --version

# 仮想環境を作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt
```

## 実行方法

### リサーチエンジンの実行

```bash
# HP・ブログから塾長のデータを収集・分析
python research_engine.py

# 出力ファイル：
# - bridge_data.db（収集データ）
# - style_profile.json（分析結果）
```

### 投稿生成エンジンのテスト

```bash
# 投稿案を自動生成
python post_generation_engine.py

# 内容をカスタマイズする場合：
# post_generation_engine.py の topic 変数を編集
```

### 投稿時間の計算

```bash
# 各プラットフォームの最適投稿時間を計算
python optimal_time_engine.py

# 出力ファイル：
# - x_schedule.json
# - threads_schedule.json
# - instagram_schedule.json
```

### スケジューラーの起動

```bash
# 自動投稿を開始（毎日 6:00 AM にポスト生成）
python scheduler.py

# 手動テスト投稿：
# scheduler.py の manual_post() 関数を実行
```

## ディレクトリ構成

```
.
├── README.md                      # このファイル
├── requirements.txt               # Python 依存関係
├── config.yaml                    # 設定ファイル
├── .env.example                   # 環境変数テンプレート
├── x-mcp-setup.md                 # X MCP サーバー設定ガイド
│
├── research_engine.py             # リサーチエンジン
├── post_generation_engine.py      # 投稿生成エンジン
├── optimal_time_engine.py         # 時間最適化エンジン
├── scheduler.py                   # メインスケジューラー
│
└── data/                          # データディレクトリ（自動作成）
    ├── bridge_data.db             # 収集データベース
    ├── style_profile.json         # スタイル分析結果
    ├── published_posts.json       # 投稿履歴
    ├── x_schedule.json            # X 投稿スケジュール
    ├── threads_schedule.json      # Threads 投稿スケジュール
    └── instagram_schedule.json    # Instagram 投稿スケジュール
```

## 主要な機能詳細

### リサーチエンジン（research_engine.py）

- HP・ブログからコンテンツを自動収集
- 塾長の投稿スタイルを分析
- キーワード頻度・感情分析を実施
- SQLite に結果を保存

**分析される要素：**
- 感情的な表現（emotional）
- 行動喚起（action）
- 教育的な内容（teaching）
- 共感（empathy）
- ストーリー（story）
- 問い掛け（question）

### 投稿生成エンジン（post_generation_engine.py）

- Claude API を使用した自動投稿生成
- リサーチ結果を学習した投稿スタイルで生成
- X・Threads・Instagram 別に最適化
- 複数案の生成機能

**生成される内容：**
- X：280字以内のツイート + ハッシュタグ
- Threads：500字以内の投稿
- Instagram：2200字以内のキャプション + ハッシュタグ

### 時間最適化エンジン（optimal_time_engine.py）

- 過去投稿のエンゲージメント分析
- プラットフォーム別の最適投稿時間を計算
- 投稿パターンが検出されないよう時間をランダマイズ
- 2週間先のスケジュールを自動生成

**デフォルト設定：**
- X：朝 7 時、昼 12 時、夜 6 時、夜 9 時
- Threads：朝 9 時、昼 2 時、夜 7 時、夜 9 時
- Instagram：朝 7 時、昼 12 時、夜 6 時、夜 8 時

### スケジューラー（scheduler.py）

- APScheduler で定期実行を管理
- 毎日 6:00 AM に投稿を生成・スケジュール
- 各プラットフォームの最適時間に自動投稿
- エンゲージメント記録・分析

## 注意事項

### API コスト

- **Claude API**：使用量に応じて課金（月額～数千円想定）
- **X・Meta API**：開発用は無料枠あり
- GitHub Actions での実行：月額無料

### セキュリティ

```bash
# .env ファイルは絶対に Git にコミットしない
echo ".env" >> .gitignore
echo "bridge_data.db" >> .gitignore
echo "*.json" >> .gitignore

# API キーはローカルのみに保管
```

### 利用規約

- 各 SNS プラットフォームの利用規約を確認してから使用
- スクレイピングは各サイトの利用規約に準拠

## トラブルシューティング

### API キーエラー

```bash
# .env ファイルが正しく読み込まれているか確認
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('CLAUDE_API_KEY'))"
```

### データベースエラー

```bash
# bridge_data.db を削除して再作成
rm bridge_data.db
python research_engine.py
```

### 投稿生成の失敗

```bash
# Claude API の配額制限をチェック
# https://console.anthropic.com/account/billing/overview
```

## カスタマイズ

### 投稿トピックの変更

`scheduler.py` の `_get_daily_topic()` 関数で投稿トピックを変更可能

### スタイル分析の調整

`research_engine.py` の `style_keywords` 辞書でキーワードを追加・削除

### 投稿時間のカスタマイズ

`optimal_time_engine.py` で デフォルト時間を調整

## ライセンス

このプロジェクトはプライベート用です。

## サポート

問題が発生した場合は、ログを確認してください：

```bash
tail -f snsposter.log
```

---

**作成日**: 2026-05-14  
**バージョン**: 1.0.0
