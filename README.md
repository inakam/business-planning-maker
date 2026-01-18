# Business Planning Maker

Agentic AIとしてビジネスプランを無限に生成し続けるシステム。

## 特徴

- 🔹 **AI駆動**: Claude CLIを使用して高品質なビジネスプランを自動生成
- 🔹 **多角的評価**: 実現可能性、収益性、革新性の3軸で評価
- 🔹 **現実的**: 投資家や起業家から見ても魅力的なプランを生成
- 🔹 **継続的改善**: Ralph Loopと連動して無限に改善

## インストール

```bash
# Claude CLIのインストール（別途必要）
# https://docs.anthropic.com/claude/reference/claude-cli

# 依存関係（Python 3.8+）
# 外部依存はありません。標準ライブラリのみで動作します。
```

## 使用方法

### 基本的な使用方法

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

### 生成されたプランの確認

```bash
# サマリー表示
python main.py --summary

# トップ10のプランを表示
python main.py --top 10
```

## 出力

生成されたビジネスプランは以下に保存されます：

- `output/markdown/` - Markdown形式のビジネスプラン
- `output/json/` - JSON形式のビジネスプラン（データ解析用）
- `output/summary_*.md` - サマリーレポート

## 評価基準

各ビジネスプランは以下の3つの観点から評価されます（0-100点）：

### 1. 実現可能性 (Feasibility) - 35%
- 市場成長率
- 市場段階
- 損益分岐期間
- LTV/CAC比率
- 投資対効果（ROI）
- チーム要件の具体性
- リスク対策の充実度

### 2. 収益性 (Profitability) - 45%
- 5年目の売上規模
- 3年目の利益率
- 成長率（3年目/1年目）
- 市場サイズ
- 市場成長ポテンシャル

### 3. 革新性 (Innovation) - 20%
- カテゴリー（AI/ML、CleanTech等）
- 市場段階（emerging、growing等）
- 問題提起の具体性
- ソリューションの革新性キーワード
- 成功要因の多様性
- 推論プロセスの充実度

## カテゴリー

以下のカテゴリーでビジネスプランを生成：

- SaaS
- Marketplace
- AI/ML
- FinTech
- HealthTech
- EdTech
- CleanTech
- E-commerce
- Consumer
- B2B

## プロジェクト構造

```
business-planning-maker/
├── src/
│   ├── models/          # データモデル
│   ├── generators/      # ビジネスプラン生成器
│   ├── evaluators/      # プラン評価器
│   └── utils/           # ユーティリティ（保存、ロギング）
├── output/
│   ├── markdown/        # Markdown出力
│   ├── json/            # JSON出力
│   └── summary_*.md     # サマリーレポート
├── logs/                # ログファイル
├── main.py              # メイン実行スクリプト
└── README.md
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
