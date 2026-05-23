# Dashboard 改善プラン

作成日: 2026-05-23  
最終更新: 2026-05-23（Duolingo Daily XP差分記録・履歴チャート追加）

---

## 現状

- `index.html` にHTML/Tailwind CDN版のモックアップが実装済み（全6改善項目 適用済み）
- GitHub: `napya0126-sudo/Naoya_Dashboard`
- Vercel: `naoya-dashboard` プロジェクト セットアップ済み

---

## 技術方針

| 項目 | 決定内容 | ステータス |
|---|---|---|
| 実装形式 | まず `index.html` を改善する（Next.js移行は後回し） | ✅ 確定 |
| フレームワーク移行 | Next.js (App Router) + Tailwind + shadcn/ui（動的データが必要になったら） | 🔄 保留 |
| デプロイ | Vercel（静的HTMLをそのままデプロイ） | ✅ 確定 |

---

## 改善項目

### 優先度：高

#### 1. 日付・グリーティングの動的化
- **改善内容**: JSで時間帯に応じて切り替え
  - 5:00〜11:59 → Good morning ☀️
  - 12:00〜17:59 → Good afternoon 🌤️
  - 18:00〜4:59 → Good evening 🌙
- **日付**: `new Date()` で自動生成（"Friday, May 23, 2026" 形式）
- **ステータス**: ✅ 実装済み

#### 2. 背景グラデーション改善
- **改善内容**: 薄ブルー → 薄パープル → 薄ピンクのパステルグラデーション
- **ステータス**: ✅ 実装済み

---

### 優先度：中

#### 3. NotebookLMカードのボタンレイアウト改善
- **改善内容**: ラベル（Morning/Evening）とタイトルを縦2行構造に変更
  ```
  🌅 Morning
     農業・酪農・フードテック  →
  ```
- **ステータス**: ✅ 実装済み

#### 4. カード左ボーダーアクセント
- **改善内容**: 各カード左側に4pxのカラーボーダー追加
  - AI Usage: パープル / Gemini Daily: グリーン / Shadowing: ピンク / NotebookLM: ブルー
- **ステータス**: ✅ 実装済み

---

### 優先度：低

#### 5. AI Usageバーチャートのラベル追加
- **改善内容**: 棒の下に曜日ラベル（M T W T F S）を追加
- **ステータス**: ✅ 実装済み

#### 6. Shadowingボタンのトーン調整
- **改善内容**: ベタ塗りピンク → `bg-pink-50 text-pink-600 border-pink-200` のソフトトーン
- **ステータス**: ✅ 実装済み

#### 7. AI Usage — Total AI Score 表示
- **改善内容**: Claude Session + Claude Weekly + Gemini Weekly の合計を「Total AI Score X / 300」として大きく表示。使うほど数値が上がるモチベーション指標
- **ステータス**: ✅ 実装済み（2026-05-23）

#### 8. AI Usage — 過去履歴グラフ（Chart.js）
- **改善内容**: `ai_usage.db` から過去14日分の日別スナップショットを取得し、積み上げ棒グラフで表示（Chart.js v4 CDN）
  - 紫濃い: Claude Session / 紫薄い: Claude Weekly / 青: Gemini Weekly
- **generate_data.py**: `history` フィールドを `ai_usage` に追加。日別最新スナップショットを集計
- **ステータス**: ✅ 実装済み（2026-05-23）

---

## カード表示順（2026-05-23 変更）

AI Usage → Gemini Daily → Shadowing → NotebookLM

---

## Duolingo カード追加計画

### 方針
- **目的**: 29歳での海外就職に向けた英語学習の進捗可視化
- **表示データ**: ストリーク日数 / 今日のXP / 累計XP
- **ユーザー名**: `RPhk251857`

### APIアクセス方法（非公式）
Duolingoは公式APIを提供していないが、以下のエンドポイントが非公式に利用可能：

```
GET https://www.duolingo.com/2017-06-30/users?username=RPhk251857
```

レスポンスから取得できる値：
- `streak` — 現在の連続学習日数
- `totalXp` — 累計XP
- `xpToday` — 今日のXP（当日分）
- `courses[].xp` — 言語別XP

### 実装メモ
- ブラウザから直接fetchすると **CORSエラー** になるため、バックエンド経由が必要
- Next.js移行後は API Route (`/api/duolingo`) でサーバーサイドfetchして返す
- 静的HTML期間中は手動更新 or Vercel Edge Functionで対応
- 利用規約グレーゾーンのため、いつか使えなくなる可能性あり（その場合は手動入力にフォールバック）

### カード表示イメージ
```
▌🦜 Duolingo                    ← 左ボーダー: オレンジ
  🔥 350-day streak
  Today: 45 XP
  Total: 128,430 XP
  [Open Duolingo →]
```

### ステータス
✅ 実装済み（`generate_data.py` + `data.json` 経由で表示。毎朝7時cron自動実行）

---

## Duolingo — Daily XP 差分記録・履歴チャート

### 改善内容
- **`duolingo_history.json`** をローカルに保存し、毎日の `total_xp` スナップショットを蓄積
- 前日との差分を `xp_earned` として計算し `data.json` の `duolingo.history` に含める
- `today_xp` フィールド: 今日の獲得XPを `data.json` トップレベルに追加
- **Duolingo カードの表示変更**:
  - 「today XP」欄を追加（緑色でハイライト、`+N` 形式）
  - 「total XP」欄（従来）はサイズ縮小してサブ情報に格下げ
  - **Daily XP バーチャート**: AI Usage チャートと同スタイルで過去14日分の獲得XPを棒グラフ表示（当日バーはオレンジ濃いめ）
- 初日は差分なし（`null`）、2日目以降から正確な1日XPが表示される

### ステータス
✅ 実装済み（2026-05-23）

---

## 検討中・未解決

| 項目 | 内容 | ステータス |
|---|---|---|
| 各アプリのリンク先URL | Vercelデプロイ済みのURLを各カードに設定する | ❓ URL未確定 |
| Shadowingアプリのログデータ場所 | 最終練習日・今週回数を動的取得するためのデータソース | ❓ 未確認 |
| 認証 | URLを知っている人のみアクセス可（当面なし）or 簡易Basic認証 | ❓ 未決定 |
| Next.js移行タイミング | NotebookLMディレクトリパース等、動的データが必要になった時点で移行 | 🔄 保留 |

---

## Mood Tracker カード（保留中）

### 背景
- 過去に [KPI Mood Tracker](https://github.com/napya0126-sudo/KPI_mood_tracker) を運用していたが続かなかった
- 続かなかった理由: UIとUXの問題 + 「記録するだけ」で見返す理由がなかった

### 再実装するなら解決すべき課題
- 入力を3タップ以内で完結させる（めんどくさくない）
- 記録した結果が「何かに活きる」仕組みが必要（ただの日記にしない）
  - 例: 週次サマリー、体調とShadowing頻度の相関、など

### ステータス
🔄 アイデアとして保留 — UIとUXが改善できる確信が持てたら着手

---

## Finance カード（未着手ワク）

### 方針
- ファイナンス管理はダッシュボードに入れる候補だが、現時点では着手しない
- 毎日目に入ることでストレスになるリスクがあるため、本人が「見たい」と思えるタイミングで検討

### ステータス
⏸ 着手しない（本人の意思決定待ち）

---

## 今後のロードマップ

1. ~~`index.html` の改善実装（優先度高・中・低 全6項目）~~ ✅ 完了
2. 各アプリのリンクURL確定 → カードに設定（Shadowing・Gemini Daily ✅ 設定済み）
   - AI Usage: URL未確定
   - NotebookLM: URL未確定
3. ~~Vercelデプロイ~~ ✅ https://naoya-dashboard.vercel.app
4. ~~AI Usage: Total AI Score + 履歴グラフ~~ ✅ 完了（2026-05-23）
5. ~~Duolingo Daily XP差分記録・履歴チャート~~ ✅ 完了（2026-05-23）
6. 必要に応じてNext.jsへ移行 → 動的データ取得
