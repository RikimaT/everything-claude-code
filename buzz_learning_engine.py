"""
Buzz Learning Engine: Analyze viral posts and extract patterns
"""
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BuzzLearningEngine:
    def __init__(self, db_path: str = "bridge_data.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize buzz analysis tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Buzz posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS buzz_posts (
                id INTEGER PRIMARY KEY,
                platform TEXT,
                post_id TEXT UNIQUE,
                content TEXT,
                engagement_score REAL,
                theme TEXT,
                structure TEXT,
                keywords TEXT,
                hashtags TEXT,
                analyzed_at TEXT
            )
        ''')

        # Buzz patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS buzz_patterns (
                id INTEGER PRIMARY KEY,
                platform TEXT,
                pattern_type TEXT,
                pattern_value TEXT,
                frequency INTEGER,
                avg_engagement REAL,
                updated_at TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def analyze_post_structure(self, content: str) -> Dict:
        """Analyze post structure pattern"""
        patterns = {
            "question_answer": content.count("？") > 0 and len(content) > 100,
            "story_based": any(kw in content for kw in ["話", "経験", "時"]),
            "emotional": any(kw in content for kw in ["思う", "感じる", "大切", "心"]),
            "actionable": any(kw in content for kw in ["できる", "してみる", "試す"]),
            "parent_focused": any(kw in content for kw in ["親", "子ども", "親御さん"]),
            "data_driven": any(kw in content for kw in ["調査", "研究", "データ", "％"])
        }

        # Determine main structure
        main_structure = max(patterns.items(), key=lambda x: x[1])[0] if any(patterns.values()) else "generic"
        return {
            "main_structure": main_structure,
            "patterns": patterns,
            "length": len(content)
        }

    def extract_keywords(self, content: str) -> List[str]:
        """Extract important keywords from post"""
        keywords = []

        # Education-related keywords
        education_keywords = [
            "自学自習", "成長欲", "人間力", "塾", "勉強", "学習",
            "親", "子ども", "成績", "実体験", "伸びしろ",
            "変な塾", "ブリッジ", "彦根", "稲枝"
        ]

        for kw in education_keywords:
            if kw in content:
                keywords.append(kw)

        return keywords

    def extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags"""
        import re
        hashtags = re.findall(r'#\w+', content)
        return hashtags

    def record_buzz_post(self, platform: str, post_id: str, content: str,
                        likes: int = 0, comments: int = 0, shares: int = 0):
        """Record a viral post for analysis"""
        engagement_score = likes + (comments * 2) + (shares * 3)

        structure = self.analyze_post_structure(content)
        keywords = self.extract_keywords(content)
        hashtags = self.extract_hashtags(content)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO buzz_posts
            (platform, post_id, content, engagement_score, theme, structure, keywords, hashtags, analyzed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            platform,
            post_id,
            content[:1000],  # Store first 1000 chars
            engagement_score,
            "education",  # Main theme
            structure["main_structure"],
            json.dumps(keywords),
            json.dumps(hashtags),
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

        # Update buzz patterns
        self._update_buzz_patterns(platform, structure, keywords, engagement_score)

    def _update_buzz_patterns(self, platform: str, structure: Dict, keywords: List[str], engagement: float):
        """Update buzz patterns from analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Record structure pattern
        cursor.execute('''
            INSERT OR REPLACE INTO buzz_patterns
            (platform, pattern_type, pattern_value, frequency, avg_engagement, updated_at)
            VALUES (?, ?, ?,
                    (SELECT COALESCE(frequency, 0) + 1 FROM buzz_patterns
                     WHERE platform = ? AND pattern_type = ? AND pattern_value = ?),
                    (SELECT COALESCE(avg_engagement, 0) FROM buzz_patterns
                     WHERE platform = ? AND pattern_type = ? AND pattern_value = ?),
                    ?)
        ''', (
            platform, "structure", structure["main_structure"],
            platform, "structure", structure["main_structure"],
            platform, "structure", structure["main_structure"],
            datetime.now().isoformat()
        ))

        # Record keyword patterns
        for kw in keywords:
            cursor.execute('''
                INSERT OR REPLACE INTO buzz_patterns
                (platform, pattern_type, pattern_value, frequency, avg_engagement, updated_at)
                VALUES (?, ?, ?,
                        (SELECT COALESCE(frequency, 0) + 1 FROM buzz_patterns
                         WHERE platform = ? AND pattern_type = ? AND pattern_value = ?),
                        ?,
                        ?)
            ''', (
                platform, "keyword", kw,
                platform, "keyword", kw,
                engagement,
                datetime.now().isoformat()
            ))

        conn.commit()
        conn.close()

    def get_buzz_insights(self, platform: str) -> Dict:
        """Get insights from buzz posts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get top structures
        cursor.execute('''
            SELECT pattern_value, AVG(avg_engagement) as avg_eng, COUNT(*) as count
            FROM buzz_patterns
            WHERE platform = ? AND pattern_type = 'structure'
            GROUP BY pattern_value
            ORDER BY avg_eng DESC
        ''', (platform,))

        structures = {row[0]: {"avg_engagement": row[1], "count": row[2]} for row in cursor.fetchall()}

        # Get top keywords
        cursor.execute('''
            SELECT pattern_value, AVG(avg_engagement) as avg_eng, COUNT(*) as count
            FROM buzz_patterns
            WHERE platform = ? AND pattern_type = 'keyword'
            GROUP BY pattern_value
            ORDER BY avg_eng DESC
            LIMIT 10
        ''', (platform,))

        keywords = {row[0]: {"avg_engagement": row[1], "count": row[2]} for row in cursor.fetchall()}

        conn.close()

        return {
            "platform": platform,
            "top_structures": structures,
            "top_keywords": keywords,
            "generated_at": datetime.now().isoformat()
        }

    def export_buzz_insights(self, platform: str):
        """Export buzz insights to JSON"""
        insights = self.get_buzz_insights(platform)

        filename = f"{platform}_buzz_insights.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(insights, f, ensure_ascii=False, indent=2)

        logger.info(f"✓ Buzz insights exported to {filename}")
        return insights


if __name__ == "__main__":
    engine = BuzzLearningEngine()

    print("📊 Buzz Learning Engine")
    print("-" * 50)

    # Example: Record a buzz post
    example_post = """
    「進学塾じゃなくて総合学習教室」って言ってる理由。
    それは、結果よりも「頑張った経験」を大切にしたいから。
    成績が全てじゃない。何かつまずいた時に思い出すのは、
    あの時の必死の頑張り。その実体験こそが人生の糧になるんですよ。
    """

    print("\n📝 Recording example buzz post...")
    engine.record_buzz_post("threads", "ex_001", example_post, likes=45, comments=8, shares=3)

    print("\n📊 Generating insights...")
    for platform in ["x", "threads", "instagram"]:
        insights = engine.get_buzz_insights(platform)
        print(f"\n{platform.upper()}:")
        print(f"  Top Structures: {list(insights['top_structures'].keys())[:3]}")
        print(f"  Top Keywords: {list(insights['top_keywords'].keys())[:5]}")

    print("\n✅ Buzz learning complete!")
