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

    def _post_threads(self):
        """Threads への定時投稿"""
        post = get_next_post("threads")
        if not post:
            logger.warning("⚠️  Threads: 投稿ストックなし")
            remaining = get_remaining_posts()
            logger.info(f"残り投稿数: {remaining}")
            return

        logger.info(f"📤 Threads 投稿開始: {post['topic']}")
        success = self.publisher.publish_to_threads(post["content"])

        if success:
            mark_post_used(post["id"])
            logger.info(f"✅ 完了 (ID: {post['id']})")

    def _post_instagram(self):
        """Instagram への定時投稿"""
        post = get_next_post("instagram")
        if not post:
            logger.warning("⚠️  Instagram: 投稿ストックなし")
            return

        logger.info(f"📤 Instagram 投稿開始: {post['topic']}")
        success = self.publisher.publish_to_instagram(post["content"])

        if success:
            mark_post_used(post["id"])
            logger.info(f"✅ 完了 (ID: {post['id']})")

    def _check_stock(self):
        """毎朝6時に投稿ストックを確認・アラート"""
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
