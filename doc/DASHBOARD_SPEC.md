# Naoya Dashboard — 要件定義

作成日: 2026-05-22  
最終更新: 2026-05-23（Vocabulary カード追記）

---

## コンセプト

**「今日、どれかひとつ触りたくなる」ハブ画面**

リンク集ではなく、各アプリの"今の状態"を一目で見せることで、自然に触りたくなるきっかけをつくる。携帯から見ることを前提にしたモバイルファースト設計。

---

## 対象アプリ（4つ）

| アプリ名 | パス | 概要 |
|---|---|---|
| Shadowing App | `shadowing-app` | 英語シャドーイング練習アプリ |
| AI Usage Tracker | `AI_limited_usage` | AIツールの使用量ダッシュボード |
| Gemini Daily Search | `Gemini_dailysearch` | Geminiによるデイリー検索・ログ管理 |
| NotebookLM Hub | `notebooklm` | 毎日配信されるポッドキャスト＋ニュース |
| Duolingo | — | 英語学習ストリーク・XP表示（非公式API連携） |

※ English Word Book は対象外

---

## 各カードに表示する「きっかけ情報」

### 🎙 Shadowing App
- 最後に練習した日（○日前）
- 今週の練習回数
- → 3日触ってないと「そろそろやろ」と思わせる

### 📊 AI Usage Tracker
- **Total AI Score**: Claude Session + Claude Weekly + Gemini Weekly の合計（最大300点）を大きく表示
- 各指標の使用量バー（Claude Session / Claude Weekly / Gemini Weekly）
- **履歴グラフ**: 過去最大14日分の積み上げ棒グラフ（Chart.js）
- データソース: `ai_usage.db` の `usage_snapshots` テーブル（日別最新スナップショット）

### 🔍 Gemini Daily Search
- 最終実行日
- 直近のトピックタイトル（1行）

### 🦜 Duolingo
- 連続学習日数（ストリーク）
- **今日の獲得XP** (`today_xp`): 前日との差分、緑色でハイライト表示
- 英語コースの累計XP
- **Daily XP 履歴チャート**: 過去14日分の1日ごと獲得XPをバーチャートで表示（Chart.js）
- データ取得: 非公式API（`duolingo.com/2017-06-30/users?username=...`）認証不要
- ローカル蓄積: `duolingo_history.json` に日別スナップショットを保存し差分計算
- 更新: `generate_data.py` から毎朝7時 cron で自動取得

### 📖 Vocabulary (単語帳)
- **総調べ単語数**: shadowing-app で字幕タップして調べた単語の累計（`vocabulary_items` の件数）
- **苦手単語 TOP5**: `lookup_count` が多い or `review_correct / review_total` が低い単語のリスト
  - 単語（英語）+ 日本語訳 + 調べた回数を表示
- データソース: shadowing-app と共通の **Supabase** `vocabulary_items` テーブルを直読み
- カラーアクセント: イエロー系（学習・記憶をイメージ）

### 🎧 NotebookLM Hub ← メイン変更点
- **今日配信されているエピソードのタイトル一覧**
  - 例: `朝: スタートアップ・プロダクト` / `夜: 農業・フードテック`
- エピソードのNotebookLMリンク（タップで開く）
- 今日の英語復習テーマ（例: `現在完了形の活用`）
- データソース: `notebooklm/archive/daily/` のディレクトリ名をパース

---

## 画面構成（モバイル縦スクロール）

カード表示順: **AI Usage → Gemini Daily → Shadowing → NotebookLM**（2026-05-23 変更）

```
┌─────────────────────────┐
│  Good morning, Hase-pyon ☀️ │  ← JS動的（時間帯で切替）
│  Friday, May 23, 2026    │  ← JS動的（new Date()）
├─────────────────────────┤
│ ▌📊 AI Usage            │  ← 左ボーダー: パープル
│ 今月 Claude: 42回         │
│ 前週比 +12% ↑            │
│ [棒グラフ M T W T F S]   │
├─────────────────────────┤
│ ▌🔍 Gemini Daily        │  ← 左ボーダー: グリーン
│ 最終実行: 昨日            │
│ 「AI規制の最新動向」        │
├─────────────────────────┤
│ ▌🎙 Shadowing           │  ← 左ボーダー: ピンク
│ 最後: 3日前 😅            │
│ 今週: 0回                │
│ [Try it today →]         │
├─────────────────────────┤
│ ▌🎧 NotebookLM          │  ← 左ボーダー: ブルー
│ 今日のポッドキャスト       │
│ 🌅 Morning              │
│   農業・酪農・フードテック → │
│ 🌃 Evening              │
│   農業・酪農・フードテック → │
│ 英語: Conjunctions ...   │
└─────────────────────────┘
```

---

## 実装済み（index.html 静的モックアップ）

| 項目 | 内容 |
|---|---|
| グリーティング動的化 | JS で時間帯判定 + `new Date()` で日付自動生成 |
| 背景グラデーション | 薄ブルー → 薄パープル → 薄ピンク |
| カード左ボーダー | 各カード左4px カラーアクセント |
| NotebookLMボタン | ラベル＋タイトル縦2行構造 |
| バーチャート曜日ラベル | M T W T F S |
| Shadowingボタン | ソフトピンク（bg-pink-50） |
| カード順変更 | AI Usage → Gemini Daily → Shadowing → NotebookLM |
| Duolingo連携 | 非公式APIでストリーク・総XP取得 → data.json経由で表示。毎朝7時cron自動実行 |
| Duolingo 差分保存・チャート | `duolingo_history.json` に日別スナップショットを蓄積し前日差分でDaily XPを算出。過去14日分をバーチャートで表示 |
| Vocabulary カード（未実装・仕様確定） | shadowing-app の Supabase `vocabulary_items` を直読み。総調べ単語数 + 苦手TOP5（lookup_count 降順）。イエロー系アクセント。Shadowing カードの直後に配置予定 |

---

## デザイン方針

**キーワード: かわいい・柔らかい・使いたくなる**

### 言語ポリシー ✅ 確定
- UIラベル・ボタン・ステータス表示は **英語基調**
- 各アプリから取得するコンテンツ（記事タイトル・トピック名など）は **原文のまま表示**
  - 例: Gemini Daily Search のトピックが日本語なら日本語で出す
  - 例: NotebookLM のエピソード名も取得したファイル名そのまま
- 「英語UIの中に日本語コンテンツが混在する」のは意図した仕様

### 方向性（要最終確認）
- パステルカラー or ソフトグラデーション背景
- カード角丸大きめ、シャドウあり
- フォント: 丸みのあるもの（例: Nunito, M PLUS Rounded）
- ダークモード固定ではなく、ライト or 淡いトーン
- 絵文字・アイコンを活用して視覚的にわかりやすく
- アニメーション: カードのふわっとした表示

### 参考イメージ（候補）
- Notion風の整頓感 ＋ パステルアクセント ✅ 採用済み
- BeReal / Daylio っぽいカジュアルさ

---

## 技術方針

- **フレームワーク**: Next.js (App Router)
- **スタイル**: Tailwind CSS + shadcn/ui
- **デプロイ**: Vercel
- **データ取得**:
  - NotebookLM: `archive/daily/` のファイル名をパースするAPI Route
  - Shadowing: ログファイルまたはDBから最終練習日を取得
  - AI Usage: `ai_usage.db` (SQLite) をAPIで読む
  - Gemini: ログファイルをパース
  - Duolingo: 非公式API（`duolingo.com/2017-06-30/users`）からストリーク・XPを取得。`generate_data.py` に実装済み。毎朝7時cron実行
- **認証**: URLを知っている人だけでOK（当面なし）or 簡易Basic認証

---

## 未解決事項

- [ ] 各アプリのVercelデプロイURL（リンク先）
- [ ] Shadowingアプリのログデータの場所
- [ ] 認証どうするか

---

## 進め方

1. ~~デザインの方向性を確定~~ ✅
2. ~~静的モックアップを作って雰囲気確認~~ ✅
3. 各アプリのリンクURL確定 → カードに設定
4. データ取得部分を繋ぎ込む（Next.js移行タイミングで）
5. Vercelにデプロイ
