import re
from rapidfuzz import fuzz
from app.models.schemas import KeywordMatchResult, ParsedResume, ParsedJD
from app.utils.variations import get_all_variations
from app.utils.text_processing import normalize_keyword


def match_keyword_in_text(
    keyword: str,
    text: str,
    sections: dict[str, str],
) -> KeywordMatchResult:
    keyword_lower = keyword.lower().strip()
    text_lower = text.lower()
    variations = get_all_variations(keyword_lower)

    # 1. Exact match
    for var in variations:
        pattern = r"\b" + re.escape(var) + r"\b"
        if re.search(pattern, text_lower, re.IGNORECASE):
            location = _find_section(var, sections)
            return KeywordMatchResult(
                keyword=keyword,
                category="",
                found=True,
                match_type="exact" if var == keyword_lower else "variation",
                match_score=1.0 if var == keyword_lower else 0.9,
                matched_text=var,
                location_in_resume=location,
            )

    # 2. Fuzzy match
    words_in_resume = re.findall(r"\b[\w.+#/-]+(?:\s+[\w.+#/-]+){0,2}\b", text_lower)
    best_score = 0.0
    best_match = ""
    for word in words_in_resume:
        ratio = fuzz.ratio(keyword_lower, word) / 100.0
        if ratio > best_score:
            best_score = ratio
            best_match = word

    if best_score >= 0.85:
        location = _find_section(best_match, sections)
        return KeywordMatchResult(
            keyword=keyword,
            category="",
            found=True,
            match_type="fuzzy",
            match_score=round(best_score * 0.9, 2),
            matched_text=best_match,
            location_in_resume=location,
        )

    # 3. Partial match using token_set_ratio for multi-word keywords
    if len(keyword_lower.split()) > 1:
        for section_name, section_text in sections.items():
            ratio = fuzz.token_set_ratio(keyword_lower, section_text.lower()) / 100.0
            if ratio >= 0.9:
                return KeywordMatchResult(
                    keyword=keyword,
                    category="",
                    found=True,
                    match_type="fuzzy",
                    match_score=round(ratio * 0.7, 2),
                    matched_text=keyword_lower,
                    location_in_resume=section_name,
                )

    return KeywordMatchResult(
        keyword=keyword,
        category="",
        found=False,
        match_type="not_found",
        match_score=0.0,
        matched_text=None,
        location_in_resume=None,
    )


def _find_section(text: str, sections: dict[str, str]) -> str:
    text_lower = text.lower()
    for section_name, section_content in sections.items():
        if text_lower in section_content.lower():
            return section_name
    return "general"


def compute_keyword_score(
    parsed_resume: ParsedResume,
    parsed_jd: ParsedJD,
) -> tuple[int, list[KeywordMatchResult]]:
    results: list[KeywordMatchResult] = []
    resume_text = parsed_resume.raw_text
    sections = parsed_resume.sections

    for kw in parsed_jd.keywords:
        result = match_keyword_in_text(kw.keyword, resume_text, sections)
        result.category = kw.category
        results.append(result)

    if not results:
        return 0, results

    total_weight = 0.0
    weighted_score = 0.0
    for r in results:
        weight = 2.0 if r.category == "required" else 1.0
        total_weight += weight
        weighted_score += r.match_score * weight

    score = int(round((weighted_score / max(total_weight, 1)) * 100))
    return min(100, score), results
