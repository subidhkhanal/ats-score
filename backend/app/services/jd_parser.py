import re
from app.models.schemas import ParsedJD, KeywordWithWeight
from app.utils.text_processing import clean_text
from app.utils.constants import EXPERIENCE_LEVELS


def extract_jd_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    section_patterns = [
        (r"(?:required|must have|minimum|essential)\s*(?:skills|qualifications|requirements)", "required"),
        (r"(?:preferred|nice to have|bonus|desired|ideal)\s*(?:skills|qualifications)", "preferred"),
        (r"(?:responsibilities|what you.ll do|role|duties|key responsibilities)", "responsibilities"),
        (r"(?:qualifications|requirements|what we.re looking for|who you are)", "qualifications"),
        (r"(?:about the role|overview|description|summary)", "description"),
        (r"(?:benefits|perks|what we offer)", "benefits"),
    ]

    lines = text.split("\n")
    current_section = "description"
    current_content: list[str] = []

    for line in lines:
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        matched = False

        for pattern, section_name in section_patterns:
            if re.search(pattern, line_lower):
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = section_name
                current_content = []
                matched = True
                break

        if not matched and line_stripped:
            current_content.append(line_stripped)

    if current_content:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def detect_experience_level(text: str) -> str:
    text_lower = text.lower()
    for level, patterns in EXPERIENCE_LEVELS.items():
        for pattern in patterns:
            if pattern in text_lower:
                return level

    years_match = re.search(r"(\d+)\+?\s*years", text_lower)
    if years_match:
        years = int(years_match.group(1))
        if years <= 2:
            return "entry"
        elif years <= 5:
            return "mid"
        elif years <= 10:
            return "senior"
        else:
            return "lead"

    return "mid"


def extract_keywords_from_jd(text: str) -> list[KeywordWithWeight]:
    try:
        from keybert import KeyBERT
        kw_model = KeyBERT(model="all-MiniLM-L6-v2")
        keywords = kw_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 3),
            stop_words="english",
            top_n=30,
            use_maxsum=True,
            nr_candidates=50,
        )
        return [
            KeywordWithWeight(keyword=kw, weight=round(score, 3), category="preferred")
            for kw, score in keywords
        ]
    except Exception:
        words = re.findall(r"\b[A-Z][a-zA-Z.+#]+(?:\s+[A-Z][a-zA-Z.+#]+)*\b", text)
        word_freq: dict[str, int] = {}
        for w in words:
            w_lower = w.lower()
            if len(w_lower) > 2:
                word_freq[w] = word_freq.get(w, 0) + 1
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:30]
        return [
            KeywordWithWeight(keyword=w, weight=round(c / max(1, sorted_words[0][1]), 3), category="preferred")
            for w, c in sorted_words
        ]


def classify_keywords(
    keywords: list[KeywordWithWeight],
    jd_sections: dict[str, str],
) -> list[KeywordWithWeight]:
    required_text = jd_sections.get("required", "").lower() + " " + jd_sections.get("qualifications", "").lower()
    preferred_text = jd_sections.get("preferred", "").lower()

    for kw in keywords:
        kw_lower = kw.keyword.lower()
        if kw_lower in required_text:
            kw.category = "required"
            kw.weight = min(1.0, kw.weight * 1.5)
        elif kw_lower in preferred_text:
            kw.category = "preferred"

    return keywords


def extract_list_items(text: str) -> list[str]:
    items = []
    for line in text.split("\n"):
        line = line.strip()
        line = re.sub(r"^[-•·*▪\d.)\]]+\s*", "", line)
        if line and len(line) > 10:
            items.append(line)
    return items


def extract_title(text: str) -> str:
    lines = text.strip().split("\n")
    for line in lines[:5]:
        line = line.strip()
        if line and len(line) < 100 and not any(
            w in line.lower() for w in ["about", "description", "overview", "company"]
        ):
            return line
    return ""


def parse_jd(text: str) -> ParsedJD:
    text = clean_text(text)
    sections = extract_jd_sections(text)
    keywords = extract_keywords_from_jd(text)
    keywords = classify_keywords(keywords, sections)
    experience_level = detect_experience_level(text)
    title = extract_title(text)

    required_skills = []
    preferred_skills = []
    for kw in keywords:
        if kw.category == "required":
            required_skills.append(kw.keyword)
        else:
            preferred_skills.append(kw.keyword)

    responsibilities = extract_list_items(sections.get("responsibilities", ""))
    qualifications = extract_list_items(sections.get("qualifications", "") + "\n" + sections.get("required", ""))

    company = None
    company_match = re.search(r"(?:at|join|about)\s+([A-Z][A-Za-z\s&]+?)(?:\s*[,.]|\s+is|\s+we)", text)
    if company_match:
        company = company_match.group(1).strip()

    return ParsedJD(
        raw_text=text,
        title=title,
        company=company,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        responsibilities=responsibilities,
        qualifications=qualifications,
        experience_level=experience_level,
        keywords=keywords,
    )
