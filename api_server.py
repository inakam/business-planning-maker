#!/usr/bin/env python3
"""
Business Planning Maker - FastAPI Server

REST APIサーバーとWeb UIを提供
"""
import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Optional
import uuid

# FastAPI関連のインポート
try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# srcをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.generators import BusinessPlanGenerator
from src.evaluators import PlanEvaluator
from src.utils import PlanStorage, PlanAnalytics
from src.models.business_plan import BusinessPlan


# FastAPIが利用できない場合のスタブ
if not FASTAPI_AVAILABLE:
    print("Error: FastAPI is not installed. Please run: pip install fastapi uvicorn")
    sys.exit(1)


# Pydanticモデル
class GenerationRequest(BaseModel):
    """プラン生成リクエスト"""
    count: int = 1
    category: Optional[str] = None
    business_model: Optional[str] = None


class PlanResponse(BaseModel):
    """プランレスポンス"""
    id: str
    title: str
    category: str
    overall_score: float
    feasibility_score: float
    profitability_score: float
    innovation_score: float
    market_size: float
    year5_revenue: float
    value_proposition: str


# FastAPIアプリケーション
app = FastAPI(
    title="Business Planning Maker API",
    description="AI-powered business plan generation system",
    version="2.0.0"
)

# グローバルインスタンス
storage = PlanStorage()
evaluator = PlanEvaluator()
generator: Optional[BusinessPlanGenerator] = None

# 生成タスクの管理
generating_tasks = {}


@app.on_event("startup")
async def startup_event():
    """起動時の初期化"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Business Planning Maker API starting...")


@app.on_event("shutdown")
async def shutdown_event():
    """シャットダウン時のクリーンアップ"""
    logger = logging.getLogger(__name__)
    logger.info("Business Planning Maker API shutting down...")


# ルート定義
@app.get("/", response_class=HTMLResponse)
async def root():
    """ルート - Web UIを返す"""
    html_path = Path(__file__).parent / "web" / "index.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Business Planning Maker</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>Business Planning Maker API</h1>
        <p>API documentation: <a href="/docs">/docs</a></p>
        <p>Web UI: <a href="/web">/web</a></p>
    </body>
    </html>
    """


@app.get("/web", response_class=HTMLResponse)
async def web_ui():
    """Web UI"""
    html_path = Path(__file__).parent / "web" / "index.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Business Planning Maker</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { background: #f0f0f0; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .card { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 8px; }
            .score { font-size: 24px; font-weight: bold; color: #2563eb; }
            .btn { background: #2563eb; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            .btn:hover { background: #1d4ed8; }
            .btn:disabled { background: #9ca3af; cursor: not-allowed; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Business Planning Maker</h1>
            <p>AI-powered business plan generation system</p>
        </div>

        <div class="card">
            <h2>Generate New Business Plan</h2>
            <button class="btn" onclick="generatePlan()" id="generateBtn">Generate Plan</button>
            <span id="status"></span>
        </div>

        <div class="card">
            <h2>Latest Plans</h2>
            <div id="plans">Loading...</div>
        </div>

        <script>
            async function generatePlan() {
                const btn = document.getElementById('generateBtn');
                const status = document.getElementById('status');
                btn.disabled = true;
                status.textContent = 'Generating...';

                try {
                    const response = await fetch('/api/generate', { method: 'POST' });
                    const data = await response.json();
                    if (data.error) {
                        status.textContent = 'Error: ' + data.error;
                    } else {
                        status.textContent = 'Generated: ' + data.plan.title;
                        loadPlans();
                    }
                } catch (e) {
                    status.textContent = 'Error: ' + e.message;
                } finally {
                    btn.disabled = false;
                }
            }

            async function loadPlans() {
                const plansDiv = document.getElementById('plans');
                try {
                    const response = await fetch('/api/plans?limit=10');
                    const data = await response.json();

                    if (data.plans.length === 0) {
                        plansDiv.innerHTML = '<p>No plans yet. Generate one!</p>';
                        return;
                    }

                    plansDiv.innerHTML = data.plans.map((plan, i) => `
                        <div style="border-bottom: 1px solid #eee; padding: 10px 0;">
                            <h3>${i + 1}. ${plan.title}</h3>
                            <p><strong>Score:</strong> <span class="score">${plan.overall_score.toFixed(1)}</span></p>
                            <p><strong>Category:</strong> ${plan.category} | <strong>Market:</strong> $${plan.market_size.toFixed(0)}B</p>
                            <p>${plan.value_proposition}</p>
                        </div>
                    `).join('');
                } catch (e) {
                    plansDiv.innerHTML = '<p>Error loading plans</p>';
                }
            }

            loadPlans();
        </script>
    </body>
    </html>
    """


@app.get("/api/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy", "version": "2.0.0"}


@app.get("/api/plans")
async def get_plans(limit: int = 10, offset: int = 0) -> dict:
    """プラン一覧取得"""
    plans = storage.load_all_plans()

    # スコア順にソート
    plans.sort(key=lambda p: p.overall_score, reverse=True)

    # ページネーション
    total = len(plans)
    plans = plans[offset:offset + limit]

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "plans": [
            {
                "id": p.id,
                "title": p.title,
                "category": p.category.value,
                "overall_score": p.overall_score,
                "feasibility_score": p.feasibility_score,
                "profitability_score": p.profitability_score,
                "innovation_score": plan.innovation_score,
                "market_size": p.market_analysis.market_size,
                "year5_revenue": p.financial_projection.year5_revenue,
                "value_proposition": p.value_proposition,
                "created_at": p.created_at.isoformat(),
            }
            for p in plans
        ]
    }


@app.get("/api/plans/{plan_id}")
async def get_plan(plan_id: str) -> dict:
    """プラン詳細取得"""
    plans = storage.load_all_plans()

    for plan in plans:
        if plan.id == plan_id:
            return {
                "id": plan.id,
                "title": plan.title,
                "category": plan.category.value,
                "iteration": plan.iteration,
                "overall_score": plan.overall_score,
                "feasibility_score": plan.feasibility_score,
                "profitability_score": plan.profitability_score,
                "innovation_score": plan.innovation_score,
                "problem_statement": plan.problem_statement,
                "solution": plan.solution,
                "value_proposition": plan.value_proposition,
                "business_model": plan.business_model,
                "market_analysis": {
                    "market_size": plan.market_analysis.market_size,
                    "market_growth_rate": plan.market_analysis.market_growth_rate,
                    "target_audience": plan.market_analysis.target_audience,
                    "market_stage": plan.market_analysis.market_stage.value,
                    "competitive_landscape": plan.market_analysis.competitive_landscape,
                    "key_success_factors": plan.market_analysis.key_success_factors,
                },
                "financial_projection": {
                    "year1_revenue": plan.financial_projection.year1_revenue,
                    "year3_revenue": plan.financial_projection.year3_revenue,
                    "year5_revenue": plan.financial_projection.year5_revenue,
                    "initial_investment": plan.financial_projection.initial_investment,
                    "break_even_months": plan.financial_projection.break_even_months,
                    "profit_margin_year3": plan.financial_projection.profit_margin_year3,
                    "customer_cac": plan.financial_projection.customer_cac,
                    "customer_ltv": plan.financial_projection.customer_ltv,
                },
                "key_milestones": plan.key_milestones,
                "team_requirements": plan.team_requirements,
                "risk_factors": plan.risk_factors,
                "mitigation_strategies": plan.mitigation_strategies,
                "reasoning": plan.reasoning,
                "tags": plan.tags,
                "created_at": plan.created_at.isoformat(),
            }

    raise HTTPException(status_code=404, detail="Plan not found")


@app.post("/api/generate")
async def generate_plan(request: GenerationRequest, background_tasks: BackgroundTasks) -> dict:
    """プラン生成（非同期）"""
    task_id = str(uuid.uuid4())

    # バックグラウンドで生成
    async def generate():
        global generator
        try:
            previous_plans = storage.load_all_plans()
            if generator is None:
                generator = BusinessPlanGenerator()

            for _ in range(request.count):
                plan = generator.generate(previous_plans=previous_plans)
                plan = evaluator.evaluate(plan)
                storage.save_plan(plan)
                previous_plans.append(plan)

            generating_tasks[task_id] = {"status": "completed"}
        except Exception as e:
            generating_tasks[task_id] = {"status": "error", "error": str(e)}

    background_tasks.add_task(lambda: asyncio.create_task(generate()))
    generating_tasks[task_id] = {"status": "generating"}

    # 最新のプランを即座に返す（同期生成）
    try:
        previous_plans = storage.load_all_plans()
        if generator is None:
            generator = BusinessPlanGenerator()

        plan = generator.generate(previous_plans=previous_plans)
        plan = evaluator.evaluate(plan)
        storage.save_plan(plan)

        return {
            "task_id": task_id,
            "status": "completed",
            "plan": {
                "id": plan.id,
                "title": plan.title,
                "category": plan.category.value,
                "overall_score": plan.overall_score,
                "feasibility_score": plan.feasibility_score,
                "profitability_score": plan.profitability_score,
                "innovation_score": plan.innovation_score,
                "market_size": plan.market_analysis.market_size,
                "year5_revenue": plan.financial_projection.year5_revenue,
                "value_proposition": plan.value_proposition,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics")
async def get_analytics() -> dict:
    """統計分析"""
    plans = storage.load_all_plans()

    if not plans:
        return {"error": "No plans available"}

    stats = PlanAnalytics.calculate_statistics(plans)
    category_dist = PlanAnalytics.analyze_category_distribution(plans)
    market_trends = PlanAnalytics.analyze_market_trends(plans)
    insights = PlanAnalytics.generate_insights(plans)

    return {
        "total_plans": len(plans),
        "statistics": stats,
        "category_distribution": category_dist,
        "market_trends": market_trends,
        "insights": insights,
    }


@app.get("/api/compare/{plan_id1}/{plan_id2}")
async def compare_plans(plan_id1: str, plan_id2: str) -> dict:
    """プラン比較"""
    plans = storage.load_all_plans()

    plan1 = next((p for p in plans if p.id == plan_id1), None)
    plan2 = next((p for p in plans if p.id == plan_id2), None)

    if not plan1 or not plan2:
        raise HTTPException(status_code=404, detail="One or both plans not found")

    return {
        "plan1": {
            "id": plan1.id,
            "title": plan1.title,
            "category": plan1.category.value,
            "overall_score": plan1.overall_score,
        },
        "plan2": {
            "id": plan2.id,
            "title": plan2.title,
            "category": plan2.category.value,
            "overall_score": plan2.overall_score,
        },
        "comparison": {
            "score_diff": plan1.overall_score - plan2.overall_score,
            "feasibility_diff": plan1.feasibility_score - plan2.feasibility_score,
            "profitability_diff": plan1.profitability_score - plan2.profitability_score,
            "innovation_diff": plan1.innovation_score - plan2.innovation_score,
        }
    }


def main():
    """サーバー起動"""
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
