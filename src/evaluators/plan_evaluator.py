"""
ビジネスプラン評価器 - 生成されたプランを多角的に評価
"""
from typing import List, Optional, Dict, Tuple
import math
from dataclasses import dataclass

from ..models.business_plan import BusinessPlan


@dataclass
class EvaluationDetail:
    """評価詳細"""
    score: float
    max_score: float
    breakdown: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]


class PlanEvaluator:
    """ビジネスプランの評価器"""

    # カテゴリ別の評価重み付け
    CATEGORY_WEIGHTS = {
        "AI/ML": {"feasibility": 0.30, "profitability": 0.40, "innovation": 0.30},
        "SaaS": {"feasibility": 0.35, "profitability": 0.45, "innovation": 0.20},
        "FinTech": {"feasibility": 0.35, "profitability": 0.40, "innovation": 0.25},
        "HealthTech": {"feasibility": 0.40, "profitability": 0.35, "innovation": 0.25},
        "CleanTech": {"feasibility": 0.30, "profitability": 0.35, "innovation": 0.35},
        "Marketplace": {"feasibility": 0.40, "profitability": 0.40, "innovation": 0.20},
        "E-commerce": {"feasibility": 0.35, "profitability": 0.45, "innovation": 0.20},
        "Consumer": {"feasibility": 0.30, "profitability": 0.50, "innovation": 0.20},
        "EdTech": {"feasibility": 0.35, "profitability": 0.35, "innovation": 0.30},
        "B2B": {"feasibility": 0.35, "profitability": 0.45, "innovation": 0.20},
        "Other": {"feasibility": 0.35, "profitability": 0.45, "innovation": 0.20},
    }

    def __init__(self, benchmark_plans: Optional[List[BusinessPlan]] = None):
        """初期化

        Args:
            benchmark_plans: ベンチマークとなるプランリスト（比較評価用）
        """
        self.benchmark_plans = benchmark_plans or []
        self.evaluation_details: Optional[EvaluationDetail] = None

    def evaluate(self, plan: BusinessPlan, detailed: bool = True) -> BusinessPlan:
        """ビジネスプランを評価してスコアを設定

        Args:
            plan: 評価対象のビジネスプラン
            detailed: 詳細評価情報を生成するかどうか

        Returns:
            スコアが設定されたビジネスプラン
        """
        feasibility_breakdown: Dict[str, float] = {}
        profitability_breakdown: Dict[str, float] = {}
        innovation_breakdown: Dict[str, float] = {}

        feasibility = self._evaluate_feasibility(plan, feasibility_breakdown)
        profitability = self._evaluate_profitability(plan, profitability_breakdown)
        innovation = self._evaluate_innovation(plan, innovation_breakdown)

        plan.feasibility_score = feasibility
        plan.profitability_score = profitability
        plan.innovation_score = innovation

        # カテゴリ別の重み付けを適用
        category = plan.category.value
        weights = self.CATEGORY_WEIGHTS.get(category, self.CATEGORY_WEIGHTS["Other"])

        plan.overall_score = (
            feasibility * weights["feasibility"] +
            profitability * weights["profitability"] +
            innovation * weights["innovation"]
        )

        # 詳細評価を生成
        if detailed:
            self.evaluation_details = self._generate_evaluation_details(
                plan, feasibility_breakdown, profitability_breakdown, innovation_breakdown
            )

        return plan

    def _evaluate_feasibility(self, plan: BusinessPlan, breakdown: Dict[str, float]) -> float:
        """実現可能性を評価（0-100）

        スコアリング基準:
        - 市場成長率 (20点): 30%以上で満点
        - 市場段階 (15点): growingが最適
        - 損益分岐期間 (15点): 18ヶ月以内で満点
        - LTV/CAC比率 (20点): 5倍以上で満点
        - ROI (15点): 5倍以上で満点
        - チーム要件 (10点): 5つ以上の具体的役割
        - リスク対策 (5点): リスクと対策が対応
        """
        score = 50.0  # 基準点

        # 市場成長率による評価（0-20点）
        growth = plan.market_analysis.market_growth_rate
        if growth >= 30:
            score += 20
            breakdown["市場成長率"] = 20.0
        elif growth >= 20:
            score += 15
            breakdown["市場成長率"] = 15.0
        elif growth >= 10:
            score += 10
            breakdown["市場成長率"] = 10.0
        else:
            score += 5
            breakdown["市場成長率"] = 5.0

        # 市場段階による評価（0-15点）
        stage = plan.market_analysis.market_stage.value
        if stage == "growing":
            score += 15
            breakdown["市場段階"] = 15.0
        elif stage == "emerging":
            score += 10
            breakdown["市場段階"] = 10.0
        elif stage == "mature":
            score += 5
            breakdown["市場段階"] = 5.0
        else:
            breakdown["市場段階"] = 0.0

        # 損益分岐期間による評価（0-15点）
        break_even = plan.financial_projection.break_even_months
        if break_even <= 18:
            score += 15
            breakdown["損益分岐期間"] = 15.0
        elif break_even <= 24:
            score += 12
            breakdown["損益分岐期間"] = 12.0
        elif break_even <= 36:
            score += 8
            breakdown["損益分岐期間"] = 8.0
        else:
            score += 3
            breakdown["損益分岐期間"] = 3.0

        # LTV/CAC比率による評価（0-20点）
        if plan.financial_projection.customer_cac > 0:
            ltv_cac = plan.financial_projection.customer_ltv / plan.financial_projection.customer_cac
            if ltv_cac >= 5:
                score += 20
                breakdown["LTV/CAC比率"] = 20.0
            elif ltv_cac >= 4:
                score += 17
                breakdown["LTV/CAC比率"] = 17.0
            elif ltv_cac >= 3:
                score += 13
                breakdown["LTV/CAC比率"] = 13.0
            elif ltv_cac >= 2:
                score += 8
                breakdown["LTV/CAC比率"] = 8.0
            else:
                score += 3
                breakdown["LTV/CAC比率"] = 3.0
        else:
            breakdown["LTV/CAC比率"] = 0.0

        # 初期投資の妥当性（0-15点）
        investment = plan.financial_projection.initial_investment
        year5_revenue = plan.financial_projection.year5_revenue
        if year5_revenue > 0:
            roi = (year5_revenue - investment) / investment * 100
            if roi >= 500:
                score += 15
                breakdown["ROI"] = 15.0
            elif roi >= 300:
                score += 12
                breakdown["ROI"] = 12.0
            elif roi >= 200:
                score += 9
                breakdown["ROI"] = 9.0
            elif roi >= 100:
                score += 5
                breakdown["ROI"] = 5.0
            else:
                score += 2
                breakdown["ROI"] = 2.0
        else:
            breakdown["ROI"] = 0.0

        # チーム要件の具体性（0-10点）
        if len(plan.team_requirements) >= 5:
            score += 10
            breakdown["チーム要件"] = 10.0
        elif len(plan.team_requirements) >= 3:
            score += 7
            breakdown["チーム要件"] = 7.0
        else:
            score += 3
            breakdown["チーム要件"] = 3.0

        # リスク対策の充実度（0-5点）
        if len(plan.mitigation_strategies) >= len(plan.risk_factors):
            score += 5
            breakdown["リスク対策"] = 5.0
        else:
            score += 2
            breakdown["リスク対策"] = 2.0

        return min(100.0, max(0.0, score))

    def _evaluate_profitability(self, plan: BusinessPlan, breakdown: Dict[str, float]) -> float:
        """収益性を評価（0-100）

        スコアリング基準:
        - 5年目売上 (25点): 1億ドル以上で満点
        - 3年目利益率 (20点): 40%以上で満点
        - 成長率 (20点): 20倍以上で満点
        - 市場サイズ (20点): 500億ドル以上で満点
        - 成長ポテンシャル (15点): 市場サイズ×成長率で評価
        """
        score = 40.0  # 基準点

        # 5年目の売上規模（0-25点）
        year5 = plan.financial_projection.year5_revenue
        if year5 >= 100_000_000:  # 1億ドル以上
            score += 25
            breakdown["5年目売上"] = 25.0
        elif year5 >= 50_000_000:  # 5000万ドル以上
            score += 22
            breakdown["5年目売上"] = 22.0
        elif year5 >= 10_000_000:  # 1000万ドル以上
            score += 18
            breakdown["5年目売上"] = 18.0
        elif year5 >= 1_000_000:  # 100万ドル以上
            score += 12
            breakdown["5年目売上"] = 12.0
        else:
            score += 5
            breakdown["5年目売上"] = 5.0

        # 3年目の利益率（0-20点）
        margin = plan.financial_projection.profit_margin_year3
        if margin >= 40:
            score += 20
            breakdown["3年目利益率"] = 20.0
        elif margin >= 30:
            score += 17
            breakdown["3年目利益率"] = 17.0
        elif margin >= 20:
            score += 13
            breakdown["3年目利益率"] = 13.0
        elif margin >= 10:
            score += 8
            breakdown["3年目利益率"] = 8.0
        else:
            score += 3
            breakdown["3年目利益率"] = 3.0

        # 成長率（3年目/1年目）（0-20点）
        if plan.financial_projection.year1_revenue > 0:
            growth_ratio = plan.financial_projection.year3_revenue / plan.financial_projection.year1_revenue
            if growth_ratio >= 20:
                score += 20
                breakdown["成長率"] = 20.0
            elif growth_ratio >= 10:
                score += 17
                breakdown["成長率"] = 17.0
            elif growth_ratio >= 5:
                score += 13
                breakdown["成長率"] = 13.0
            elif growth_ratio >= 2:
                score += 8
                breakdown["成長率"] = 8.0
            else:
                score += 3
                breakdown["成長率"] = 3.0
        else:
            breakdown["成長率"] = 0.0

        # 市場サイズ（0-20点）
        market_size = plan.market_analysis.market_size
        if market_size >= 500:
            score += 20
            breakdown["市場サイズ"] = 20.0
        elif market_size >= 100:
            score += 17
            breakdown["市場サイズ"] = 17.0
        elif market_size >= 50:
            score += 13
            breakdown["市場サイズ"] = 13.0
        elif market_size >= 10:
            score += 8
            breakdown["市場サイズ"] = 8.0
        else:
            score += 3
            breakdown["市場サイズ"] = 3.0

        # 市場成長率×市場サイズの複合評価（0-15点）
        growth_potential = (market_size * plan.market_analysis.market_growth_rate) / 100
        if growth_potential >= 50:
            score += 15
            breakdown["成長ポテンシャル"] = 15.0
        elif growth_potential >= 20:
            score += 12
            breakdown["成長ポテンシャル"] = 12.0
        elif growth_potential >= 10:
            score += 8
            breakdown["成長ポテンシャル"] = 8.0
        else:
            score += 3
            breakdown["成長ポテンシャル"] = 3.0

        return min(100.0, max(0.0, score))

    def _evaluate_innovation(self, plan: BusinessPlan, breakdown: Dict[str, float]) -> float:
        """革新性を評価（0-100）

        スコアリング基準:
        - カテゴリ (20点): AI/ML等で高評価
        - 市場段階 (20点): emergingで高評価
        - 問題提起 (20点): 具体的な説明
        - 革新キーワード (10点): AI等のキーワード
        - 成功要因 (15点): 4つ以上
        - 推論プロセス (15点): 詳細な説明
        """
        score = 50.0  # 基準点

        # カテゴリによる評価（0-20点）
        category = plan.category.value
        high_innovation = ["AI/ML", "CleanTech", "FinTech", "HealthTech"]
        if category in high_innovation:
            score += 20
            breakdown["カテゴリ"] = 20.0
        else:
            score += 10
            breakdown["カテゴリ"] = 10.0

        # 市場段階（0-20点）
        stage = plan.market_analysis.market_stage.value
        if stage == "emerging":
            score += 20
            breakdown["市場段階"] = 20.0
        elif stage == "growing":
            score += 15
            breakdown["市場段階"] = 15.0
        elif stage == "mature":
            score += 5
            breakdown["市場段階"] = 5.0
        else:
            breakdown["市場段階"] = 0.0

        # 問題提起の具体性（0-20点）
        problem_len = len(plan.problem_statement)
        if problem_len >= 200:
            score += 15
            breakdown["問題提起"] = 15.0
        elif problem_len >= 100:
            score += 10
            breakdown["問題提起"] = 10.0
        else:
            score += 5
            breakdown["問題提起"] = 5.0

        # ソリューションに革新性を示すキーワードが含まれるか（0-10点）
        innovation_keywords = ["AI", "機械学習", "自動化", "ブロックチェーン", "新規", "独自", "特許",
                              "プラットフォーム", "エコシステム", "革命", "変革"]
        solution_lower = plan.solution.lower() + plan.value_proposition.lower()
        keyword_count = sum(1 for kw in innovation_keywords if kw.lower() in solution_lower)
        points = min(10, keyword_count * 2.5)
        score += points
        breakdown["革新キーワード"] = points

        # 成功要因の多様性（0-15点）
        if len(plan.market_analysis.key_success_factors) >= 4:
            score += 15
            breakdown["成功要因"] = 15.0
        elif len(plan.market_analysis.key_success_factors) >= 3:
            score += 10
            breakdown["成功要因"] = 10.0
        else:
            score += 5
            breakdown["成功要因"] = 5.0

        # 推論プロセスの充実度（0-15点）
        reasoning_len = len(plan.reasoning)
        if reasoning_len >= 200:
            score += 15
            breakdown["推論プロセス"] = 15.0
        elif reasoning_len >= 100:
            score += 10
            breakdown["推論プロセス"] = 10.0
        elif reasoning_len >= 50:
            score += 5
            breakdown["推論プロセス"] = 5.0
        else:
            breakdown["推論プロセス"] = 0.0

        return min(100.0, max(0.0, score))

    def _generate_evaluation_details(
        self,
        plan: BusinessPlan,
        feasibility_breakdown: Dict[str, float],
        profitability_breakdown: Dict[str, float],
        innovation_breakdown: Dict[str, float]
    ) -> EvaluationDetail:
        """評価詳細を生成

        Args:
            plan: ビジネスプラン
            feasibility_breakdown: 実現可能性の内訳
            profitability_breakdown: 収益性の内訳
            innovation_breakdown: 革新性の内訳

        Returns:
            評価詳細
        """
        strengths = []
        weaknesses = []
        recommendations = []

        # 実現可能性の分析
        if plan.feasibility_score >= 80:
            strengths.append("実現可能性が非常に高い（市場条件と財務指標が優秀）")
        elif plan.feasibility_score < 60:
            weaknesses.append("実現可能性に課題あり（市場または財務指標の改善が必要）")

        # LTV/CAC分析
        if plan.financial_projection.customer_cac > 0:
            ltv_cac = plan.financial_projection.customer_ltv / plan.financial_projection.customer_cac
            if ltv_cac >= 5:
                strengths.append(f"優秀なLTV/CAC比率（{ltv_cac:.1f}倍）")
            elif ltv_cac < 3:
                weaknesses.append(f"LTV/CAC比率が低い（{ltv_cac:.1f}倍）")
                recommendations.append("顧客生涯価値の向上またはCACの削減を検討")

        # 収益性の分析
        if plan.profitability_score >= 80:
            strengths.append("収益性の見込みが非常に高い")
        elif plan.profitability_score < 60:
            weaknesses.append("収益性に課題あり")
            recommendations.append("市場規模または成長戦略の再検討を推奨")

        # 革新性の分析
        if plan.innovation_score >= 80:
            strengths.append("高い革新性と市場差別化")
        elif plan.innovation_score < 60:
            weaknesses.append("革新性が不足")
            recommendations.append("独自の技術またはビジネスモデルの強化を推奨")

        # 市場段階の分析
        stage = plan.market_analysis.market_stage.value
        if stage == "emerging":
            recommendations.append("新興市場のため早期参入の優位性あり but リスクも考慮必要")
        elif stage == "declining":
            weaknesses.append("衰退市場でのビジネス")

        return EvaluationDetail(
            score=plan.overall_score,
            max_score=100.0,
            breakdown={
                "実現可能性": feasibility_breakdown,
                "収益性": profitability_breakdown,
                "革新性": innovation_breakdown
            },
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations
        )

    def compare_with_benchmark(self, plan: BusinessPlan) -> Optional[Dict[str, float]]:
        """ベンチマークと比較評価

        Args:
            plan: 評価対象のビジネスプラン

        Returns:
            比較結果（ベンチマークがある場合）
        """
        if not self.benchmark_plans:
            return None

        avg_feasibility = sum(p.feasibility_score for p in self.benchmark_plans) / len(self.benchmark_plans)
        avg_profitability = sum(p.profitability_score for p in self.benchmark_plans) / len(self.benchmark_plans)
        avg_innovation = sum(p.innovation_score for p in self.benchmark_plans) / len(self.benchmark_plans)
        avg_overall = sum(p.overall_score for p in self.benchmark_plans) / len(self.benchmark_plans)

        return {
            "feasibility_diff": plan.feasibility_score - avg_feasibility,
            "profitability_diff": plan.profitability_score - avg_profitability,
            "innovation_diff": plan.innovation_score - avg_innovation,
            "overall_diff": plan.overall_score - avg_overall,
            "percentile": self._calculate_percentile(plan.overall_score, [p.overall_score for p in self.benchmark_plans])
        }

    def _calculate_percentile(self, score: float, benchmark_scores: List[float]) -> float:
        """パーセンタイルを計算

        Args:
            score: 対象スコア
            benchmark_scores: ベンチマークスコアリスト

        Returns:
            パーセンタイル（0-100）
        """
        rank = sum(1 for s in benchmark_scores if s < score)
        return (rank / len(benchmark_scores)) * 100 if benchmark_scores else 0

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

    def generate_evaluation_report(self, plan: BusinessPlan) -> str:
        """評価レポートを生成（Markdown形式）

        Args:
            plan: ビジネスプラン

        Returns:
            Markdown形式の評価レポート
        """
        if not self.evaluation_details:
            self.evaluate(plan)

        details = self.evaluation_details
        comparison = self.compare_with_benchmark(plan)

        md = f"""# ビジネスプラン評価レポート

## {plan.title}

**カテゴリ:** {plan.category.value} | **総合スコア:** {plan.overall_score:.1f}/100

---

## 総合評価

- **実現可能性:** {plan.feasibility_score:.1f}/100
- **収益性:** {plan.profitability_score:.1f}/100
- **革新性:** {plan.innovation_score:.1f}/100

"""

        if details:
            md += """## 強み

"""
            for strength in details.strengths:
                md += f"- ✅ {strength}\n"

            if details.weaknesses:
                md += """
## 課題

"""
                for weakness in details.weaknesses:
                    md += f"- ⚠️ {weakness}\n"

            if details.recommendations:
                md += """
## 推奨事項

"""
                for rec in details.recommendations:
                    md += f"- 💡 {rec}\n"

        if comparison:
            md += f"""
## ベンチマーク比較

- 実現可能性: {comparison['feasibility_diff']:+.1f}ポイント
- 収益性: {comparison['profitability_diff']:+.1f}ポイント
- 革新性: {comparison['innovation_diff']:+.1f}ポイント
- 総合: {comparison['overall_diff']:+.1f}ポイント
- パーセンタイル: {comparison['percentile']:.1f}%
"""

        return md
