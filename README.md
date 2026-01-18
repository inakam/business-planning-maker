# Business Planning Maker

Agentic AIとしてビジネスプランを無限に生成し続けるシステム。

## 特徴

- 🔹 **AI駆動**: Claude CLIを使用して高品質なビジネスプランを自動生成
- 🔹 **多角的評価**: 実現可能性、収益性、革新性の3軸で評価
- 🔹 **現実的**: 投資家や起業家から見ても魅力的なプランを生成
- 🔹 **継続的改善**: Ralph Loopと連動して無限に改善
- 🌐 **REST API**: FastAPIベースのAPIサーバー
- 🎨 **Web UI**: シンプルなWebインターフェース
- 📊 **分析機能**: 統計分析とプラン比較

## インストール

```bash
# Claude CLIのインストール（別途必要）
# https://docs.anthropic.com/claude/reference/claude-cli

# 基本機能 - 標準ライブラリのみで動作
python main.py --help

# APIサーバー機能 - 依存関係のインストール
pip install -r requirements.txt
```

## 使用方法

### コマンドラインインターフェース

#### 基本的な使用方法

```bash
# 1つのプランを生成
python main.py

# 5つのプランを一括生成
python main.py --count 5

# 無限に生成（5分間隔）
python main.py --continuous

# 10分間隔で最大100件まで生成
python main.py --continuous --interval 10 --max-iterations 100
```

#### 生成されたプランの確認

```bash
# サマリー表示
python main.py --summary

# トップ10のプランを表示
python main.py --top 10

# 統計分析
python main.py --analytics

# プラン比較（スコア順のインデックスを指定）
python main.py --compare 1 2

# 詳細評価
python main.py --evaluate 1
```

### APIサーバー

#### サーバー起動

```bash
# デフォルト設定（ポート8000）
python main.py --server

# カスタムポート
python main.py --server --port 9000

# カスタムホストとポート
python main.py --server --host 127.0.0.1 --port 8080
```

サーバー起動後、以下にアクセス：

- **Web UI**: http://localhost:8000/web
- **APIドキュメント**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

#### APIエンドポイント

| エンドポイント | 説明 |
|--------------|------|
| `GET /` | API情報 |
| `GET /web` | Web UI |
| `GET /api/health` | ヘルスチェック |
| `GET /api/plans` | プラン一覧（`?limit=10&offset=0`） |
| `GET /api/plans/{id}` | プラン詳細 |
| `POST /api/generate` | プラン生成 |
| `GET /api/analytics` | 統計分析 |
| `GET /api/compare/{id1}/{id2}` | プラン比較 |

#### API使用例

```bash
# プラン一覧取得
curl http://localhost:8000/api/plans?limit=10

# プラン生成
curl -X POST http://localhost:8000/api/generate -H "Content-Type: application/json" -d '{"count": 1}'

# 統計分析
curl http://localhost:8000/api/analytics
```

## 出力

生成されたビジネスプランは以下に保存されます：

- `output/markdown/` - Markdown形式のビジネスプラン
- `output/json/` - JSON形式のビジネスプラン（データ解析用）
- `output/summary_*.md` - サマリーレポート

## 評価基準

各ビジネスプランは以下の3つの観点から評価されます（0-100点）：

### 1. 実現可能性 (Feasibility)
- 市場成長率（20点）
- 市場段階（15点）
- 損益分岐期間（15点）
- LTV/CAC比率（20点）
- ROI（15点）
- チーム要件（10点）
- リスク対策（5点）

### 2. 収益性 (Profitability)
- 5年目売上（25点）
- 3年目利益率（20点）
- 成長率（20点）
- 市場サイズ（20点）
- 成長ポテンシャル（15点）

### 3. 革新性 (Innovation)
- カテゴリー（20点）
- 市場段階（20点）
- 問題提起（20点）
- 革新キーワード（10点）
- 成功要因（15点）
- 推論プロセス（15点）

**カテゴリ別の評価重み付け**:
- AI/ML: 革新性30%、収益性40%、実現可能性30%
- CleanTech: 革新性35%、収益性35%、実現可能性30%
- SaaS: 革新性20%、収益性45%、実現可能性35%
- など...

## カテゴリー

以下の11カテゴリーでビジネスプランを生成（各10テーマ）：

- **SaaS** - サブスクリプション、B2B SaaS等
- **Marketplace** - B2B/Consumerマーケットプレイス
- **AI/ML** - 生成AI、分析AI等
- **FinTech** - 決済、借入、保険等
- **HealthTech** - リモート医療、診断AI等
- **EdTech** - リスキリング、LMS等
- **CleanTech** - カーボンフットプリント、再生可能エネルギー等
- **E-commerce** - D2C、ライブコマース等
- **Consumer** - ヘルスケア、フィットネス等
- **B2B** - 調達、サプライチェーン等

## プロジェクト構造

```
business-planning-maker/
├── src/
│   ├── models/          # データモデル
│   │   └── business_plan.py
│   ├── generators/      # ビジネスプラン生成器
│   │   └── business_plan_generator.py
│   ├── evaluators/      # プラン評価器
│   │   └── plan_evaluator.py
│   └── utils/           # ユーティリティ
│       ├── storage.py    # 保存・読み込み
│       └── analytics.py  # 統計分析
├── output/
│   ├── markdown/        # Markdown出力
│   ├── json/            # JSON出力
│   └── summary_*.md     # サマリーレポート
├── logs/                # ログファイル
├── main.py              # メイン実行スクリプト
├── api_server.py        # FastAPIサーバー
└── README.md
```

## 高度な使用方法

### 分析機能

```bash
# 統計分析（平均、中央値、標準偏差等）
python main.py --analytics

# 出力例:
# - スコア統計
# - カテゴリ別分布
# - 市場トレンド
# - 主要なインサイト
```

### プラン比較

```bash
# スコア順のインデックスで2つのプランを比較
python main.py --compare 1 2

# 出力例:
# - プラン概要
# - 評価スコア比較
# - 市場分析比較
# - 財務予測比較
```

### 詳細評価

```bash
# 特定プランの詳細評価レポート
python main.py --evaluate 1

# 出力例:
# - 総合評価
# - 強み
# - 課題
# - 推奨事項
# - ベンチマーク比較
```

## Ralph Loopとの連携

このプロジェクトはRalph Loopと連動して動作します：

```bash
/ralph-loop:ralph-loop "ビジネスプランをclaude codeで無限に作り出す仕組みを作ってください..."
```

ループの各イテレーションで：
1. 既存のプランを確認
2. 新しいプランを生成
3. 評価して改善
4. 結果を保存

## ライセンス

MIT License
