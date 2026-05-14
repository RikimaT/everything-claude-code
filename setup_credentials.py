"""
認証情報セットアップスクリプト
実行: python3 setup_credentials.py
"""
import requests
import json

TOKEN = "THAAVSOljQdH1BYmI0MUtEOEIyWXlFeW1oeXlRZAmtvNmJOX2hQWU9OZAmNBV21Qc0x1ZA2dEQU5QZAXlWbEEyYTNPSDl5YWF1RFQ2UFA5a3MtLUdHNVNuSFVQZAElaWjFpMUNmaUs1SE5XZA1VvWW1LY3ZAmN0NaQkpxc0RjSm1lY2lFNExrRldzcmpTeTNoVURsQzQZD"

print("🔍 Threadsユーザー情報を取得中...")

try:
    r = requests.get(
        "https://graph.threads.net/v1.0/me",
        params={"fields": "id,username", "access_token": TOKEN},
        timeout=10
    )
    data = r.json()

    if "error" in data:
        print(f"❌ エラー: {data['error']['message']}")
        print("トークンが無効です。Meta開発者ポータルで新しいトークンを生成してください。")
        exit(1)

    user_id = data["id"]
    username = data.get("username", "")
    print(f"✅ ユーザーID取得: {user_id} (@{username})")

    env_content = f"""META_ACCESS_TOKEN={TOKEN}
THREADS_USER_ID={user_id}
INSTAGRAM_ACCOUNT_ID=
"""

    with open(".env", "w") as f:
        f.write(env_content)

    import os
    os.chmod(".env", 0o600)

    print("\n✅ .envファイルを作成しました！")
    print(f"  THREADS_USER_ID = {user_id}")
    print("\n次のコマンドでテスト投稿できます:")
    print("  python3 scheduler.py --test-threads")

except requests.exceptions.ConnectionError:
    print("❌ ネットワーク接続エラー")
except Exception as e:
    print(f"❌ エラー: {e}")
