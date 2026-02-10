from fastapi import APIRouter, Form
from app.models.schemas import ParsedResume, ParsedJD
from app.services.resume_parser import parse_resume
from app.services.jd_parser import parse_jd

router = APIRouter()


@router.post("/parse/resume", response_model=ParsedResume)
async def parse_resume_endpoint(
    resume_text: str = Form(""),
):
    return parse_resume(text=resume_text)


@router.post("/parse/jd", response_model=ParsedJD)
async def parse_jd_endpoint(
    jd_text: str = Form(...),
):
    return parse_jd(jd_text)
