"""
Trending Engine: Fetch and analyze trending topics and news for post ideas
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict
import logging
import feedparser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrendingEngine:
    def __init__(self, db_path: str = "bridge_data.db"):
        self.db_path = db_path
        self.init_db()

        # RSS feeds for education-related news
        self.feeds = {
            "education_news": "https://www.mext.go.jp/rss/", # 文科省
            "parenting": "https://news.google.com/rss/search?q=子育て&hl=ja&gl=JP&ceid=JP%3Aja",
            "shiga_news": "https://news.google.com/rss/search?q=滋賀県&hl=ja&gl=JP&ceid=JP%3Aja",
            "trends": "https://trends.google.com/trends/trendingsearches/daily/rss?geo=JP"
        }

    def init_db(self):
        """Initialize trending news tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trending_topics (
                id INTEGER PRIMARY KEY,
                topic TEXT UNIQUE,
                category TEXT,
                relevance_score REAL,
                articles_count INTEGER,
                last_updated TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trending_articles (
                id INTEGER PRIMARY KEY,
                title TEXT,
                summary TEXT,
                source TEXT,
                url TEXT,
                category TEXT,
                fetched_at TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generated_trending_posts (
                id INTEGER PRIMARY KEY,
                trend_topic TEXT,
                platform TEXT,
                post_content TEXT,
                generated_at TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def fetch_trending_topics(self):
        """Fetch trending topics from RSS feeds"""
        topics = {
            "education": [],
            "parenting": [],
            "regional": [],
            "general_trends": []
        }

        # Fetch from each feed
        for feed_name, feed_url in self.feeds.items():
            try:
                feed = feedparser.parse(feed_url)

                category = self._categorize_feed(feed_name)

                for entry in feed.entries[:10]:  # Get top 10 entries
                    title = entry.get("title", "")
                    summary = entry.get("summary", "")[:500]

                    topics[category].append({
                        "title": title,
                        "summary": summary,
                        "source": feed_name
                    })

                logger.info(f"✓ Fetched from {feed_name}: {len(feed.entries)} items")

            except Exception as e:
                logger.warning(f"⚠ Failed to fetch {feed_name}: {e}")

        self._save_trending_articles(topics)
        return topics

    def _categorize_feed(self, feed_name: str) -> str:
        """Categorize feed by name"""
        categorization = {
            "education_news": "education",
            "parenting": "parenting",
            "shiga_news": "regional",
            "trends": "general_trends"
        }
        return categorization.get(feed_name, "general_trends")

    def _save_trending_articles(self, topics: Dict[str, List]):
        """Save trending articles to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for category, articles in topics.items():
            for article in articles:
                cursor.execute('''
                    INSERT OR IGNORE INTO trending_articles
                    (title, summary, source, category, fetched_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    article["title"],
                    article["summary"],
                    article["source"],
                    category,
                    datetime.now().isoformat()
                ))

        conn.commit()
        conn.close()

    def analyze_trending_for_post(self, platform: str = "all") -> List[Dict]:
        """Analyze trending topics and generate post ideas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get recent articles
        cursor.execute('''
            SELECT title, summary, category FROM trending_articles
            WHERE fetched_at > datetime('now', '-1 day')
            ORDER BY fetched_at DESC
            LIMIT 20
        ''')

        articles = cursor.fetchall()
        conn.close()

        # Convert to usable format
        trending_ideas = []

        for title, summary, category in articles:
            idea = {
                "title": title,
                "summary": summary,
                "category": category,
                "post_angles": self._generate_post_angles(title, summary, category)
            }
            trending_ideas.append(idea)

        return trending_ideas

    def _generate_post_angles(self, title: str, summary: str, category: str) -> List[str]:
        """Generate multiple post angles for a trending topic"""
        angles = []

        # Parent-focused angle
        if category in ["education", "parenting", "general_trends"]:
            angles.append(f"親向け: '{title}' について、親の視点での考え方")

        # Educational angle
        if category in ["education", "regional"]:
            angles.append(f"教育視点: '{title}' が子どもの成長に与える影響")

        # Local angle
        if category == "regional":
            angles.append(f"地域密着: 彦根・滋賀での '{title}' の現状")

        # Conversational angle
        angles.append(f"日記的: '{title}' から感じたこと・思ったこと")

        return angles

    def get_today_trending(self) -> Dict:
        """Get trending topics for today"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT DISTINCT title, category, COUNT(*) as frequency
            FROM trending_articles
            WHERE fetched_at > datetime('now', '-24 hours')
            GROUP BY title
            ORDER BY frequency DESC
            LIMIT 10
        ''')

        trending = {
            "fetched_at": datetime.now().isoformat(),
            "topics": []
        }

        for title, category, frequency in cursor.fetchall():
            trending["topics"].append({
                "title": title,
                "category": category,
                "frequency": frequency
            })

        conn.close()
        return trending

    def record_generated_trending_post(self, topic: str, platform: str, content: str):
        """Record a generated post based on trending topic"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO generated_trending_posts
            (trend_topic, platform, post_content, generated_at)
            VALUES (?, ?, ?, ?)
        ''', (
            topic,
            platform,
            content[:1000],
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

    def export_trending_ideas(self, output_file: str = "trending_ideas.json"):
        """Export trending ideas for post generation"""
        ideas = self.analyze_trending_for_post()

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(ideas, f, ensure_ascii=False, indent=2)

        logger.info(f"✓ Trending ideas exported to {output_file}")
        return ideas


# Local news sources (optional, no RSS needed)
class LocalNewsCollector:
    """Collect local news without RSS (manual or from specific sites)"""

    @staticmethod
    def get_seasonal_topics() -> List[str]:
        """Get topics based on current season/date"""
        from datetime import datetime

        month = datetime.now().month

        seasonal = {
            1: ["新年の目標", "受験シーズン", "冬休みの過ごし方"],
            2: ["受験本番", "学年末テスト", "春への準備"],
            3: ["新学年準備", "春休み", "進学"],
            4: ["新学期スタート", "新しい環境", "適応"],
            5: ["GW", "中間テスト", "親子時間"],
            6: ["梅雨", "テスト対策", "夏休み準備"],
            7: ["夏休み", "学習計画", "地域イベント"],
            8: ["夏休み後半", "宿題", "開発休暇"],
            9: ["新学期", "秋祭り", "文化祭"],
            10: ["運動会", "秋の行楽", "ハロウィン"],
            11: ["文化祭", "感謝祭", "受験勉強"],
            12: ["冬休み", "クリスマス", "年末"]
        }

        return seasonal.get(month, ["日常の学び", "親子時間"])

    @staticmethod
    def get_event_topics() -> List[str]:
        """Get topics from upcoming events"""
        return [
            "彦根城まつり",
            "滋賀県教育委員会のニュース",
            "全国学力テスト",
            "大学入試改革",
            "オリンピック関連教育"
        ]


if __name__ == "__main__":
    engine = TrendingEngine()

    print("📈 Trending Engine")
    print("-" * 50)

    print("\n📰 Fetching trending topics...")
    topics = engine.fetch_trending_topics()

    print("\n📊 Today's trending:")
    today_trending = engine.get_today_trending()
    for topic in today_trending["topics"][:5]:
        print(f"  - {topic['title']} ({topic['category']})")

    print("\n💡 Post angle ideas:")
    ideas = engine.analyze_trending_for_post()
    for idea in ideas[:3]:
        print(f"\n  Topic: {idea['title']}")
        for angle in idea["post_angles"][:2]:
            print(f"    → {angle}")

    print("\n📅 Seasonal topics:")
    for topic in LocalNewsCollector.get_seasonal_topics():
        print(f"  - {topic}")

    print("\n✅ Trending analysis complete!")
