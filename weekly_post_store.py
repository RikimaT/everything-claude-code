"""
Weekly Post Store: 週次投稿ファイルの読み書き管理
Claude Code で生成した投稿をスケジューラーが使用する
"""
import json
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional


POSTS_FILE = "weekly_posts.json"


def load_weekly_posts() -> Dict:
    """週次投稿ファイルを読み込む"""
    if not os.path.exists(POSTS_FILE):
        return {"week_start": None, "posts": []}
    with open(POSTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_weekly_posts(data: Dict):
    """週次投稿ファイルを保存する"""
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_next_post(platform: str) -> Optional[Dict]:
    """指定プラットフォームの次の未使用投稿を取得"""
    data = load_weekly_posts()
    today = date.today().isoformat()

    for post in data.get("posts", []):
        if (post["platform"] == platform
                and not post.get("used", False)
                and post.get("date", "") <= today):
            return post

    return None


def mark_post_used(post_id: int):
    """投稿を使用済みにマーク"""
    data = load_weekly_posts()
    for post in data["posts"]:
        if post["id"] == post_id:
            post["used"] = True
            post["posted_at"] = datetime.now().isoformat()
            break
    save_weekly_posts(data)


def get_remaining_posts() -> Dict[str, int]:
    """残りの未使用投稿数をプラットフォーム別に返す"""
    data = load_weekly_posts()
    remaining = {"threads": 0, "instagram": 0, "x": 0}
    for post in data.get("posts", []):
        if not post.get("used", False):
            platform = post.get("platform", "")
            if platform in remaining:
                remaining[platform] += 1
    return remaining


def create_empty_week_template() -> Dict:
    """空の週次投稿テンプレートを作成"""
    today = date.today()
    posts = []
    post_id = 1

    # Threads: 毎日3回
    for day_offset in range(7):
        day = (today + timedelta(days=day_offset)).isoformat()
        for time_slot in ["09:00", "14:00", "21:00"]:
            posts.append({
                "id": post_id,
                "date": day,
                "platform": "threads",
                "scheduled_time": time_slot,
                "content": "",
                "topic": "",
                "used": False
            })
            post_id += 1

    # Instagram: 週4回（月水金日）
    for day_offset in [0, 2, 4, 6]:
        day = (today + timedelta(days=day_offset)).isoformat()
        posts.append({
            "id": post_id,
            "date": day,
            "platform": "instagram",
            "scheduled_time": "12:00",
            "content": "",
            "topic": "",
            "used": False
        })
        post_id += 1

    return {
        "week_start": today.isoformat(),
        "generated_at": datetime.now().isoformat(),
        "posts": posts
    }


def show_status():
    """投稿の残り状況を表示"""
    remaining = get_remaining_posts()
    print("\n📊 今週の投稿残り状況:")
    for platform, count in remaining.items():
        emoji = "✅" if count > 0 else "⚠️ "
        print(f"  {emoji} {platform}: {count}件")


if __name__ == "__main__":
    show_status()
