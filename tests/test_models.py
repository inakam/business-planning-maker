"""
データモデルのユニットテスト
"""
import pytest
from datetime import datetime

from src.models.business_plan import (
    BusinessPlan, PlanCategory, MarketAnalysis, MarketStage,
    FinancialProjection
)


class TestMarketAnalysis:
    """市場分析モデルのテスト"""

    def test_market_analysis_creation(self):
        """市場分析の作成"""
        analysis = MarketAnalysis(
            market_size=100.0,
            market_growth_rate=20.0,
            target_audience="中小企業",
            market_stage=MarketStage.GROWING,
            competitive_landscape="競合あり",
            key_success_factors=["技術", "ブランド"]
        )

        assert analysis.market_size == 100.0
        assert analysis.market_growth_rate == 20.0
        assert analysis.target_audience == "中小企業"
        assert analysis.market_stage == MarketStage.GROWING
        assert len(analysis.key_success_factors) == 2

    def test_market_stage_enum(self):
        """市場段階Enumのテスト"""
        assert MarketStage.EMERGING.value == "emerging"
        assert MarketStage.GROWING.value == "growing"
        assert MarketStage.MATURE.value == "mature"
        assert MarketStage.DECLINING.value == "declining"


class TestFinancialProjection:
    """財務予測モデルのテスト"""

    def test_financial_projection_creation(self):
        """財務予測の作成"""
        projection = FinancialProjection(
            year1_revenue=100_000,
            year3_revenue=1_000_000,
            year5_revenue=10_000_000,
            initial_investment=500_000,
            break_even_months=18,
            profit_margin_year3=25.0,
            customer_cac=500,
            customer_ltv=1500
        )

        assert projection.year1_revenue == 100_000
        assert projection.year3_revenue == 1_000_000
        assert projection.year5_revenue == 10_000_000
        assert projection.break_even_months == 18
        assert projection.profit_margin_year3 == 25.0

    def test_ltv_cac_ratio(self):
        """LTV/CAC比率の計算"""
        projection = FinancialProjection(
            year1_revenue=100_000,
            year3_revenue=1_000_000,
            year5_revenue=10_000_000,
            initial_investment=500_000,
            break_even_months=18,
            profit_margin_year3=25.0,
            customer_cac=500,
            customer_ltv=1500
        )

        ratio = projection.customer_ltv / projection.customer_cac
        assert ratio == 3.0


class TestBusinessPlan:
    """ビジネスプランモデルのテスト"""

    def test_business_plan_creation(self, sample_market_analysis, sample_financial_projection):
        """ビジネスプランの作成"""
        plan = BusinessPlan(
            id="test-1",
            title="テストプラン",
            category=PlanCategory.SAAS,
            iteration=1,
            problem_statement="問題",
            solution="ソリューション",
            value_proposition="価値",
            business_model="モデル",
            market_analysis=sample_market_analysis,
            financial_projection=sample_financial_projection,
            key_milestones=["マイルストーン1"],
            team_requirements=["CEO"],
            risk_factors=["リスク"],
            mitigation_strategies=["対策"],
            reasoning="推論",
            tags=["tag1"]
        )

        assert plan.id == "test-1"
        assert plan.title == "テストプラン"
        assert plan.category == PlanCategory.SAAS
        assert plan.iteration == 1

    def test_business_plan_scores_initialized(self, sample_market_analysis, sample_financial_projection):
        """スコアの初期化"""
        plan = BusinessPlan(
            id="test-2",
            title="テストプラン2",
            category=PlanCategory.AI_ML,
            market_analysis=sample_market_analysis,
            financial_projection=sample_financial_projection
        )

        # スコアは初期値0
        assert plan.feasibility_score == 0.0
        assert plan.profitability_score == 0.0
        assert plan.innovation_score == 0.0
        assert plan.overall_score == 0.0

    def test_to_markdown(self, sample_market_analysis, sample_financial_projection):
        """Markdown出力のテスト"""
        plan = BusinessPlan(
            id="test-3",
            title="マークダウンテスト",
            category=PlanCategory.FINTECH,
            market_analysis=sample_market_analysis,
            financial_projection=sample_financial_projection,
            key_milestones=["マイルストーン"],
            team_requirements=["CEO"],
            risk_factors=["リスク"],
            mitigation_strategies=["対策"],
            reasoning="推論",
            tags=["test"]
        )

        md = plan.to_markdown()

        assert "# マークダウンテスト" in md
        assert plan.category.value in md
        assert "## 評価スコア" in md
        assert "## 市場分析" in md
        assert "## 財務予測" in md
        assert "## 実行計画" in md

    def test_to_json(self, sample_market_analysis, sample_financial_projection):
        """JSON出力のテスト"""
        plan = BusinessPlan(
            id="test-4",
            title="JSONテスト",
            category=PlanCategory.HEALTHTECH,
            created_at=datetime(2026, 1, 18, 12, 0, 0),
            market_analysis=sample_market_analysis,
            financial_projection=sample_financial_projection
        )

        data = plan.to_json()

        assert data["id"] == "test-4"
        assert data["title"] == "JSONテスト"
        assert data["category"] == "HealthTech"
        assert data["created_at"] == "2026-01-18T12:00:00"
        assert "market_analysis" in data
        assert "financial_projection" in data


class TestPlanCategory:
    """プランカテゴリーEnumのテスト"""

    def test_all_categories_exist(self):
        """全カテゴリーが定義されているか"""
        expected_categories = {
            "SaaS", "Marketplace", "AI/ML", "FinTech", "HealthTech",
            "EdTech", "CleanTech", "E-commerce", "Consumer", "B2B", "Other"
        }

        actual_categories = {cat.value for cat in PlanCategory}

        assert actual_categories == expected_categories

    def test_category_values(self):
        """カテゴリー値の確認"""
        assert PlanCategory.SAAS.value == "SaaS"
        assert PlanCategory.AI_ML.value == "AI/ML"
        assert PlanCategory.FINTECH.value == "FinTech"
        assert PlanCategory.MARKETPLACE.value == "Marketplace"
