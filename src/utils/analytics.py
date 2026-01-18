"""
分析ユーティリティ - ビジネスプランの統計分析と比較機能
"""
from typing import List, Dict, Optional
import statistics
from collections import Counter

from ..models.business_plan import BusinessPlan


class PlanAnalytics:
    """ビジネスプランの分析ユーティリティ"""

    @staticmethod
    def calculate_statistics(plans: List[BusinessPlan]) -> Dict[str, Dict[str, float]]:
        """基本統計量を計算

        Args:
            plans: ビジネスプランのリスト

        Returns:
            統計情報の辞書
        """
        if not plans:
            return {}

        scores = {
            "総合スコア": [p.overall_score for p in plans],
            "実現可能性": [p.feasibility_score for p in plans],
            "収益性": [p.profitability_score for p in plans],
            "革新性": [p.innovation_score for p in plans],
        }

        stats = {}
        for name, values in scores.items():
            stats[name] = {
                "平均": statistics.mean(values),
                "中央値": statistics.median(values),
                "最小": min(values),
                "最大": max(values),
                "標準偏差": statistics.stdev(values) if len(values) > 1 else 0,
            }

        return stats

    @staticmethod
    def analyze_category_distribution(plans: List[BusinessPlan]) -> Dict[str, int]:
        """カテゴリ別の分布を分析

        Args:
            plans: ビジネスプランのリスト

        Returns:
            カテゴリ別のカウント
        """
        categories = [p.category.value for p in plans]
        return dict(Counter(categories))

    @staticmethod
    def analyze_market_trends(plans: List[BusinessPlan]) -> Dict[str, float]:
        """市場トレンドを分析

        Args:
            plans: ビジネスプランのリスト

        Returns:
            市場指標の平均値
        """
        if not plans:
            return {}

        return {
            "平均市場規模（億ドル）": statistics.mean([p.market_analysis.market_size for p in plans]),
            "平均成長率（%）": statistics.mean([p.market_analysis.market_growth_rate for p in plans]),
            "平均損益分岐（ヶ月）": statistics.mean([p.financial_projection.break_even_months for p in plans]),
            "平均LTV/CAC比率": statistics.mean([
                p.financial_projection.customer_ltv / p.financial_projection.customer_cac
                for p in plans
                if p.financial_projection.customer_cac > 0
            ]) if any(p.financial_projection.customer_cac > 0 for p in plans) else 0,
        }

    @staticmethod
    def find_similar_plans(target_plan: BusinessPlan, plans: List[BusinessPlan], top_n: int = 5) -> List[tuple]:
        """類似のプランを検索

        Args:
            target_plan: 対象プラン
            plans: 検索対象のプランリスト
            top_n: 上位N件

        Returns:
            (プラン, 類似度スコア)のリスト
        """
        from difflib import SequenceMatcher

        similarities = []
        for plan in plans:
            if plan.id == target_plan.id:
                continue

            # タイトル、カテゴリ、タグの類似度
            title_sim = SequenceMatcher(None, target_plan.title.lower(), plan.title.lower()).ratio()
            category_match = 1.0 if target_plan.category == plan.category else 0.0

            # タグの重複
            target_tags = set(target_plan.tags)
            plan_tags = set(plan.tags)
            tag_overlap = len(target_tags & plan_tags) / len(target_tags | plan_tags) if (target_tags | plan_tags) else 0.0

            # 総合類似度
            overall_sim = (title_sim * 0.5 + category_match * 0.2 + tag_overlap * 0.3)
            similarities.append((plan, overall_sim))

        # 類似度順にソート
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]

    @staticmethod
    def generate_comparison_report(plan1: BusinessPlan, plan2: BusinessPlan) -> str:
        """2つのプランを比較するレポートを生成

        Args:
            plan1: 比較対象1
            plan2: 比較対象2

        Returns:
            Markdown形式の比較レポート
        """
        md = f"""# ビジネスプラン比較レポート

## プラン概要

| 項目 | プランA | プランB |
|------|---------|---------|
| タイトル | {plan1.title} | {plan2.title} |
| カテゴリ | {plan1.category.value} | {plan2.category.value} |
| 総合スコア | {plan1.overall_score:.1f} | {plan2.overall_score:.1f} |

---

## 評価スコア比較

| 項目 | プランA | プランB | 優位 |
|------|---------|---------|------|
| 実現可能性 | {plan1.feasibility_score:.1f} | {plan2.feasibility_score:.1f} | {"A" if plan1.feasibility_score > plan2.feasibility_score else "B" if plan2.feasibility_score > plan1.feasibility_score else "="} |
| 収益性 | {plan1.profitability_score:.1f} | {plan2.profitability_score:.1f} | {"A" if plan1.profitability_score > plan2.profitability_score else "B" if plan2.profitability_score > plan1.profitability_score else "="} |
| 革新性 | {plan1.innovation_score:.1f} | {plan2.innovation_score:.1f} | {"A" if plan1.innovation_score > plan2.innovation_score else "B" if plan2.innovation_score > plan1.innovation_score else "="} |

---

## 市場分析比較

| 項目 | プランA | プランB |
|------|---------|---------|
| 市場規模 | ${plan1.market_analysis.market_size:,.0f}億 | ${plan2.market_analysis.market_size:,.0f}億 |
| 成長率 | {plan1.market_analysis.market_growth_rate:.1f}% | {plan2.market_analysis.market_growth_rate:.1f}% |
| 市場段階 | {plan1.market_analysis.market_stage.value} | {plan2.market_analysis.market_stage.value} |

---

## 財務予測比較

| 項目 | プランA | プランB |
|------|---------|---------|
| 5年目売上 | ${plan1.financial_projection.year5_revenue:,.0f} | ${plan2.financial_projection.year5_revenue:,.0f} |
| 初期投資 | ${plan1.financial_projection.initial_investment:,.0f} | ${plan2.financial_projection.initial_investment:,.0f} |
| 損益分岐 | {plan1.financial_projection.break_even_months}ヶ月 | {plan2.financial_projection.break_even_months}ヶ月 |
| LTV/CAC | {plan1.financial_projection.customer_ltv / plan1.financial_projection.customer_cac if plan1.financial_projection.customer_cac > 0 else 0:.1f}x | {plan2.financial_projection.customer_ltv / plan2.financial_projection.customer_cac if plan2.financial_projection.customer_cac > 0 else 0:.1f}x |

---

## 特徴比較

### プランAの特徴
- {plan1.value_proposition}

### プランBの特徴
- {plan2.value_proposition}

---

## 総合評価

**総合スコア差:** {abs(plan1.overall_score - plan2.overall_score):.1f}ポイント

"""

        if plan1.overall_score > plan2.overall_score:
            md += f"プランAが{plan1.overall_score - plan2.overall_score:.1f}ポイント優れています。\n\n"
        elif plan2.overall_score > plan1.overall_score:
            md += f"プランBが{plan2.overall_score - plan1.overall_score:.1f}ポイント優れています。\n\n"
        else:
            md += "両プランは同点です。\n\n"

        return md

    @staticmethod
    def generate_insights(plans: List[BusinessPlan]) -> List[str]:
        """プランセットからインサイトを抽出

        Args:
            plans: ビジネスプランのリスト

        Returns:
            インサイトのリスト
        """
        if not plans:
            return []

        insights = []

        # 最高スコアのプラン
        best_plan = max(plans, key=lambda p: p.overall_score)
        insights.append(f"最高スコア: 「{best_plan.title}」({best_plan.overall_score:.1f}点)")

        # 最も人気のあるカテゴリ
        category_dist = PlanAnalytics.analyze_category_distribution(plans)
        if category_dist:
            top_category = max(category_dist.items(), key=lambda x: x[1])
            insights.append(f"最も多いカテゴリ: {top_category[0]} ({top_category[1]}件)")

        # 市場トレンド
        market_trends = PlanAnalytics.analyze_market_trends(plans)
        if market_trends:
            insights.append(f"平均市場規模: ${market_trends['平均市場規模（億ドル）']:.0f}億")
            insights.append(f"平均成長率: {market_trends['平均成長率（%）']:.1f}%")

        # LTV/CAC比率が最も高いプラン
        valid_ltv_cac = [
            (p, p.financial_projection.customer_ltv / p.financial_projection.customer_cac)
            for p in plans
            if p.financial_projection.customer_cac > 0
        ]
        if valid_ltv_cac:
            best_ltv_cac = max(valid_ltv_cac, key=lambda x: x[1])
            insights.append(f"最高LTV/CAC比率: 「{best_ltv_cac[0].title}」({best_ltv_cac[1]:.1f}倍)")

        return insights
