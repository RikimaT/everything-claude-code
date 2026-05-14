# GitHub Secrets 設定手順（田中さん用・1回だけ）

OAuth でトークンを取得した後、GitHub Actions が無料で毎日自動投稿できるようにするための**最終ステップ**です。

## いつやるか

Claude が OAuth トークンを取得し終わったあと、Claude から「以下の値を GitHub Secrets に追加してください」と通知されます。そのとき以下の手順を実行してください。

## 手順

1. ブラウザで以下を開く：

   ```
   https://github.com/RikimaT/everything-claude-code/settings/secrets/actions
   ```

2. 「New repository secret」をクリック

3. 以下の3つを順番に登録：

   | Name | Value |
   |---|---|
   | `META_ACCESS_TOKEN` | Claude から渡された長期トークン |
   | `THREADS_USER_ID` | Claude から渡されたユーザーID |
   | `INSTAGRAM_ACCOUNT_ID` | （Instagram も有効化する場合のみ） |

4. 各 Secret 入力後「Add secret」をクリック

## スケジュール

設定後、以下のタイミングで GitHub Actions が**無料で**自動投稿します：

- **Threads**: 毎日 09:00 / 14:00 / 21:00 (JST)
- **Instagram**: 月・水・金・日 12:00 (JST)

## 動作確認

`.github/workflows/sns-auto-post.yml` の `workflow_dispatch` から手動実行してテストできます：

```
https://github.com/RikimaT/everything-claude-code/actions/workflows/sns-auto-post.yml
```

「Run workflow」→ Platform 選択 →「Run workflow」で即時実行されます。

## 投稿内容のストック

`weekly_posts.json` がリポジトリにコミットされている必要があります。Claude が事前に作成済みのものを使うか、`generate_weekly_posts.py` で新規生成してください（後者は CLAUDE_API_KEY が必要）。
