"""
評価器のユニットテスト
"""
import pytest

from src.evaluators import PlanEvaluator
from src.models.business_plan import (
    BusinessPlan, PlanCategory, MarketAnalysis, MarketStage,
    FinancialProjection
)


class TestPlanEvaluator:
    """プラン評価器のテスト"""

    @pytest.fixture
    def high_score_plan(self):
        """高スコアのビジネスプラン"""
        return BusinessPlan(
            id="high-score",
            title="高スコアプラン",
            category=PlanCategory.AI_ML,
            market_analysis=MarketAnalysis(
                market_size=500.0,
                market_growth_rate=35.0,
                target_audience="大企業",
                market_stage=MarketStage.GROWING,
                competitive_landscape="競合少ない",
                key_success_factors=["技術", "ブランド", "チーム", "資金", "タイミング"]
            ),
            financial_projection=FinancialProjection(
                year1_revenue=1_000_000,
                year3_revenue=50_000_000,
                year5_revenue=200_000_000,
                initial_investment=2_000_000,
                break_even_months=18,
                profit_margin_year3=40.0,
                customer_cac=1000,
                customer_ltv=5000
            ),
            problem_statement="深刻な問題が存在し、緊急性が高い。多くの企業が生産性向上を求めている。",
            solution="革新的なAIソリューションを提供。特許技術を使用。",
            value_proposition="コストを80%削減、効率を5倍向上。独自のAI技術。",
            key_milestones=["MVP", "顧客獲得", "シリーズA", "黒字化"],
            team_requirements=["CEO", "CTO", "AIエンジニア", "セールス", "CS"],
            risk_factors=["技術リスク", "市場リスク", "競合リスク"],
            mitigation_strategies=["技術的優位性", "早期参入", "継続的革新"],
            reasoning="市場規模が大きく、成長率が高い。独自技術で差別化可能。",
            tags=["ai", "機械学習", "革新"]
        )

    @pytest.fixture
    def low_score_plan(self):
        """低スコアのビジネスプラン"""
        return BusinessPlan(
            id="low-score",
            title="低スコアプラン",
            category=PlanCategory.SAAS,
            market_analysis=MarketAnalysis(
                market_size=1.0,  # 小さい市場
                market_growth_rate=2.0,  # 低成長
                target_audience="ニッチ市場",
                market_stage=MarketStage.DECLINING,  # 衰退市場
                competitive_landscape="激しい競争",
                key_success_factors=["価格"]
            ),
            financial_projection=FinancialProjection(
                year1_revenue=10_000,
                year3_revenue=15_000,
                year5_revenue=20_000,
                initial_investment=1_000_000,
                break_even_months=84,  # 7年以上
                profit_margin_year3=5.0,  # 低利益率
                customer_cac=10000,
                customer_ltv=8000  # LTV < CAC
            ),
            problem_statement="小",
            solution="普通",
            value_proposition="少",
            key_milestones=["x"],
            team_requirements=["創業者"],
            risk_factors=["競合"],
            mitigation_strategies=["頑張る"],
            reasoning="市場が小さい",
            tags=["saas"]
        )

    def test_evaluate_sets_scores(self, high_score_plan):
        """評価でスコアが設定される"""
        evaluator = PlanEvaluator()
        evaluated = evaluator.evaluate(high_score_plan)

        assert evaluated.feasibility_score > 0
        assert evaluated.profitability_score > 0
        assert evaluated.innovation_score > 0
        assert evaluated.overall_score > 0

    def test_high_score_plan_gets_high_score(self, high_score_plan):
        """高スコアプランは高く評価される"""
        evaluator = PlanEvaluator()
        evaluated = evaluator.evaluate(high_score_plan)

        assert evaluated.overall_score >= 70.0
        assert evaluated.feasibility_score >= 70.0
        assert evaluated.profitability_score >= 70.0
        assert evaluated.innovation_score >= 70.0

    def test_low_score_plan_gets_lower_score(self, low_score_plan):
        """低スコアプランは低く評価される"""
        evaluator = PlanEvaluator()
        evaluated = evaluator.evaluate(low_score_plan)

        assert evaluated.overall_score < 70.0

    def test_category_weights(self):
        """カテゴリ別重み付けの確認"""
        weights = PlanEvaluator.CATEGORY_WEIGHTS

        # 各カテゴリーの重み合計が1.0であること
        for category, weight_dict in weights.items():
            total = sum(weight_dict.values())
            assert abs(total - 1.0) < 0.001, f"{category} weights sum to {total}, expected 1.0"

    def test_evaluate_feasibility_breakdown(self, high_score_plan):
        """実現可能性評価の内訳確認"""
        evaluator = PlanEvaluator()
        evaluator.evaluate(high_score_plan)

        details = evaluator.evaluation_details
        assert details is not None
        assert "実現可能性" in details.breakdown

        # 主要な評価項目が含まれている
        breakdown = details.breakdown["実現可能性"]
        expected_keys = ["市場成長率", "市場段階", "損益分岐期間", "LTV/CAC比率"]
        for key in expected_keys:
            assert key in breakdown

    def test_evaluation_details_has_strengths(self, high_score_plan):
        """評価詳細に強みが含まれる"""
        evaluator = PlanEvaluator()
        evaluator.evaluate(high_score_plan)

        details = evaluator.evaluation_details
        assert details is not None
        assert len(details.strengths) > 0

    def test_rank_plans(self, high_score_plan, low_score_plan):
        """プランのランキング"""
        evaluator = PlanEvaluator()
        plan1 = evaluator.evaluate(high_score_plan)
        plan2 = evaluator.evaluate(low_score_plan)

        ranked = evaluator.rank_plans([plan1, plan2])

        assert ranked[0].overall_score >= ranked[1].overall_score

    def test_filter_top_plans(self, high_score_plan, low_score_plan):
        """トッププランのフィルタリング"""
        evaluator = PlanEvaluator()
        plans = [evaluator.evaluate(high_score_plan), evaluator.evaluate(low_score_plan)]

        top = evaluator.filter_top_plans(plans, top_n=1, min_score=50.0)

        assert len(top) <= 1
        if len(top) > 0:
            assert top[0].overall_score >= 50.0

    def test_benchmark_comparison(self, high_score_plan):
        """ベンチマーク比較"""
        evaluator = PlanEvaluator(benchmark_plans=[high_score_plan])

        comparison = evaluator.compare_with_benchmark(high_score_plan)

        assert comparison is not None
        assert "feasibility_diff" in comparison
        assert "profitability_diff" in comparison
        assert "innovation_diff" in comparison
        assert "overall_diff" in comparison
        assert "percentile" in comparison

    def test_percentile_calculation(self):
        """パーセンタイル計算のテスト"""
        evaluator = PlanEvaluator()

        # 10個のプランでテスト
        scores = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

        # 80点の場合、7個が下回る -> 70パーセンタイル
        percentile = evaluator._calculate_percentile(80, scores)
        assert percentile == 70.0

        # 100点の場合、9個が下回る -> 90パーセンタイル
        percentile = evaluator._calculate_percentile(100, scores)
        assert percentile == 90.0

        # 10点の場合、0個が下回る -> 0パーセンタイル
        percentile = evaluator._calculate_percentile(10, scores)
        assert percentile == 0.0

    def test_generate_evaluation_report(self, high_score_plan):
        """評価レポートの生成"""
        evaluator = PlanEvaluator()
        evaluator.evaluate(high_score_plan)

        report = evaluator.generate_evaluation_report(high_score_plan)

        assert "## " in report  # Markdown headers
        assert high_score_plan.title in report
        assert "実現可能性" in report
        assert "収益性" in report
        assert "革新性" in report
