import json
import re
import logging
from app.models.schemas import LLMAnalysis
from app.config import get_settings

logger = logging.getLogger(__name__)


ANALYSIS_PROMPT = """You are an expert ATS analyst and career advisor. Analyze this resume against the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

QUANTITATIVE SCORES (already computed):
- Keyword Match: {keyword_score}%
- Semantic Similarity: {semantic_score}%
- Structure Score: {structure_score}%

Provide your analysis as JSON with these fields:
{{
  "qualitative_fit": "strong_match" | "good_match" | "partial_match" | "weak_match",
  "fit_explanation": "2-3 sentence explanation of overall fit",
  "strengths": ["list of 3-5 strengths this candidate has for this role"],
  "gaps": ["list of 3-5 gaps or missing qualifications"],
  "bullet_rewrites": [
    {{
      "original": "original bullet from resume",
      "improved": "rewritten bullet optimized for this JD",
      "reason": "why this is better"
    }}
  ],
  "missing_keywords_to_add": [
    {{
      "keyword": "keyword to add",
      "where": "which section to add it in",
      "how": "suggested phrasing"
    }}
  ],
  "skills_section_rewrite": "optimized skills section text for this JD",
  "interview_readiness": 7,
  "interview_topics": ["likely interview topics based on JD"],
  "overall_recommendation": "1-2 paragraph actionable recommendation"
}}

Return ONLY the JSON object, no other text."""


def _parse_llm_json(text: str) -> dict:
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


async def analyze_with_llm(
    resume_text: str,
    jd_text: str,
    keyword_score: int,
    semantic_score: int,
    structure_score: int,
) -> LLMAnalysis | None:
    settings = get_settings()
    if not settings.gemini_api_key:
        logger.warning("No Gemini API key configured, skipping LLM analysis")
        return None

    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        prompt = ANALYSIS_PROMPT.format(
            resume_text=resume_text[:4000],
            jd_text=jd_text[:3000],
            keyword_score=keyword_score,
            semantic_score=semantic_score,
            structure_score=structure_score,
        )

        response = model.generate_content(prompt)
        result = _parse_llm_json(response.text)

        if not result:
            logger.warning("Failed to parse LLM response")
            return None

        return LLMAnalysis(
            qualitative_fit=result.get("qualitative_fit", "partial_match"),
            fit_explanation=result.get("fit_explanation", ""),
            strengths=result.get("strengths", []),
            gaps=result.get("gaps", []),
            bullet_rewrites=result.get("bullet_rewrites", []),
            missing_keywords_to_add=result.get("missing_keywords_to_add", []),
            skills_section_rewrite=result.get("skills_section_rewrite", ""),
            interview_readiness=result.get("interview_readiness", 5),
            interview_topics=result.get("interview_topics", []),
            overall_recommendation=result.get("overall_recommendation", ""),
        )

    except Exception as e:
        logger.error(f"LLM analysis failed: {e}")
        return None
