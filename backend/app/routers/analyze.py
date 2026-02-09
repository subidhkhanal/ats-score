import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional

from app.models.schemas import ATSAnalysisResponse
from app.services.resume_parser import parse_resume
from app.services.jd_parser import parse_jd
from app.services.keyword_matcher import compute_keyword_score
from app.services.semantic_scorer import compute_semantic_score
from app.services.structure_scorer import compute_structure_score
from app.services.llm_analyzer import analyze_with_llm
from app.services.score_aggregator import compute_overall_score, get_recruiter_status, get_rank_estimate
from app.services.suggestion_engine import generate_suggestions

router = APIRouter()


@router.post("/analyze", response_model=ATSAnalysisResponse)
async def analyze_resume(
    resume_file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    jd_text: str = Form(...),
    include_llm_analysis: bool = Form(True),
):
    # Extract resume text
    file_bytes = None
    input_format = "txt"

    if resume_file:
        file_bytes = await resume_file.read()
        filename = resume_file.filename or ""
        if filename.endswith(".pdf"):
            input_format = "pdf"
        elif filename.endswith(".docx"):
            input_format = "docx"
        elif filename.endswith(".tex"):
            input_format = "txt"
            resume_text = file_bytes.decode("utf-8", errors="ignore")
            file_bytes = None
        else:
            resume_text = file_bytes.decode("utf-8", errors="ignore")
            file_bytes = None

    if not resume_text and not file_bytes:
        resume_text = ""

    # Parse resume and JD
    parsed_resume = parse_resume(
        text=resume_text or "",
        input_format=input_format,
        file_bytes=file_bytes,
    )
    parsed_jd = parse_jd(jd_text)

    # Layer 1: Keyword matching
    keyword_score, keyword_results = compute_keyword_score(parsed_resume, parsed_jd)

    # Layer 2: Semantic similarity
    semantic_score, semantic_results = compute_semantic_score(parsed_resume, parsed_jd)

    # Layer 3: Structure scoring
    structure_score, structure_results = compute_structure_score(parsed_resume)

    # Overall score
    overall_score = compute_overall_score(keyword_score, semantic_score, structure_score)
    recruiter_status = get_recruiter_status(overall_score)
    rank_estimate = get_rank_estimate(overall_score)

    # LLM analysis (optional)
    llm_analysis = None
    if include_llm_analysis:
        llm_analysis = await analyze_with_llm(
            resume_text=parsed_resume.raw_text,
            jd_text=jd_text,
            keyword_score=keyword_score,
            semantic_score=semantic_score,
            structure_score=structure_score,
        )

    # Generate suggestions
    suggestions = generate_suggestions(
        keyword_results=keyword_results,
        structure_results=structure_results,
        semantic_results=semantic_results,
        llm_analysis=llm_analysis,
    )

    analysis_id = str(uuid.uuid4())[:8]

    return ATSAnalysisResponse(
        overall_score=overall_score,
        keyword_score=keyword_score,
        semantic_score=semantic_score,
        structure_score=structure_score,
        recruiter_status=recruiter_status,
        rank_estimate=rank_estimate,
        keyword_results=keyword_results,
        semantic_results=semantic_results,
        structure_results=structure_results,
        parsed_resume=parsed_resume,
        parsed_jd=parsed_jd,
        llm_analysis=llm_analysis,
        suggestions=suggestions,
        analysis_id=analysis_id,
        analyzed_at=datetime.utcnow(),
    )
