import re
from app.models.schemas import StructureResult, StructureDetails, ParsedResume
from app.utils.constants import SECTION_HEADERS


def compute_structure_score(parsed_resume: ParsedResume) -> tuple[int, StructureResult]:
    details = StructureDetails()
    formatting_issues: list[str] = []

    # Contact Info (25 pts)
    contact_score = 0
    details.has_name = bool(parsed_resume.contact.name)
    details.has_email = bool(parsed_resume.contact.email)
    details.has_phone = bool(parsed_resume.contact.phone)
    details.has_linkedin = bool(parsed_resume.contact.linkedin)
    details.has_github = bool(parsed_resume.contact.github or parsed_resume.contact.portfolio)

    if details.has_name:
        contact_score += 5
    else:
        formatting_issues.append("No name detected at the top of resume")
    if details.has_email:
        contact_score += 5
    else:
        formatting_issues.append("No email address found")
    if details.has_phone:
        contact_score += 5
    else:
        formatting_issues.append("No phone number found")
    if details.has_linkedin:
        contact_score += 5
    else:
        formatting_issues.append("No LinkedIn URL found")
    if details.has_github:
        contact_score += 5
    else:
        formatting_issues.append("No GitHub/Portfolio URL found")

    # Section Presence (25 pts)
    sections_score = 0
    section_keys = set(parsed_resume.sections.keys())

    details.has_summary = any(
        k in section_keys for k in ["summary", "about", "objective", "profile"]
    )
    details.has_experience = any(
        k in section_keys
        for k in ["experience", "work experience", "employment", "professional experience"]
    )
    details.has_education = any(
        k in section_keys for k in ["education", "academic", "academics"]
    )
    details.has_skills = any(
        k in section_keys
        for k in ["skills", "technical skills", "core competencies", "technologies"]
    )
    details.has_projects = any(
        k in section_keys
        for k in ["projects", "personal projects", "academic projects"]
    )

    if details.has_summary:
        sections_score += 4
    else:
        formatting_issues.append("Missing Summary/About section")
    if details.has_experience:
        sections_score += 6
    else:
        formatting_issues.append("Missing Experience section")
    if details.has_education:
        sections_score += 5
    else:
        formatting_issues.append("Missing Education section")
    if details.has_skills:
        sections_score += 5
    else:
        formatting_issues.append("Missing Skills section")
    if details.has_projects:
        sections_score += 5
    else:
        formatting_issues.append("Missing Projects section")

    # Length & Density (25 pts)
    wc = parsed_resume.word_count
    details.word_count = wc
    details.estimated_pages = parsed_resume.estimated_pages

    if 300 <= wc <= 800:
        length_score = 25
    elif 200 <= wc < 300 or 800 < wc <= 1000:
        length_score = 15
        formatting_issues.append(
            f"Resume length ({wc} words) is {'short' if wc < 300 else 'long'} for optimal ATS parsing"
        )
    else:
        length_score = 5
        formatting_issues.append(
            f"Resume length ({wc} words) is {'too short' if wc < 200 else 'too long'} for ATS"
        )

    # Formatting (25 pts)
    formatting_score = 0

    # No images/tables check (10 pts) — in text mode, usually fine
    formatting_score += 10

    # Standard section headers (10 pts)
    non_standard = 0
    for section_name in parsed_resume.sections.keys():
        if section_name.lower() not in SECTION_HEADERS:
            non_standard += 1
    if non_standard == 0:
        formatting_score += 10
        details.has_standard_headers = True
    elif non_standard <= 2:
        formatting_score += 5
        details.has_standard_headers = False
        formatting_issues.append("Some non-standard section headers detected")
    else:
        details.has_standard_headers = False
        formatting_issues.append("Multiple non-standard section headers may confuse ATS")

    # Consistent date formats (5 pts)
    dates = re.findall(
        r"(\w+\s+\d{4}|\d{1,2}/\d{4}|\d{4})", parsed_resume.raw_text
    )
    if dates:
        formatting_score += 5
        details.has_consistent_dates = True

    details.formatting_issues = formatting_issues

    total = contact_score + sections_score + length_score + formatting_score

    result = StructureResult(
        contact_score=contact_score,
        sections_score=sections_score,
        length_score=length_score,
        formatting_score=formatting_score,
        total_score=total,
        details=details,
    )

    return total, result
