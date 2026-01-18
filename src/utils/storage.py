"""
ユーティリティモジュール
"""
import os
import json
import glob
from datetime import datetime
from typing import List, Optional

from ..models.business_plan import BusinessPlan


class PlanStorage:
    """ビジネスプランの保存・読み込み管理"""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.plans_dir = os.path.join(output_dir, "plans")
        self.json_dir = os.path.join(output_dir, "json")
        self.markdown_dir = os.path.join(output_dir, "markdown")

        # ディレクトリ作成
        os.makedirs(self.plans_dir, exist_ok=True)
        os.makedirs(self.json_dir, exist_ok=True)
        os.makedirs(self.markdown_dir, exist_ok=True)

    def save_plan(self, plan: BusinessPlan) -> str:
        """ビジネスプランを保存

        Args:
            plan: 保存するビジネスプラン

        Returns:
            保存先のパス
        """
        # ファイル名（スコアとタイトルを含む）
        safe_title = plan.title.replace("/", "-").replace("\\", "-")[:50]
        timestamp = plan.created_at.strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{plan.overall_score:.0f}_{safe_title}"

        # Markdown形式で保存
        md_path = os.path.join(self.markdown_dir, f"{filename}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(plan.to_markdown())

        # JSON形式で保存
        json_path = os.path.join(self.json_dir, f"{filename}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(plan.to_json(), f, ensure_ascii=False, indent=2)

        return md_path

    def load_all_plans(self) -> List[BusinessPlan]:
        """保存された全プランを読み込み

        Returns:
            ビジネスプランのリスト
        """
        plans = []
        json_files = glob.glob(os.path.join(self.json_dir, "*.json"))

        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                plan = self._dict_to_plan(data)
                plans.append(plan)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")

        # 作成日時でソート（新しい順）
        plans.sort(key=lambda p: p.created_at, reverse=True)
        return plans

    def _dict_to_plan(self, data: dict) -> BusinessPlan:
        """辞書からBusinessPlanオブジェクトを作成"""
        from ..models.business_plan import MarketAnalysis, MarketStage, FinancialProjection, PlanCategory

        # 日時をパース
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])

        # market_analysisを復元
        if "market_analysis" in data and data["market_analysis"]:
            ma = data["market_analysis"]
            if "market_stage" in ma:
                ma["market_stage"] = MarketStage(ma["market_stage"])
            data["market_analysis"] = MarketAnalysis(**ma)

        # financial_projectionを復元
        if "financial_projection" in data and data["financial_projection"]:
            data["financial_projection"] = FinancialProjection(**data["financial_projection"])

        # categoryを復元
        if "category" in data:
            if isinstance(data["category"], str):
                data["category"] = PlanCategory(data["category"])

        return BusinessPlan(**data)

    def get_latest_plans(self, n: int = 10) -> List[BusinessPlan]:
        """最新のN件のプランを取得

        Args:
            n: 取得件数

        Returns:
            ビジネスプランのリスト
        """
        all_plans = self.load_all_plans()
        return all_plans[:n]

    def get_best_plans(self, n: int = 10) -> List[BusinessPlan]:
        """スコアが高い上位N件のプランを取得

        Args:
            n: 取得件数

        Returns:
            ビジネスプランのリスト
        """
        all_plans = self.load_all_plans()
        all_plans.sort(key=lambda p: p.overall_score, reverse=True)
        return all_plans[:n]

    def generate_summary_report(self) -> str:
        """サマリーレポートを生成

        Returns:
            マークダウン形式のサマリーレポート
        """
        all_plans = self.load_all_plans()

        if not all_plans:
            return "# ビジネスプラン生成レポート\n\nプランがまだ生成されていません。"

        # カテゴリ別集計
        category_count = {}
        for plan in all_plans:
            cat = plan.category.value
            category_count[cat] = category_count.get(cat, 0) + 1

        # スコア統計
        scores = [p.overall_score for p in all_plans]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)

        # トッププラン
        top_plans = sorted(all_plans, key=lambda p: p.overall_score, reverse=True)[:5]

        md = f"""# ビジネスプラン生成サマリー

**生成日時:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**総プラン数:** {len(all_plans)}

---

## 統計情報

- **平均スコア:** {avg_score:.1f}
- **最高スコア:** {max_score:.1f}
- **最低スコア:** {min_score:.1f}

## カテゴリ別生成数

"""
        for cat, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
            md += f"- **{cat}:** {count}件\n"

        md += "\n## トップ5ビジネスプラン\n\n"

        for i, plan in enumerate(top_plans, 1):
            md += f"""### {i}. {plan.title}

- **スコア:** {plan.overall_score:.1f}
- **カテゴリ:** {plan.category.value}
- **市場規模:** ${plan.market_analysis.market_size:,.0f}億
- **5年目売上見込み:** ${plan.financial_projection.year5_revenue:,.0f}

{plan.value_proposition}

---

"""

        return md

    def save_summary_report(self) -> str:
        """サマリーレポートを保存

        Returns:
            保存先のパス
        """
        report = self.generate_summary_report()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(self.output_dir, f"summary_{timestamp}.md")

        with open(path, "w", encoding="utf-8") as f:
            f.write(report)

        return path


def setup_logging(log_dir: str = "logs") -> None:
    """ロギング設定

    Args:
        log_dir: ログ保存先ディレクトリ
    """
    os.makedirs(log_dir, exist_ok=True)

    import logging

    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"business_plan_gen_{timestamp}.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
