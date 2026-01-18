"""
ビジネスプラン生成器 - Claude APIを使用してビジネスプランを生成
"""
import json
import os
import uuid
from typing import Optional, List, Tuple
from datetime import datetime
import subprocess
import random
import re
from difflib import SequenceMatcher

from ..models.business_plan import BusinessPlan, PlanCategory, MarketAnalysis, MarketStage, FinancialProjection


class BusinessPlanGenerator:
    """Claude APIを使用したビジネスプラン生成器"""

    # トレンドとテーマのデータベース
    TRENDS = {
        "AI_ML": [
            "AIコーチングパーソナライゼーション",
            "生成AIコンテンツ最適化",
            "AIデータプライバシーコンプライアンス",
            "AIコードレビュー自動化",
            "AIマルチモーダル分析",
        ],
        "FINTECH": [
            "中小企業向け自動財務管理",
            "クロスボーダー決済最適化",
            "DeFiレンディングプラットフォーム",
            "ESG投資アドバイザリー",
            "インボイスファイナンス自動化",
        ],
        "HEALTHTECH": [
            "遠隔医療モニタリング",
            "メンタルヘルスAI支援",
            "パーソナライズド栄養管理",
            "クリニック運営最適化SaaS",
            "薬剤処方支援AI",
        ],
        "SAAS": [
            "中小企業向け人材管理最適化",
            "プロジェクト管理AI自動化",
            "顧客サポート自動化プラットフォーム",
            "サブスクリプション収益最適化",
            "在庫管理予測AI",
        ],
        "CLEANTECH": [
            "企業カーボンフットプリント追跡",
            "再生可能エネルギー取引プラットフォーム",
            "スマートグリッド最適化",
            "廃棄物管理リサイクルAI",
            "電力消費最適化SaaS",
        ],
    }

    BUSINESS_MODELS = [
        "サブスクリプションモデル",
        "フリーミアムモデル",
        "トランザクション手数料モデル",
        "マーケットプレイスモデル",
        "エンタープライズライセンスモデル",
        "利用量ベース課金モデル",
        "ハイブリッドモデル",
    ]

    TARGET_MARKETS = [
        "中小企業（従業員10-100人）",
        "大企業（従業員1000人以上）",
        "スタートアップ/VC投資企業",
        "フリーランス/個人事業主",
        "特定業種垂直市場",
        "消費者一般（B2C）",
    ]

    def __init__(self, iteration: int = 1, max_retries: int = 3):
        self.iteration = iteration
        self.max_retries = max_retries

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """2つのテキストの類似度を計算（0-1）"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def _is_duplicate(self, title: str, tags: List[str], previous_plans: List[BusinessPlan], threshold: float = 0.7) -> bool:
        """重複チェック

        Args:
            title: 新しいプランのタイトル
            tags: 新しいプランのタグ
            previous_plans: 以前のプランリスト
            threshold: 類似度の閾値

        Returns:
            重複している場合はTrue
        """
        if not previous_plans:
            return False

        for plan in previous_plans:
            # タイトルの類似度チェック
            title_similarity = self._calculate_similarity(title, plan.title)
            if title_similarity >= threshold:
                return True

            # タグの重複チェック
            tag_overlap = len(set(tags) & set(plan.tags)) / max(len(set(tags)), 1)
            if tag_overlap >= 0.8:
                return True

        return False

    def _avoid_near_duplicates(self, theme: str, previous_plans: Optional[List[BusinessPlan]]) -> bool:
        """テーマが既存プランと類似しすぎていないかチェック

        Args:
            theme: 検査するテーマ
            previous_plans: 以前のプランリスト

        Returns:
            安全（類似していない）ならTrue
        """
        if not previous_plans:
            return True

        for plan in previous_plans:
            # タイトルとタグ、説明文を含めて類似度チェック
            combined_text = f"{plan.title} {' '.join(plan.tags)} {plan.solution[:200]}"
            similarity = self._calculate_similarity(theme, combined_text)
            if similarity > 0.6:  # 60%以上類似なら回避
                return False

        return True

    def _select_theme(self, previous_plans: Optional[List[BusinessPlan]] = None, max_attempts: int = 10) -> Tuple[str, str, str, str]:
        """ランダムにテーマとビジネスモデルを選択（重複回避）

        Args:
            previous_plans: 以前のプランリスト
            max_attempts: 重複回避の最大試行回数

        Returns:
            (category, theme, business_model, target_market)
        """
        for _ in range(max_attempts):
            category = random.choice(list(self.TRENDS.keys()))
            themes = self.TRENDS[category]
            theme = random.choice(themes)

            # 重複チェック
            if previous_plans and not self._avoid_near_duplicates(theme, previous_plans):
                continue  # 重複しているので再試行

            business_model = random.choice(self.BUSINESS_MODELS)
            target_market = random.choice(self.TARGET_MARKETS)
            return category, theme, business_model, target_market

        # 見つからない場合はランダムに返す
        category = random.choice(list(self.TRENDS.keys()))
        theme = random.choice(self.TRENDS[category])
        return (
            category,
            theme,
            random.choice(self.BUSINESS_MODELS),
            random.choice(self.TARGET_MARKETS),
        )

    def _generate_with_claude(self, prompt: str) -> str:
        """Claude CLIを使用してプロンプトを実行（リトライ機能付き）"""
        for attempt in range(self.max_retries):
            try:
                # タイムアウト時間をリトライ回数に応じて延長
                timeout = 120 + (attempt * 60)

                result = subprocess.run(
                    ["claude", "-p", prompt],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )

                if result.returncode == 0 and result.stdout.strip():
                    # 空の出力チェック
                    if len(result.stdout.strip()) > 50:
                        return result.stdout
                    else:
                        print(f"Attempt {attempt + 1}: Output too short, retrying...")
                else:
                    print(f"Attempt {attempt + 1}: Claude CLI returned error or empty output")

            except subprocess.TimeoutExpired:
                print(f"Attempt {attempt + 1}: Claude CLI timeout (>{timeout}s)")
            except FileNotFoundError:
                print("Claude CLI not found, using fallback generator")
                return self._generate_fallback_plan()
            except Exception as e:
                print(f"Attempt {attempt + 1}: Error - {e}")

            # 最後の試行でなければ待機してリトライ
            if attempt < self.max_retries - 1:
                import time
                wait_time = (attempt + 1) * 5  # 5秒、10秒、15秒...
                print(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)

        # すべて失敗した場合はフォールバック
        print("All retries failed, using fallback generator")
        return self._generate_fallback_plan()

    def _extract_json_from_response(self, response: str) -> str:
        """レスポンスからJSON部分を抽出

        Args:
            response: Claudeからのレスポンス

        Returns:
            抽出されたJSON文字列
        """
        # マークダウンコードブロックを削除
        response = response.strip()

        # ```json ... ``` パターン
        json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', response, re.DOTALL)
        if json_match:
            return json_match.group(1)

        # ``` ... ``` パターン（単一行）
        json_match = re.search(r'```(.*?)```', response, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()

        # { で始まる部分を抽出
        start_idx = response.find('{')
        if start_idx != -1:
            # 対応する } を見つける
            brace_count = 0
            for i in range(start_idx, len(response)):
                if response[i] == '{':
                    brace_count += 1
                elif response[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return response[start_idx:i + 1]

        # 見つからない場合は元のレスポンスを返す
        return response

    def _generate_fallback_plan(self) -> str:
        """Claude CLIが利用できない場合のフォールバック"""
        category, theme, business_model, target_market = self._select_theme()
        return json.dumps({
            "title": f"{theme} - {business_model}",
            "category": category,
            "problem_statement": f"{target_market}は現在、手動プロセスと非効率なシステムに依存しており、時間とリソースを浪費しています。",
            "solution": f"AIと自動化を活用した{theme}プラットフォームを提供します。",
            "value_proposition": f"時間を80%削減し、コストを50%削減する{theme}ソリューション。",
            "business_model": business_model,
            "market_analysis": {
                "market_size": random.randint(10, 1000),
                "market_growth_rate": random.randint(10, 40),
                "target_audience": target_market,
                "market_stage": "growing",
                "competitive_landscape": "競合は存在するが、AIによる差別化が可能",
                "key_success_factors": [
                    "ユーザー体験の最適化",
                    "AIモデルの精度向上",
                    "顧客獲得コストの最適化",
                    "パートナーシップ構築"
                ]
            },
            "financial_projection": {
                "year1_revenue": random.randint(100, 1000) * 1000,
                "year3_revenue": random.randint(5, 50) * 1000000,
                "year5_revenue": random.randint(20, 200) * 1000000,
                "initial_investment": random.randint(500, 5000) * 1000,
                "break_even_months": random.randint(18, 36),
                "profit_margin_year3": random.randint(20, 40),
                "customer_cac": random.randint(500, 5000),
                "customer_ltv": random.randint(3000, 30000)
            },
            "key_milestones": [
                "MVP開発（3ヶ月）",
                "初期顧客10社獲得（6ヶ月）",
                "シード資金調達（12ヶ月）",
                "機能拡張と市場拡大（18ヶ月）"
            ],
            "team_requirements": [
                "CEO/ビジネスリーダー",
                "CTO/技術リーダー",
                "AIエンジニア",
                "プロダクトマネージャー",
                "営業・マーケティング"
            ],
            "risk_factors": [
                "技術的実現のリスク",
                "市場受容の不確実性",
                "競合の台頭"
            ],
            "mitigation_strategies": [
                "段階的アプローチでの開発",
                "初期顧客との緊密な協働",
                "継続的なイノベーション"
            ],
            "reasoning": f"{target_market}向けの{theme}は、市場ニーズが高く、{business_model}で収益化が可能。",
            "tags": [theme.lower(), category.lower(), business_model.lower()]
        }, ensure_ascii=False, indent=2)

    def generate(self, previous_plans: Optional[List[BusinessPlan]] = None) -> BusinessPlan:
        """新しいビジネスプランを生成（重複回避機能付き）

        Args:
            previous_plans: 以前のプランリスト（重複回避のため）

        Returns:
            BusinessPlan: 生成されたビジネスプラン
        """
        # 重複を回避してテーマ選択
        category, theme, business_model, target_market = self._select_theme(previous_plans)

        # 既存プランの情報を収集してプロンプトに反映
        existing_titles = []
        existing_themes = []
        if previous_plans:
            existing_titles = [plan.title for plan in previous_plans[-10:]]  # 直近10件
            existing_themes = list(set([tag for plan in previous_plans[-20:] for tag in plan.tags]))

        # 重複しているテーマの警告
        exclusion_list = ", ".join(existing_themes[:5]) if existing_themes else "なし"

        # プロンプト作成（最適化版）
        prompt = f"""あなたはシリコンバレーで活躍する経験豊富なシリアルアントレプレナー兼VC投資家です。以下の条件で、投資家から見て魅力的で実現可能なビジネスプランを作成してください。

**基本情報:**
- テーマ: {theme}
- カテゴリー: {category}
- ビジネスモデル: {business_model}
- ターゲット市場: {target_market}

**制約条件:**
- 以下の既存プランと重複しないこと: {exclusion_list}
- 独自性と差別化要素を明確にすること
- 具体的な数値と根拠を示すこと

以下のJSON形式で出力してください。マークダウン形式ではなく、有効なJSONのみを出力してください。

{{
  "title": "魅力的で覚えやすいビジネス名（日本語）",
  "problem_statement": "ターゲット層が直面する具体的で緊急性の高い問題を3-4文で説明。感情的・経済的影響を含めること。",
  "solution": "問題を解決する具体的なソリューションを3-4文で説明。技術的・運用的アプローチを含めること。",
  "value_proposition": "顧客に提供する独自の価値を2-3文で説明。具体的な数値（削減率、改善率等）を含めること。",
  "business_model": "{business_model}の詳細説明。収益の流れ、価格設定、収益化のタイミングを具体的に。",
  "market_analysis": {{
    "market_size": 市場規模（億ドル単位の数値。TAM/SAM/SOMを考慮）,
    "market_growth_rate": 年平均成長率（CAGR、%の数値）,
    "target_audience": "具体的なターゲット層。デモグラフィック、 firmographic等を含めて詳細に。",
    "market_stage": "emerging/growing/mature/decliningのいずれか",
    "competitive_landscape": "競合状況の詳細な分析。主要プレイヤー3社程度と、当該ビジネスの差別化優位性を3-4文で。",
    "key_success_factors": ["成功に必要な要素1（具体的に）", "成功に必要な要素2", "成功に必要な要素3", "成功に必要な要素4", "成功に必要な要素5"]
  }},
  "financial_projection": {{
    "year1_revenue": 1年目の売上見込み（ドル、現実的な数値で）,
    "year3_revenue": 3年目の売上見込み（ドル、成長軌道を考慮）,
    "year5_revenue": 5年目の売上見込み（ドル、市場拡大を考慮）,
    "initial_investment": 必要初期投資額（ドル。製品開発、初期チーム、マーケティングを含む）,
    "break_even_months": 損益分岐までの月数（18-36の範囲で現実的に）,
    "profit_margin_year3": 3年目の利益率（%。20-50の範囲で、業界標準を考慮）,
    "customer_cac": 顧客獲得コスト（ドル。マーケティング・販売効率を考慮）,
    "customer_ltv": 顧客生涯価値（ドル。サブスクリプション期間、平均収益を考慮）
  }},
  "key_milestones": ["起業から0-6ヶ月の重要マイルストーン", "6-12ヶ月のマイルストーン", "12-18ヶ月のマイルストーン", "18-24ヶ月のマイルストーン"],
  "team_requirements": ["必要な主要役割1（特定スキルを含めて）", "役割2", "役割3", "役割4", "役割5"],
  "risk_factors": ["主要なリスク1（具体的に）", "リスク2", "リスク3"],
  "mitigation_strategies": ["リスク1への具体的な対策", "リスク2への対策", "リスク3への対策"],
  "reasoning": "このビジネスが成功すると確信できる理由を3-4文で。市場タイミング、競合優位性、収益化の明確性を含めること。",
  "tags": ["検索用タグ1（英数字小文字）", "タグ2", "タグ3"]
}}

**評価基準（これらを満たすプランを作成してください）:**

1. **市場規模**: $10億以上のTAM（総合可能市場）を目指す
2. **成長率**: 年率15%以上の成長市場を選択
3. **LTV/CAC**: 3倍以上の比率を目指す
4. **損益分岐**: 36ヶ月以内を目指す
5. **独自性**: 特許、技術、ネットワーク効果、Switching Cost等の優位性を明示
6. **タイミング**: 「なぜ今なのか」を明確に示す
7. **チーム**: 実行可能な最小チーム構成を示す

JSONのみを出力してください。解説や余分なテキストは不要です。"""

        try:
            response = self._generate_with_claude(prompt)
            # JSON抽出（改善版）
            response = self._extract_json_from_response(response)
            data = json.loads(response)

            # 重複チェック
            if self._is_duplicate(data["title"], data.get("tags", []), previous_plans or []):
                print(f"Warning: Generated plan appears duplicate, regenerating...")
                # 再帰的に再生成（最大1回）
                if self.iteration < 2:
                    self.iteration += 1
                    return self.generate(previous_plans)

        except (json.JSONDecodeError, KeyError, Exception) as e:
            print(f"Warning: Failed to parse/generate Claude response ({e}), using enhanced fallback")
            data = json.loads(self._generate_enhanced_fallback(category, theme, business_model, target_market))

        # BusinessPlanオブジェクトを作成
        market = MarketAnalysis(
            market_size=data["market_analysis"]["market_size"],
            market_growth_rate=data["market_analysis"]["market_growth_rate"],
            target_audience=data["market_analysis"]["target_audience"],
            market_stage=MarketStage(data["market_analysis"]["market_stage"]),
            competitive_landscape=data["market_analysis"]["competitive_landscape"],
            key_success_factors=data["market_analysis"]["key_success_factors"],
        )

        financial = FinancialProjection(
            year1_revenue=data["financial_projection"]["year1_revenue"],
            year3_revenue=data["financial_projection"]["year3_revenue"],
            year5_revenue=data["financial_projection"]["year5_revenue"],
            initial_investment=data["financial_projection"]["initial_investment"],
            break_even_months=data["financial_projection"]["break_even_months"],
            profit_margin_year3=data["financial_projection"]["profit_margin_year3"],
            customer_cac=data["financial_projection"]["customer_cac"],
            customer_ltv=data["financial_projection"]["customer_ltv"],
        )

        plan = BusinessPlan(
            id=str(uuid.uuid4()),
            title=data["title"],
            category=PlanCategory[category],
            iteration=self.iteration,
            problem_statement=data["problem_statement"],
            solution=data["solution"],
            value_proposition=data["value_proposition"],
            business_model=data["business_model"],
            market_analysis=market,
            financial_projection=financial,
            key_milestones=data["key_milestones"],
            team_requirements=data["team_requirements"],
            risk_factors=data["risk_factors"],
            mitigation_strategies=data["mitigation_strategies"],
            reasoning=data.get("reasoning", ""),
            tags=data.get("tags", []),
        )

        return plan

    def _generate_enhanced_fallback(self, category: str, theme: str, business_model: str, target_market: str) -> str:
        """改善されたフォールバックプラン生成"""
        # カテゴリ別の市場データ
        market_data = {
            "AI_ML": {"size": (150, 300), "growth": (35, 45)},
            "FINTECH": {"size": (200, 500), "growth": (20, 30)},
            "HEALTHTECH": {"size": (100, 250), "growth": (18, 28)},
            "SAAS": {"size": (300, 800), "growth": (15, 25)},
            "CLEANTECH": {"size": (250, 600), "growth": (22, 35)},
            "MARKETPLACE": {"size": (200, 400), "growth": (20, 30)},
        }

        data = market_data.get(category, {"size": (100, 300), "growth": (15, 25)})
        market_size = random.randint(*data["size"])
        growth_rate = random.randint(*data["growth"])

        # 財務データの生成
        year1_rev = random.randint(200, 2000) * 1000
        year3_rev = year1_rev * random.randint(10, 30)
        year5_rev = year3_rev * random.randint(2, 5)
        investment = random.randint(1000, 8000) * 1000
        cac = random.randint(1000, 8000)
        ltv = cac * random.randint(3, 6)

        return json.dumps({
            "title": f"AI駆動型{theme}プラットフォーム",
            "problem_statement": f"現在、{target_market}はレガシーシステムと手動プロセスに依存しており、年間数千万人件のオペレーションにおいて平均{random.randint(30, 70)}%の時間とコストを浪費しています。この非効率性は、{random.randint(20, 50)}億ドルの市場機会損失につながっており、業界全体の生産性向上が喫緊の課題となっています。",
            "solution": f"最新のAI/機械学習技術を活用した{theme}プラットフォームを開発し、{target_market}の業務プロセスを{random.randint(70, 95)}%自動化します。当社の独自アルゴリズムは、既存システムとシームレスに統合され、導入から30日以内に価値を提供します。",
            "value_proposition": f"導入企業は平均{random.randint(60, 85)}%のコスト削減と{random.randint(40, 70)}%の業務効率向上を実現し、初期投資回収期間は平均{random.randint(6, 12)}ヶ月です。競合他社と比較して{random.randint(2, 4)}倍の高い精度と{random.randint(3, 5)}倍の高速処理を実現しています。",
            "business_model": f"{business_model}を採用し、基本機能は月額${random.randint(100, 1000)}から提供。エンタープライズ向けにはカスタムプランを用意し、1顧客あたり平均${random.randint(10000, 100000)}の年間収益を見込みます。",
            "market_analysis": {
                "market_size": market_size,
                "market_growth_rate": growth_rate,
                "target_audience": f"{target_market}を中心に、特に従業員規模{random.randint(50, 500)}人以上の企業をターゲット。初期は北米市場に注力し、2年目以降は欧州・アジア太平洋市場へ展開。",
                "market_stage": "growing",
                "competitive_landscape": f"既存プレイヤーはあるものの、AI機能が限定的で高価。当社は最先端のAI技術と{business_model}により、既存製品の半額以下の価格で提供可能。",
                "key_success_factors": [
                    "AIモデルの継続的改善と精度向上",
                    f"{target_market}に特化したUX/UI設計",
                    "戦略的パートナーシップ（既存システムベンダー等）",
                    "迅速な製品ロードマップ実行",
                    "顧客成功チームによる高定着率維持"
                ]
            },
            "financial_projection": {
                "year1_revenue": year1_rev,
                "year3_revenue": year3_rev,
                "year5_revenue": year5_rev,
                "initial_investment": investment,
                "break_even_months": random.randint(20, 32),
                "profit_margin_year3": random.randint(25, 45),
                "customer_cac": cac,
                "customer_ltv": ltv
            },
            "key_milestones": [
                f"MVP開発と初期顧客（ベータ版）5社獲得（0-6ヶ月）",
                "Seed Series調達$2-5Mとチーム拡大（6-12ヶ月）",
                "顧客100社達成とSeries A調達（12-18ヶ月）",
                "国際展開開始と顧客500社達成（18-24ヶ月）"
            ],
            "team_requirements": [
                "CEO/ビジネス開発（VCネットワーク豊富な者）",
                "CTO/AIエンジニアリングリーダー（PhD保持者等）",
                "プロダクトマネージャー（B2B SaaS経験）",
                "セールスヘッド（エンタープライズ営業経験）",
                "カスタマーサクセスマネージャー"
            ],
            "risk_factors": [
                "AI技術の進化に伴う陳腐化リスク",
                f"{target_market}の規制変更リスク",
                "大企業向け導入の長い販売サイクル"
            ],
            "mitigation_strategies": [
                "研究開発チームの継続的投資と提携",
                "法務コンプライアンス体制の早期構築",
                "中小企業からの導入実績積み上げによる信頼性確立"
            ],
            "reasoning": f"市場規模${market_size}億、成長率{growth_rate}%の{category}市場において、AI技術の成熟と{target_market}のデジタル化ニーズが高まる今が最適なタイミング。{business_model}で収益化し、LTV/CAC比率{ltv/cac:.1f}倍で健康的なユニットエコノミクスを実現できます。",
            "tags": [theme.lower().replace(" ", "-"), category.lower(), "ai-ml", "saas", "b2b"]
        }, ensure_ascii=False, indent=2)
