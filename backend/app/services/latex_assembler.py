from app.services.latex_parser import LatexResumeMap


def assemble_optimized_latex(
    original_map: LatexResumeMap,
    optimized_about: str | None = None,
    optimized_skills: str | None = None,
    optimized_bullets: dict[int, str] | None = None,
) -> str:
    lines = original_map.raw_latex.splitlines()

    # Replace individual bullets by line number
    if optimized_bullets:
        for line_num, new_bullet in optimized_bullets.items():
            idx = line_num - 1  # line numbers are 1-indexed
            if 0 <= idx < len(lines):
                lines[idx] = new_bullet

    # Replace skills block if optimized
    if optimized_skills and original_map.skills_section:
        start = original_map.skills_section.start_line - 1
        end = original_map.skills_section.end_line

        # Keep the \section line, replace content
        section_line = lines[start]
        for i in range(start, min(end, len(lines))):
            lines[i] = None  # type: ignore

        # Reconstruct: section header + new content
        lines[start] = section_line + "\n" + optimized_skills

    # Replace about block if optimized
    if optimized_about and original_map.about_section:
        start = original_map.about_section.start_line - 1
        end = original_map.about_section.end_line

        section_line = lines[start]
        for i in range(start, min(end, len(lines))):
            lines[i] = None  # type: ignore

        lines[start] = section_line + "\n" + optimized_about

    return "\n".join(line for line in lines if line is not None)
