"""
Research Engine: Collect and analyze data from HP, blogs, and SNS
"""
import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

class ResearchEngine:
    def __init__(self):
        self.db_path = "bridge_data.db"
        self.init_db()

    def init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY,
                platform TEXT,
                post_id TEXT UNIQUE,
                content TEXT,
                author TEXT,
                posted_at TEXT,
                likes INTEGER,
                comments INTEGER,
                style_tags TEXT,
                collected_at TEXT
            )
        ''')

        # Website content table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS website_content (
                id INTEGER PRIMARY KEY,
                source_url TEXT,
                title TEXT,
                content TEXT,
                collected_at TEXT
            )
        ''')

        # Style analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS style_analysis (
                id INTEGER PRIMARY KEY,
                keyword TEXT UNIQUE,
                frequency INTEGER,
                category TEXT,
                updated_at TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def collect_hp_content(self):
        """Collect content from HP (bridge-inae.hp.peraichi.com, rikima81.com)"""
        urls = [
            os.getenv("BRIDGE_HP_URL", "https://bridge-inae.hp.peraichi.com"),
            os.getenv("RIKIMA_HP_URL", "https://rikima81.com")
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        for url in urls:
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                resp.encoding = 'utf-8'
                soup = BeautifulSoup(resp.content, 'html.parser')

                # Remove script and style
                for script in soup(["script", "style"]):
                    script.decompose()

                text = soup.get_text()
                title = soup.find('title')
                title_text = title.string if title else "No title"

                self._save_website_content(url, title_text, text)
                print(f"✓ Collected from {url}")
            except Exception as e:
                print(f"✗ Error collecting {url}: {e}")

    def _save_website_content(self, url: str, title: str, content: str):
        """Save website content to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO website_content
            (source_url, title, content, collected_at)
            VALUES (?, ?, ?, ?)
        ''', (url, title, content[:5000], datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def analyze_style(self):
        """Analyze posting style from collected data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get all posts
        cursor.execute('SELECT content FROM posts ORDER BY posted_at DESC LIMIT 100')
        posts = cursor.fetchall()

        # Get website content
        cursor.execute('SELECT content FROM website_content LIMIT 50')
        websites = cursor.fetchall()

        style_keywords = {
            "emotional": ["思う", "感じる", "大切", "重要", "心", "感動"],
            "action": ["する", "できる", "達成", "実現", "成長", "挑戦"],
            "teaching": ["教える", "学ぶ", "教育", "習う", "塾", "勉強"],
            "empathy": ["親", "子ども", "親御さん", "子どもたち", "家族"],
            "story": ["話", "経験", "ストーリー", "背景", "あの時"],
            "question": ["？", "どう", "なぜ", "どうして"],
        }

        all_text = ""
        for post in posts:
            all_text += post[0] + " "
        for website in websites:
            all_text += website[0] + " "

        # Count keyword frequency
        analysis = {}
        for category, keywords in style_keywords.items():
            count = sum(all_text.count(kw) for kw in keywords)
            analysis[category] = count
            self._save_style_analysis(category, count)

        return analysis

    def _save_style_analysis(self, keyword: str, frequency: int):
        """Save style analysis to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO style_analysis
            (keyword, frequency, category, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (keyword, frequency, "style", datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def get_style_profile(self) -> Dict:
        """Get analyzed style profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT keyword, frequency FROM style_analysis ORDER BY frequency DESC')
        results = cursor.fetchall()
        conn.close()

        return {kw: freq for kw, freq in results}

    def export_analysis(self):
        """Export analysis result"""
        profile = self.get_style_profile()
        with open("style_profile.json", "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        print("✓ Style profile exported to style_profile.json")


if __name__ == "__main__":
    engine = ResearchEngine()
    print("🔍 Starting research engine...")

    print("\n📥 Collecting HP content...")
    engine.collect_hp_content()

    print("\n📊 Analyzing style...")
    analysis = engine.analyze_style()
    print(f"Style analysis: {analysis}")

    print("\n💾 Exporting analysis...")
    engine.export_analysis()

    print("\n✅ Research complete!")
