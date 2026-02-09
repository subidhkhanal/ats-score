import numpy as np
from app.models.schemas import SemanticResult, ParsedResume, ParsedJD
from app.config import get_settings

_model = None


def _get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            settings = get_settings()
            _model = SentenceTransformer(
                "all-MiniLM-L6-v2",
                cache_folder=settings.model_cache_dir,
            )
        except Exception:
            _model = None
    return _model


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def compute_semantic_score(
    parsed_resume: ParsedResume,
    parsed_jd: ParsedJD,
) -> tuple[int, SemanticResult]:
    model = _get_model()
    if model is None:
        return 0, SemanticResult()

    resume_skills = parsed_resume.sections.get("skills", "") or parsed_resume.sections.get("technical skills", "")
    resume_experience = ""
    for key in ["experience", "work experience", "professional experience"]:
        if key in parsed_resume.sections:
            resume_experience = parsed_resume.sections[key]
            break
    resume_education = parsed_resume.sections.get("education", "")
    resume_full = parsed_resume.raw_text

    jd_full = parsed_jd.raw_text
    jd_required = " ".join(parsed_jd.required_skills)
    jd_responsibilities = " ".join(parsed_jd.responsibilities) if parsed_jd.responsibilities else jd_full
    jd_qualifications = " ".join(parsed_jd.qualifications) if parsed_jd.qualifications else ""

    texts_to_encode = [
        resume_skills or "no skills listed",
        resume_experience or "no experience listed",
        resume_education or "no education listed",
        resume_full,
        jd_required or jd_full,
        jd_responsibilities,
        jd_qualifications or jd_full,
        jd_full,
    ]

    embeddings = model.encode(texts_to_encode, show_progress_bar=False)

    skills_sim = cosine_similarity(embeddings[0], embeddings[4])
    experience_sim = cosine_similarity(embeddings[1], embeddings[5])
    education_sim = cosine_similarity(embeddings[2], embeddings[6])
    overall_sim = cosine_similarity(embeddings[3], embeddings[7])

    # Weighted average
    weighted = (
        skills_sim * 0.40
        + experience_sim * 0.35
        + education_sim * 0.15
        + overall_sim * 0.10
    )

    section_similarities = {
        "skills": round(skills_sim * 100, 1),
        "experience": round(experience_sim * 100, 1),
        "education": round(education_sim * 100, 1),
        "overall": round(overall_sim * 100, 1),
    }

    result = SemanticResult(
        overall_similarity=round(weighted, 3),
        skills_similarity=round(skills_sim, 3),
        experience_similarity=round(experience_sim, 3),
        education_similarity=round(education_sim, 3),
        section_similarities=section_similarities,
    )

    score = int(round(weighted * 100))
    return min(100, max(0, score)), result
