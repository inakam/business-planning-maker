"""
テスト用共通フィクスチャー
"""
import sys
from pathlib import Path
import pytest
import tempfile
import shutil
from datetime import datetime

# srcをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.business_plan import (
    BusinessPlan, PlanCategory, MarketAnalysis, MarketStage,
    FinancialProjection
)
from src.evaluators import PlanEvaluator
from src.generators import BusinessPlanGenerator
from src.utils import PlanStorage


@pytest.fixture
def temp_output_dir():
    """一時的な出力ディレクトリ"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_market_analysis():
    """サンプル市場分析データ"""
    return MarketAnalysis(
        market_size=100.0,
        market_growth_rate=20.0,
        target_audience="中小企業",
        market_stage=MarketStage.GROWING,
        competitive_landscape="競合が存在するが差別化可能",
        key_success_factors=["技術優位性", "顧客基盤", "ブランド力"]
    )


@pytest.fixture
def sample_financial_projection():
    """サンプル財務予測データ"""
    return FinancialProjection(
        year1_revenue=500_000,
        year3_revenue=5_000_000,
        year5_revenue=20_000_000,
        initial_investment=1_000_000,
        break_even_months=24,
        profit_margin_year3=30.0,
        customer_cac=1000,
        customer_ltv=3000
    )


@pytest.fixture
def sample_business_plan(sample_market_analysis, sample_financial_projection):
    """サンプルビジネスプラン"""
    return BusinessPlan(
        id="test-plan-1",
        title="テストビジネスプラン",
        category=PlanCategory.SAAS,
        iteration=1,
        problem_statement="テスト問題提起",
        solution="テストソリューション",
        value_proposition="テスト価値提案",
        business_model="サブスクリプションモデル",
        market_analysis=sample_market_analysis,
        financial_projection=sample_financial_projection,
        key_milestones=["MVP開発", "初期顧客獲得"],
        team_requirements=["CEO", "CTO"],
        risk_factors=["技術リスク"],
        mitigation_strategies=["段階的開発"],
        reasoning="テスト推論",
        tags=["test", "saas"]
    )


@pytest.fixture
def storage(temp_output_dir):
    """テスト用ストレージ"""
    return PlanStorage(output_dir=temp_output_dir)


@pytest.fixture
def evaluator():
    """テスト用評価器"""
    return PlanEvaluator()


@pytest.fixture
def generator():
    """テスト用生成器"""
    return BusinessPlanGenerator(iteration=1)
