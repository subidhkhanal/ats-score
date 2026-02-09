import re
from dataclasses import dataclass, field


@dataclass
class LatexBullet:
    plain_text: str
    latex_text: str
    line_number: int


@dataclass
class LatexExperienceEntry:
    company: str
    role: str
    dates: str
    latex_block: str
    bullets: list[LatexBullet] = field(default_factory=list)


@dataclass
class LatexProjectEntry:
    name: str
    latex_block: str
    bullets: list[LatexBullet] = field(default_factory=list)


@dataclass
class LatexSection:
    name: str
    plain_text: str
    latex_content: str
    start_line: int
    end_line: int


@dataclass
class LatexResumeMap:
    raw_latex: str
    preamble: str
    header: str
    sections: list[LatexSection] = field(default_factory=list)
    postamble: str = ""
    skills_block: str | None = None
    about_block: str | None = None
    experience_entries: list[LatexExperienceEntry] | None = None
    project_entries: list[LatexProjectEntry] | None = None
    skills_section: LatexSection | None = None
    about_section: LatexSection | None = None


def latex_to_plain(latex: str) -> str:
    text = latex
    text = re.sub(r"%.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\\href\{[^}]*\}\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\myuline\s*\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\textbf\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\textit\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\texttt\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\resumeItem\{(.*?)\}", r"\1", text, flags=re.DOTALL)
    text = re.sub(
        r"\\resumeSubheading\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}",
        r"\1 | \3 | \2 | \4", text,
    )
    text = re.sub(
        r"\\resumeProjectHeading\{([^}]*)\}\{([^}]*)\}",
        r"\1 | \2", text,
    )
    text = re.sub(r"\\section\{([^}]*)\}", r"\n\1\n", text)
    text = re.sub(r"\\[a-zA-Z]+\*?\{[^}]*\}", "", text)
    text = re.sub(r"\\[a-zA-Z]+\*?", "", text)
    text = re.sub(r"\\begin\{[^}]*\}", "", text)
    text = re.sub(r"\\end\{[^}]*\}", "", text)
    text = re.sub(r"[{}$\\|]", "", text)
    text = re.sub(r"\n\s*\n", "\n", text)
    text = re.sub(r"  +", " ", text)
    return text.strip()


def parse_latex_resume(latex_source: str) -> LatexResumeMap:
    lines = latex_source.splitlines()

    # Find \begin{document}
    doc_start = 0
    for i, line in enumerate(lines):
        if "\\begin{document}" in line:
            doc_start = i + 1
            break

    preamble = "\n".join(lines[:doc_start])

    # Find \end{document}
    doc_end = len(lines) - 1
    for i in range(len(lines) - 1, -1, -1):
        if "\\end{document}" in lines[i]:
            doc_end = i
            break

    postamble = "\n".join(lines[doc_end:])

    # Parse sections
    sections: list[LatexSection] = []
    current_section_name = ""
    current_section_start = doc_start
    current_section_lines: list[str] = []
    header_lines: list[str] = []
    found_first_section = False

    for i in range(doc_start, doc_end):
        line = lines[i]
        section_match = re.match(r"\s*\\section\{([^}]+)\}", line)

        if section_match:
            if current_section_name:
                latex_content = "\n".join(current_section_lines)
                sections.append(LatexSection(
                    name=current_section_name,
                    plain_text=latex_to_plain(latex_content),
                    latex_content=latex_content,
                    start_line=current_section_start + 1,
                    end_line=i,
                ))
            elif not found_first_section:
                header_lines = current_section_lines[:]

            found_first_section = True
            current_section_name = section_match.group(1).strip()
            current_section_start = i
            current_section_lines = [line]
        else:
            current_section_lines.append(line)

    # Last section
    if current_section_name:
        latex_content = "\n".join(current_section_lines)
        sections.append(LatexSection(
            name=current_section_name,
            plain_text=latex_to_plain(latex_content),
            latex_content=latex_content,
            start_line=current_section_start + 1,
            end_line=doc_end,
        ))

    # Extract experience entries
    experience_entries = _extract_experience_entries(lines, sections)
    project_entries = _extract_project_entries(lines, sections)

    # Find skills and about sections
    skills_section = None
    about_section = None
    skills_block = None
    about_block = None

    for s in sections:
        name_lower = s.name.lower()
        if "skill" in name_lower or "technologies" in name_lower:
            skills_section = s
            skills_block = s.latex_content
        elif "about" in name_lower or "summary" in name_lower or "objective" in name_lower:
            about_section = s
            about_block = s.latex_content

    return LatexResumeMap(
        raw_latex=latex_source,
        preamble=preamble,
        header="\n".join(header_lines),
        sections=sections,
        postamble=postamble,
        skills_block=skills_block,
        about_block=about_block,
        experience_entries=experience_entries,
        project_entries=project_entries,
        skills_section=skills_section,
        about_section=about_section,
    )


def _extract_experience_entries(
    lines: list[str], sections: list[LatexSection]
) -> list[LatexExperienceEntry]:
    entries: list[LatexExperienceEntry] = []
    exp_section = None
    for s in sections:
        if "experience" in s.name.lower():
            exp_section = s
            break

    if not exp_section:
        return entries

    current_entry: LatexExperienceEntry | None = None
    block_lines: list[str] = []

    for i in range(exp_section.start_line - 1, exp_section.end_line):
        if i >= len(lines):
            break
        line = lines[i]
        subheading_match = re.search(
            r"\\resumeSubheading\s*\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}",
            line,
        )

        if subheading_match:
            if current_entry:
                current_entry.latex_block = "\n".join(block_lines)
                entries.append(current_entry)

            current_entry = LatexExperienceEntry(
                company=subheading_match.group(1),
                role=subheading_match.group(3),
                dates=subheading_match.group(2),
                latex_block="",
            )
            block_lines = [line]
        elif current_entry:
            block_lines.append(line)
            item_match = re.search(r"\\resumeItem\{(.*?)\}", line, re.DOTALL)
            if item_match:
                current_entry.bullets.append(LatexBullet(
                    plain_text=latex_to_plain(item_match.group(1)),
                    latex_text=line.strip(),
                    line_number=i + 1,
                ))

    if current_entry:
        current_entry.latex_block = "\n".join(block_lines)
        entries.append(current_entry)

    return entries


def _extract_project_entries(
    lines: list[str], sections: list[LatexSection]
) -> list[LatexProjectEntry]:
    entries: list[LatexProjectEntry] = []
    proj_section = None
    for s in sections:
        if "project" in s.name.lower():
            proj_section = s
            break

    if not proj_section:
        return entries

    current_entry: LatexProjectEntry | None = None
    block_lines: list[str] = []

    for i in range(proj_section.start_line - 1, proj_section.end_line):
        if i >= len(lines):
            break
        line = lines[i]
        proj_match = re.search(
            r"\\resumeProjectHeading\s*\{([^}]*)\}\{([^}]*)\}", line
        )

        if proj_match:
            if current_entry:
                current_entry.latex_block = "\n".join(block_lines)
                entries.append(current_entry)

            current_entry = LatexProjectEntry(
                name=latex_to_plain(proj_match.group(1)),
                latex_block="",
            )
            block_lines = [line]
        elif current_entry:
            block_lines.append(line)
            item_match = re.search(r"\\resumeItem\{(.*?)\}", line, re.DOTALL)
            if item_match:
                current_entry.bullets.append(LatexBullet(
                    plain_text=latex_to_plain(item_match.group(1)),
                    latex_text=line.strip(),
                    line_number=i + 1,
                ))

    if current_entry:
        current_entry.latex_block = "\n".join(block_lines)
        entries.append(current_entry)

    return entries


def validate_latex_syntax(tex_content: str) -> dict:
    errors = []

    open_count = tex_content.count("{")
    close_count = tex_content.count("}")
    if open_count != close_count:
        errors.append(f"Unbalanced braces: {open_count} open, {close_count} close")

    begins = re.findall(r"\\begin\{(\w+)\}", tex_content)
    ends = re.findall(r"\\end\{(\w+)\}", tex_content)
    if sorted(begins) != sorted(ends):
        errors.append(f"Mismatched environments: begins={begins}, ends={ends}")

    if "\\begin{document}" not in tex_content:
        errors.append("Missing \\begin{document}")
    if "\\end{document}" not in tex_content:
        errors.append("Missing \\end{document}")

    return {"valid": len(errors) == 0, "errors": errors}
