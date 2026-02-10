from fastapi import APIRouter, Form

from app.models.schemas import OptimizeResponse, ATSAnalysisResponse
from app.services.resume_parser import parse_resume, is_latex
from app.services.jd_parser import parse_jd
from app.services.keyword_matcher import compute_keyword_score
from app.services.semantic_scorer import compute_semantic_score
from app.services.structure_scorer import compute_structure_score
from app.services.score_aggregator import compute_overall_score, get_recruiter_status, get_rank_estimate
from app.services.suggestion_engine import generate_suggestions
from app.services.llm_analyzer import analyze_with_llm
from app.services.resume_optimizer import optimize_resume
from datetime import datetime
import uuid

router = APIRouter()


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_resume_endpoint(
    resume_text: str = Form(""),
    jd_text: str = Form(...),
):
    raw_latex = resume_text if is_latex(resume_text) else None

    # Run full analysis first
    parsed_resume = parse_resume(text=resume_text)
    parsed_jd = parse_jd(jd_text)

    keyword_score, keyword_results = compute_keyword_score(parsed_resume, parsed_jd)
    semantic_score, semantic_results = compute_semantic_score(parsed_resume, parsed_jd)
    structure_score, structure_results = compute_structure_score(parsed_resume)
    overall_score = compute_overall_score(keyword_score, semantic_score, structure_score)

    llm_analysis = await analyze_with_llm(
        resume_text=parsed_resume.raw_text,
        jd_text=jd_text,
        keyword_score=keyword_score,
        semantic_score=semantic_score,
        structure_score=structure_score,
    )

    suggestions = generate_suggestions(keyword_results, structure_results, semantic_results, llm_analysis)

    analysis = ATSAnalysisResponse(
        overall_score=overall_score,
        keyword_score=keyword_score,
        semantic_score=semantic_score,
        structure_score=structure_score,
        recruiter_status=get_recruiter_status(overall_score),
        rank_estimate=get_rank_estimate(overall_score),
        keyword_results=keyword_results,
        semantic_results=semantic_results,
        structure_results=structure_results,
        parsed_resume=parsed_resume,
        parsed_jd=parsed_jd,
        llm_analysis=llm_analysis,
        suggestions=suggestions,
        analysis_id=str(uuid.uuid4())[:8],
        analyzed_at=datetime.utcnow(),
    )

    # Run optimization
    result = await optimize_resume(
        resume_text=parsed_resume.raw_text,
        jd_text=jd_text,
        analysis=analysis,
        raw_latex=raw_latex,
    )

    return result
