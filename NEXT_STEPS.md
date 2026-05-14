# 次のステップ - SNS自動投稿システム起動ガイド

月末集客（5月31日）に向けて、このシステムを起動するための手順書です。

## 📋 完成したコンポーネント

✅ **5つの統合エンジン**
1. **Research Engine** - 塾長スタイル分析
2. **Buzz Learning Engine** - バズパターン学習（🆕）
3. **Trending Engine** - トレンド・季節ネタ分析（🆕）
4. **Post Generation Engine** - 投稿生成（buzz + trending 統合）
5. **Optimal Time Engine** - 最適投稿時間計算

✅ **スケジューリング**
- SNS Scheduler（毎日6:00 AM 自動トリガー）

✅ **統合テスト**
- test_integration.py で全エンジン動作確認済み

---

## 🚀 起動手順

### Phase 1: API設定（必須）【~5月18日】

#### Step 1: API キー取得
```bash
# API_SETUP.md の指示に従って取得
# - X（Twitter）API
# - Meta（Threads・Instagram）API
# - Claude API
```

**所要時間:** 約30分

#### Step 2: .env 設定
```bash
# .env ファイル作成
cp .env.example .env

# 取得したキーを記入
nano .env

# ファイル権限設定
chmod 600 .env
```

**確認:**
```bash
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
keys = ['X_OAUTH_CONSUMER_KEY', 'META_ACCESS_TOKEN', 'CLAUDE_API_KEY']
for key in keys:
    value = os.getenv(key)
    status = '✓' if value else '✗'
    print(f'{status} {key}')
"
```

---

### Phase 2: スタイル学習【5月19日】

#### Step 1: 塾長のスタイル分析
```bash
# HP・ブログから塾長のスタイル抽出
python research_engine.py

# 出力確認
cat style_profile.json
```

**出力ファイル:** `style_profile.json`
```json
{
  "emotional": 45,
  "teaching": 50,
  "empathy": 40,
  "action": 35,
  "story": 30,
  "question": 25
}
```

**所要時間:** 約10分

#### Step 2: バズパターン学習（初期化）
```bash
# 過去の高エンゲージメント投稿を入力
python -c "
from buzz_learning_engine import BuzzLearningEngine
engine = BuzzLearningEngine()

# 例：過去投稿を分析
posts = [
    # Threads から高いいいね数の投稿
    {
        'platform': 'threads',
        'post_id': 'threads_001',
        'content': '投稿内容をここに記入',
        'likes': 100,
        'comments': 15,
        'shares': 5
    },
    # Instagram から高いいいね数の投稿
    {
        'platform': 'instagram',
        'post_id': 'ig_001',
        'content': '投稿内容をここに記入',
        'likes': 200,
        'comments': 30,
        'shares': 10
    }
]

for post in posts:
    engine.record_buzz_post(
        post['platform'],
        post['post_id'],
        post['content'],
        post['likes'],
        post['comments'],
        post['shares']
    )

print('✓ バズパターン学習完了')
"
```

**過去投稿の取得方法:**
1. Threads・Instagram の過去投稿を確認
2. いいね数・コメント数の多い投稿 5～10個を選定
3. 上記スクリプトで記録

---

### Phase 3: テスト実行【5月20～22日】

#### Step 1: 統合テスト実行
```bash
python test_integration.py
```

**確認項目:**
- ✓ Buzz Learning Engine が投稿を記録
- ✓ Trending Engine が季節トピック取得
- ✓ Post Generation がバズパターンを参照

#### Step 2: 手動投稿テスト
```bash
python -c "
from scheduler import SNSScheduler

scheduler = SNSScheduler()

# 手動テスト投稿
scheduler.manual_post('子どもの成長と親の関わり')

# 生成された投稿を確認
import json
with open('published_posts.json') as f:
    posts = json.load(f)
    for post in posts[-3:]:  # 最後の3投稿表示
        print(f\"{post['platform']}: {post['content'][:80]}\")
"
```

**確認項目:**
- ✓ X投稿：280字以内 + ハッシュタグ
- ✓ Threads投稿：500字以内 + 日記的表現
- ✓ Instagram投稿：2200字以内 + 絵文字

#### Step 3: 実際に投稿テスト（オプション）
```bash
# 実際のSNSに投稿する場合は以下を実装
# scheduler.py の _publish_to_x(), _publish_to_threads(), _publish_to_instagram()
# で実際の API 呼び出しコード追加

# 現在は console に出力するのみ
```

---

### Phase 4: 本番運用【5月23日～31日】

#### Step 1: スケジューラー起動
```bash
# バックグラウンド実行
python scheduler.py &

# または
nohup python scheduler.py > scheduler.log 2>&1 &
```

#### Step 2: 毎日の監視
```bash
# ログファイル監視
tail -f snsposter.log

# スケジュール確認
python -c "
from scheduler import SNSScheduler
scheduler = SNSScheduler()
for job in scheduler.get_scheduled_jobs():
    print(f\"{job['id']}: {job['next_run']}\")
"
```

#### Step 3: エンゲージメント記録
```bash
# 毎日のエンゲージメント数を記録
# published_posts.json に自動保存されます

python -c "
import json
from datetime import datetime, timedelta

with open('published_posts.json') as f:
    posts = json.load(f)

# 本日の投稿
today = datetime.now().strftime('%Y-%m-%d')
today_posts = [p for p in posts if p['published_at'].startswith(today)]

for post in today_posts:
    print(f\"{post['platform']}: {post['topic']}\")
"
```

#### Step 4: パターン最適化（オプション）
```bash
# 毎週木曜に実行：バズパターン再分析
python -c "
from buzz_learning_engine import BuzzLearningEngine

engine = BuzzLearningEngine()

# 現在のバズパターン確認
for platform in ['x', 'threads', 'instagram']:
    insights = engine.get_buzz_insights(platform)
    print(f\"{platform}: {insights['top_structures']}\")
"
```

---

## 📊 ファイル構成（最終）

```
.
├── 【システムファイル】
├── research_engine.py              # 塾長スタイル分析
├── buzz_learning_engine.py         # バズパターン学習（新規）
├── trending_engine.py              # トレンド分析（新規）
├── post_generation_engine.py       # 投稿生成（拡張）
├── optimal_time_engine.py          # 時間最適化
├── scheduler.py                    # スケジューラー（拡張）
│
├── 【設定ファイル】
├── .env                            # API キー（要作成）
├── .env.example                    # テンプレート
├── config.yaml                     # 設定
├── requirements.txt                # 依存関係
│
├── 【ドキュメント】
├── README.md                       # 基本情報
├── API_SETUP.md                    # API 取得ガイド
├── SYSTEM_ARCHITECTURE.md          # システムアーキテクチャ（新規）
├── NEXT_STEPS.md                   # このファイル
│
├── 【データベース】（自動生成）
├── bridge_data.db                  # メインデータベース
├── style_profile.json              # 塾長スタイル分析結果
├── published_posts.json            # 投稿履歴
│
└── 【テスト】
└── test_integration.py             # 統合テスト（新規）
```

---

## ✅ チェックリスト

### API 設定【5月18日】
- [ ] X API キー取得
- [ ] Meta API キー取得
- [ ] Claude API キー取得
- [ ] .env ファイル作成・設定
- [ ] API 接続テスト

### スタイル学習【5月19日】
- [ ] research_engine.py 実行
- [ ] style_profile.json 生成確認
- [ ] 過去投稿をbuzz_engine に入力
- [ ] バズパターン学習開始

### テスト実行【5月20～22日】
- [ ] test_integration.py で統合テスト
- [ ] 手動投稿テスト
- [ ] 生成投稿品質確認
- [ ] 投稿時間確認

### 本番化【5月23日～31日】
- [ ] スケジューラー起動
- [ ] 毎日投稿開始
- [ ] エンゲージメント監視
- [ ] パターン最適化（随時）

---

## 🆘 トラブルシューティング

### Q: API キーが見つからない
**A:** .env ファイルが正しく設定されているか確認
```bash
cat .env | grep CLAUDE_API_KEY
```

### Q: バズパターンが収集できない
**A:** 過去投稿を手動入力してください
```bash
python buzz_learning_engine.py
# ウィザードで過去投稿を入力
```

### Q: トレンドトピックが取得できない
**A:** RSS フィード URL が無効な場合があります
- LocalNewsCollector の季節・行事ネタで補完
- または RSS フィード URL を更新

### Q: Claude API が limit に達した
**A:** console.anthropic.com で配額確認・調整
```bash
# 開発時は安価なモデルに変更
# post_generation_engine.py の self.model = "claude-3-5-haiku-20241022"
```

### Q: 投稿が投稿されない
**A:** scheduler.log を確認
```bash
tail -f snsposter.log
```

---

## 📞 サポート

問題が発生した場合：
1. ログファイル確認: `snsposter.log`
2. データベース確認: `bridge_data.db` スキーマ
3. API ステータス確認: X・Meta・Anthropic の公式サイト

---

## 🎯 月末集客戦略

**投稿スケジュール:**
- X: 毎日 1 回（複数時間帯）
- Threads: 毎日 3 回（朝・昼・晩）
- Instagram: 週 3～4 回（曜日固定）

**コンテンツ戦略:**
1. **トレンド活用**: 現在の教育・育児ホットトピックスを即座に取り込み
2. **バズパターン**: 高エンゲージメント構造を自動的に選定
3. **ローカル発信**: 滋賀県・彦根市の季節行事・教育情報
4. **親向け共感**: 保護者の悩みに即座に応答

**期待効果:**
- 投稿フォロワー数 +20～30%（28日間で）
- エンゲージメント率 +15～25%
- 体験授業問い合わせ +10～15 件程度

---

**準備完了日**: 2026-05-14  
**システムバージョン**: 1.0.0  
**目標達成日**: 2026-05-31
