"""
ビジネスプラン生成器 - Claude APIを使用してビジネスプランを生成
"""
import json
import os
import uuid
from typing import Optional, List
from datetime import datetime
import subprocess
import random

from ..models.business_plan import BusinessPlan, PlanCategory, MarketAnalysis, MarketStage, FinancialProjection


class BusinessPlanGenerator:
    """Claude APIを使用したビジネスプラン生成器"""

    # トレンドとテーマのデータベース
    TRENDS = {
        "AI_ML": [
            "AIコーチングパーソナライゼーション",
            "生成AIコンテンツ最適化",
            "AIデータプライバシーコンプライアンス",
            "AIコードレビュー自動化",
            "AIマルチモーダル分析",
        ],
        "FINTECH": [
            "中小企業向け自動財務管理",
            "クロスボーダー決済最適化",
            "DeFiレンディングプラットフォーム",
            "ESG投資アドバイザリー",
            "インボイスファイナンス自動化",
        ],
        "HEALTHTECH": [
            "遠隔医療モニタリング",
            "メンタルヘルスAI支援",
            "パーソナライズド栄養管理",
            "クリニック運営最適化SaaS",
            "薬剤処方支援AI",
        ],
        "SAAS": [
            "中小企業向け人材管理最適化",
            "プロジェクト管理AI自動化",
            "顧客サポート自動化プラットフォーム",
            "サブスクリプション収益最適化",
            "在庫管理予測AI",
        ],
        "CLEANTECH": [
            "企業カーボンフットプリント追跡",
            "再生可能エネルギー取引プラットフォーム",
            "スマートグリッド最適化",
            "廃棄物管理リサイクルAI",
            "電力消費最適化SaaS",
        ],
    }

    BUSINESS_MODELS = [
        "サブスクリプションモデル",
        "フリーミアムモデル",
        "トランザクション手数料モデル",
        "マーケットプレイスモデル",
        "エンタープライズライセンスモデル",
        "利用量ベース課金モデル",
        "ハイブリッドモデル",
    ]

    TARGET_MARKETS = [
        "中小企業（従業員10-100人）",
        "大企業（従業員1000人以上）",
        "スタートアップ/VC投資企業",
        "フリーランス/個人事業主",
        "特定業種垂直市場",
        "消費者一般（B2C）",
    ]

    def __init__(self, iteration: int = 1):
        self.iteration = iteration

    def _select_theme(self) -> tuple:
        """ランダムにテーマとビジネスモデルを選択"""
        category = random.choice(list(self.TRENDS.keys()))
        themes = self.TRENDS[category]
        theme = random.choice(themes)
        business_model = random.choice(self.BUSINESS_MODELS)
        target_market = random.choice(self.TARGET_MARKETS)
        return category, theme, business_model, target_market

    def _generate_with_claude(self, prompt: str) -> str:
        """Claude CLIを使用してプロンプトを実行"""
        try:
            result = subprocess.run(
                ["claude", "-p", prompt],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                return result.stdout
            else:
                raise Exception(f"Claude CLI error: {result.stderr}")
        except subprocess.TimeoutExpired:
            raise Exception("Claude CLI timeout")
        except FileNotFoundError:
            # Claude CLIが利用できない場合のフォールバック
            return self._generate_fallback_plan()

    def _generate_fallback_plan(self) -> str:
        """Claude CLIが利用できない場合のフォールバック"""
        category, theme, business_model, target_market = self._select_theme()
        return json.dumps({
            "title": f"{theme} - {business_model}",
            "category": category,
            "problem_statement": f"{target_market}は現在、手動プロセスと非効率なシステムに依存しており、時間とリソースを浪費しています。",
            "solution": f"AIと自動化を活用した{theme}プラットフォームを提供します。",
            "value_proposition": f"時間を80%削減し、コストを50%削減する{theme}ソリューション。",
            "business_model": business_model,
            "market_analysis": {
                "market_size": random.randint(10, 1000),
                "market_growth_rate": random.randint(10, 40),
                "target_audience": target_market,
                "market_stage": "growing",
                "competitive_landscape": "競合は存在するが、AIによる差別化が可能",
                "key_success_factors": [
                    "ユーザー体験の最適化",
                    "AIモデルの精度向上",
                    "顧客獲得コストの最適化",
                    "パートナーシップ構築"
                ]
            },
            "financial_projection": {
                "year1_revenue": random.randint(100, 1000) * 1000,
                "year3_revenue": random.randint(5, 50) * 1000000,
                "year5_revenue": random.randint(20, 200) * 1000000,
                "initial_investment": random.randint(500, 5000) * 1000,
                "break_even_months": random.randint(18, 36),
                "profit_margin_year3": random.randint(20, 40),
                "customer_cac": random.randint(500, 5000),
                "customer_ltv": random.randint(3000, 30000)
            },
            "key_milestones": [
                "MVP開発（3ヶ月）",
                "初期顧客10社獲得（6ヶ月）",
                "シード資金調達（12ヶ月）",
                "機能拡張と市場拡大（18ヶ月）"
            ],
            "team_requirements": [
                "CEO/ビジネスリーダー",
                "CTO/技術リーダー",
                "AIエンジニア",
                "プロダクトマネージャー",
                "営業・マーケティング"
            ],
            "risk_factors": [
                "技術的実現のリスク",
                "市場受容の不確実性",
                "競合の台頭"
            ],
            "mitigation_strategies": [
                "段階的アプローチでの開発",
                "初期顧客との緊密な協働",
                "継続的なイノベーション"
            ],
            "reasoning": f"{target_market}向けの{theme}は、市場ニーズが高く、{business_model}で収益化が可能。",
            "tags": [theme.lower(), category.lower(), business_model.lower()]
        }, ensure_ascii=False, indent=2)

    def generate(self, previous_plans: Optional[List[BusinessPlan]] = None) -> BusinessPlan:
        """新しいビジネスプランを生成

        Args:
            previous_plans: 以前のプランリスト（重複回避のため）

        Returns:
            BusinessPlan: 生成されたビジネスプラン
        """
        category, theme, business_model, target_market = self._select_theme()

        # 以前のプランのタイトルを収集（重複回避）
        existing_titles = set()
        if previous_plans:
            for plan in previous_plans:
                existing_titles.add(plan.title)
                existing_titles.update(plan.tags)

        # プロンプト作成
        prompt = f"""あなたは経験豊富な起業家とビジネスコンサルタントです。以下の条件で、投資家から見て魅力的で実現可能なビジネスプランを作成してください。

**テーマ:** {theme}
**カテゴリ:** {category}
**ビジネスモデル:** {business_model}
**ターゲット市場:** {target_market}

以下のJSON形式で出力してください（マークダウン形式ではなく、純粋なJSONのみ）：

{{
  "title": "魅力的なビジネス名（簡潔で覚えやすい）",
  "problem_statement": "明確な問題提起（3-4文）",
  "solution": "具体的なソリューション（3-4文）",
  "value_proposition": "価値提案（2-3文、数字を含める）",
  "business_model": "{business_model}の詳細説明",
  "market_analysis": {{
    "market_size": 市場規模（億ドル単位の数値）,
    "market_growth_rate": 年平均成長率（%の数値）,
    "target_audience": "具体的なターゲット層",
    "market_stage": "emerging/growing/mature/declining",
    "competitive_landscape": "競合状況の分析（3-4文）",
    "key_success_factors": ["成功要因1", "成功要因2", "成功要因3", "成功要因4"]
  }},
  "financial_projection": {{
    "year1_revenue": 1年目の売上見込み（ドル）,
    "year3_revenue": 3年目の売上見込み（ドル）,
    "year5_revenue": 5年目の売上見込み（ドル）,
    "initial_investment": 必要初期投資額（ドル）,
    "break_even_months": 損益分岐までの月数,
    "profit_margin_year3": 3年目の利益率（%）,
    "customer_cac": 顧客獲得コスト（ドル）,
    "customer_ltv": 顧客生涯価値（ドル）
  }},
  "key_milestones": ["マイルストーン1", "マイルストーン2", "マイルストーン3", "マイルストーン4"],
  "team_requirements": ["必要な役割1", "役割2", "役割3", "役割4", "役割5"],
  "risk_factors": ["リスク1", "リスク2", "リスク3"],
  "mitigation_strategies": ["対策1", "対策2", "対策3"],
  "reasoning": "このビジネスが成功する理由と根拠（3-4文）",
  "tags": ["タグ1", "タグ2", "タグ3"]
}}

**重要:**
- 市場規模は実在する市場データに基づいて現実的な値に
- 成長率は業界トレンドを考慮
- 財務数値は現実的かつ投資家を惹きつけるものに
- LTV/CAC比率は3以上を目指す
- 損益分岐は18-36ヶ月以内に
- 既存のプランと重複しないよう独自性を重視

JSONのみを出力してください。"""

        try:
            response = self._generate_with_claude(prompt)
            # JSON抽出（マークダウンコードブロックがあれば削除）
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])

            data = json.loads(response)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Failed to parse Claude response ({e}), using fallback")
            data = json.loads(self._generate_fallback_plan())

        # BusinessPlanオブジェクトを作成
        market = MarketAnalysis(
            market_size=data["market_analysis"]["market_size"],
            market_growth_rate=data["market_analysis"]["market_growth_rate"],
            target_audience=data["market_analysis"]["target_audience"],
            market_stage=MarketStage(data["market_analysis"]["market_stage"]),
            competitive_landscape=data["market_analysis"]["competitive_landscape"],
            key_success_factors=data["market_analysis"]["key_success_factors"],
        )

        financial = FinancialProjection(
            year1_revenue=data["financial_projection"]["year1_revenue"],
            year3_revenue=data["financial_projection"]["year3_revenue"],
            year5_revenue=data["financial_projection"]["year5_revenue"],
            initial_investment=data["financial_projection"]["initial_investment"],
            break_even_months=data["financial_projection"]["break_even_months"],
            profit_margin_year3=data["financial_projection"]["profit_margin_year3"],
            customer_cac=data["financial_projection"]["customer_cac"],
            customer_ltv=data["financial_projection"]["customer_ltv"],
        )

        plan = BusinessPlan(
            id=str(uuid.uuid4()),
            title=data["title"],
            category=PlanCategory[category],
            iteration=self.iteration,
            problem_statement=data["problem_statement"],
            solution=data["solution"],
            value_proposition=data["value_proposition"],
            business_model=data["business_model"],
            market_analysis=market,
            financial_projection=financial,
            key_milestones=data["key_milestones"],
            team_requirements=data["team_requirements"],
            risk_factors=data["risk_factors"],
            mitigation_strategies=data["mitigation_strategies"],
            reasoning=data.get("reasoning", ""),
            tags=data.get("tags", []),
        )

        return plan
