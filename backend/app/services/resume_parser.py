import re
import io
from pathlib import Path
from app.models.schemas import (
    ParsedResume, ContactInfo, ExperienceEntry,
    EducationEntry, ProjectEntry,
)
from app.utils.text_processing import (
    clean_text, extract_emails, extract_phones,
    extract_urls, count_words, estimate_pages,
)
from app.utils.constants import SECTION_HEADERS


def is_latex(text: str) -> bool:
    return "\\documentclass" in text or "\\begin{document}" in text


def extract_text_from_pdf(file_bytes: bytes) -> str:
    import fitz
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    doc.close()
    return text.strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])


def latex_to_plain(latex: str) -> str:
    text = latex
    text = re.sub(r"%.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\\href\{[^}]*\}\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\myuline\s*\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\textbf\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\textit\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\texttt\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\resumeItem\{(.*?)\}", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"\\resumeSubheading\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}", r"\1 | \3 | \2 | \4", text)
    text = re.sub(r"\\resumeProjectHeading\{([^}]*)\}\{([^}]*)\}", r"\1 | \2", text)
    text = re.sub(r"\\section\{([^}]*)\}", r"\n\1\n", text)
    text = re.sub(r"\\[a-zA-Z]+\*?\{[^}]*\}", "", text)
    text = re.sub(r"\\[a-zA-Z]+\*?", "", text)
    text = re.sub(r"\\begin\{[^}]*\}", "", text)
    text = re.sub(r"\\end\{[^}]*\}", "", text)
    text = re.sub(r"[{}$\\|]", "", text)
    text = re.sub(r"\n\s*\n", "\n", text)
    text = re.sub(r"  +", " ", text)
    return text.strip()


def detect_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    lines = text.split("\n")
    current_section = ""
    current_content: list[str] = []

    for line in lines:
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        line_clean = re.sub(r"[^a-z\s]", "", line_lower).strip()

        matched = False
        for header in SECTION_HEADERS:
            if line_clean == header or line_lower.startswith(header):
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = header
                current_content = []
                matched = True
                break

        if not matched and line_stripped:
            if line_stripped.isupper() and len(line_stripped.split()) <= 4 and len(line_stripped) > 2:
                clean = re.sub(r"[^a-z\s]", "", line_stripped.lower()).strip()
                for header in SECTION_HEADERS:
                    if clean == header or header in clean:
                        if current_section and current_content:
                            sections[current_section] = "\n".join(current_content).strip()
                        current_section = header
                        current_content = []
                        matched = True
                        break

        if not matched and current_section:
            current_content.append(line_stripped)
        elif not matched and not current_section and line_stripped:
            current_content.append(line_stripped)

    if current_section and current_content:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def extract_contact_info(text: str) -> ContactInfo:
    emails = extract_emails(text)
    phones = extract_phones(text)
    urls = extract_urls(text)

    lines = text.split("\n")
    name = ""
    for line in lines[:5]:
        line = line.strip()
        if line and not any(c in line for c in ["@", "http", "+", "(", ")"]):
            if len(line.split()) <= 5 and len(line) > 2:
                name = line
                break

    location = ""
    location_patterns = [
        r"(?:location|address|based in)[:\s]*(.+)",
        r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s*[A-Z]{2}(?:\s\d{5})?)",
    ]
    for pattern in location_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            break

    return ContactInfo(
        name=name,
        email=emails[0] if emails else "",
        phone=phones[0] if phones else "",
        linkedin=urls["linkedin"][0] if urls["linkedin"] else "",
        github=urls["github"][0] if urls["github"] else "",
        location=location,
        portfolio=urls["other"][0] if urls["other"] else "",
    )


def extract_skills_from_text(text: str, sections: dict[str, str]) -> list[str]:
    skills_text = ""
    for key in ["skills", "technical skills", "core competencies", "technologies"]:
        if key in sections:
            skills_text = sections[key]
            break

    if not skills_text:
        skills_text = text

    skills: list[str] = []
    separators = [",", ";", "•", "·", "|", "\n"]
    for sep in separators:
        if sep in skills_text:
            parts = skills_text.split(sep)
            for part in parts:
                part = part.strip()
                part = re.sub(r"^[-•·\s]+", "", part)
                part = re.sub(r"\s*[:]\s*$", "", part)
                if part and len(part) < 50 and len(part) > 1:
                    category_match = re.match(r"^(.+?):\s*(.+)$", part)
                    if category_match:
                        sub_skills = category_match.group(2).split(",")
                        skills.extend([s.strip() for s in sub_skills if s.strip()])
                    else:
                        skills.append(part)
            break

    return list(dict.fromkeys(skills))


def extract_experience(sections: dict[str, str]) -> list[ExperienceEntry]:
    experiences: list[ExperienceEntry] = []
    exp_text = ""
    for key in ["experience", "work experience", "employment", "professional experience"]:
        if key in sections:
            exp_text = sections[key]
            break

    if not exp_text:
        return experiences

    entries = re.split(r"\n(?=[A-Z])", exp_text)
    for entry_text in entries:
        lines = [l.strip() for l in entry_text.strip().split("\n") if l.strip()]
        if not lines:
            continue

        company = lines[0] if lines else ""
        role = ""
        dates = ""
        bullets = []

        date_pattern = r"(\w+\s+\d{4}\s*[-–]\s*(?:\w+\s+\d{4}|Present|Current))"
        for line in lines:
            match = re.search(date_pattern, line, re.IGNORECASE)
            if match:
                dates = match.group(1)
                role_part = line.replace(dates, "").strip().strip("|").strip("-").strip()
                if role_part and not role:
                    role = role_part
                break

        for line in lines[1:]:
            if line.startswith(("•", "-", "·", "*", "▪")):
                bullets.append(re.sub(r"^[•\-·*▪]\s*", "", line))
            elif re.match(r"^\d+\.", line):
                bullets.append(re.sub(r"^\d+\.\s*", "", line))

        if company or role:
            experiences.append(ExperienceEntry(
                company=company, role=role, dates=dates, bullets=bullets
            ))

    return experiences


def extract_education(sections: dict[str, str]) -> list[EducationEntry]:
    education: list[EducationEntry] = []
    edu_text = ""
    for key in ["education", "academic", "academics"]:
        if key in sections:
            edu_text = sections[key]
            break

    if not edu_text:
        return education

    lines = [l.strip() for l in edu_text.split("\n") if l.strip()]
    current_entry: dict = {}

    for line in lines:
        degree_patterns = [
            r"(Bachelor|Master|Ph\.?D|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|MBA|B\.?Tech|M\.?Tech|Associate)",
        ]
        is_degree = any(re.search(p, line, re.IGNORECASE) for p in degree_patterns)

        if is_degree or (not current_entry and line):
            if current_entry:
                education.append(EducationEntry(**current_entry))
            current_entry = {"school": "", "degree": line, "dates": "", "gpa": "", "details": []}
        elif current_entry:
            date_match = re.search(r"(\d{4}\s*[-–]\s*(?:\d{4}|Present))", line)
            gpa_match = re.search(r"GPA[:\s]*([0-9.]+)", line, re.IGNORECASE)
            if date_match:
                current_entry["dates"] = date_match.group(1)
                school_part = line.replace(date_match.group(1), "").strip().strip("|").strip("-").strip()
                if school_part:
                    current_entry["school"] = school_part
            elif gpa_match:
                current_entry["gpa"] = gpa_match.group(1)
            else:
                current_entry["details"].append(line)

    if current_entry:
        education.append(EducationEntry(**current_entry))

    return education


def parse_resume(text: str, input_format: str = "txt", file_bytes: bytes | None = None) -> ParsedResume:
    raw_latex = None
    if file_bytes and input_format == "pdf":
        text = extract_text_from_pdf(file_bytes)
    elif file_bytes and input_format == "docx":
        text = extract_text_from_docx(file_bytes)
    elif is_latex(text):
        raw_latex = text
        input_format = "latex"
        text = latex_to_plain(text)

    text = clean_text(text)
    sections = detect_sections(text)
    contact = extract_contact_info(text)
    skills = extract_skills_from_text(text, sections)
    experience = extract_experience(sections)
    education = extract_education(sections)

    projects: list[ProjectEntry] = []
    for key in ["projects", "personal projects", "academic projects"]:
        if key in sections:
            proj_lines = sections[key].split("\n")
            current_proj: dict | None = None
            for line in proj_lines:
                line = line.strip()
                if not line:
                    continue
                if not line.startswith(("•", "-", "·", "*")) and len(line) < 100:
                    if current_proj:
                        projects.append(ProjectEntry(**current_proj))
                    current_proj = {"name": line, "description": "", "tech_used": [], "bullets": []}
                elif current_proj:
                    bullet = re.sub(r"^[•\-·*]\s*", "", line)
                    current_proj["bullets"].append(bullet)
            if current_proj:
                projects.append(ProjectEntry(**current_proj))
            break

    certs: list[str] = []
    for key in ["certifications", "certificates", "licenses"]:
        if key in sections:
            certs = [l.strip() for l in sections[key].split("\n") if l.strip()]
            break

    wc = count_words(text)

    return ParsedResume(
        raw_text=text,
        raw_latex=raw_latex,
        input_format=input_format,
        contact=contact,
        sections=sections,
        latex_sections=None,
        skills=skills,
        experience=experience,
        education=education,
        projects=projects,
        certifications=certs,
        word_count=wc,
        estimated_pages=estimate_pages(wc),
    )
