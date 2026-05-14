"""
Threads トークン取得（手動コード入力版）
oauth_setup.py のサーバーが使えない環境向け
"""
import requests
import os
import sys

APP_ID = "1497785435190397"
REDIRECT_URI = "https://oauth.pstmn.io/v1/callback"
SCOPE = "threads_basic,threads_content_publish"

import urllib.parse
auth_url = (
    f"https://threads.net/oauth/authorize"
    f"?client_id={APP_ID}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI, safe='')}"
    f"&scope={urllib.parse.quote(SCOPE, safe='')}"
    f"&response_type=code"
)

print("=" * 60)
print("Threads アクセストークン取得（手動版）")
print("=" * 60)
print()
print("【STEP 1】以下のURLをブラウザ（Safari）で開いてください：")
print()
print(auth_url)
print()
print("→ ログイン・許可後、Postman のコールバックページが開き、")
print("  Authorization code が表示されます。")
print("  そのコード（または page の URL 全体）をコピーしてください。")
print("  例: https://oauth.pstmn.io/v1/callback?code=XXXXXXXX")
print()

redirect_url = input("【STEP 2】リダイレクト後のURLを貼り付けてください:\n> ").strip()

parsed = urllib.parse.urlparse(redirect_url)
params = urllib.parse.parse_qs(parsed.query)
code = params.get("code", [None])[0]
if not code:
    # URLではなくcodeだけ貼り付けた場合も対応
    code = redirect_url.strip().split("code=")[-1].split("&")[0].split("#")[0]

if not code or len(code) < 10:
    print("❌ codeが取得できませんでした。URLを正しく貼り付けてください。")
    sys.exit(1)

print(f"\n✅ code取得: {code[:20]}...")

print()
app_secret = input("【STEP 3】App Secret を入力してください\n（Meta開発者ポータル → アプリの設定 → ベーシック）\n> ").strip()

print("\nトークン交換中...")

r = requests.post("https://graph.threads.net/oauth/access_token", data={
    "client_id": APP_ID,
    "client_secret": app_secret,
    "grant_type": "authorization_code",
    "redirect_uri": REDIRECT_URI,
    "code": code
})
data = r.json()

if "access_token" not in data:
    print(f"❌ 失敗: {data}")
    sys.exit(1)

short_token = data["access_token"]
user_id = str(data.get("user_id", ""))
print(f"✅ 短期トークン取得。長期トークンに変換中...")

r2 = requests.get("https://graph.threads.net/access_token", params={
    "grant_type": "th_exchange_token",
    "client_secret": app_secret,
    "access_token": short_token
})
data2 = r2.json()
long_token = data2.get("access_token", short_token)

env_path = os.path.join(os.path.dirname(__file__), ".env")
env_content = f"""META_ACCESS_TOKEN={long_token}
THREADS_USER_ID={user_id}
INSTAGRAM_ACCOUNT_ID=
"""
with open(env_path, "w") as f:
    f.write(env_content)
os.chmod(env_path, 0o600)

print(f"\n✅ .env ファイルを保存しました！")
print(f"   THREADS_USER_ID = {user_id}")
print(f"\n🚀 テスト投稿:")
print(f"   python3 scheduler.py --test-threads")
