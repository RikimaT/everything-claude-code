"""
Threads OAuth セットアップ - これを実行してブラウザでURLを開くだけで完了
"""
import http.server
import urllib.parse
import threading
import webbrowser
import requests
import os

APP_ID = "1497785435190397"
REDIRECT_URI = "http://localhost:8080"
SCOPE = "threads_basic,threads_content_publish"

print("=" * 50)
print("Threads アクセストークン 自動取得ツール")
print("=" * 50)

app_secret = input("\nThreadsのapp secret を入力してください\n（Meta開発者ポータル → アプリの設定 → ベーシック → Threadsのapp secret → 表示）\n> ").strip()

token_result = {}

class OAuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        if "code" in params:
            code = params["code"][0]
            print(f"\n✅ 認証コード取得成功！トークンを交換中...")

            try:
                r = requests.post("https://graph.threads.net/oauth/access_token", data={
                    "client_id": APP_ID,
                    "client_secret": app_secret,
                    "grant_type": "authorization_code",
                    "redirect_uri": REDIRECT_URI,
                    "code": code
                })
                data = r.json()

                if "access_token" in data:
                    short_token = data["access_token"]
                    user_id = data.get("user_id", "")

                    # 長期トークンに交換
                    r2 = requests.get("https://graph.threads.net/access_token", params={
                        "grant_type": "th_exchange_token",
                        "client_secret": app_secret,
                        "access_token": short_token
                    })
                    data2 = r2.json()
                    long_token = data2.get("access_token", short_token)

                    token_result["token"] = long_token
                    token_result["user_id"] = str(user_id)

                    self.wfile.write(b"<h1>\xe2\x9c\x85 \xe6\x88\x90\xe5\x8a\x9f\xef\xbc\x81\xe3\x81\x93\xe3\x81\xae\xe3\x82\xbf\xe3\x83\x96\xe3\x82\x92\xe9\x96\x89\xe3\x81\x98\xe3\x81\xa6\xe3\x81\x8f\xe3\x81\xa0\xe3\x81\x95\xe3\x81\x84</h1>")
                else:
                    print(f"❌ トークン取得失敗: {data}")
                    self.wfile.write(b"<h1>\xe2\x9d\x8c \xe5\xa4\xb1\xe6\x95\x97</h1>")
            except Exception as e:
                print(f"❌ エラー: {e}")
                self.wfile.write(b"<h1>\xe2\x9d\x8c \xe3\x82\xa8\xe3\x83\xa9\xe3\x83\xbc</h1>")
        else:
            self.wfile.write(b"<h1>\xe2\x9d\x8c \xe3\x82\xb3\xe3\x83\xbc\xe3\x83\x89\xe3\x81\x8c\xe3\x81\x82\xe3\x82\x8a\xe3\x81\xbe\xe3\x81\x9b\xe3\x82\x93</h1>")

        threading.Thread(target=server.shutdown, daemon=True).start()

    def log_message(self, format, *args):
        pass

server = http.server.HTTPServer(("localhost", 8080), OAuthHandler)

auth_url = (
    f"https://threads.net/oauth/authorize"
    f"?client_id={APP_ID}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&scope={SCOPE}"
    f"&response_type=code"
)

print(f"\n📋 以下のURLをブラウザで開いてください：")
print(f"\n{auth_url}\n")
print("待機中...")

server.serve_forever()

if token_result.get("token"):
    token = token_result["token"]
    user_id = token_result["user_id"]

    env_path = os.path.join(os.path.dirname(__file__), ".env")
    env_content = f"""META_ACCESS_TOKEN={token}
THREADS_USER_ID={user_id}
INSTAGRAM_ACCOUNT_ID=
"""
    with open(env_path, "w") as f:
        f.write(env_content)
    os.chmod(env_path, 0o600)

    print(f"\n✅ .env ファイルを保存しました！")
    print(f"   THREADS_USER_ID = {user_id}")
    print(f"\n🚀 次のコマンドでテスト投稿してください：")
    print(f"   python3 scheduler.py --test-threads")
else:
    print("\n❌ トークン取得に失敗しました。もう一度試してください。")
