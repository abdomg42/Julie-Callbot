from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.db import get_db

router = APIRouter(prefix="/views", tags=["views"])

@router.get("/active-interactions")
async def active_interactions(
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Get currently active interactions (pending or in_progress)"""
    q = text("""
        SELECT * FROM public.v_active_interactions 
        LIMIT :limit
    """)
    res = await db.execute(q, {"limit": limit})
    return {"items": res.mappings().all()}

@router.get("/pending-handoffs")
async def pending_handoffs(
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Get pending handoff requests"""
    q = text("""
        SELECT * FROM public.v_pending_handoffs 
        LIMIT :limit
    """)
    res = await db.execute(q, {"limit": limit})
    return {"items": res.mappings().all()}

@router.get("/daily-stats")
async def daily_stats(
    limit: int = Query(60, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Get daily statistics for the last N days"""
    q = text("""
        SELECT *
        FROM public.v_daily_stats
        ORDER BY date DESC
        LIMIT :limit
    """)
    res = await db.execute(q, {"limit": limit})
    return {"items": res.mappings().all()}

@router.get("/statistics/summary")
async def statistics_summary(db: AsyncSession = Depends(get_db)):
    """Get overall statistics summary"""
    q = text("""
        SELECT 
            COUNT(*) as total_interactions,
            COUNT(*) FILTER (WHERE status = 'completed') as completed_interactions,
            COUNT(*) FILTER (WHERE status = 'failed') as failed_interactions,
            COUNT(*) FILTER (WHERE is_handoff = true) as total_handoffs,
            ROUND(AVG(confidence)::numeric, 2) as avg_confidence,
            ROUND(AVG(CAST(execution_time_ms AS numeric)), 0)::integer as avg_execution_time,
            ROUND(AVG(CAST(customer_satisfaction AS numeric)), 2) as avg_satisfaction,
            COUNT(DISTINCT customer_id) as unique_customers,
            COUNT(DISTINCT channel) as channels_used,
            COUNT(satisfaction_score) as feedbacks_collected,
            SUM(CASE WHEN satisfaction_score = 1 THEN 1 ELSE 0 END) as satisfied_count,
            SUM(CASE WHEN satisfaction_score = 2 THEN 1 ELSE 0 END) as unsatisfied_count,
            ROUND(
            100.0 * SUM(CASE WHEN satisfaction_score = 1 THEN 1 ELSE 0 END)
            / NULLIF(COUNT(satisfaction_score), 0),
            2
            ) as satisfaction_rate_pct,
            ROUND(
            100.0 * COUNT(satisfaction_score) / NULLIF(COUNT(*), 0),
            2
            ) as feedback_collection_rate_pct,
            COUNT(*) FILTER (WHERE urgency = 'critical') as critical_issues,
            COUNT(*) FILTER (WHERE urgency = 'high') as high_priority_issues
        FROM public.callbot_interactions
        WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
    """)
    res = await db.execute(q)
    return res.mappings().first()

@router.get("/statistics/by-intent")
async def statistics_by_intent(db: AsyncSession = Depends(get_db)):
    """Get statistics grouped by intent"""
    q = text("""
        SELECT 
            intent,
            COUNT(*) as total,
            COUNT(satisfaction_score) as feedbacks_collected,
            ROUND(
            100.0 * SUM(CASE WHEN satisfaction_score = 1 THEN 1 ELSE 0 END)
            / NULLIF(COUNT(satisfaction_score), 0),
            1
            ) as satisfaction_rate_pct
            COUNT(*) FILTER (WHERE status = 'completed') as completed,
            ROUND(AVG(confidence)::numeric, 2) as avg_confidence,
            ROUND(AVG(CAST(customer_satisfaction AS numeric)), 2) as avg_satisfaction
        FROM public.callbot_interactions
        WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY intent
        ORDER BY total DESC
    """)
    res = await db.execute(q)
    return {"items": res.mappings().all()}

@router.get("/statistics/by-channel")
async def statistics_by_channel(db: AsyncSession = Depends(get_db)):
    """Get statistics grouped by channel"""
    q = text("""
        SELECT 
            channel,
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE status = 'completed') as completed,
            COUNT(*) FILTER (WHERE is_handoff = true) as handoffs,
            COUNT(satisfaction_score) as feedbacks_collected,
            ROUND(
            100.0 * SUM(CASE WHEN satisfaction_score = 1 THEN 1 ELSE 0 END)
            / NULLIF(COUNT(satisfaction_score), 0),
            1
            ) as satisfaction_rate_pct
            ROUND(AVG(CAST(customer_satisfaction AS numeric)), 2) as avg_satisfaction
        FROM public.callbot_interactions
        WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY channel
        ORDER BY total DESC
    """)
    res = await db.execute(q)
    return {"items": res.mappings().all()}

@router.get("/satisfaction/summary")
async def satisfaction_summary(
    days: int = Query(7, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    q = text("SELECT * FROM public.get_satisfaction_statistics(:days)")
    res = await db.execute(q, {"days": days})
    return res.mappings().first()

@router.get("/satisfaction/daily")
async def satisfaction_daily(
    limit: int = Query(90, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    q = text("""
        SELECT *
        FROM public.v_satisfaction_stats
        ORDER BY date DESC
        LIMIT :limit
    """)
    res = await db.execute(q, {"limit": limit})
    return {"items": res.mappings().all()}

@router.get("/satisfaction/by-intent")
async def satisfaction_by_intent(db: AsyncSession = Depends(get_db)):
    q = text("SELECT * FROM public.v_satisfaction_by_intent")
    res = await db.execute(q)
    return {"items": res.mappings().all()}

@router.get("/satisfaction/unsatisfied")
async def unsatisfied_interactions(
    limit: int = Query(200, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    q = text("""
        SELECT *
        FROM public.v_unsatisfied_interactions
        ORDER BY created_at DESC
        LIMIT :limit
    """)
    res = await db.execute(q, {"limit": limit})
    return {"items": res.mappings().all()}
