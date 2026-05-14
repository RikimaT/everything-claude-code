# SNS 自動投稿システム - システムアーキテクチャ

## 概要

彦根市稲枝の総合学習塾「ブリッジ」の SNS 自動投稿システムは、複数の学習エンジンが連携して、塾長の投稿スタイルを学習し、現在のトレンド・バズパターンを分析し、最適な投稿を自動生成・配信するシステムです。

## システムアーキテクチャ図

```
┌─────────────────────────────────────────────────────────────────┐
│                    データ収集層                                  │
├─────────────────────────────────────────────────────────────────┤
│  • ブリッジHP      • ブログ（Note）   • Instagram   • Threads    │
│  • Ameblo         • 過去の投稿メタデータ                          │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                  学習エンジン層（3つの学習エンジン）              │
├─────────────────────────────────────────────────────────────────┤
│  1️⃣  Research Engine (研究エンジン)                             │
│     └→ 塾長の投稿スタイル分析                                    │
│     └→ キーワード頻度分析                                       │
│     └→ style_profile.json 生成                                  │
│                                                                  │
│  2️⃣  Buzz Learning Engine (バズ学習エンジン)                    │
│     └→ 過去投稿のエンゲージメント分析                            │
│     └→ 高エンゲージメント構造パターン抽出                        │
│     └→ キーワード・ハッシュタグ頻度追跡                         │
│     └→ プラットフォーム別バズパターン保存                       │
│                                                                  │
│  3️⃣  Trending Engine (トレンドエンジン)                         │
│     └→ RSS フィード解析（教育・育児・地域ニュース）             │
│     └→ 季節・行事ベースのトピック生成                          │
│     └→ 投稿アングル提案（地域密着・教育視点・親向け）           │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│              投稿生成層（Post Generation Engine）                 │
├─────────────────────────────────────────────────────────────────┤
│  • style_profile を読み込み                                      │
│  • buzz_patterns を参照（現在バズっている構造）                 │
│  • trending_topics を参照（時事ネタ）                            │
│  • Claude API で最適な投稿を生成                                 │
│  • プラットフォーム別最適化                                      │
│    - X: 280字以内 + 日本語ハッシュタグ                           │
│    - Threads: 500字以内 + 日記的な個人発信                       │
│    - Instagram: 2200字以内 + 絵文字・装飾                        │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│               時間最適化層（Optimal Time Engine）                 │
├─────────────────────────────────────────────────────────────────┤
│  • 過去投稿のエンゲージメント時系列分析                          │
│  • プラットフォーム別最適投稿時間計算                            │
│  • 2週間先のスケジュール生成                                     │
│  • ±30分のランダマイズで投稿パターン隠蔽                        │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│              スケジューリング層（SNS Scheduler）                  │
├─────────────────────────────────────────────────────────────────┤
│  • APScheduler による定期実行管理                                │
│  • 毎日 6:00 AM に投稿生成トリガー                               │
│  • X・Threads・Instagram への自動投稿                             │
│  • エンゲージメント記録・分析                                    │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                データベース層（SQLite）                          │
├─────────────────────────────────────────────────────────────────┤
│  • bridge_data.db                                                │
│    - posts テーブル                                              │
│    - website_content テーブル                                    │
│    - style_analysis テーブル                                     │
│    - buzz_posts テーブル                                         │
│    - buzz_patterns テーブル                                      │
│    - trending_topics テーブル                                    │
│    - trending_articles テーブル                                  │
│    - generated_trending_posts テーブル                           │
└─────────────────────────────────────────────────────────────────┘
```

## 各エンジンの機能詳細

### 1. Research Engine（研究エンジン）
**ファイル:** `research_engine.py`

```python
from research_engine import ResearchEngine

engine = ResearchEngine()

# HP・ブログからデータ収集
website_data = engine.fetch_website_content()

# スタイル分析実行
style_profile = engine.analyze_style()

# 結果を JSON で保存
engine.export_style_profile("style_profile.json")
```

**分析対象:**
- HP: `bridge-inae.hp.peraichi.com`
- ブログ: `note.com/rikima81+4`
- SNS: `Instagram` `Threads` `Ameblo`

**分析要素:**
```json
{
  "emotional": 45,      // 感情的表現の強さ
  "teaching": 50,       // 教育的コンテンツ比率
  "empathy": 40,        // 共感表現の頻度
  "action": 35,         // 行動喚起の強度
  "story": 30,          // ストーリー性
  "question": 25        // 問いかけ比率
}
```

---

### 2. Buzz Learning Engine（バズ学習エンジン）
**ファイル:** `buzz_learning_engine.py`

```python
from buzz_learning_engine import BuzzLearningEngine

engine = BuzzLearningEngine()

# 高エンゲージメント投稿を記録
engine.record_buzz_post(
    platform="threads",
    post_id="post_001",
    content="投稿コンテンツ",
    likes=45,
    comments=8,
    shares=3
)

# バズパターン抽出
insights = engine.get_buzz_insights("threads")
print(insights)
# {
#   "top_structures": {"story_based": {...}, "emotional": {...}},
#   "top_keywords": {"自学自習": {...}, "親": {...}}
# }
```

**エンゲージメントスコア計算:**
```
engagement_score = likes + (comments × 2) + (shares × 3)
```

**抽出される構造パターン:**
- `question_answer` - 問いと答えの形式
- `story_based` - ストーリー仕立て
- `emotional` - 感情的アピール
- `actionable` - 実行可能なアドバイス
- `parent_focused` - 親向けコンテンツ
- `data_driven` - データ・統計ベース

**継続的学習:**
- 毎日の投稿後、buzz_engine に記録
- 自動的に patterns テーブル更新
- 次の投稿生成の参考に

---

### 3. Trending Engine（トレンドエンジン）
**ファイル:** `trending_engine.py`

```python
from trending_engine import TrendingEngine, LocalNewsCollector

engine = TrendingEngine()

# トレンドトピック取得
topics = engine.fetch_trending_topics()

# 季節ネタ取得
seasonal = LocalNewsCollector.get_seasonal_topics()
# 5月例: ["GW", "中間テスト", "親子時間"]

# 行事ネタ取得
events = LocalNewsCollector.get_event_topics()
# ["彦根城まつり", "全国学力テスト", ...]

# 投稿アングル生成
ideas = engine.analyze_trending_for_post()
# [
#   {
#     "title": "GW",
#     "post_angles": [
#       "親向け: GWについて、親の視点での考え方",
#       "地域密着: 彦根・滋賀でのGWの現状"
#     ]
#   }
# ]
```

**データソース:**
- RSS フィード（教育ニュース、育児ネタ、地域ニュース）
- 季節イベント（月別）
- 地域イベント（滋賀県・彦根市）

**投稿アングル提案:**
```
1. 親向けアングル       - 親の視点・悩みに焦点
2. 教育視点            - 子どもの成長への影響
3. 地域密着            - 彦根・滋賀での事例
4. 日記的              - 塾長の個人的な思考
```

---

### 4. Post Generation Engine（投稿生成エンジン）
**ファイル:** `post_generation_engine.py`

```python
from post_generation_engine import PostGenerationEngine

engine = PostGenerationEngine()

# 複数の情報源を統合
posts = engine.generate_post(
    topic="子どもの成長と親の関わり",
    platform="all"
)

# 生成内容例
# {
#   "x": "子どもが成長する時、親ができることは...",
#   "threads": "今日考えたこと。子どもの成長について...",
#   "instagram": "親御さんからよく相談されること..."
# }
```

**プロンプト構成:**
```
1. ブリッジの基本情報
2. 塾長のキャラクター
3. 投稿スタイルの特徴 (style_profile)
4. 【NEW】現在バズっている構造パターン (buzz_patterns)
5. 【NEW】現在のトレンド・時事ネタ (trending_topics)
6. トピック
7. プラットフォーム別要件
```

**プラットフォーム別最適化:**

| プラットフォーム | 特性 | 投稿スタイル |
|---|---|---|
| **X** | リアルタイム・拡散 | 短くて鋭い問いかけ + ハッシュタグ |
| **Threads** | コミュニティ・会話 | 日記的・個人的な思考 + ローカル視点 |
| **Instagram** | ビジュアル・フォロワー | 詳しい解説 + 絵文字・装飾 |

---

### 5. Optimal Time Engine（時間最適化エンジン）
**ファイル:** `optimal_time_engine.py`

```python
from optimal_time_engine import OptimalTimeEngine

engine = OptimalTimeEngine()

# プラットフォーム別最適時間計算
x_schedule = engine.calculate_next_optimal_time("x")
threads_schedule = engine.calculate_next_optimal_time("threads")
instagram_schedule = engine.calculate_next_optimal_time("instagram")

# 2週間分のスケジュール生成
schedule = engine.generate_two_week_schedule()
```

**デフォルト最適時間:**
```
X:          朝7時、昼12時、夜6時、夜9時
Threads:    朝9時、昼2時、夜7時、夜9時
Instagram:  朝7時、昼12時、夜6時、夜8時
```

**ランダマイズ:**
- ±30分のランダマイズ
- 自動投稿パターン隠蔽
- エンゲージメント分析による微調整

---

### 6. SNS Scheduler（スケジューラー）
**ファイル:** `scheduler.py`

```python
from scheduler import SNSScheduler

scheduler = SNSScheduler()

# スケジューラー開始
scheduler.start()  # 毎日 6:00 AM に投稿生成開始

# 手動テスト
scheduler.manual_post("子どもの成長と親の関わり")

# スケジュール確認
jobs = scheduler.get_scheduled_jobs()
```

**スケジューリング手順:**

1. **毎日 6:00 AM**
   - `_get_daily_topic()` で本日のトピック決定
   - トレンド → 季節ネタ → 定義済みトピック の優先順で選択

2. **投稿生成**
   - `post_generation_engine.generate_post()` で全プラットフォーム投稿生成
   - style_profile + buzz_patterns + trending_topics を参照

3. **時間計算**
   - `optimal_time_engine.calculate_next_optimal_time()` で各プラットフォームの最適時間計算
   - ±30分のランダマイズ適用

4. **スケジュール登録**
   - APScheduler で各プラットフォーム・時刻の投稿をジョブ登録

5. **投稿実行**
   - 指定時刻に自動投稿
   - エンゲージメント記録
   - buzz_engine に記録して継続学習

---

## データフロー

### 日次フロー（毎日 6:00 AM）

```
┌─ 6:00 AM トリガー
│
├─ 1. トピック決定
│  ├─ trending_engine.get_trending_ideas()
│  ├─ LocalNewsCollector.get_seasonal_topics()
│  └─ 優先度順に選択 (trending > seasonal > predefined)
│
├─ 2. 投稿生成
│  ├─ style_profile 読み込み
│  ├─ buzz_engine.get_buzz_insights() で現在パターン取得
│  ├─ trending_engine.get_trending_ideas() で時事ネタ取得
│  └─ Claude API で投稿生成（style + buzz + trending 統合）
│
├─ 3. 時間最適化
│  └─ optimal_time_engine で各プラットフォームの投稿時刻計算
│
├─ 4. スケジュール登録
│  └─ APScheduler で投稿ジョブ登録
│
└─ 指定時刻に自動投稿
   ├─ X API / Meta API で投稿実行
   └─ buzz_engine に記録（継続学習）
```

### 継続学習フロー

```
投稿実行
  ↓
エンゲージメント記録
  ↓
buzz_engine.record_buzz_post()
  ↓
patterns テーブル更新
  ↓
次の投稿生成の参考に → 以降の投稿がより効果的に
```

---

## 必要な環境設定

### 1. API キー取得（API_SETUP.md 参照）

```bash
# X API
X_OAUTH_CONSUMER_KEY=...
X_OAUTH_CONSUMER_SECRET=...
X_BEARER_TOKEN=...

# Meta API (Threads・Instagram)
META_ACCESS_TOKEN=...
META_BUSINESS_ID=...
INSTAGRAM_ACCOUNT_ID=...

# Claude API
CLAUDE_API_KEY=...
```

### 2. データベース初期化

```bash
python research_engine.py     # style_profile.json 生成
python buzz_learning_engine.py # buzz パターン学習開始
python trending_engine.py      # トレンド取得開始
```

### 3. スケジューラー起動

```bash
python scheduler.py
```

---

## 月末集客対応スケジュール

### Phase 1: セットアップ（～5月20日）
- [ ] API キー取得・設定
- [ ] research_engine で塾長スタイル分析完了
- [ ] 過去投稿をbuzz_engine に入力
- [ ] RSS フィード設定確認

### Phase 2: テスト・最適化（5月21日～27日）
- [ ] scheduler 動作テスト
- [ ] 生成投稿品質確認
- [ ] エンゲージメント分析開始
- [ ] 投稿時間微調整

### Phase 3: 本番運用（5月28日～31日）
- [ ] 本番スケジューラー起動
- [ ] 毎日投稿開始
- [ ] エンゲージメント監視
- [ ] リアルタイム最適化

---

## 注意事項

### コスト
- **Claude API**: 使用量に応じて課金（月額～数千円想定）
- **X・Meta API**: 開発用は無料
- **その他**: 無料

### セキュリティ
```bash
# .env ファイル Git コミット禁止
echo ".env" >> .gitignore

# API キーはローカルのみに保管
chmod 600 .env
```

### トラブルシューティング

**バズパターンが収集できない場合:**
- buzz_engine.record_buzz_post() で手動入力

**トレンドトピックが取得できない場合:**
- RSS フィードが無効の場合が多い
- LocalNewsCollector の季節・行事ネタで補完

**投稿生成失敗時:**
- Claude API 配額確認（console.anthropic.com）
- .env ファイル設定確認

---

## 今後の拡張可能性

1. **フォロワー数トラッキング**
   - エンゲージメント率による自動最適化

2. **感情分析の高度化**
   - NLP による詳細な投稿スタイル分析

3. **複数アカウント対応**
   - 塾の複数 SNS アカウント一括管理

4. **A/B テスト**
   - 複数案自動生成・比較・学習

5. **ユーザーコメント分析**
   - コメント内容を学習して投稿内容改善

---

**最後更新**: 2026-05-14  
**バージョン**: 1.0.0  
**準備完了**: 月末集客に向けて全エンジン統合完了
