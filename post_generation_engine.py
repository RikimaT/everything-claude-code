"""
Post Generation Engine: Generate SNS posts using Claude API
"""
import os
import json
from datetime import datetime, timedelta
import random
from typing import List, Dict
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class PostGenerationEngine:
    def __init__(self):
        self.client = Anthropic()
        self.model = "claude-opus-4-7"
        self.style_profile = self.load_style_profile()
        self.bridge_character = self._build_bridge_character()

    def load_style_profile(self) -> Dict:
        """Load style profile from analysis"""
        try:
            with open("style_profile.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️ style_profile.json not found. Using default profile.")
            return {
                "emotional": 45,
                "teaching": 50,
                "empathy": 40,
                "action": 35,
                "story": 30,
                "question": 25
            }

    def _build_bridge_character(self) -> str:
        """Build character profile from style analysis"""
        profile_str = "彦根市稲枝の総合学習塾「ブリッジ」のキャラクター："
        profile_str += """
- 塾長は田中力磨（著書2冊、16年の塾経営）
- 「自学自習」を重視し、生徒の成長欲を引き出す
- 固定の授業ではなく「変な塾」というアプローチ
- 親向けと生徒向けの両方に訴求
- 実体験・ストーリーに基づいた教育観
- 成績向上より「人間力」を重視
- 子どもの「伸びしろ診断」など実践的なコンテンツ
"""
        return profile_str

    def generate_post(self, topic: str, platform: str = "all") -> Dict[str, str]:
        """Generate post content for specified platform"""
        prompt = self._build_generation_prompt(topic, platform)

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = message.content[0].text
        posts = self._parse_posts(response_text, platform)

        return posts

    def _build_generation_prompt(self, topic: str, platform: str) -> str:
        """Build prompt for post generation"""
        base_prompt = f"""
あなたは「総合学習塾ブリッジ」の SNS 投稿を作成するアシスタントです。

【ブリッジの特徴】
{self.bridge_character}

【投稿スタイルの特徴】
- 感情的で親しみやすい
- 親の悩みや子どもの成長に共感
- 「なぜ？」という問いかけで深掘り
- ストーリーと具体例を交える
- 行動喚起（体験授業など）は控えめ

【生成するプラットフォーム】
{platform}

【本日のトピック】
{topic}

以下の形式で投稿を生成してください：

"""

        if platform == "all" or platform == "x":
            base_prompt += """
【X投稿】（280字以内）
本文:

ハッシュタグ:

---
"""

        if platform == "all" or platform == "threads":
            base_prompt += """
【Threads投稿】（500字以内）
本文:

---
"""

        if platform == "all" or platform == "instagram":
            base_prompt += """
【Instagram投稿】（2200字以内）
本文:

絵文字・装飾:

ハッシュタグ:

---
"""

        return base_prompt

    def _parse_posts(self, response_text: str, platform: str) -> Dict[str, str]:
        """Parse generated posts from response"""
        posts = {}

        platforms = ["x", "threads", "instagram"] if platform == "all" else [platform]

        for p in platforms:
            marker = f"【{p.upper()}投稿】"
            if marker in response_text:
                start = response_text.find(marker) + len(marker)
                end = response_text.find("---", start)
                content = response_text[start:end].strip()
                posts[p] = content

        return posts

    def generate_multiple_options(self, topic: str, platform: str = "all", num_options: int = 3) -> List[Dict]:
        """Generate multiple post options for selection"""
        options = []

        for i in range(num_options):
            posts = self.generate_post(topic, platform)
            options.append({
                "id": i + 1,
                "posts": posts,
                "timestamp": datetime.now().isoformat()
            })

        return options


if __name__ == "__main__":
    engine = PostGenerationEngine()

    print("🚀 Post Generation Engine")
    print("-" * 50)

    # Example topic
    topic = "子どもが勉強に向き合う時、親ができることは？"

    print(f"\n📝 Generating posts for topic: {topic}")
    print("\n生成中...")

    # Generate multiple options
    options = engine.generate_multiple_options(topic, platform="x", num_options=1)

    for opt in options:
        print(f"\n【Option {opt['id']}】")
        for platform, content in opt["posts"].items():
            print(f"\n{platform.upper()}:")
            print(content[:200] + "..." if len(content) > 200 else content)

    print("\n✅ Generation complete!")
