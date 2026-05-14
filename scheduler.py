"""
SNS Scheduler: Schedule and publish posts to X, Threads, Instagram
weekly_posts.json から投稿を読み込み、指定時間に自動配信する
"""
import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

from weekly_post_store import get_next_post, mark_post_used, get_remaining_posts
from trending_engine import TrendingEngine, LocalNewsCollector

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("snsposter.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MetaAPIPublisher:
    """Meta API (Threads・Instagram) への投稿"""

    def __init__(self):
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.instagram_account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
        self.threads_user_id = os.getenv("THREADS_USER_ID")

        # THREADS_USER_ID が未設定の場合、トークンから自動取得して保存
        if self.access_token and not self.threads_user_id:
            self.threads_user_id = self._fetch_and_save_user_id()

    def _fetch_and_save_user_id(self) -> Optional[str]:
        """トークンからThreadsユーザーIDを自動取得して.envに保存"""
        try:
            r = requests.get(
                "https://graph.threads.net/v1.0/me",
                params={"fields": "id,username", "access_token": self.access_token},
                timeout=10
            )
            data = r.json()
            if "id" in data:
                user_id = data["id"]
                username = data.get("username", "")
                logger.info(f"✅ ThreadsユーザーID自動取得: {user_id} (@{username})")

                # .envに追記
                env_path = os.path.join(os.path.dirname(__file__), ".env")
                lines = []
                if os.path.exists(env_path):
                    with open(env_path, "r") as f:
                        lines = f.readlines()

                updated = False
                for i, line in enumerate(lines):
                    if line.startswith("THREADS_USER_ID="):
                        lines[i] = f"THREADS_USER_ID={user_id}\n"
                        updated = True
                        break
                if not updated:
                    lines.append(f"THREADS_USER_ID={user_id}\n")

                with open(env_path, "w") as f:
                    f.writelines(lines)

                return user_id
            else:
                logger.error(f"❌ ユーザーID取得失敗: {data}")
                return None
        except Exception as e:
            logger.error(f"❌ ユーザーID取得エラー: {e}")
            return None

    def publish_to_threads(self, content: str) -> bool:
        """Threads に投稿する"""
        if not self.access_token or not self.threads_user_id:
            logger.warning("⚠️  Threads API 未設定 - コンソールに出力します")
            logger.info(f"[Threads 投稿内容]\n{content}\n")
            return False

        try:
            # Step 1: メディアコンテナを作成
            create_url = f"https://graph.threads.net/v1.0/{self.threads_user_id}/threads"
            create_res = requests.post(create_url, data={
                "media_type": "TEXT",
                "text": content,
                "access_token": self.access_token
            })
            create_res.raise_for_status()
            container_id = create_res.json().get("id")

            # Step 2: 投稿を公開
            time.sleep(5)  # Threads API の推奨待機
            publish_url = f"https://graph.threads.net/v1.0/{self.threads_user_id}/threads_publish"
            publish_res = requests.post(publish_url, data={
                "creation_id": container_id,
                "access_token": self.access_token
            })
            publish_res.raise_for_status()

            logger.info(f"✅ Threads 投稿完了: {content[:40]}...")
            return True

        except Exception as e:
            logger.error(f"❌ Threads 投稿失敗: {e}")
            return False

    def publish_to_instagram(self, content: str) -> bool:
        """Instagram に投稿する（テキストのみ：キャプション付き画像は別途対応）"""
        if not self.access_token or not self.instagram_account_id:
            logger.warning("⚠️  Instagram API 未設定 - コンソールに出力します")
            logger.info(f"[Instagram 投稿内容]\n{content}\n")
            return False

        try:
            # Instagram はテキストのみ投稿不可なので、ここではログのみ
            # 実際の画像投稿は別途 image_url パラメータが必要
            logger.info(f"[Instagram] 投稿準備: {content[:40]}...")
            logger.info("ℹ️  Instagram は画像必須のため、手動投稿してください")
            return True

        except Exception as e:
            logger.error(f"❌ Instagram 投稿失敗: {e}")
            return False


class SNSScheduler:
    def __init__(self):
        self.scheduler = BlockingScheduler(timezone="Asia/Tokyo")
        self.publisher = MetaAPIPublisher()
        self.trending_engine = TrendingEngine()
        self._today_trends: list = []

    def _refresh_trends(self):
        """毎朝6時にトレンドを取得して当日の投稿に反映させるためキャッシュする"""
        try:
            self.trending_engine.fetch_trending_topics()
            ideas = self.trending_engine.analyze_trending_for_post()
            # 今月の季節ネタも追加
            seasonal = LocalNewsCollector.get_seasonal_topics()
            self._today_trends = [idea["title"] for idea in ideas[:3]] + seasonal[:2]
            logger.info(f"📰 本日のトレンド更新: {self._today_trends[:3]}")
        except Exception as e:
            logger.warning(f"⚠️  トレンド取得失敗（投稿は続行）: {e}")
            self._today_trends = LocalNewsCollector.get_seasonal_topics()[:3]

    def _inject_trend(self, content: str) -> str:
        """投稿内容にその日のトレンドを自然に追記する"""
        if not self._today_trends:
            return content

        trend = self._today_trends[0]

        # 投稿末尾がハッシュタグなら手前に追記、そうでなければ末尾に
        lines = content.strip().split("\n")
        hashtag_start = next(
            (i for i, l in enumerate(lines) if l.strip().startswith("#")), None
        )

        trend_note = f"\n\n（今日は「{trend}」について考えながら書きました）"

        if hashtag_start is not None:
            lines.insert(hashtag_start, trend_note.strip())
            return "\n".join(lines)
        else:
            return content + trend_note

    def _post_threads(self):
        """Threads への定時投稿（当日のトレンドを反映）"""
        post = get_next_post("threads")
        if not post:
            logger.warning("⚠️  Threads: 投稿ストックなし")
            remaining = get_remaining_posts()
            logger.info(f"残り投稿数: {remaining}")
            return

        # その日のトレンドを投稿に自然に織り込む
        content = self._inject_trend(post["content"])

        logger.info(f"📤 Threads 投稿開始: {post['topic']}")
        success = self.publisher.publish_to_threads(content)

        if success:
            mark_post_used(post["id"])
            logger.info(f"✅ 完了 (ID: {post['id']})")

    def _post_instagram(self):
        """Instagram への定時投稿（当日のトレンドを反映）"""
        post = get_next_post("instagram")
        if not post:
            logger.warning("⚠️  Instagram: 投稿ストックなし")
            return

        content = self._inject_trend(post["content"])

        logger.info(f"📤 Instagram 投稿開始: {post['topic']}")
        success = self.publisher.publish_to_instagram(content)

        if success:
            mark_post_used(post["id"])
            logger.info(f"✅ 完了 (ID: {post['id']})")

    def _check_stock(self):
        """毎朝6時: トレンド更新 + 投稿ストック確認"""
        # トレンドを先に更新（当日の9時投稿から反映される）
        self._refresh_trends()

        remaining = get_remaining_posts()
        total = sum(remaining.values())
        logger.info(f"📊 投稿ストック確認: {remaining}")

        if total < 7:
            logger.warning(
                "⚠️  投稿が残り少なくなっています！"
                " Claude Code で「今週の投稿を生成して」と伝えてください。"
            )

    def setup_jobs(self):
        """投稿ジョブのスケジュール設定"""

        # Threads: 毎日 9:00 / 14:00 / 21:00
        self.scheduler.add_job(
            self._post_threads, CronTrigger(hour=9, minute=0, timezone="Asia/Tokyo"),
            id="threads_morning", replace_existing=True
        )
        self.scheduler.add_job(
            self._post_threads, CronTrigger(hour=14, minute=0, timezone="Asia/Tokyo"),
            id="threads_noon", replace_existing=True
        )
        self.scheduler.add_job(
            self._post_threads, CronTrigger(hour=21, minute=0, timezone="Asia/Tokyo"),
            id="threads_night", replace_existing=True
        )

        # Instagram: 月・水・金・日 12:00
        self.scheduler.add_job(
            self._post_instagram,
            CronTrigger(day_of_week="mon,wed,fri,sun", hour=12, minute=0, timezone="Asia/Tokyo"),
            id="instagram_post", replace_existing=True
        )

        # 毎朝 6:00 にストック確認
        self.scheduler.add_job(
            self._check_stock, CronTrigger(hour=6, minute=0, timezone="Asia/Tokyo"),
            id="stock_check", replace_existing=True
        )

        logger.info("✅ スケジュール設定完了")
        logger.info("  Threads:   毎日 9:00 / 14:00 / 21:00")
        logger.info("  Instagram: 月・水・金・日 12:00")
        logger.info("  ストック確認: 毎朝 6:00")

    def start(self):
        """スケジューラーを起動（ブロッキング）"""
        self.setup_jobs()
        # 起動時にもトレンドを取得しておく
        self._refresh_trends()
        remaining = get_remaining_posts()
        logger.info(f"📦 現在の投稿ストック: {remaining}")

        logger.info("🚀 スケジューラー起動！ Ctrl+C で停止")
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("⏹️  スケジューラー停止")

    def run_once_now(self, platform: str):
        """テスト用: 今すぐ1投稿する"""
        logger.info(f"🧪 テスト投稿: {platform}")
        if platform == "threads":
            self._post_threads()
        elif platform == "instagram":
            self._post_instagram()


if __name__ == "__main__":
    import sys

    scheduler = SNSScheduler()

    if "--test-threads" in sys.argv:
        # テスト: Threads に今すぐ1投稿
        scheduler.run_once_now("threads")
    elif "--test-instagram" in sys.argv:
        # テスト: Instagram に今すぐ1投稿
        scheduler.run_once_now("instagram")
    elif "--status" in sys.argv:
        # 残り投稿数を確認
        remaining = get_remaining_posts()
        print("\n📊 投稿ストック状況:")
        for platform, count in remaining.items():
            emoji = "✅" if count > 0 else "⚠️ "
            print(f"  {emoji} {platform}: {count}件")
    else:
        # 通常起動
        scheduler.start()
