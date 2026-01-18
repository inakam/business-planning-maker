"""
ビジネスプランのデータモデル
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class PlanCategory(Enum):
    """ビジネスプランのカテゴリ"""
    SAAS = "SaaS"
    MARKETPLACE = "Marketplace"
    AI_ML = "AI/ML"
    FINTECH = "FinTech"
    HEALTHTECH = "HealthTech"
    EDTECH = "EdTech"
    CLEANTECH = "CleanTech"
    ECOMMERCE = "E-commerce"
    CONSUMER = "Consumer"
    B2B = "B2B"
    OTHER = "Other"


class MarketStage(Enum):
    """市場の段階"""
    EMERGING = "emerging"
    GROWING = "growing"
    MATURE = "mature"
    DECLINING = "declining"


@dataclass
class FinancialProjection:
    """財務予測"""
    year1_revenue: float
    year3_revenue: float
    year5_revenue: float
    initial_investment: float
    break_even_months: int
    profit_margin_year3: float
    customer_cac: float
    customer_ltv: float


@dataclass
class MarketAnalysis:
    """市場分析"""
    market_size: float
    market_growth_rate: float
    target_audience: str
    market_stage: MarketStage
    competitive_landscape: str
    key_success_factors: List[str]


@dataclass
class BusinessPlan:
    """ビジネスプラン"""
    id: str
    title: str
    category: PlanCategory
    created_at: datetime = field(default_factory=datetime.now)
    iteration: int = 1

    # コアコンポーネント
    problem_statement: str = ""
    solution: str = ""
    value_proposition: str = ""
    business_model: str = ""

    # 市場分析
    market_analysis: Optional[MarketAnalysis] = None

    # 財務予測
    financial_projection: Optional[FinancialProjection] = None

    # 実行計画
    key_milestones: List[str] = field(default_factory=list)
    team_requirements: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)

    # 評価スコア
    feasibility_score: float = 0.0
    profitability_score: float = 0.0
    innovation_score: float = 0.0
    overall_score: float = 0.0

    # メタデータ
    reasoning: str = ""
    references: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Markdown形式で出力"""
        md = f"""# {self.title}

**カテゴリ:** {self.category.value} | **作成日時:** {self.created_at.strftime('%Y-%m-%d %H:%M:%S')} | **イテレーション:** {self.iteration}

---

## 評価スコア

- **実現可能性:** {self.feasibility_score:.1f}/100
- **収益性:** {self.profitability_score:.1f}/100
- **革新性:** {self.innovation_score:.1f}/100
- **総合スコア:** {self.overall_score:.1f}/100

---

## 問題提起

{self.problem_statement}

## ソリューション

{self.solution}

## 価値提案

{self.value_proposition}

## ビジネスモデル

{self.business_model}

"""
        if self.market_analysis:
            md += f"""## 市場分析

### 市場規模
- **市場サイズ:** ${self.market_analysis.market_size:,.0f}億
- **成長率:** {self.market_analysis.market_growth_rate:.1f}%
- **市場段階:** {self.market_analysis.market_stage.value}

### ターゲット層
{self.market_analysis.target_audience}

### 競合環境
{self.market_analysis.competitive_landscape}

### 成功要因
"""
            for factor in self.market_analysis.key_success_factors:
                md += f"- {factor}\n"
            md += "\n"

        if self.financial_projection:
            md += f"""## 財務予測

### 収益予想
- **1年目:** ${self.financial_projection.year1_revenue:,.0f}
- **3年目:** ${self.financial_projection.year3_revenue:,.0f}
- **5年目:** ${self.financial_projection.year5_revenue:,.0f}

### 投資指標
- **初期投資額:** ${self.financial_projection.initial_investment:,.0f}
- **損益分岐点:** {self.financial_projection.break_even_months}ヶ月
- **3年目利益率:** {self.financial_projection.profit_margin_year3:.1f}%
- **顧客獲得コスト (CAC):** ${self.financial_projection.customer_cac:,.0f}
- **顧客生涯価値 (LTV):** ${self.financial_projection.customer_ltv:,.0f}
- **LTV/CAC比率:** {self.financial_projection.customer_ltv / self.financial_projection.customer_cac if self.financial_projection.customer_cac > 0 else 0:.2f}x

"""

        md += """## 実行計画

### 重要マイルストーン
"""
        for milestone in self.key_milestones:
            md += f"- {milestone}\n"

        md += """
### 必要なチーム
"""
        for req in self.team_requirements:
            md += f"- {req}\n"

        md += """
### リスク要因と対策
"""
        for i, (risk, mitigation) in enumerate(zip(self.risk_factors, self.mitigation_strategies), 1):
            md += f"{i}. **{risk}**\n   - 対策: {mitigation}\n"

        if self.reasoning:
            md += f"""

## 推論プロセス

{self.reasoning}
"""

        if self.tags:
            md += f"\n**タグ:** {', '.join(self.tags)}\n"

        return md

    def to_json(self) -> dict:
        """JSON形式に変換"""
        from dataclasses import asdict

        data = asdict(self)
        # datetimeを文字列に変換
        data['created_at'] = self.created_at.isoformat()
        # Enumを文字列に変換
        if self.market_analysis:
            data['market_analysis']['market_stage'] = self.market_analysis.market_stage.value
        data['category'] = self.category.value
        return data
