"""
統合テスト - エンドツーエンドのテスト
"""
import pytest
import json
import tempfile
import shutil
from pathlib import Path

from src.generators import BusinessPlanGenerator
from src.evaluators import PlanEvaluator
from src.utils import PlanStorage
from src.models.business_plan import PlanCategory


class TestEndToEnd:
    """エンドツーエンドの統合テスト"""

    def test_full_generation_workflow(self):
        """完全な生成ワークフローのテスト"""
        # 1. プラン生成
        generator = BusinessPlanGenerator(iteration=1)
        plan = generator.generate(previous_plans=None)

        # 2. プラン評価
        evaluator = PlanEvaluator()
        plan = evaluator.evaluate(plan)

        # 3. 検証
        assert plan.id is not None
        assert len(plan.title) > 0
        assert plan.overall_score > 0
        assert plan.feasibility_score > 0
        assert plan.profitability_score > 0
        assert plan.innovation_score > 0

    def test_storage_workflow(self):
        """ストレージワークフローのテスト"""
        temp_dir = tempfile.mkdtemp()

        try:
            storage = PlanStorage(output_dir=temp_dir)

            # プラン生成と保存
            generator = BusinessPlanGenerator(iteration=1)
            plan = generator.generate(previous_plans=None)
            evaluator = PlanEvaluator()
            plan = evaluator.evaluate(plan)

            # 保存
            path = storage.save_plan(plan)

            # 検証
            assert Path(path).exists()

            # 読み込み
            loaded_plans = storage.load_all_plans()
            assert len(loaded_plans) == 1
            assert loaded_plans[0].id == plan.id

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_multiple_generation_cycle(self):
        """複数回の生成サイクルのテスト"""
        temp_dir = tempfile.mkdtemp()

        try:
            storage = PlanStorage(output_dir=temp_dir)
            generator = BusinessPlanGenerator(iteration=1)
            evaluator = PlanEvaluator()

            previous_plans = []

            # 3つのプランを生成
            for i in range(3):
                plan = generator.generate(previous_plans=previous_plans)
                plan = evaluator.evaluate(plan)
                storage.save_plan(plan)
                previous_plans.append(plan)

            # 検証
            loaded_plans = storage.load_all_plans()
            assert len(loaded_plans) == 3

            # 全て異なるタイトルであるべき（重複回避）
            titles = [p.title for p in loaded_plans]
            assert len(set(titles)) == len(titles), "Generated plans should have unique titles"

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_summary_report_generation(self):
        """サマリーレポート生成のテスト"""
        temp_dir = tempfile.mkdtemp()

        try:
            storage = PlanStorage(output_dir=temp_dir)
            generator = BusinessPlanGenerator(iteration=1)
            evaluator = PlanEvaluator()

            # プラン生成
            for _ in range(2):
                plan = generator.generate(previous_plans=None)
                plan = evaluator.evaluate(plan)
                storage.save_plan(plan)

            # サマリー生成
            summary_path = storage.save_summary_report()

            # 検証
            assert Path(summary_path).exists()

            content = Path(summary_path).read_text(encoding="utf-8")
            assert "ビジネスプラン生成サマリー" in content
            assert "総プラン数" in content

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_category_coverage(self):
        """全カテゴリーのカバレッジ確認"""
        generator = BusinessPlanGenerator(iteration=1)

        # 全カテゴリーがTRENDSに含まれている
        expected_categories = {
            "AI_ML", "FINTECH", "HEALTHTECH", "SAAS", "CLEANTECH",
            "MARKETPLACE", "EDTECH", "ECOMMERCE", "CONSUMER", "B2B"
        }

        actual_categories = set(generator.TRENDS.keys())

        assert actual_categories == expected_categories

    def test_theme_diversity(self):
        """テーマの多様性テスト"""
        generator = BusinessPlanGenerator(iteration=1)

        total_themes = sum(len(themes) for themes in generator.TRENDS.values())

        # 100テーマ以上あるはず（10カテゴリー × 10テーマ）
        assert total_themes >= 100

    def test_business_model_coverage(self):
        """ビジネスモデルのカバレッジ"""
        generator = BusinessPlanGenerator(iteration=1)

        expected_models = [
            "サブスクリプションモデル",
            "フリーミアムモデル",
            "トランザクション手数料モデル",
            "マーケットプレイスモデル",
            "エンタープライズライセンスモデル",
            "利用量ベース課金モデル",
            "ハイブリッドモデル"
        ]

        assert generator.BUSINESS_MODELS == expected_models

    def test_target_market_coverage(self):
        """ターゲット市場のカバレッジ"""
        generator = BusinessPlanGenerator(iteration=1)

        expected_markets = [
            "中小企業（従業員10-100人）",
            "大企業（従業員1000人以上）",
            "スタートアップ/VC投資企業",
            "フリーランス/個人事業主",
            "特定業種垂直市場",
            "消費者一般（B2C）"
        ]

        assert generator.TARGET_MARKETS == expected_markets


class TestAnalytics:
    """分析機能の統合テスト"""

    def test_analytics_with_multiple_plans(self):
        """複数プランでの分析機能テスト"""
        from src.utils import PlanAnalytics

        temp_dir = tempfile.mkdtemp()

        try:
            storage = PlanStorage(output_dir=temp_dir)
            generator = BusinessPlanGenerator(iteration=1)
            evaluator = PlanEvaluator()

            # 5つのプランを生成
            plans = []
            for _ in range(5):
                plan = generator.generate(previous_plans=plans)
                plan = evaluator.evaluate(plan)
                storage.save_plan(plan)
                plans.append(plan)

            # 統計分析
            stats = PlanAnalytics.calculate_statistics(plans)
            assert stats is not None
            assert "総合スコア" in stats
            assert "平均" in stats["総合スコア"]

            # カテゴリ分布
            category_dist = PlanAnalytics.analyze_category_distribution(plans)
            assert len(category_dist) > 0

            # 市場トレンド
            trends = PlanAnalytics.analyze_market_trends(plans)
            assert "平均市場規模（億ドル）" in trends

            # インサイト
            insights = PlanAnalytics.generate_insights(plans)
            assert len(insights) > 0

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_comparison_report(self):
        """プラン比較レポートのテスト"""
        from src.utils import PlanAnalytics

        temp_dir = tempfile.mkdtemp()

        try:
            storage = PlanStorage(output_dir=temp_dir)
            generator = BusinessPlanGenerator(iteration=1)
            evaluator = PlanEvaluator()

            # 2つのプランを生成
            plan1 = generator.generate(previous_plans=None)
            plan1 = evaluator.evaluate(plan1)

            plan2 = generator.generate(previous_plans=[plan1])
            plan2 = evaluator.evaluate(plan2)

            # 比較レポート生成
            report = PlanAnalytics.generate_comparison_report(plan1, plan2)

            # 検証
            assert "## プラン概要" in report
            assert plan1.title in report
            assert plan2.title in report
            assert "## 評価スコア比較" in report

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestDuplicateAvoidance:
    """重複回避機能のテスト"""

    def test_similarity_calculation(self):
        """類似度計算のテスト"""
        generator = BusinessPlanGenerator()

        # 全く同じテキスト
        similarity = generator._calculate_similarity("同じテキスト", "同じテキスト")
        assert similarity == 1.0

        # 全く異なるテキスト
        similarity = generator._calculate_similarity("aaa", "bbb")
        assert similarity < 0.5

        # 似ているが異なる
        similarity = generator._calculate_similarity("ビジネスプラン", "ビジネスプラン2")
        assert 0.7 < similarity < 0.95

    def test_duplicate_detection(self):
        """重複検出のテスト"""
        generator = BusinessPlanGenerator(iteration=1)

        # 既存プランなし
        assert not generator._is_duplicate("新規プラン", ["new"], [])

        # 既存プランあり（重複）
        existing_plan = type('obj', (object,), {
            'title': "AIビジネスプラン",
            'tags': ["ai", "ml"]
        })()
        assert generator._is_duplicate("AIビジネスプラン", ["ai"], [existing_plan])

    def test_theme_selection_with_duplicates(self):
        """重複を回避したテーマ選択"""
        from src.models.business_plan import BusinessPlan, MarketAnalysis, MarketStage, FinancialProjection

        generator = BusinessPlanGenerator(iteration=1)

        # 類似の既存プランを作成
        existing_plan = type('obj', (object,), {
            'title': "AIデータプライバシーコンプライアンス",
            'tags': ["ai", "データプライバシー"],
            'solution': "AIデータプライバシーコンプライアンスのソリューション"
        })()

        # 重複回避を考慮したテーマ選択
        category, theme, model, market = generator._select_theme(previous_plans=[existing_plan])

        # 結果を確認
        assert category in generator.TRENDS
        assert theme in generator.TRENDS[category]
        assert len(theme) > 0
