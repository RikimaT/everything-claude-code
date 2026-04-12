# X公式MCPサーバー（xmcp）× Claude Code 完全連携ガイド

**目標：** Xの投稿・リサーチ・分析・いいね・リポストをターミナル内で完結させる
**所要時間：** 約10分

---

## ステップ1：X Developer App作成（約3分）

### 1-1. developer.x.com にログイン

Xアカウントで https://developer.x.com にログインし、Developer Portalへ進みます。

### 1-2. 新しいアプリを作成

1. 左メニュー → **Projects & Apps** → **+ Add App**
2. App名を入力（例：`my-claude-xmcp`）
3. Environment は **Development** を選択
4. **Create** をクリック

> ⚠️ **警告：** 次の画面に表示される `API Key` と `API Secret` は**この1回しか表示されません**。必ずメモしてください。

### 1-3. APIキーをメモ

```
API Key:    [ここに自分のAPI Keyを貼り付けて保管]
API Secret: [ここに自分のAPI Secretを貼り付けて保管]
```

### 1-4. User Authentication Settings を設定

1. 作成したアプリの **Settings** タブを開く
2. **User authentication settings** セクション → **Set up**
3. 以下を**正確に**設定：

| 項目 | 設定値 |
|------|--------|
| App permissions | **Read and Write** |
| Type of App | Web App, Automated App or Bot |
| Callback URI / Redirect URL | `http://127.0.0.1:8976/oauth/callback` |
| Website URL | `http://localhost`（任意） |

> ⚠️ **Callback URLは一字一句正確に入力してください。** ポート番号 `8976` を間違えると認証が失敗します。

4. **Save** をクリック

### 1-5. Bearer Token を生成・メモ

1. **Keys and Tokens** タブを開く
2. **Bearer Token** セクション → **Generate**
3. 表示されたトークンをメモ

```
Bearer Token: [ここに自分のBearer Tokenを貼り付けて保管]
```

---

## ステップ2：xmcpサーバーのセットアップ（約5分）

### 2-1. リポジトリをクローン

```bash
git clone https://github.com/xdevplatform/xmcp.git
cd xmcp
```

### 2-2. 環境変数ファイルを作成

```bash
cp env.example .env
```

### 2-3. .env ファイルを編集

`.env` をテキストエディタで開き、以下の値を設定します：

```env
# === 必須設定 ===
X_OAUTH_CONSUMER_KEY=あなたのAPI Key
X_OAUTH_CONSUMER_SECRET=あなたのAPI Secret
X_BEARER_TOKEN=あなたのBearer Token

# === ツールの絞り込み（推奨：必要なものだけ許可）===
X_API_TOOL_ALLOWLIST=searchPostsRecent,createPosts,getUsersMe,likePost,repostPost

# === サーバー設定（変更不要）===
X_OAUTH_CALLBACK_HOST=127.0.0.1
X_OAUTH_CALLBACK_PORT=8976
MCP_PORT=8000
```

> 🔒 **セキュリティ注意：** `.env` ファイルは絶対にGitにコミットしないでください。`.gitignore` に含まれていることを確認してください。

**利用可能な主要ツール一覧：**

| ツール名 | 説明 |
|---------|------|
| `searchPostsRecent` | 最新投稿を検索 |
| `createPosts` | 投稿を作成 |
| `getUsersMe` | 自分のプロフィール取得 |
| `likePost` | いいねする |
| `repostPost` | リポストする |
| `deletePostById` | 投稿を削除 |
| `getUsersIdTimeline` | タイムライン取得 |
| `getMentionsTimeline` | メンション一覧取得 |

### 2-4. Python仮想環境を作成・依存関係をインストール

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2-5. サーバーを起動

```bash
python server.py
```

> 🌐 **初回起動時にブラウザが自動的に開きます。** XへのOAuth認証を「許可」してください。
> ✅ 認証が完了すると `http://127.0.0.1:8000/mcp` でサーバーが起動します。
> ⚠️ **このターミナルは閉じないでください。** Claude Codeを使う間は常に起動しておく必要があります。

---

## ステップ3：Claude Codeに接続（約2分）

### 3-1. 別のターミナルでClaude CodeにxmcpをMCPサーバーとして登録

```bash
claude mcp add xmcp --transport http http://127.0.0.1:8000/mcp
```

> **解説：**
> - `xmcp` — Claude Code内での識別名（任意）
> - `--transport http` — FastMCPのStreamable HTTP形式を指定
> - `http://127.0.0.1:8000/mcp` — ステップ2で起動したサーバーのエンドポイント

### 3-2. 登録確認

```bash
claude mcp list
```

以下のような出力が表示されれば成功です：

```
xmcp: http://127.0.0.1:8000/mcp (http)
```

### 3-3. 手動設定（任意：設定ファイルで管理したい場合）

CLIコマンドの代わりに、`~/.claude/settings.json`（グローバル）または
プロジェクトルートの `.claude/settings.json`（プロジェクト専用）を直接編集することもできます：

```json
{
  "mcpServers": {
    "xmcp": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

> ⚠️ **settings.jsonを編集する場合：** 既存の設定を上書きしないよう `mcpServers` キーのみ追加・編集してください。

---

## ステップ4：動作確認テスト

### 4-1. Claude Codeを起動

```bash
claude
```

### 4-2. MCPツールの確認

Claude Code内で：
```
/mcp
```
`xmcp` が一覧に表示されていればOKです。

### 4-3. テストコマンド（Claude Code内でそのままコピペ）

**自分のプロフィールを取得（最初の動作確認に最適）：**
```
xmcpのgetUsersMeツールを使って私のXプロフィール情報を表示してください
```

**キーワード検索：**
```
xmcpのsearchPostsRecentツールで「Claude Code」に関する最新の投稿を10件検索してください
```

**投稿を作成（テスト用）：**
```
xmcpのcreatePostsツールで「Claude CodeからXに投稿テスト！ #ClaudeCode #MCP」と投稿してください
```

**いいねする：**
```
xmcpのlikePostツールで、ポストID [投稿ID] にいいねしてください
```

---

## トラブルシューティング

### サーバーが起動しない

```bash
# Pythonバージョンを確認（3.9以上が必要）
python --version

# 仮想環境が有効か確認
which python   # .venv/bin/python が表示されるはず

# .envが正しく作成されているか確認
cat .env
```

### OAuth認証でエラーが出る

- Callback URL が `http://127.0.0.1:8976/oauth/callback` と**完全に一致**しているか確認
- App permissions が **Read and Write** になっているか確認
- ブラウザのポップアップブロッカーが「許可」をブロックしていないか確認

### Claude CodeでMCPツールが見つからない

```bash
# xmcpサーバーが起動中か確認
curl http://127.0.0.1:8000/mcp

# Claude Codeに登録されているか確認
claude mcp list

# 削除して再登録
claude mcp remove xmcp
claude mcp add xmcp --transport http http://127.0.0.1:8000/mcp
```

### ポート競合エラー

```bash
# MCP_PORTを変更（.envで設定）
MCP_PORT=8001

# Claude Codeの登録も更新
claude mcp remove xmcp
claude mcp add xmcp --transport http http://127.0.0.1:8001/mcp
```

---

## 毎回の起動手順（2ステップ）

セットアップ完了後、毎回の使用時は以下の2ステップだけです：

```bash
# ターミナル1: xmcpサーバーを起動
cd ~/path/to/xmcp
source .venv/bin/activate
python server.py

# ターミナル2: Claude Codeを起動
claude
```

Claude Codeは自動的にxmcpサーバーに接続します。

---

## 参考リンク

- [xmcp公式リポジトリ](https://github.com/xdevplatform/xmcp)
- [X Developer Portal](https://developer.x.com)
- [FastMCP ドキュメント](https://github.com/jlowin/fastmcp)
