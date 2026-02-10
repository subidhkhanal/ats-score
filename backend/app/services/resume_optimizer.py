import json
import re
import logging
from app.models.schemas import (
    OptimizeResponse, ResumeChange, BulletChange,
    KeywordImpossible, LatexBulletChange, ValidationResult,
    ParsedResume, ParsedJD, ATSAnalysisResponse,
)
from app.services.latex_parser import parse_latex_resume, LatexResumeMap
from app.services.latex_assembler import assemble_optimized_latex
from app.services.optimization_validator import (
    validate_optimization, validate_latex_output, extract_skills_from_text,
)
from app.services.resume_parser import is_latex, latex_to_plain
from app.config import get_settings

logger = logging.getLogger(__name__)

OPTIMIZE_PROMPT_PLAIN = """You are an expert resume optimizer. Your job is to rewrite resume content to maximize ATS keyword matching against a specific job description, while keeping everything 100% truthful.

ORIGINAL RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

ANALYSIS RESULTS:
- Missing required keywords: {missing_required}
- Missing preferred keywords: {missing_preferred}
- Weak sections (low semantic similarity): {weak_sections}
- Current ATS score: {current_score}%

SKILLS ALREADY IN RESUME (extracted):
{existing_skills}

RULES — YOU MUST FOLLOW THESE:
1. ONLY use technologies/skills that are already present in the resume or are directly implied (e.g., Next.js implies React.js, FastAPI implies Python)
2. Do NOT add any skill or technology the candidate hasn't demonstrated
3. Preserve the factual content of every bullet point — only change phrasing
4. Do NOT inflate any metrics, numbers, or achievements
5. Keep language natural and professional — no keyword stuffing
6. Prioritize adding missing REQUIRED keywords over preferred ones
7. Focus changes on: Skills section, Summary/About section, and Experience bullet points

RESPOND AS JSON:
{{
  "optimized_summary": "rewritten summary/about section aligned to JD",
  "optimized_skills": "rewritten skills section with JD-relevant ordering and grouping",
  "bullet_changes": [
    {{
      "section": "experience",
      "entry_index": 0,
      "bullet_index": 0,
      "original": "original bullet text",
      "optimized": "rewritten bullet with keywords naturally integrated",
      "keywords_added": ["keyword1", "keyword2"],
      "reason": "why this change improves ATS matching"
    }}
  ],
  "keywords_successfully_added": ["list of missing keywords now present"],
  "keywords_impossible_to_add": [
    {{
      "keyword": "keyword that couldn't be added",
      "reason": "why — e.g., candidate has no related experience"
    }}
  ],
  "estimated_new_score": 82,
  "optimization_notes": "brief summary of what was changed and why"
}}

Return ONLY the JSON object."""


OPTIMIZE_PROMPT_LATEX = """You are an expert resume optimizer that edits LaTeX source code directly.

Your job is to rewrite specific LaTeX blocks to maximize ATS keyword matching, while preserving ALL LaTeX formatting, commands, and structure.

JOB DESCRIPTION:
{jd_text}

ANALYSIS RESULTS:
- Missing required keywords: {missing_required}
- Missing preferred keywords: {missing_preferred}
- Current ATS score: {current_score}%

SKILLS ALREADY IN RESUME (extracted):
{existing_skills}

LATEX BLOCKS TO OPTIMIZE:

1. ABOUT SECTION (current LaTeX):
{about_latex}

2. SKILLS SECTION (current LaTeX):
{skills_latex}

3. EXPERIENCE BULLETS (current LaTeX):
{experience_bullets_latex}

4. PROJECT BULLETS (current LaTeX):
{project_bullets_latex}

CRITICAL LATEX RULES:
1. Output VALID LaTeX that compiles — balanced braces, proper escaping
2. PRESERVE all existing commands: \\href{{}}{{}}, \\myuline{{}}, \\resumeItem{{}}, \\textbf{{}}
3. PRESERVE all hyperlinks and URLs exactly as they are
4. Do NOT add new LaTeX packages or custom commands
5. Only modify TEXT CONTENT inside \\resumeItem{{}}, \\textbf{{}} : content, and the About paragraph
6. Escape special characters: & → \\& , % → \\%
7. \\resumeItem{{}} content must be on a SINGLE line

CONTENT RULES:
1. ONLY use technologies/skills already present or directly implied
2. Preserve factual content — only change phrasing
3. Do NOT inflate metrics or numbers
4. Keep language natural — no keyword stuffing

RESPOND AS JSON:
{{
  "optimized_about": "the full LaTeX content for the ABOUT section",
  "optimized_skills_block": "the full LaTeX for the skills block",
  "bullet_changes": [
    {{
      "section": "experience",
      "entry_index": 0,
      "bullet_index": 0,
      "original_latex": "\\\\resumeItem{{original text here}}",
      "optimized_latex": "\\\\resumeItem{{optimized text with keywords}}",
      "keywords_added": ["keyword1", "keyword2"],
      "reason": "why this change improves ATS matching"
    }}
  ],
  "keywords_successfully_added": ["list of missing keywords now present"],
  "keywords_impossible_to_add": [
    {{
      "keyword": "keyword",
      "reason": "why it couldn't be added truthfully"
    }}
  ],
  "optimization_notes": "brief summary of changes"
}}

Return ONLY the JSON object."""


def _parse_json(text: str) -> dict:
    text = text.strip()
    json_match = re.search(r"\{[\s\S]*\}", text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


async def optimize_resume(
    resume_text: str,
    jd_text: str,
    analysis: ATSAnalysisResponse,
    raw_latex: str | None = None,
) -> OptimizeResponse:
    settings = get_settings()
    is_latex_input = raw_latex is not None and is_latex(raw_latex)
    input_format = "latex" if is_latex_input else "plain"

    # Get missing keywords
    missing_required = [
        r.keyword for r in analysis.keyword_results
        if not r.found and r.category == "required"
    ]
    missing_preferred = [
        r.keyword for r in analysis.keyword_results
        if not r.found and r.category == "preferred"
    ]
    existing_skills = analysis.parsed_resume.skills
    weak_sections = [
        k for k, v in analysis.semantic_results.section_similarities.items()
        if v < 50
    ]

    # Call LLM for optimization
    llm_result = await _call_optimization_llm(
        resume_text=resume_text,
        jd_text=jd_text,
        missing_required=missing_required,
        missing_preferred=missing_preferred,
        existing_skills=existing_skills,
        current_score=analysis.overall_score,
        weak_sections=weak_sections,
        is_latex=is_latex_input,
        raw_latex=raw_latex,
    )

    if not llm_result:
        return OptimizeResponse(
            input_format=input_format,
            original_text=resume_text,
            optimized_text=resume_text,
            original_score=analysis.overall_score,
            optimized_score=analysis.overall_score,
            score_delta=0,
            validation=ValidationResult(valid=False, message="LLM optimization failed"),
        )

    # Build optimized text
    optimized_text = resume_text
    optimized_latex = None
    latex_validation = None
    changes: list[ResumeChange] = []
    bullet_changes: list[BulletChange] = []
    latex_bullet_changes: list[LatexBulletChange] | None = None

    optimized_summary = llm_result.get("optimized_summary", "") or llm_result.get("optimized_about", "")
    optimized_skills = llm_result.get("optimized_skills", "") or llm_result.get("optimized_skills_block", "")

    if is_latex_input and raw_latex:
        latex_map = parse_latex_resume(raw_latex)
        optimized_bullets_map: dict[int, str] = {}
        latex_bullet_changes = []

        for bc in llm_result.get("bullet_changes", []):
            if isinstance(bc, dict) and "optimized_latex" in bc:
                line_num = 0
                section = bc.get("section", "experience")
                entry_idx = bc.get("entry_index", 0)
                bullet_idx = bc.get("bullet_index", 0)

                entries = latex_map.experience_entries if section == "experience" else latex_map.project_entries
                if entries and entry_idx < len(entries):
                    entry = entries[entry_idx]
                    if bullet_idx < len(entry.bullets):
                        line_num = entry.bullets[bullet_idx].line_number

                if line_num > 0:
                    optimized_bullets_map[line_num] = bc["optimized_latex"]
                    latex_bullet_changes.append(LatexBulletChange(
                        section=section,
                        entry_index=entry_idx,
                        bullet_index=bullet_idx,
                        original_latex=bc.get("original_latex", ""),
                        optimized_latex=bc["optimized_latex"],
                        line_number=line_num,
                        keywords_added=bc.get("keywords_added", []),
                        reason=bc.get("reason", ""),
                    ))

        optimized_latex = assemble_optimized_latex(
            latex_map,
            optimized_about=optimized_summary if optimized_summary else None,
            optimized_skills=optimized_skills if optimized_skills else None,
            optimized_bullets=optimized_bullets_map if optimized_bullets_map else None,
        )
        optimized_text = latex_to_plain(optimized_latex)
        latex_validation = validate_latex_output(optimized_latex)
    else:
        for bc in llm_result.get("bullet_changes", []):
            if isinstance(bc, dict):
                bullet_changes.append(BulletChange(
                    section=bc.get("section", "experience"),
                    entry_index=bc.get("entry_index", 0),
                    bullet_index=bc.get("bullet_index", 0),
                    original=bc.get("original", ""),
                    optimized=bc.get("optimized", ""),
                    keywords_added=bc.get("keywords_added", []),
                    reason=bc.get("reason", ""),
                ))

        if optimized_summary:
            optimized_text = _replace_section(optimized_text, "summary", optimized_summary)
            optimized_text = _replace_section(optimized_text, "about", optimized_summary)
        if optimized_skills:
            optimized_text = _replace_section(optimized_text, "skills", optimized_skills)

        for bc in bullet_changes:
            if bc.original and bc.optimized:
                optimized_text = optimized_text.replace(bc.original, bc.optimized)

    # Build changes list
    if optimized_summary:
        changes.append(ResumeChange(
            section="summary",
            change_type="rewrite",
            original="",
            optimized=optimized_summary if not is_latex_input else latex_to_plain(optimized_summary),
            original_latex=None,
            optimized_latex=optimized_summary if is_latex_input else None,
            keywords_added=[],
            reason="Aligned summary with job description",
        ))

    if optimized_skills:
        changes.append(ResumeChange(
            section="skills",
            change_type="rewrite",
            original="",
            optimized=optimized_skills if not is_latex_input else latex_to_plain(optimized_skills),
            original_latex=None,
            optimized_latex=optimized_skills if is_latex_input else None,
            keywords_added=[],
            reason="Reordered and aligned skills with JD requirements",
        ))

    # Validate
    original_skills_set = set(s.lower() for s in existing_skills)
    validation = validate_optimization(resume_text, optimized_text, original_skills_set)

    keywords_added = llm_result.get("keywords_successfully_added", [])
    keywords_impossible = [
        KeywordImpossible(keyword=k.get("keyword", ""), reason=k.get("reason", ""))
        for k in llm_result.get("keywords_impossible_to_add", [])
        if isinstance(k, dict)
    ]

    return OptimizeResponse(
        input_format=input_format,
        original_text=resume_text,
        optimized_text=optimized_text,
        original_latex=raw_latex,
        optimized_latex=optimized_latex,
        original_score=analysis.overall_score,
        optimized_score=llm_result.get("estimated_new_score", analysis.overall_score + 5),
        score_delta=llm_result.get("estimated_new_score", analysis.overall_score + 5) - analysis.overall_score,
        changes=changes,
        validation=validation,
        latex_validation=latex_validation,
        fabricated_skills_removed=validation.fabricated_skills,
        keywords_added=keywords_added,
        keywords_impossible=keywords_impossible,
        optimized_summary=optimized_summary if not is_latex_input else latex_to_plain(optimized_summary),
        optimized_skills=optimized_skills if not is_latex_input else latex_to_plain(optimized_skills),
        optimized_bullets=bullet_changes,
        optimized_about_latex=optimized_summary if is_latex_input else None,
        optimized_skills_latex=optimized_skills if is_latex_input else None,
        optimized_bullets_latex=latex_bullet_changes,
    )


def _replace_section(text: str, section_name: str, new_content: str) -> str:
    lines = text.split("\n")
    result: list[str] = []
    in_section = False
    replaced = False

    for line in lines:
        line_lower = line.strip().lower()
        if section_name.lower() in line_lower and not in_section:
            in_section = True
            result.append(line)
            result.append(new_content)
            replaced = True
            continue

        if in_section:
            if line.strip() and line.strip().isupper() and len(line.strip().split()) <= 4:
                in_section = False
                result.append(line)
            continue

        result.append(line)

    if not replaced:
        return text

    return "\n".join(result)


async def _call_optimization_llm(
    resume_text: str,
    jd_text: str,
    missing_required: list[str],
    missing_preferred: list[str],
    existing_skills: list[str],
    current_score: int,
    weak_sections: list[str],
    is_latex: bool = False,
    raw_latex: str | None = None,
) -> dict | None:
    settings = get_settings()
    if not settings.gemini_api_key:
        logger.warning("No Gemini API key, skipping optimization")
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        if is_latex and raw_latex:
            latex_map = parse_latex_resume(raw_latex)

            exp_bullets = ""
            if latex_map.experience_entries:
                for entry in latex_map.experience_entries:
                    for bullet in entry.bullets:
                        exp_bullets += f"  Line {bullet.line_number}: {bullet.latex_text}\n"

            proj_bullets = ""
            if latex_map.project_entries:
                for entry in latex_map.project_entries:
                    for bullet in entry.bullets:
                        proj_bullets += f"  Line {bullet.line_number}: {bullet.latex_text}\n"

            prompt = OPTIMIZE_PROMPT_LATEX.format(
                jd_text=jd_text[:3000],
                missing_required=", ".join(missing_required),
                missing_preferred=", ".join(missing_preferred),
                existing_skills=", ".join(existing_skills),
                current_score=current_score,
                about_latex=latex_map.about_block or "No about section found",
                skills_latex=latex_map.skills_block or "No skills section found",
                experience_bullets_latex=exp_bullets or "No experience bullets found",
                project_bullets_latex=proj_bullets or "No project bullets found",
            )
        else:
            prompt = OPTIMIZE_PROMPT_PLAIN.format(
                resume_text=resume_text[:4000],
                jd_text=jd_text[:3000],
                missing_required=", ".join(missing_required),
                missing_preferred=", ".join(missing_preferred),
                weak_sections=", ".join(weak_sections),
                current_score=current_score,
                existing_skills=", ".join(existing_skills),
            )

        response = model.generate_content(prompt)
        return _parse_json(response.text)

    except Exception as e:
        logger.error(f"Optimization LLM call failed: {e}")
        return None
