from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from app.models.schemas import ParsedResume, ParsedJD
from app.services.resume_parser import parse_resume
from app.services.jd_parser import parse_jd

router = APIRouter()


@router.post("/parse/resume", response_model=ParsedResume)
async def parse_resume_endpoint(
    resume_file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
):
    file_bytes = None
    input_format = "txt"

    if resume_file:
        file_bytes = await resume_file.read()
        filename = resume_file.filename or ""
        if filename.endswith(".pdf"):
            input_format = "pdf"
        elif filename.endswith(".docx"):
            input_format = "docx"
        else:
            resume_text = file_bytes.decode("utf-8", errors="ignore")
            file_bytes = None

    return parse_resume(
        text=resume_text or "",
        input_format=input_format,
        file_bytes=file_bytes,
    )


@router.post("/parse/jd", response_model=ParsedJD)
async def parse_jd_endpoint(
    jd_text: str = Form(...),
):
    return parse_jd(jd_text)
