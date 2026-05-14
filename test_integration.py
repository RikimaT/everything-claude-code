#!/usr/bin/env python3
"""
Integration test: Verify that buzz learning, trending, and post generation work together
"""
import json
from datetime import datetime
from buzz_learning_engine import BuzzLearningEngine
from trending_engine import TrendingEngine, LocalNewsCollector
from post_generation_engine import PostGenerationEngine

def test_buzz_learning():
    """Test buzz learning engine"""
    print("\n📊 Testing Buzz Learning Engine...")
    print("-" * 50)
    engine = BuzzLearningEngine()

    # Sample high-engagement posts to analyze
    sample_posts = [
        {
            "platform": "threads",
            "post_id": "sample_001",
            "content": "「進学塾じゃなくて総合学習教室」って言ってる理由。それは、結果よりも「頑張った経験」を大切にしたいから。成績が全てじゃない。",
            "likes": 45,
            "comments": 8,
            "shares": 3
        },
        {
            "platform": "x",
            "post_id": "sample_002",
            "content": "子どもが勉強に向き合う時、親ができることは？→聞くことです。「何が分からない？」ではなく「どう思う？」と。",
            "likes": 120,
            "comments": 15,
            "shares": 8
        },
        {
            "platform": "instagram",
            "post_id": "sample_003",
            "content": "親御さんから「うちの子、伸びしろはありますか？」という相談をよく受けます。答えは「ある」です。誰でも成長可能性を持っています。",
            "likes": 80,
            "comments": 12,
            "shares": 5
        }
    ]

    for post in sample_posts:
        print(f"\n✓ Recording post from {post['platform']}")
        engine.record_buzz_post(
            post["platform"],
            post["post_id"],
            post["content"],
            post["likes"],
            post["comments"],
            post["shares"]
        )

    # Get insights
    print("\n📈 Generating insights...")
    for platform in ["threads", "x", "instagram"]:
        insights = engine.get_buzz_insights(platform)
        print(f"\n{platform.upper()} Insights:")
        if insights.get("top_structures"):
            print(f"  Top Structures: {list(insights['top_structures'].keys())}")
        if insights.get("top_keywords"):
            print(f"  Top Keywords: {list(insights['top_keywords'].keys())[:5]}")

    return engine


def test_trending_engine():
    """Test trending engine"""
    print("\n\n📈 Testing Trending Engine...")
    print("-" * 50)
    engine = TrendingEngine()

    print("\n📰 Fetching trending topics...")
    # Note: This will try to fetch from RSS feeds, may fail without internet
    try:
        topics = engine.fetch_trending_topics()
        print("✓ Trending topics fetched:")
        for category, articles in topics.items():
            print(f"  {category}: {len(articles)} articles")
    except Exception as e:
        print(f"⚠️  RSS fetch failed (expected if no internet): {e}")

    print("\n💡 Getting seasonal topics...")
    seasonal = LocalNewsCollector.get_seasonal_topics()
    print(f"✓ Seasonal topics for this month: {seasonal[:3]}")

    print("\n📅 Getting event topics...")
    events = LocalNewsCollector.get_event_topics()
    print(f"✓ Event topics: {events[:2]}")

    return engine


def test_post_generation_with_context():
    """Test post generation with buzz and trending context"""
    print("\n\n🚀 Testing Post Generation with Context...")
    print("-" * 50)

    engine = PostGenerationEngine()

    print("\n✓ Buzz insights available:")
    buzz_x = engine.get_buzz_insights("x")
    print(f"  X buzz patterns: {list(buzz_x.get('top_structures', {}).keys())}")

    print("\n✓ Trending ideas available:")
    trending = engine.get_trending_ideas()
    print(f"  Trending topics found: {len(trending)} ideas")
    if trending:
        print(f"  Sample: {trending[0].get('title', 'N/A')}")

    print("\n✓ Formatted prompts for context:")
    buzz_context = engine._format_buzz_context("x")
    trending_context = engine._format_trending_context()
    print(f"  Buzz context length: {len(buzz_context)} chars")
    print(f"  Trending context length: {len(trending_context)} chars")

    return engine


def test_integration_summary():
    """Show how everything integrates"""
    print("\n\n✅ Integration Summary")
    print("=" * 50)
    print("""
The SNS posting system now integrates:

1. 🔍 RESEARCH ENGINE
   - Analyzes past posts to build style profile
   - Learns塾長's communication patterns

2. 📊 BUZZ LEARNING ENGINE (NEW)
   - Continuously analyzes viral posts
   - Extracts high-engagement patterns
   - Tracks keywords and structures that work

3. 📈 TRENDING ENGINE (NEW)
   - Fetches current trending topics from RSS
   - Analyzes seasonal and event-based content
   - Generates post angle ideas

4. 🚀 POST GENERATION ENGINE (ENHANCED)
   - Incorporates buzz patterns into prompts
   - References current trending topics
   - Combines with style profile for optimal posts
   - Generates platform-specific content

WORKFLOW:
Daily 6:00 AM → Generate posts using:
  • Base style profile (from research_engine)
  • Current buzz patterns (from buzz_learning_engine)
  • Trending topics (from trending_engine)
  • Platform-specific strategies
→ Output: X, Threads, Instagram posts ready for scheduled posting

CONTINUOUS LEARNING:
  • Buzz engine learns from daily posts
  • Trending engine refreshes topics
  • Patterns inform next day's generation
    """)


if __name__ == "__main__":
    print("\n🔬 Integration Test: Buzz + Trending + Post Generation")
    print("=" * 50)

    # Test each engine
    buzz_engine = test_buzz_learning()
    trending_engine = test_trending_engine()
    post_engine = test_post_generation_with_context()

    # Show integration
    test_integration_summary()

    print("\n✅ All integration tests complete!")
