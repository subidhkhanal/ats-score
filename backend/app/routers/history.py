import json
from fastapi import APIRouter, HTTPException
from app.models.database import get_session, AnalysisRecord, init_db

router = APIRouter()


@router.get("/history")
async def get_history():
    init_db()
    session = get_session()
    try:
        records = session.query(AnalysisRecord).order_by(
            AnalysisRecord.created_at.desc()
        ).limit(50).all()
        return [
            {
                "id": r.id,
                "overall_score": r.overall_score,
                "keyword_score": r.keyword_score,
                "semantic_score": r.semantic_score,
                "structure_score": r.structure_score,
                "recruiter_status": r.recruiter_status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ]
    finally:
        session.close()


@router.get("/history/{analysis_id}")
async def get_analysis(analysis_id: str):
    init_db()
    session = get_session()
    try:
        record = session.query(AnalysisRecord).filter(
            AnalysisRecord.id == analysis_id
        ).first()
        if not record:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return json.loads(record.result_json) if record.result_json else {}
    finally:
        session.close()


@router.delete("/history/{analysis_id}")
async def delete_analysis(analysis_id: str):
    init_db()
    session = get_session()
    try:
        record = session.query(AnalysisRecord).filter(
            AnalysisRecord.id == analysis_id
        ).first()
        if not record:
            raise HTTPException(status_code=404, detail="Analysis not found")
        session.delete(record)
        session.commit()
        return {"status": "deleted"}
    finally:
        session.close()
