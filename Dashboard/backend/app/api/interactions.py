from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.db import get_db

router = APIRouter(prefix="/interactions", tags=["interactions"])

@router.get("/")
async def list_interactions(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: str = Query(None),
    channel: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all interactions with optional filters"""
    where_clauses = []
    params = {"limit": limit, "offset": offset}
    
    if status:
        where_clauses.append("status = :status")
        params["status"] = status
    if channel:
        where_clauses.append("channel = :channel")
        params["channel"] = channel
    
    where_clause = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    q = text(f"""
        SELECT 
            interaction_id,
            created_at,
            updated_at,
            customer_id,
            customer_name,
            customer_email,
            customer_phone,
            session_id,
            channel,
            intent,
            urgency,
            emotion,
            confidence,
            customer_message,
            bot_response,
            conversation_history,
            action_taken,
            action_type,
            success,
            execution_time_ms,
            is_handoff,
            handoff_reason,
            handoff_queue,
            handoff_department,
            assigned_agent,
            ticket_status,
            status,
            priority,
            resolved_at,
            resolution_time_seconds,
            customer_satisfaction,
            satisfaction_score,
            feedback_comment,
            metadata
        FROM public.callbot_interactions
        {where_clause}
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
    """)
    res = await db.execute(q, params)
    rows = res.mappings().all()
    return {"count": len(rows), "items": rows}

@router.get("/{interaction_id}")
async def get_interaction(interaction_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single interaction by ID"""
    q = text("""
        SELECT 
            interaction_id,
            created_at,
            updated_at,
            customer_id,
            customer_name,
            customer_email,
            customer_phone,
            session_id,
            channel,
            intent,
            urgency,
            emotion,
            confidence,
            customer_message,
            bot_response,
            conversation_history,
            action_taken,
            action_type,
            success,
            execution_time_ms,
            is_handoff,
            handoff_reason,
            handoff_queue,
            handoff_department,
            assigned_agent,
            ticket_status,
            status,
            priority,
            resolved_at,
            resolution_time_seconds,
            customer_satisfaction,
            satisfaction_score,
            feedback_comment,
            metadata
        FROM public.callbot_interactions
        WHERE interaction_id = :id
        LIMIT 1
    """)
    res = await db.execute(q, {"id": interaction_id})
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return row
