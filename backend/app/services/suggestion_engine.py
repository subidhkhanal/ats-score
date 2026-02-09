from app.models.schemas import (
    Suggestion, KeywordMatchResult, StructureResult,
    SemanticResult, LLMAnalysis,
)


def generate_suggestions(
    keyword_results: list[KeywordMatchResult],
    structure_results: StructureResult,
    semantic_results: SemanticResult,
    llm_analysis: LLMAnalysis | None,
) -> list[Suggestion]:
    suggestions: list[Suggestion] = []

    # Missing required keywords
    missing_required = [
        r for r in keyword_results
        if not r.found and r.category == "required"
    ]
    if missing_required:
        keywords = ", ".join([r.keyword for r in missing_required[:5]])
        suggestions.append(Suggestion(
            priority="high",
            category="keywords",
            title="Add Missing Required Keywords",
            description=f"Your resume is missing these required keywords: {keywords}. Add them naturally to your skills or experience sections.",
            estimated_impact=min(15, len(missing_required) * 3),
        ))

    # Missing preferred keywords
    missing_preferred = [
        r for r in keyword_results
        if not r.found and r.category == "preferred"
    ]
    if missing_preferred:
        keywords = ", ".join([r.keyword for r in missing_preferred[:5]])
        suggestions.append(Suggestion(
            priority="medium",
            category="keywords",
            title="Add Preferred Keywords",
            description=f"Consider adding these preferred keywords: {keywords}",
            estimated_impact=min(8, len(missing_preferred) * 2),
        ))

    # Structure improvements
    details = structure_results.details
    if not details.has_summary:
        suggestions.append(Suggestion(
            priority="high",
            category="structure",
            title="Add a Professional Summary",
            description="Add a 2-3 sentence summary at the top of your resume tailored to this role.",
            estimated_impact=5,
        ))

    if not details.has_linkedin:
        suggestions.append(Suggestion(
            priority="low",
            category="structure",
            title="Add LinkedIn URL",
            description="Include your LinkedIn profile URL in the contact section.",
            estimated_impact=2,
        ))

    if not details.has_github:
        suggestions.append(Suggestion(
            priority="low",
            category="structure",
            title="Add GitHub/Portfolio Link",
            description="Include a link to your GitHub or portfolio to showcase your work.",
            estimated_impact=2,
        ))

    if details.word_count < 300:
        suggestions.append(Suggestion(
            priority="high",
            category="structure",
            title="Expand Resume Content",
            description=f"Your resume is only {details.word_count} words. Aim for 400-700 words with detailed bullet points.",
            estimated_impact=8,
        ))
    elif details.word_count > 1000:
        suggestions.append(Suggestion(
            priority="medium",
            category="structure",
            title="Condense Resume",
            description=f"Your resume is {details.word_count} words. Try to keep it under 800 words for a single-page format.",
            estimated_impact=4,
        ))

    # Semantic improvements
    if semantic_results.skills_similarity < 0.5:
        suggestions.append(Suggestion(
            priority="high",
            category="semantic",
            title="Align Skills with Job Requirements",
            description="Your skills section has low similarity to the job requirements. Reorder and rephrase skills to match the JD language.",
            estimated_impact=10,
        ))

    if semantic_results.experience_similarity < 0.4:
        suggestions.append(Suggestion(
            priority="medium",
            category="semantic",
            title="Tailor Experience Descriptions",
            description="Your experience descriptions don't closely match the job responsibilities. Rewrite bullets to use similar language as the JD.",
            estimated_impact=8,
        ))

    # LLM suggestions
    if llm_analysis:
        for gap in llm_analysis.gaps[:3]:
            suggestions.append(Suggestion(
                priority="medium",
                category="gaps",
                title="Address Experience Gap",
                description=gap,
                estimated_impact=5,
            ))

        for kw_add in llm_analysis.missing_keywords_to_add[:3]:
            if isinstance(kw_add, dict):
                suggestions.append(Suggestion(
                    priority="high",
                    category="keywords",
                    title=f"Add '{kw_add.get('keyword', '')}'",
                    description=f"Add to {kw_add.get('where', 'skills')} section: {kw_add.get('how', '')}",
                    estimated_impact=3,
                ))

    # Sort by impact
    suggestions.sort(key=lambda s: s.estimated_impact, reverse=True)
    return suggestions
