"""
SNS Scheduler: Schedule and publish posts to X, Threads, Instagram
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

from research_engine import ResearchEngine
from post_generation_engine import PostGenerationEngine
from optimal_time_engine import OptimalTimeEngine
from buzz_learning_engine import BuzzLearningEngine
from trending_engine import TrendingEngine, LocalNewsCollector

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SNSScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.research_engine = ResearchEngine()
        self.post_gen = PostGenerationEngine()
        self.time_engine = OptimalTimeEngine()
        self.buzz_engine = BuzzLearningEngine()
        self.trending_engine = TrendingEngine()
        self.scheduled_posts = {}

    def schedule_daily_post(self, topic: str = None):
        """Schedule daily post for all platforms"""
        if topic is None:
            topic = self._get_daily_topic()

        logger.info(f"📝 Scheduling daily post for topic: {topic}")

        # Generate posts for all platforms
        posts = self.post_gen.generate_post(topic, platform="all")

        # Calculate optimal times for each platform
        for platform in ["x", "threads", "instagram"]:
            next_time = self.time_engine.calculate_next_optimal_time(platform)

            # Schedule the post
            job_id = f"{platform}_{next_time.isoformat()}"
            self.scheduler.add_job(
                func=self._publish_post,
                trigger="date",
                run_date=next_time,
                args=[platform, posts.get(platform, ""), topic],
                id=job_id,
                replace_existing=True
            )

            logger.info(f"✓ Scheduled {platform} post for {next_time.strftime('%Y-%m-%d %H:%M')}")

    def _get_daily_topic(self) -> str:
        """Get daily topic from trending, seasonal, or predefined list"""
        import random

        # Try to get trending topics
        try:
            trending_ideas = self.trending_engine.analyze_trending_for_post()
            if trending_ideas:
                # Use a trending topic with post angles
                idea = trending_ideas[0]
                if idea.get("post_angles"):
                    return idea["post_angles"][0]
        except Exception as e:
            logger.warning(f"⚠️  Could not fetch trending: {e}")

        # Try seasonal topics
        try:
            seasonal = LocalNewsCollector.get_seasonal_topics()
            if seasonal:
                selected = random.choice(seasonal)
                return f"今月のテーマ「{selected}」について、親ができることは？"
        except Exception as e:
            logger.warning(f"⚠️  Could not get seasonal topics: {e}")

        # Fall back to predefined topics
        topics = [
            "子どもが勉強に向き合う時、親ができることは？",
            "自学自習のスイッチを入れるには",
            "成績と成長欲の関係",
            "親の言葉が子どもに与える影響",
            "失敗から学ぶことの大切さ",
            "子どもの伸びしろはどこに？",
            "固定の授業ではなく、個別の成長に焦点を",
            "親のメンタル、塾の選び方",
        ]

        return random.choice(topics)

    def _publish_post(self, platform: str, content: str, topic: str):
        """Publish post to platform"""
        logger.info(f"🚀 Publishing to {platform.upper()}: {content[:50]}...")

        try:
            if platform == "x":
                self._publish_to_x(content)
            elif platform == "threads":
                self._publish_to_threads(content)
            elif platform == "instagram":
                self._publish_to_instagram(content)

            # Record posting
            self._record_post(platform, content, topic)

            logger.info(f"✓ Successfully published to {platform}")

        except Exception as e:
            logger.error(f"✗ Failed to publish to {platform}: {e}")

    def _publish_to_x(self, content: str):
        """Publish to X (Twitter)"""
        # This would use tweepy or X API
        logger.info(f"[X] {content[:100]}...")

    def _publish_to_threads(self, content: str):
        """Publish to Threads"""
        # This would use Meta API for Threads
        logger.info(f"[Threads] {content[:100]}...")

    def _publish_to_instagram(self, content: str):
        """Publish to Instagram"""
        # This would use Meta API for Instagram
        logger.info(f"[Instagram] {content[:100]}...")

    def _record_post(self, platform: str, content: str, topic: str):
        """Record published post"""
        if not os.path.exists("published_posts.json"):
            published = []
        else:
            with open("published_posts.json", "r", encoding="utf-8") as f:
                published = json.load(f)

        published.append({
            "platform": platform,
            "topic": topic,
            "content": content[:500],
            "published_at": datetime.now().isoformat()
        })

        with open("published_posts.json", "w", encoding="utf-8") as f:
            json.dump(published, f, ensure_ascii=False, indent=2)

    def start(self):
        """Start scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✓ Scheduler started")

            # Schedule daily post at 6 AM
            self.scheduler.add_job(
                func=self.schedule_daily_post,
                trigger="cron",
                hour=6,
                minute=0,
                id="daily_schedule",
                replace_existing=True
            )

            logger.info("✓ Daily scheduler job added (6:00 AM)")

    def stop(self):
        """Stop scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("✓ Scheduler stopped")

    def manual_post(self, topic: str):
        """Manually trigger post for testing"""
        logger.info(f"🧪 Manual post test for topic: {topic}")
        self.schedule_daily_post(topic)

    def get_scheduled_jobs(self) -> List[Dict]:
        """Get list of scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        return jobs


if __name__ == "__main__":
    scheduler = SNSScheduler()

    print("🚀 SNS Scheduler")
    print("-" * 50)

    # Manual test post
    print("\n🧪 Testing post generation...")
    scheduler.manual_post("子どもの成長と親の関わり方")

    print("\n📅 Scheduled jobs:")
    for job in scheduler.get_scheduled_jobs():
        print(f"  - {job['id']}: {job.get('next_run', 'N/A')}")

    print("\n✅ Scheduler ready!")
