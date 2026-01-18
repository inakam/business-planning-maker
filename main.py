#!/usr/bin/env python3
"""
Business Planning Maker - メイン実行スクリプト

Agentic AIとしてビジネスプランを無限に生成し続けるシステム
"""
import argparse
import logging
import sys
import time
from pathlib import Path

# srcをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.generators import BusinessPlanGenerator
from src.evaluators import PlanEvaluator
from src.utils import PlanStorage, setup_logging


def generate_single_plan(iteration: int, previous_plans=None, storage=None) -> bool:
    """単一のビジネスプランを生成

    Args:
        iteration: 現在のイテレーション数
        previous_plans: 以前のプランリスト
        storage: 保存先ストレージ

    Returns:
        成功した場合はTrue
    """
    logger = logging.getLogger(__name__)
    logger.info(f"=== イテレーション {iteration} ===")

    try:
        # 生成器の初期化
        generator = BusinessPlanGenerator(iteration=iteration)

        # ビジネスプラン生成
        logger.info("ビジネスプランを生成中...")
        plan = generator.generate(previous_plans=previous_plans)
        logger.info(f"生成完了: {plan.title}")

        # 評価
        logger.info("プランを評価中...")
        evaluator = PlanEvaluator()
        plan = evaluator.evaluate(plan)
        logger.info(f"評価完了 - 総合スコア: {plan.overall_score:.1f}")

        # 保存
        logger.info("プランを保存中...")
        if storage is None:
            storage = PlanStorage()
        path = storage.save_plan(plan)
        logger.info(f"保存完了: {path}")

        # 結果表示
        print(f"\n{'='*60}")
        print(f"✅ ビジネスプラン #{iteration} 生成完了")
        print(f"{'='*60}")
        print(f"タイトル: {plan.title}")
        print(f"カテゴリ: {plan.category.value}")
        print(f"スコア: {plan.overall_score:.1f} (実現可能性: {plan.feasibility_score:.1f}, "
              f"収益性: {plan.profitability_score:.1f}, 革新性: {plan.innovation_score:.1f})")
        print(f"市場規模: ${plan.market_analysis.market_size:,.0f}億")
        print(f"5年目売上: ${plan.financial_projection.year5_revenue:,.0f}")
        print(f"{'='*60}\n")

        return True

    except Exception as e:
        logger.error(f"エラーが発生しました: {e}", exc_info=True)
        print(f"❌ エラー: {e}")
        return False


def generate_batch_plans(count: int, iteration_start: int = 1) -> None:
    """バッチでビジネスプランを生成

    Args:
        count: 生成数
        iteration_start: 開始イテレーション番号
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    storage = PlanStorage()

    # 以前のプランを読み込み
    previous_plans = storage.load_all_plans()
    logger.info(f"既存のプラン数: {len(previous_plans)}")

    for i in range(count):
        iteration = iteration_start + i
        success = generate_single_plan(iteration, previous_plans, storage)

        if success:
            # 最新のプランリストを更新
            previous_plans = storage.load_all_plans()
        else:
            logger.warning(f"イテレーション {iteration} が失敗しました。次に進みます。")

        # 次の生成前に少し待機（APIレート制限対策）
        if i < count - 1:
            time.sleep(2)

    # サマリーレポート生成
    logger.info("サマリーレポートを生成中...")
    summary_path = storage.save_summary_report()
    logger.info(f"サマリー保存: {summary_path}")
    print(f"\n📊 サマリーレポート: {summary_path}")


def generate_continuous(interval_minutes: int = 5, max_iterations: int = 0) -> None:
    """継続的にビジネスプランを生成（無限モード）

    Args:
        interval_minutes: 生成間隔（分）
        max_iterations: 最大イテレーション数（0で無限）
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    storage = PlanStorage()

    iteration = 1
    previous_plans = storage.load_all_plans()
    logger.info(f"既存のプラン数: {len(previous_plans)}")
    logger.info(f"無限生成モード開始（間隔: {interval_minutes}分）")

    try:
        while True:
            if max_iterations > 0 and iteration > max_iterations:
                logger.info(f"最大イテレーション数 {max_iterations} に到達")
                break

            success = generate_single_plan(iteration, previous_plans, storage)

            if success:
                previous_plans = storage.load_all_plans()

                # 10回ごとにサマリー更新
                if iteration % 10 == 0:
                    summary_path = storage.save_summary_report()
                    logger.info(f"サマリー更新: {summary_path}")

                iteration += 1
            else:
                logger.warning("生成失敗。1分待機してリトライ...")
                time.sleep(60)

            # 次の生成まで待機
            logger.info(f"次の生成まで {interval_minutes} 分待機...")
            time.sleep(interval_minutes * 60)

    except KeyboardInterrupt:
        logger.info("ユーザーにより中断されました")

        # 最終サマリー
        summary_path = storage.save_summary_report()
        logger.info(f"最終サマリー: {summary_path}")
        print(f"\n📊 最終サマリーレポート: {summary_path}")


def show_summary() -> None:
    """サマリーを表示"""
    storage = PlanStorage()
    report = storage.generate_summary_report()
    print(report)


def list_top_plans(n: int = 10) -> None:
    """トッププランを一覧表示

    Args:
        n: 表示件数
    """
    storage = PlanStorage()
    plans = storage.get_best_plans(n)

    if not plans:
        print("プランがまだ生成されていません。")
        return

    print(f"\n=== トップ {n} ビジネスプラン ===\n")

    for i, plan in enumerate(plans, 1):
        print(f"{i}. {plan.title}")
        print(f"   スコア: {plan.overall_score:.1f} | "
              f"カテゴリ: {plan.category.value} | "
              f"市場: ${plan.market_analysis.market_size:,.0f}億")
        print(f"   {plan.value_proposition[:100]}...")
        print()


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Business Planning Maker - ビジネスプラン無限生成システム",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s --count 5              # 5つのプランを生成
  %(prog)s --continuous           # 無限に生成（5分間隔）
  %(prog)s --continuous --interval 10  # 10分間隔で無限生成
  %(prog)s --summary              # サマリーを表示
  %(prog)s --top 10               # トップ10を表示
        """
    )

    parser.add_argument(
        "-c", "--count",
        type=int,
        default=1,
        help="生成するプラン数（デフォルト: 1）"
    )

    parser.add_argument(
        "--continuous",
        action="store_true",
        help="継続生成モード（無限に生成）"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="連続生成モードでの間隔（分、デフォルト: 5）"
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=0,
        help="最大イテレーション数（0で無限、デフォルト: 0）"
    )

    parser.add_argument(
        "--summary",
        action="store_true",
        help="サマリーレポートを表示"
    )

    parser.add_argument(
        "--top",
        type=int,
        metavar="N",
        help="上位N件のプランを表示"
    )

    parser.add_argument(
        "--iteration-start",
        type=int,
        default=1,
        help="開始イテレーション番号（デフォルト: 1）"
    )

    args = parser.parse_args()

    # サマリーモード
    if args.summary:
        show_summary()
        return

    # トップ表示モード
    if args.top:
        list_top_plans(args.top)
        return

    # 連続生成モード
    if args.continuous:
        generate_continuous(
            interval_minutes=args.interval,
            max_iterations=args.max_iterations
        )
        return

    # バッチ生成モード
    if args.count > 0:
        generate_batch_plans(
            count=args.count,
            iteration_start=args.iteration_start
        )
        return


if __name__ == "__main__":
    main()
