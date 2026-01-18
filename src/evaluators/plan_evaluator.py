"""
ビジネスプラン評価器 - 生成されたプランを多角的に評価
"""
from typing import List
import math

from ..models.business_plan import BusinessPlan


class PlanEvaluator:
    """ビジネスプランの評価器"""

    def evaluate(self, plan: BusinessPlan) -> BusinessPlan:
        """ビジネスプランを評価してスコアを設定

        Args:
            plan: 評価対象のビジネスプラン

        Returns:
            スコアが設定されたビジネスプラン
        """
        feasibility = self._evaluate_feasibility(plan)
        profitability = self._evaluate_profitability(plan)
        innovation = self._evaluate_innovation(plan)

        plan.feasibility_score = feasibility
        plan.profitability_score = profitability
        plan.innovation_score = innovation

        # 重み付け総合スコア
        plan.overall_score = (
            feasibility * 0.35 +
            profitability * 0.45 +
            innovation * 0.20
        )

        return plan

    def _evaluate_feasibility(self, plan: BusinessPlan) -> float:
        """実現可能性を評価（0-100）"""
        score = 50.0  # 基準点

        # 市場成長率による評価（0-20点）
        growth = plan.market_analysis.market_growth_rate
        if growth >= 30:
            score += 20
        elif growth >= 20:
            score += 15
        elif growth >= 10:
            score += 10
        else:
            score += 5

        # 市場段階による評価（0-15点）
        stage = plan.market_analysis.market_stage.value
        if stage == "growing":
            score += 15
        elif stage == "emerging":
            score += 10
        elif stage == "mature":
            score += 5

        # 損益分岐期間による評価（0-15点）
        break_even = plan.financial_projection.break_even_months
        if break_even <= 18:
            score += 15
        elif break_even <= 24:
            score += 12
        elif break_even <= 36:
            score += 8
        else:
            score += 3

        # LTV/CAC比率による評価（0-20点）
        if plan.financial_projection.customer_cac > 0:
            ltv_cac = plan.financial_projection.customer_ltv / plan.financial_projection.customer_cac
            if ltv_cac >= 5:
                score += 20
            elif ltv_cac >= 4:
                score += 17
            elif ltv_cac >= 3:
                score += 13
            elif ltv_cac >= 2:
                score += 8
            else:
                score += 3

        # 初期投資の妥当性（0-15点）
        investment = plan.financial_projection.initial_investment
        year5_revenue = plan.financial_projection.year5_revenue
        if year5_revenue > 0:
            roi = (year5_revenue - investment) / investment * 100
            if roi >= 500:
                score += 15
            elif roi >= 300:
                score += 12
            elif roi >= 200:
                score += 9
            elif roi >= 100:
                score += 5
            else:
                score += 2

        # チーム要件の具体性（0-10点）
        if len(plan.team_requirements) >= 5:
            score += 10
        elif len(plan.team_requirements) >= 3:
            score += 7
        else:
            score += 3

        # リスク対策の充実度（0-5点）
        if len(plan.mitigation_strategies) >= len(plan.risk_factors):
            score += 5
        else:
            score += 2

        return min(100.0, max(0.0, score))

    def _evaluate_profitability(self, plan: BusinessPlan) -> float:
        """収益性を評価（0-100）"""
        score = 40.0  # 基準点

        # 5年目の売上規模（0-25点）
        year5 = plan.financial_projection.year5_revenue
        if year5 >= 100_000_000:  # 1億ドル以上
            score += 25
        elif year5 >= 50_000_000:  # 5000万ドル以上
            score += 22
        elif year5 >= 10_000_000:  # 1000万ドル以上
            score += 18
        elif year5 >= 1_000_000:  # 100万ドル以上
            score += 12
        else:
            score += 5

        # 3年目の利益率（0-20点）
        margin = plan.financial_projection.profit_margin_year3
        if margin >= 40:
            score += 20
        elif margin >= 30:
            score += 17
        elif margin >= 20:
            score += 13
        elif margin >= 10:
            score += 8
        else:
            score += 3

        # 成長率（3年目/1年目）（0-20点）
        if plan.financial_projection.year1_revenue > 0:
            growth_ratio = plan.financial_projection.year3_revenue / plan.financial_projection.year1_revenue
            if growth_ratio >= 20:
                score += 20
            elif growth_ratio >= 10:
                score += 17
            elif growth_ratio >= 5:
                score += 13
            elif growth_ratio >= 2:
                score += 8
            else:
                score += 3

        # 市場サイズ（0-20点）
        market_size = plan.market_analysis.market_size
        if market_size >= 500:
            score += 20
        elif market_size >= 100:
            score += 17
        elif market_size >= 50:
            score += 13
        elif market_size >= 10:
            score += 8
        else:
            score += 3

        # 市場成長率×市場サイズの複合評価（0-15点）
        growth_potential = (market_size * plan.market_analysis.market_growth_rate) / 100
        if growth_potential >= 50:
            score += 15
        elif growth_potential >= 20:
            score += 12
        elif growth_potential >= 10:
            score += 8
        else:
            score += 3

        return min(100.0, max(0.0, score))

    def _evaluate_innovation(self, plan: BusinessPlan) -> float:
        """革新性を評価（0-100）"""
        score = 50.0  # 基準点

        # カテゴリによる評価（0-20点）
        category = plan.category.value
        high_innovation = ["AI/ML", "CleanTech", "FinTech", "HealthTech"]
        if category in high_innovation:
            score += 20
        else:
            score += 10

        # 市場段階（0-20点）
        stage = plan.market_analysis.market_stage.value
        if stage == "emerging":
            score += 20
        elif stage == "growing":
            score += 15
        elif stage == "mature":
            score += 5

        # 問題提起の具体性（長さとキーワード）（0-20点）
        problem_len = len(plan.problem_statement)
        if problem_len >= 200:
            score += 15
        elif problem_len >= 100:
            score += 10
        else:
            score += 5

        # ソリューションに革新性を示すキーワードが含まれるか（0-10点）
        innovation_keywords = ["AI", "機械学習", "自動化", "ブロックチェーン", "新規", "独自", "特許",
                              "プラットフォーム", "エコシステム", "革命", "変革"]
        solution_lower = plan.solution.lower() + plan.value_proposition.lower()
        keyword_count = sum(1 for kw in innovation_keywords if kw.lower() in solution_lower)
        score += min(10, keyword_count * 2.5)

        # 成功要因の多様性（0-15点）
        if len(plan.market_analysis.key_success_factors) >= 4:
            score += 15
        elif len(plan.market_analysis.key_success_factors) >= 3:
            score += 10
        else:
            score += 5

        # 推論プロセスの充実度（0-15点）
        reasoning_len = len(plan.reasoning)
        if reasoning_len >= 200:
            score += 15
        elif reasoning_len >= 100:
            score += 10
        elif reasoning_len >= 50:
            score += 5

        return min(100.0, max(0.0, score))

    def rank_plans(self, plans: List[BusinessPlan]) -> List[BusinessPlan]:
        """プランを総合スコアでランキング

        Args:
            plans: ビジネスプランのリスト

        Returns:
            総合スコア順にソートされたリスト
        """
        return sorted(plans, key=lambda p: p.overall_score, reverse=True)

    def filter_top_plans(self, plans: List[BusinessPlan], top_n: int = 5, min_score: float = 60.0) -> List[BusinessPlan]:
        """トッププランのみを抽出

        Args:
            plans: ビジネスプランのリスト
            top_n: 上位N件
            min_score: 最低スコア

        Returns:
            フィルタリングされたプランリスト
        """
        ranked = self.rank_plans(plans)
        filtered = [p for p in ranked if p.overall_score >= min_score]
        return filtered[:top_n]
