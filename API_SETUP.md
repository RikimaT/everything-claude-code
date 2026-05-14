# API キー取得・設定ガイド

月末集客に間に合わせるため、以下の手順を **今日中に** 完了してください。

---

## 📋 取得が必要な API

| API | 優先度 | 所要時間 | 月額費用 |
|-----|-------|--------|--------|
| **X（Twitter）** | ⭐⭐⭐ | 10分 | 無料（開発用） |
| **Meta（Threads・Instagram）** | ⭐⭐⭐ | 15分 | 無料（開発用） |
| **Claude API** | ⭐⭐⭐ | 5分 | 利用額による（推定月￥1,000-5,000） |

---

## 🔴 【最優先】X API キー取得（10分）

### Step 1: X Developer Portal にログイン

1. https://developer.x.com にアクセス
2. X（Twitter）アカウントでログイン
3. 「Developer Portal」をクリック

### Step 2: アプリを作成

1. 左メニュー → **「Projects & Apps」** → **「+ Add App」**
2. App 名を入力：`bridge-sns-poster`
3. Environment: **「Development」** を選択
4. **「Create」** をクリック

⚠️ **重要：次の画面に表示される API Key と API Secret は 2 度と表示されません。すぐにメモしてください。**

### Step 3: APIキーをメモ

表示された以下をテキストエディタにコピー：

```
API Key:       ________________________
API Secret:    ________________________
Bearer Token:  ________________________（後で生成）
```

### Step 4: User Authentication を設定

1. 作成したアプリの **「Settings」** タブを開く
2. **「User authentication settings」** → **「Set up」**
3. 以下を設定（**一字一句正確に**）：

| 項目 | 設定値 |
|------|--------|
| App permissions | **Read and Write** ✓ |
| Type of App | **Web App, Automated App or Bot** |
| Callback URI / Redirect URL | `http://127.0.0.1:8976/oauth/callback` |
| Website URL | `http://localhost` |

⚠️ **Callback URI のポート番号 `8976` を間違えないでください！**

4. **「Save」** をクリック

### Step 5: Bearer Token を生成

1. **「Keys and Tokens」** タブを開く
2. **「Bearer Token」** セクション → **「Regenerate」**
3. 表示されたトークンをコピー

```
Bearer Token: ________________________
```

---

## 🟦 Meta API キー取得（Threads・Instagram 共通、15分）

### Step 1: Meta Developers にログイン

1. https://developers.meta.com にアクセス
2. Facebook アカウントでログイン

### Step 2: Business App を作成

1. **「My Apps」** → **「Create App」**
2. App Type: **「Business」** を選択
3. 以下を入力：
   - App Name: `bridge-sns-scheduler`
   - App Purpose: メール確認後に選択

4. **「Create App」** をクリック

### Step 3: Threads と Instagram を追加

1. アプリダッシュボードで **「Add Product」**
2. 以下のプロダクトを追加：
   - **Threads**
   - **Instagram**

### Step 4: Access Token を生成

1. **「Settings」** → **「Users and Permissions」**
2. **「Generate Access Token」**
3. 以下を許可：
   - `instagram_business_management`
   - `threads_manage`

表示されたトークンをコピー：

```
Meta Access Token: ________________________
```

### Step 5: Business ID と Instagram Account ID を確認

1. **「Settings」** → **「Basic」**
2. **App ID** をコピー（Business ID と同じ場合あり）
3. Instagram Business Account を リンク
   - 既存の `bridge_inae` Instagram アカウントをリンク
4. **Instagram Account ID** をコピー

```
Meta Business ID:     ________________________
Instagram Account ID: ________________________
```

---

## 🟪 Claude API キー取得（5分）

### Step 1: Anthropic Console にログイン

1. https://console.anthropic.com にアクセス
2. 「Create account」または「Sign in」

### Step 2: API キーを生成

1. 左メニュー → **「API keys」**
2. **「Create Key」** をクリック
3. Key name: `bridge-sns-poster`
4. 生成されたキーをコピー

```
Claude API Key: ________________________
```

### Step 3: 配額を確認（重要）

1. **「Billing」** → **「Overview」**
2. 現在の配額を確認
3. 必要に応じて月間 API 予算を設定（推奨：$20/月程度）

---

## 🔧 .env ファイルに設定

### Step 1: .env ファイルを作成

```bash
cp .env.example .env
```

### Step 2: .env を編集

取得したキーを以下に記入：

```bash
# .env

# X API
X_OAUTH_CONSUMER_KEY=【X API Key】
X_OAUTH_CONSUMER_SECRET=【X API Secret】
X_BEARER_TOKEN=【X Bearer Token】

# Meta API
META_ACCESS_TOKEN=【Meta Access Token】
META_BUSINESS_ID=【Meta Business ID】
INSTAGRAM_ACCOUNT_ID=【Instagram Account ID】

# Claude API
CLAUDE_API_KEY=【Claude API Key】
```

### Step 3: ファイルの権限を設定

```bash
chmod 600 .env
```

### Step 4: Git にコミットされていないか確認

```bash
# .env が .gitignore に含まれていることを確認
cat .gitignore | grep ".env"

# Git のステージングから外す（万一の場合）
git rm --cached .env 2>/dev/null || true
```

---

## ✅ 動作確認

### テスト 1: 環境変数の読み込み確認

```bash
python -c "
from dotenv import load_dotenv
import os
load_dotenv()

keys = ['X_OAUTH_CONSUMER_KEY', 'META_ACCESS_TOKEN', 'CLAUDE_API_KEY']
for key in keys:
    value = os.getenv(key)
    status = '✓' if value else '✗'
    print(f'{status} {key}: {value[:20]}...' if value else f'{status} {key}: NOT SET')
"
```

期待される出力：
```
✓ X_OAUTH_CONSUMER_KEY: abc...
✓ META_ACCESS_TOKEN: xyz...
✓ CLAUDE_API_KEY: sk-...
```

### テスト 2: Claude API の動作確認

```bash
python -c "
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

response = client.messages.create(
    model='claude-opus-4-7',
    max_tokens=100,
    messages=[
        {'role': 'user', 'content': '「総合学習塾ブリッジ」について1行で説明してください'}
    ]
)

print('✓ Claude API is working!')
print(response.content[0].text)
"
```

---

## 🚨 FAQ・トラブルシューティング

### Q: X API で 「Callback URL が無効」というエラーが出た

**A:** Callback URI が **完全に一致** していることを確認してください：
```
http://127.0.0.1:8976/oauth/callback
```

数字や文字を1つ間違えても失敗します。

### Q: Meta Business ID が見つからない

**A:** Facebook Business Manager から確認できます：
1. https://business.facebook.com
2. 左下の **「⚙️ Settings」** → **「Business Settings」**
3. **「Business Information」** に記載されています

### Q: Claude API の配額制限に達した

**A:** 以下で対策できます：
1. **「Billing」** → **「Limits」** で月間上限を設定
2. 実装中は `claude-3-5-haiku-20241022`（安価版）で開発
3. 本番運用時は `claude-opus-4-7` に変更

### Q: .env ファイルが見つからない

**A:** 作成してください：
```bash
cp .env.example .env
nano .env  # または任意のエディタで編集
```

---

## 📅 次のステップ

API キーをすべて設定できたら：

```bash
# 1. 環境変数確認
python API_SETUP.md の テスト 1 を実行

# 2. リサーチエンジンを実行
python research_engine.py

# 3. 投稿生成をテスト
python post_generation_engine.py

# 4. スケジューラーを起動
python scheduler.py
```

---

**設定完了までの目安時間：30分**  
**月末集客に間に合わせるため、本日中に完了してください！**
