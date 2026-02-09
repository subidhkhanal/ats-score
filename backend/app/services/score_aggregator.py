from app.models.schemas import ATSAnalysisResponse, Suggestion


def get_recruiter_status(score: int) -> str:
    if score >= 80:
        return "SHORTLIST"
    elif score >= 65:
        return "REVIEW"
    elif score >= 50:
        return "MAYBE"
    else:
        return "AUTO_REJECTED"


def get_rank_estimate(score: int) -> str:
    if score >= 80:
        return "Top 10%"
    elif score >= 65:
        return "Top 25%"
    elif score >= 50:
        return "Top 50%"
    else:
        return "Bottom 50%"


def compute_overall_score(
    keyword_score: int,
    semantic_score: int,
    structure_score: int,
) -> int:
    weighted = (
        keyword_score * 0.40
        + semantic_score * 0.35
        + structure_score * 0.25
    )
    return int(round(weighted))
