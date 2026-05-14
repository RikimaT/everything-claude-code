"""
週次投稿ジェネレーター
使い方: Claude Code でこのファイルを実行するか、
        「今週の投稿を生成して」と Claude Code に依頼する

生成された投稿は weekly_posts.json に保存され、
スケジューラーが毎日自動で投稿します。
"""
import json
from datetime import date, timedelta
from weekly_post_store import save_weekly_posts, create_empty_week_template
from trending_engine import LocalNewsCollector


def build_generation_prompt() -> str:
    """Claude Code に渡す投稿生成プロンプトを作成"""
    today = date.today()
    seasonal_topics = LocalNewsCollector.get_seasonal_topics()
    event_topics = LocalNewsCollector.get_event_topics()

    prompt = f"""
総合学習塾ブリッジ（彦根市稲枝）のSNS投稿を1週間分生成してください。

【塾の特徴】
- 塾長：田中力磨（著書2冊、16年の塾経営）
- 「自学自習」を重視、生徒の成長欲を引き出す
- 「変な塾」というアプローチ（固定授業なし）
- 成績より「人間力」を重視
- 彦根市稲枝の地域密着型

【今月のトレンドキーワード】
{', '.join(seasonal_topics[:4])}

【地域イベント】
{', '.join(event_topics[:3])}

【生成する投稿数と形式】
- Threads: 21投稿（1日3回 × 7日）
  - 500字以内
  - 日記的・個人的な語り口
  - 地域密着（滋賀・彦根の話題も時々）
  - 親向けの共感メッセージ

- Instagram: 4投稿（週4回）
  - 2200字以内
  - 絵文字を使って親しみやすく
  - 教育的な内容・実体験ベース
  - ハッシュタグ付き

【出力形式】（JSONで出力してください）
```json
{{
  "week_start": "{today.isoformat()}",
  "posts": [
    {{
      "id": 1,
      "date": "YYYY-MM-DD",
      "platform": "threads",
      "scheduled_time": "09:00",
      "content": "投稿内容...",
      "topic": "トピック名",
      "used": false
    }},
    ...
  ]
}}
```

投稿内容は全て日本語で、親しみやすく、押しつけがましくない文体で生成してください。
塾の宣伝は控えめにし、「共感」「ストーリー」「問いかけ」を意識してください。
"""
    return prompt


def generate_sample_posts() -> dict:
    """
    サンプル投稿を生成（Claude Code が実際に生成する際の参考）
    実際はClaude Codeに上記プロンプトで生成してもらう
    """
    today = date.today()
    posts = []
    post_id = 1

    # Threadsの投稿サンプル（7日分）
    threads_samples = [
        ("子どもが「わかった！」と言う瞬間",
         "今日、教室でこんな場面があった。\n\nずっと分からなかった問題を、何度も悩んで、ようやく「あ！わかった！」って顔が変わった瞬間。\n\n成績とか点数とか、そういうことじゃなくて。\nあの「わかった！」の表情こそ、学ぶことの本質だと思う。\n\n子どもが輝く瞬間は、テストの点じゃない。\n#彦根 #稲枝 #塾"),
        ("GWどう過ごしましたか？",
         "GWが終わって、子どもたちと話してみると面白い。\n\n「遊んだだけ」って言う子。\n「勉強もした」って言う子。\n\nどちらもいい。\n問題は何をしたかじゃなくて、「自分で決めて動けたか」ということ。\n\n親が全部決めてあげた休みより、自分で考えた休みのほうが、成長になる。"),
        ("親の言葉が子どもを変える",
         "「勉強しなさい」と言われ続けた子は、勉強が嫌いになる。\n\n「今日どんなこと考えた？」と聞かれた子は、考えることが好きになる。\n\n言葉一つで、子どもの未来が変わる。\n怖いことだけど、逆に言えば、チャンスでもある。"),
        ("「変な塾」って言われる理由",
         "よく「ブリッジって普通の塾と違うよね」と言われる。\n\nそう、違う。\n\nテストの点を上げることより、「勉強したい」と思える子を育てたい。\n16年間、そこだけはブレずにやってきた。\n\n変わってるかもしれないけど、それがブリッジのやり方。"),
        ("子どもの伸びしろ、どこにある？",
         "「うちの子、伸びしろありますか？」\n\nよく聞かれる質問。\n\n答えは必ず「あります」。\n\nただ、それがどこにあるかは、子どもによって違う。\n点数じゃないところに伸びしろがある子のほうが、むしろ多い。"),
        ("失敗から学ぶって、どういうこと？",
         "失敗を叱ると、子どもは失敗を隠すようになる。\n\n失敗を一緒に考えると、子どもは次に活かすようになる。\n\n「なんでこうなったんだろうね」\nこの一言で、子どもの思考が動き出す。"),
        ("自学自習のスイッチ",
         "「自分から勉強してほしい」\n親御さんからよく聞く願い。\n\nそのスイッチがどこにあるか、子どもによって違う。\n\n好きなことと結びついたとき。\n達成感を感じたとき。\n誰かに認めてもらったとき。\n\nスイッチを探す旅が、塾でできることだと思っている。"),
    ]

    # Threadsの投稿を7日×3回分
    for day_offset in range(7):
        day = (today + timedelta(days=day_offset)).isoformat()
        sample = threads_samples[day_offset % len(threads_samples)]
        topic, content = sample

        for time_slot in ["09:00", "14:00", "21:00"]:
            # 時間帯によって少しトーンを変える
            if time_slot == "21:00":
                post_content = f"今日の終わりに一つ。\n\n{content}"
            elif time_slot == "14:00":
                post_content = content
            else:
                post_content = f"おはようございます。\n\n{content}"

            posts.append({
                "id": post_id,
                "date": day,
                "platform": "threads",
                "scheduled_time": time_slot,
                "content": post_content,
                "topic": topic,
                "used": False
            })
            post_id += 1

    # Instagram投稿（週4回）
    instagram_samples = [
        ("子どもが自分から学ぶ環境を作る3つのポイント",
         "✏️ 子どもが自分から勉強するって、どういうこと？\n\n「勉強しなさい」\nこの言葉、毎日言ってませんか？\n\n実は、この言葉が逆効果になることがある。\n\n彦根で16年、学習塾をやってきた中で気づいたこと。\n子どもが自分から学ぶには、3つの環境が必要です。\n\n---\n\n① 失敗できる場所\n正解ばかり求めると、子どもは挑戦しなくなる。\n「間違えてもいい」環境が、チャレンジ精神を育てる。\n\n② 達成感が生まれる場所\n小さな「できた！」が積み重なると、\n「もっとやりたい」に変わる。\n\n③ 認めてもらえる場所\n「頑張ったね」の一言が、次への原動力になる。\n\n---\n\n📚 ブリッジが大切にしていること\n成績を上げることより、「学ぶことが楽しい」と感じてもらうこと。\n\nそれが、長い目で見たときに一番の近道だと信じています。\n\n#教育 #子育て #塾 #彦根 #稲枝 #自学自習 #学習 #成長"),
        ("中間テスト前にやっておくべきこと",
         "📝 テスト前の過ごし方、間違えてませんか？\n\n5月は中間テストの季節。\n毎年この時期になると、子どもも親も焦り始める。\n\nでも、ちょっと待って。\nテスト直前に詰め込んでも、実は点数は上がらない。\n\n16年の指導経験から言うと、\n大事なのは「2週間前からどう過ごすか」。\n\n---\n\n✅ テスト2週間前にやること\n\n1. 範囲を確認して「わからないところ」をリストアップ\n2. 一日の学習時間を決める（30分でもOK）\n3. 「できた！」を記録する（ノートに書くだけでOK）\n\n---\n\n❌ やってはいけないこと\n\n・テスト前日に夜更かしして詰め込む\n・「とりあえず教科書を読む」だけ\n・苦手科目を後回しにする\n\n---\n\n🌱 大切なのは点数より「自分で動けたか」\n\nテストは結果より、準備のプロセスが大事。\n「自分で計画を立てて実行できた」という経験が、\n本当の意味での成長につながります。\n\n#中間テスト #テスト勉強 #子育て #塾 #彦根 #稲枝 #学習法"),
        ("親ができる「最高の学習サポート」とは",
         "👨‍👩‍👧 親が子どもの勉強に関わるとき、気をつけてほしいこと。\n\n「教えてあげよう」と思う気持ち、わかります。\nでも、ちょっと待って。\n\n教えすぎると、子どもは「自分で考えること」をやめてしまう。\n\n---\n\n🔑 親ができる最高のサポート\n\n「答えを教える」のではなく、\n「一緒に考える」こと。\n\n「どう思う？」\n「なんでそう考えたの？」\n\nこの2つの質問が、子どもの思考力を育てます。\n\n---\n\n📖 ブリッジでのエピソード\n\n先日、こんな場面がありました。\nずっと悩んでいた子が、突然「あ！わかった！」と。\n\nそのとき、私は何も教えていない。\nただ「どこで詰まってる？」と聞いただけ。\n\n子どもには、自分で考える力が必ずある。\nその力を信じることが、最高のサポートです。\n\n#子育て #教育 #学習サポート #塾 #彦根 #稲枝 #思考力 #自学自習"),
        ("「成績が上がらない」本当の理由",
         "📊 成績が上がらないのは、勉強量の問題じゃないかもしれない。\n\n「もっと勉強させればいい」\nと思っている保護者の方へ。\n\n16年間、たくさんの子どもを見てきた中で気づいたこと。\n成績が上がらない本当の理由は、意外なところにある。\n\n---\n\n🔍 よくある原因3つ\n\n① 「わからない」が言えない環境\n間違いを怒られる経験が多いと、\n子どもは「わからない」と言えなくなる。\n\n② 自分の「理解できた」が確認できていない\n「読んだ」と「理解した」は違う。\n自分で説明できるかどうかが重要。\n\n③ 「なぜ学ぶのか」が見えていない\n目的のない学習は続かない。\nどんな小さな目標でも、「目的」があると違う。\n\n---\n\n💡 まず試してほしいこと\n\n今夜、子どもに聞いてみてください。\n「今日、学校でどんなことが面白かった？」\n\n勉強の話じゃなくていい。\n子どもが話したくなる環境を作ることが、\n実は学習改善の第一歩です。\n\n#教育 #成績アップ #子育て #塾選び #彦根 #稲枝 #ブリッジ #学習"),
    ]

    for idx, (day_offset, (topic, content)) in enumerate(
            zip([0, 2, 4, 6], instagram_samples)):
        day = (today + timedelta(days=day_offset)).isoformat()
        posts.append({
            "id": post_id,
            "date": day,
            "platform": "instagram",
            "scheduled_time": "12:00",
            "content": content,
            "topic": topic,
            "used": False
        })
        post_id += 1

    return {
        "week_start": today.isoformat(),
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "posts": posts
    }


if __name__ == "__main__":
    print("📅 週次投稿ジェネレーター")
    print("=" * 50)
    print()

    import sys
    if "--show-prompt" in sys.argv:
        print("【Claude Code に貼り付けるプロンプト】")
        print("-" * 50)
        print(build_generation_prompt())
    else:
        print("サンプル投稿を生成して weekly_posts.json に保存します...")
        data = generate_sample_posts()
        save_weekly_posts(data)

        threads_count = sum(1 for p in data["posts"] if p["platform"] == "threads")
        ig_count = sum(1 for p in data["posts"] if p["platform"] == "instagram")

        print(f"\n✅ 生成完了！")
        print(f"  Threads: {threads_count}投稿")
        print(f"  Instagram: {ig_count}投稿")
        print(f"\n📁 保存先: weekly_posts.json")
        print("\n次は以下を実行してスケジューラーを起動してください:")
        print("  python scheduler.py")
