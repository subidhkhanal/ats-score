# AI-Powered ATS Score Analyzer — Project Requirements

## Project Overview

Build **ResumeRadar** — an AI-powered Applicant Tracking System (ATS) score analyzer that goes beyond simple keyword matching. It uses **semantic similarity via embeddings**, **LLM-powered analysis**, and **traditional keyword matching** (a hybrid approach) to replicate and exceed what real ATS systems like Greenhouse, Lever, Workday, and iCIMS do.

This is a **full-stack web application** with a Next.js frontend and FastAPI backend.

**Target users**: Job seekers who want to see exactly how their resume scores against a specific job description, the way a FAANG recruiter would see it.

---

## Tech Stack

### Frontend
- **Next.js 14+** (App Router)
- **React 18+**
- **TypeScript**
- **Tailwind CSS** for styling
- **shadcn/ui** for UI components
- **Recharts** for data visualizations (score gauges, radar charts)

### Backend
- **Python 3.11+**
- **FastAPI** with async endpoints
- **Pydantic v2** for request/response validation and structured output schemas
- **python-multipart** for form data handling
- **spaCy** (en_core_web_sm or en_core_web_md) for NLP entity extraction, POS tagging
- **KeyBERT** for keyword extraction from JD and resume
- **RapidFuzz** for fuzzy keyword matching
- **sentence-transformers** (`all-MiniLM-L6-v2`) for semantic embedding generation
- **scikit-learn** for cosine similarity computation
- **Google Gemini API** (`google-generativeai`) for LLM-powered qualitative analysis (free tier)
- **uvicorn** as ASGI server

### Infrastructure
- **Docker** + **docker-compose** for containerized deployment
- **SQLite** (via SQLAlchemy) for storing analysis history locally
- **GitHub Actions** for CI/CD (lint, test, build)

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Next.js Frontend                   │
│  ┌───────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Paste     │  │  Score   │  │  Recruiter       │  │
│  │  LaTeX +   │  │  Dashboard│  │  Simulation View │  │
│  │  Paste JD  │  │  + Charts│  │  (Greenhouse UI) │  │
│  └─────┬─────┘  └────┬─────┘  └────────┬─────────┘  │
│        │              │                  │            │
│        └──────────────┼──────────────────┘            │
│                       │ REST API                      │
└───────────────────────┼───────────────────────────────┘
                        │
┌───────────────────────┼───────────────────────────────┐
│                  FastAPI Backend                       │
│                       │                               │
│  ┌────────────────────▼────────────────────────┐      │
│  │           /api/v1/analyze                    │      │
│  │  Receives LaTeX resume text + JD text          │      │
│  └────────────────────┬────────────────────────┘      │
│                       │                               │
│  ┌────────────────────▼────────────────────────┐      │
│  │        Resume & JD Parser Module             │      │
│  │  - LaTeX text extraction                       │      │
│  │  - Section detection (Education, Skills...)   │      │
│  │  - Contact info extraction (regex + spaCy)    │      │
│  │  - spaCy NER for entities                     │      │
│  └────────────────────┬────────────────────────┘      │
│                       │                               │
│  ┌────────────────────▼────────────────────────┐      │
│  │     Three-Layer Scoring Engine               │      │
│  │                                              │      │
│  │  Layer 1: Keyword Match (40% weight)         │      │
│  │  - KeyBERT extraction from JD                │      │
│  │  - RapidFuzz matching against resume          │      │
│  │  - Required vs Preferred classification       │      │
│  │                                              │      │
│  │  Layer 2: Semantic Similarity (35% weight)   │      │
│  │  - sentence-transformers embeddings           │      │
│  │  - Section-level cosine similarity            │      │
│  │  - Skills, Experience, Education separately   │      │
│  │                                              │      │
│  │  Layer 3: Structure & Format (25% weight)    │      │
│  │  - Section presence check                     │      │
│  │  - Contact info completeness                  │      │
│  │  - Resume length/density analysis             │      │
│  │  - ATS-friendly formatting check              │      │
│  └────────────────────┬────────────────────────┘      │
│                       │                               │
│  ┌────────────────────▼────────────────────────┐      │
│  │      LLM Analysis Module (Gemini)            │      │
│  │  - Qualitative fit assessment                 │      │
│  │  - Bullet point rewrite suggestions           │      │
│  │  - Missing experience gap analysis            │      │
│  │  - Tailored improvement recommendations       │      │
│  │  - Interview readiness score                  │      │
│  └────────────────────┬────────────────────────┘      │
│                       │                               │
│  ┌────────────────────▼────────────────────────┐      │
│  │         Response Aggregator                  │      │
│  │  - Combine all scores into final ATS score    │      │
│  │  - Generate recruiter simulation view         │      │
│  │  - Rank suggestions by impact                 │      │
│  └─────────────────────────────────────────────┘      │
│                                                       │
│  ┌─────────────────────────────────────────────┐      │
│  │         SQLite History (Optional)            │      │
│  │  - Store past analyses for comparison         │      │
│  └─────────────────────────────────────────────┘      │
└───────────────────────────────────────────────────────┘
```

---

## Detailed Feature Requirements

### 1. Resume Input (Frontend)

- **LaTeX Paste**: Textarea for pasting raw LaTeX resume source code
- **LaTeX Badge**: Show a "LaTeX Mode" badge so the user knows the optimizer will output valid LaTeX
- **Character/Word Count**: Show live word count below textarea

### 2. Job Description Input (Frontend)

- **Text Paste**: Textarea for pasting full JD
- **URL Import** (stretch goal): Paste a job URL, backend scrapes and extracts JD text
- **JD Section Detection**: Auto-detect "Required Skills", "Preferred Skills", "Responsibilities" sections
- **Word Count**: Show live word count

### 3. Resume Parser (Backend)

The parser extracts structured data from the resume. It handles **LaTeX input** exclusively.

```python
class ParsedResume(BaseModel):
    raw_text: str                          # plain text extracted from any format
    raw_latex: str | None                  # original LaTeX source (None if input wasn't LaTeX)
    input_format: str                      # "latex"
    contact: ContactInfo                   # name, email, phone, linkedin, github, location
    sections: dict[str, str]               # detected sections and their plain text content
    latex_sections: dict[str, str] | None  # sections with LaTeX markup preserved
    skills: list[str]                      # extracted skills
    experience: list[ExperienceEntry]      # company, role, dates, bullets
    education: list[EducationEntry]        # school, degree, dates
    projects: list[ProjectEntry]           # name, description, tech used
    certifications: list[str]
    word_count: int
    estimated_pages: int
```

**Implementation**:
- Use **spaCy** NER to extract names, organizations, dates, locations
- Use **regex patterns** for email, phone, LinkedIn, GitHub URLs
- Use **heuristic section detection**: scan for common section headers ("EXPERIENCE", "EDUCATION", "SKILLS", "PROJECTS", "ABOUT", "SUMMARY", "CERTIFICATIONS") with fuzzy matching

#### 3.1 LaTeX-Aware Parser (`latex_parser.py`)

When input is detected as LaTeX (contains `\documentclass` or `\begin{document}`), use a specialized parser:

**Detection**:
```python
def is_latex(text: str) -> bool:
    return "\\documentclass" in text or "\\begin{document}" in text
```

**LaTeX Section Extraction** — parse the LaTeX source to extract sections while preserving their LaTeX markup:

```python
class LatexSection(BaseModel):
    name: str              # "EXPERIENCE", "SKILLS", "EDUCATION", etc.
    plain_text: str        # section content with LaTeX stripped (for scoring)
    latex_content: str     # section content with LaTeX preserved (for rewriting)
    start_line: int        # line number where section starts in source
    end_line: int          # line number where section ends
    
class LatexResumeMap(BaseModel):
    """Complete structural map of the LaTeX resume for targeted editing."""
    preamble: str          # everything before \begin{document}
    header: str            # name/contact LaTeX block
    sections: list[LatexSection]
    postamble: str         # \end{document} and anything after
    
    # Granular edit targets
    skills_block: str | None       # raw LaTeX of the skills section
    about_block: str | None        # raw LaTeX of the about/summary section
    experience_entries: list[LatexExperienceEntry] | None
    project_entries: list[LatexProjectEntry] | None
```

**LaTeX Experience Entry Parsing** — extract individual entries with their LaTeX structure:

```python
class LatexExperienceEntry(BaseModel):
    company: str
    role: str
    dates: str
    latex_block: str           # full LaTeX block for this entry
    bullets: list[LatexBullet]

class LatexBullet(BaseModel):
    plain_text: str            # "Developed a Canadian immigration platform"
    latex_text: str            # "\\resumeItem{Developed a {\\href{...}{\\myuline {Canadian immigration platform}}}}"
    line_number: int           # exact line in source file
    
class LatexProjectEntry(BaseModel):
    name: str
    latex_block: str
    bullets: list[LatexBullet]
```

**Parser Implementation Strategy**:

The LaTeX parser should work by recognizing common resume LaTeX patterns. It does NOT need to be a full LaTeX compiler. It should handle these patterns:

```python
# Section detection patterns
SECTION_PATTERNS = [
    r'\\section\{([^}]+)\}',               # \section{SKILLS}
    r'\\section\s*\{([^}]+)\}',            # \section {EDUCATION}
]

# Experience/project entry patterns  
ENTRY_PATTERNS = [
    r'\\resumeSubheading\s*\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}',  # {company}{dates}{role}{location}
    r'\\resumeProjectHeading\s*\{([^}]*)\}\{([^}]*)\}',                       # {name}{dates}
]

# Bullet point patterns
BULLET_PATTERNS = [
    r'\\resumeItem\{(.*?)\}',              # \resumeItem{text}
    r'\\item\s*(.*?)(?=\\item|\\end)',      # \item text
]

# Skills section patterns
SKILLS_PATTERNS = [
    r'\\textbf\{([^}]+)\}\s*\{?:\s*([^}\\]+)',  # \textbf{Front-end} {: Next.js, Material UI}
]

# Contact info patterns (in LaTeX header)
CONTACT_PATTERNS = [
    r'\\texttt\{([^}]*@[^}]*)\}',          # email in \texttt{}
    r'\\texttt\{([+\d-]+)\}',              # phone in \texttt{}
    r'\\href\{([^}]*linkedin[^}]*)\}',      # linkedin href
    r'\\href\{([^}]*github[^}]*)\}',        # github href
]
```

**Plain Text Extraction** (for scoring): Strip all LaTeX commands to get clean text:
```python
def latex_to_plain(latex: str) -> str:
    """Strip LaTeX to plain text for ATS scoring."""
    text = latex
    # Remove comments
    text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)
    # Remove href but keep display text: \href{url}{display} → display
    text = re.sub(r'\\href\{[^}]*\}\{([^}]*)\}', r'\1', text)
    # Remove myuline but keep text: \myuline{text} → text
    text = re.sub(r'\\myuline\s*\{([^}]*)\}', r'\1', text)
    # Remove textbf but keep text: \textbf{text} → text
    text = re.sub(r'\\textbf\{([^}]*)\}', r'\1', text)
    # Remove textit but keep text
    text = re.sub(r'\\textit\{([^}]*)\}', r'\1', text)
    # Remove texttt but keep text
    text = re.sub(r'\\texttt\{([^}]*)\}', r'\1', text)
    # Remove resumeItem wrapper but keep content
    text = re.sub(r'\\resumeItem\{(.*?)\}', r'\1', text, flags=re.DOTALL)
    # Remove remaining commands: \command or \command{...}
    text = re.sub(r'\\[a-zA-Z]+\*?\{[^}]*\}', '', text)
    text = re.sub(r'\\[a-zA-Z]+\*?', '', text)
    # Remove environments
    text = re.sub(r'\\begin\{[^}]*\}', '', text)
    text = re.sub(r'\\end\{[^}]*\}', '', text)
    # Remove special chars
    text = re.sub(r'[{}$\\|]', '', text)
    # Clean up whitespace
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r'  +', ' ', text)
    return text.strip()
```

### 4. JD Parser (Backend)

```python
class ParsedJD(BaseModel):
    raw_text: str
    title: str  # job title
    company: str | None
    required_skills: list[str]
    preferred_skills: list[str]
    responsibilities: list[str]
    qualifications: list[str]
    experience_level: str  # entry, mid, senior, lead
    keywords: list[KeywordWithWeight]  # keyword + importance weight
```

**Implementation**:
- Use **KeyBERT** to extract top-N keywords/keyphrases from the JD (n=30)
- Classify keywords into required vs preferred based on which JD section they appear in
- Use spaCy to extract specific technical terms, tools, frameworks
- Detect experience level from phrases like "X+ years", "entry level", "senior"

### 5. Three-Layer Scoring Engine (Backend)

#### Layer 1: Keyword Match Score (40% of total)

```python
class KeywordMatchResult(BaseModel):
    keyword: str
    category: str  # "required" | "preferred"
    found: bool
    match_type: str  # "exact" | "fuzzy" | "variation" | "not_found"
    match_score: float  # 0.0 to 1.0
    matched_text: str | None  # what text in resume matched
    location_in_resume: str | None  # which section it was found in
```

**Implementation**:
- For each JD keyword, search the resume using:
  1. **Exact match** (case-insensitive) → score 1.0
  2. **Variation match** (e.g., "React.js" ↔ "ReactJS" ↔ "React") using a built-in synonym/variation dictionary → score 0.9
  3. **Fuzzy match** using **RapidFuzz** (threshold >= 85) → score 0.7-0.9
  4. **Not found** → score 0.0
- Weight required keywords at 2x vs preferred keywords
- Final keyword score = weighted average of all keyword match scores

**Variation Dictionary** (maintain a comprehensive one):
```python
VARIATIONS = {
    "react": ["react", "react.js", "reactjs"],
    "node": ["node", "node.js", "nodejs"],
    "next": ["next", "next.js", "nextjs"],
    "vue": ["vue", "vue.js", "vuejs"],
    "typescript": ["typescript", "ts"],
    "javascript": ["javascript", "js", "es6", "es2015"],
    "python": ["python", "python3", "py"],
    "postgresql": ["postgresql", "postgres", "psql"],
    "mongodb": ["mongodb", "mongo"],
    "kubernetes": ["kubernetes", "k8s"],
    "ci/cd": ["ci/cd", "cicd", "ci cd", "continuous integration", "continuous deployment"],
    "oop": ["oop", "object-oriented", "object oriented programming"],
    "rest": ["rest", "restful", "rest api", "rest apis", "restful api"],
    "graphql": ["graphql", "graph ql"],
    "websocket": ["websocket", "websockets", "web socket"],
    "aws": ["aws", "amazon web services"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl"],
    "nlp": ["nlp", "natural language processing"],
    "llm": ["llm", "large language model", "large language models"],
    "docker": ["docker", "containerization", "containers"],
    "full-stack": ["full-stack", "full stack", "fullstack"],
    "front-end": ["front-end", "frontend", "front end"],
    "back-end": ["back-end", "backend", "back end"],
    "async": ["async", "asynchronous", "async/await"],
    "ui/ux": ["ui/ux", "ui ux", "uiux", "user interface", "user experience"],
    # ... extend to 100+ common tech terms
}
```

#### Layer 2: Semantic Similarity Score (35% of total)

```python
class SemanticResult(BaseModel):
    overall_similarity: float  # 0.0 to 1.0
    skills_similarity: float
    experience_similarity: float
    education_similarity: float
    section_similarities: dict[str, float]
```

**Implementation**:
- Load `all-MiniLM-L6-v2` from sentence-transformers (384-dimensional embeddings)
- Generate embeddings for:
  - Full resume text
  - Each resume section separately (skills, experience, education, projects)
  - Full JD text
  - JD required skills section
  - JD responsibilities section
- Compute **cosine similarity** between:
  - Resume skills ↔ JD required skills
  - Resume experience ↔ JD responsibilities
  - Resume education ↔ JD qualifications
  - Full resume ↔ Full JD
- Weighted average: Skills (40%), Experience (35%), Education (15%), Overall (10%)
- Normalize to 0-100 scale

**Why section-level, not full-document**: A single embedding for the entire resume loses granularity. Matching skills-to-skills and experience-to-responsibilities gives much more accurate results (based on Resume2Vec research).

#### Layer 3: Structure & Format Score (25% of total)

```python
class StructureResult(BaseModel):
    contact_score: float  # 0-100
    sections_score: float  # 0-100
    length_score: float  # 0-100
    formatting_score: float  # 0-100
    details: StructureDetails
```

**Checks**:
- **Contact Info** (25 pts):
  - Name detected: 5 pts
  - Email detected: 5 pts
  - Phone detected: 5 pts
  - LinkedIn URL detected: 5 pts
  - GitHub/Portfolio URL detected: 5 pts
- **Section Presence** (25 pts):
  - Has Summary/About: 4 pts
  - Has Experience: 6 pts
  - Has Education: 5 pts
  - Has Skills: 5 pts
  - Has Projects: 5 pts
- **Length & Density** (25 pts):
  - Word count between 300-800 (1 page): 25 pts
  - Word count 200-300 or 800-1000: 15 pts
  - Word count <200 or >1000: 5 pts
- **Formatting** (25 pts):
  - No images/tables that break ATS: 10 pts
  - Standard section headers (not creative names): 10 pts
  - Consistent date formats: 5 pts

### 6. LLM Analysis Module (Backend)

Use **Google Gemini API** (free tier: `gemini-2.5-flash`) for qualitative analysis.

**API Call Structure**:
```python
prompt = f"""
You are an expert ATS analyst and career advisor. Analyze this resume against the job description.

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
  "interview_readiness": 1-10,
  "interview_topics": ["likely interview topics based on JD"],
  "overall_recommendation": "1-2 paragraph actionable recommendation"
}}
"""
```

**Important**: The LLM analysis is a supplement to the quantitative scores, not a replacement. The final ATS score comes from the three-layer engine. The LLM provides the "how to fix it" intelligence.

**Fallback**: If Gemini API is unavailable or rate-limited, the system should still return the quantitative scores and basic rule-based suggestions. The LLM section should be marked as "unavailable" gracefully.

### 7. Response Aggregator (Backend)

```python
class ATSAnalysisResponse(BaseModel):
    # Core Scores
    overall_score: int  # 0-100, weighted combination
    keyword_score: int  # 0-100
    semantic_score: int  # 0-100
    structure_score: int  # 0-100

    # Recruiter Simulation
    recruiter_status: str  # "SHORTLIST" | "REVIEW" | "MAYBE" | "AUTO_REJECTED"
    rank_estimate: str  # "Top 10%" | "Top 25%" | "Top 50%" | "Bottom 50%"

    # Detailed Breakdowns
    keyword_results: list[KeywordMatchResult]
    semantic_results: SemanticResult
    structure_results: StructureResult

    # Parsed Data
    parsed_resume: ParsedResume
    parsed_jd: ParsedJD

    # LLM Analysis
    llm_analysis: LLMAnalysis | None  # None if LLM unavailable

    # Prioritized Suggestions
    suggestions: list[Suggestion]  # sorted by impact

    # Metadata
    analysis_id: str
    analyzed_at: datetime
```

**Score → Status Mapping**:
- 80-100: **SHORTLIST** (Top 10% — recruiter will definitely see this)
- 65-79: **REVIEW** (Top 25% — likely to be seen)
- 50-64: **MAYBE** (Top 50% — depends on applicant volume)
- 0-49: **AUTO_REJECTED** (Bottom 50% — filtered out before human review)

### 8. Frontend Dashboard

#### 8.1 Recruiter Simulation View
Simulate what a recruiter sees in Greenhouse/Lever:
- Candidate card with name, status badge (SHORTLIST/REVIEW/MAYBE/REJECTED)
- Match score prominently displayed
- Quick stats: keywords matched, experience level match
- Make it look like an actual ATS dashboard (dark theme, clean layout)

#### 8.2 Score Overview Tab
- **Large circular gauge** for overall ATS score (animated)
- **Three smaller gauges** for Keyword, Semantic, and Structure scores
- **Radar chart** (using Recharts) showing Skills, Experience, Education, Projects, Format as axes
- Score breakdown explanation

#### 8.3 Keyword Analysis Tab
- Two columns: **Found** (green badges) and **Missing** (red badges)
- Each keyword shows: match type (exact/fuzzy/variation), which resume section it was found in
- Filter by: Required vs Preferred
- Sortable by match confidence

#### 8.4 Semantic Analysis Tab
- **Section-level similarity bars**: Skills (X%), Experience (X%), Education (X%)
- Visual comparison: side-by-side highlight of what matched semantically
- "Your resume talks about X, but the JD emphasizes Y" insights

#### 8.5 Structure Check Tab
- Checklist style: ✅ Contact Info, ✅ Skills Section, ❌ Summary Missing...
- Each item expandable with explanation
- ATS parsing simulation: show what the ATS would extract vs what's actually there

#### 8.6 AI Recommendations Tab (LLM-powered)
- **Prioritized suggestion cards**: High/Medium/Low priority with estimated score impact
- **Bullet Rewrite Tool**: Original → Improved side-by-side comparison
- **Skills Section Rewrite**: One-click copy of optimized skills section
- **Gap Analysis**: What you're missing and how to address it
- **Interview Prep**: Likely interview topics based on the JD

#### 8.7 History & Comparison (stretch goal)
- Save past analyses in SQLite
- Compare score changes between resume versions
- Track improvement over time with line chart

#### 8.8 Auto-Optimize Tab
- **"Optimize My Resume" button**: One-click triggers the optimization pipeline
- **Before/After split view**: Original resume on the left, optimized on the right
- **Diff highlighting**: Green highlights for added keywords, yellow for reworded bullets
- **LaTeX diff view**: Show syntax-highlighted LaTeX diff (green for additions, red for removals)
- **Score comparison bar**: Original score → Optimized score side-by-side with animated transition
- **Section-by-section review**: User can accept/reject each change individually (checkboxes)
- **"Apply Selected Changes" button**: Merges only accepted changes into final version
- **Download options**:
  - Download complete `.tex` file (ready to compile with pdflatex/xelatex)
  - "Copy LaTeX" button to copy the full optimized `.tex` to clipboard
- **Truthfulness guard**: Banner stating "Only your existing skills and experience are used — nothing fabricated"
- **LaTeX badge**: Show "LaTeX Mode — output is a compilable .tex file"

### 9. Auto-Optimize Resume (Backend)

This feature takes the analysis results and automatically rewrites the resume to maximize ATS score **using only the candidate's real experience**. It does NOT fabricate skills or experience.

#### 9.1 How It Works

```
┌──────────────────────────────────────────────────────────┐
│                 Auto-Optimize Pipeline                     │
│                                                           │
│  Step 1: ANALYZE                                          │
│  ├── Run full 3-layer analysis                            │
│  ├── Identify missing keywords                            │
│  ├── Identify weak semantic sections                      │
│  ├── Get structure gaps                                   │
│  └── Map LaTeX structure for targeted editing              │
│                                                           │
│  Step 2: PLAN CHANGES                                     │
│  ├── Map missing keywords → existing experience           │
│  │   (which bullet points COULD mention this keyword?)    │
│  ├── Identify bullets that can be keyword-enriched        │
│  ├── Plan skills section rewrite                          │
│  ├── Plan summary/about section rewrite                   │
│  └── Map each change to exact line numbers in .tex        │
│                                                           │
│  Step 3: REWRITE (LLM — Gemini)                           │
│  ├── Rewrite individual LaTeX blocks in-place             │
│  ├── Rewrite skills section to match JD ordering          │
│  ├── Rewrite summary to align with JD                     │
│  └── Constraint: ONLY use skills/tech already in resume   │
│                                                           │
│  Step 4: VALIDATE                                         │
│  ├── Re-run 3-layer scoring on optimized version          │
│  ├── Verify no new skills were fabricated                 │
│  │   (diff original skills set vs optimized skills set)   │
│  ├── Verify LaTeX output compiles (syntax check)          │
│  ├── Compute score delta                                  │
│  └── If score didn't improve, retry with different prompt │
│                                                           │
│  Step 5: RETURN                                           │
│  ├── Original vs Optimized LaTeX                          │
│  ├── List of all changes with reasons                     │
│  ├── Original score vs New score                          │
│  ├── Per-change accept/reject metadata                    │
│  └── Complete compilable .tex file                        │
└──────────────────────────────────────────────────────────┘
```

#### 9.1.1 LaTeX Optimization Strategy

The optimizer performs **surgical edits directly on the LaTeX source**, preserving all formatting, custom commands, packages, and structure. It does NOT convert to plain text and back.

**Key Principle**: The optimizer only touches content inside `\resumeItem{}`, `\textbf{} {:}` (skills), and `\section{ABOUT}` blocks. It never modifies the preamble, custom commands, margins, fonts, or document structure.

**How LaTeX Rewriting Works**:

```
ORIGINAL LaTeX bullet:
\resumeItem{Developed a {\href{https://www.pathtopr.ca}{\myuline {Canadian immigration platform}}}}

OPTIMIZED LaTeX bullet:
\resumeItem{Developed a full-stack {\href{https://www.pathtopr.ca}{\myuline {Canadian immigration platform}}} using React.js and FastAPI with RESTful API integration}

What changed: Added "full-stack", "React.js", "FastAPI", "RESTful API" — all preserved the \href and \myuline commands intact.
```

**LLM Gets LaTeX Context**: The Gemini prompt includes the raw LaTeX of each section so it can output valid LaTeX:

```python
LATEX_OPTIMIZE_PROMPT = """
You are an expert resume optimizer that works directly with LaTeX source code.

IMPORTANT LATEX RULES:
1. Preserve ALL LaTeX commands exactly: \\href{{}}{{}}, \\myuline{{}}, \\textbf{{}}, \\resumeItem{{}}
2. Do NOT add new LaTeX commands that aren't already in the template
3. Do NOT modify anything outside the content areas (no preamble, no \\documentclass, no margins)
4. Keep all hyperlinks, URLs, and formatting intact
5. Only modify the TEXT CONTENT inside existing LaTeX commands
6. Escape special LaTeX characters: & → \\& , % → \\% , $ → \\$
7. Keep \\vspace, \\hspace, and spacing commands unchanged

ORIGINAL LATEX SKILLS SECTION:
{skills_latex}

OPTIMIZED SKILLS (rewrite ONLY the content after the colons, keep \\textbf and structure):
"""
```

**LaTeX Assembly**: After getting individual optimized blocks from the LLM, reconstruct the full `.tex` file:

```python
def assemble_optimized_latex(
    original_map: LatexResumeMap,
    optimized_about: str | None,
    optimized_skills: str | None, 
    optimized_bullets: dict[int, str],  # line_number → new LaTeX bullet
) -> str:
    """Rebuild complete .tex file with surgical replacements."""
    lines = original_map.raw_latex.splitlines()
    
    # Replace individual bullets by line number
    for line_num, new_bullet in optimized_bullets.items():
        lines[line_num - 1] = new_bullet  # line numbers are 1-indexed
    
    # Replace skills block if optimized
    if optimized_skills:
        for i in range(original_map.skills_section.start_line - 1, 
                       original_map.skills_section.end_line):
            lines[i] = ""  # clear old
        lines[original_map.skills_section.start_line - 1] = optimized_skills
    
    # Replace about block if optimized
    if optimized_about:
        for i in range(original_map.about_section.start_line - 1,
                       original_map.about_section.end_line):
            lines[i] = ""
        lines[original_map.about_section.start_line - 1] = optimized_about
    
    return "\n".join(line for line in lines if line is not None)
```

**LaTeX Syntax Validation** (post-optimization):
```python
def validate_latex_syntax(tex_content: str) -> LatexValidation:
    """Basic syntax checks without requiring a full LaTeX compiler."""
    errors = []
    
    # Check balanced braces
    open_count = tex_content.count('{')
    close_count = tex_content.count('}')
    if open_count != close_count:
        errors.append(f"Unbalanced braces: {open_count} open, {close_count} close")
    
    # Check begin/end environment matching
    begins = re.findall(r'\\begin\{(\w+)\}', tex_content)
    ends = re.findall(r'\\end\{(\w+)\}', tex_content)
    if begins != ends:
        errors.append(f"Mismatched environments: begins={begins}, ends={ends}")
    
    # Check document structure
    if '\\begin{document}' not in tex_content:
        errors.append("Missing \\begin{document}")
    if '\\end{document}' not in tex_content:
        errors.append("Missing \\end{document}")
    
    # Check no broken href commands
    hrefs = re.findall(r'\\href\{[^}]*\}\{[^}]*\}', tex_content)
    # Verify all href are well-formed
    
    return LatexValidation(valid=len(errors) == 0, errors=errors)
```

#### 9.2 Optimization Rules (Truthfulness Guardrails)

These rules are **non-negotiable** and must be enforced both in the LLM prompt and in post-processing validation:

1. **Never add a skill/technology the candidate doesn't already have.** If "React.js" is missing and the resume has no JavaScript frontend work, do NOT add it.
2. **Only surface implicit skills.** If the resume says "Built a web app with Next.js" — adding "React.js" is valid because Next.js is built on React. If it says "Built REST APIs with FastAPI" — adding "Python" is valid because FastAPI is Python.
3. **Reword, don't fabricate.** "Developed a website" → "Developed a responsive web application using React.js with RESTful API integration" is valid ONLY if React and REST are already evidenced elsewhere in the resume.
4. **Preserve meaning.** The core achievement in each bullet must remain the same. Only the phrasing and keyword density changes.
5. **Don't inflate metrics.** If the resume says "grew traffic 200%" — never change to "grew traffic 500%".
6. **Maintain natural language.** Don't keyword-stuff. "Built React.js REST API WebSocket full-stack application" reads like spam. Keep it human.

#### 9.3 LLM Prompt for Optimization

**LLM Prompt for LaTeX Optimization**:
```python
OPTIMIZE_PROMPT_LATEX = """
You are an expert resume optimizer that edits LaTeX source code directly.

Your job is to rewrite specific LaTeX blocks to maximize ATS keyword matching, while preserving ALL LaTeX formatting, commands, and structure.

FULL ORIGINAL LATEX SOURCE:
{raw_latex}

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
5. Do NOT modify \\resumeSubheading, \\resumeProjectHeading structure
6. Only modify TEXT CONTENT inside \\resumeItem{{}}, \\textbf{{}} : content, and the About paragraph
7. Escape special characters: & → \\& , % → \\% , $ → \\$ , # → \\#
8. Keep all \\vspace, \\hspace, spacing commands unchanged
9. \\resumeItem{{}} content must be on a SINGLE line (no line breaks inside)

CONTENT RULES:
1. ONLY use technologies/skills already present or directly implied
2. Preserve factual content — only change phrasing
3. Do NOT inflate metrics or numbers
4. Keep language natural — no keyword stuffing

RESPOND AS JSON:
{{
  "optimized_about": "the full LaTeX content for the ABOUT section (just the paragraph text, no \\section command)",
  "optimized_skills_block": "the full LaTeX for the skills \\begin{{itemize}}...\\end{{itemize}} block",
  "bullet_changes": [
    {{
      "section": "experience" | "projects",
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
"""
```

**Example — How the LaTeX optimizer transforms skills section**:

Input:
```latex
\\textbf{{Front-end}} {{: Next.js, Material UI, Tailwind CSS}}\\\\
\\textbf{{Back-end}} {{: Python, FastAPI}}\\\\
\\textbf{{AI/LLM}} {{: OpenAI API}}\\\\
\\textbf{{Database}} {{: SQL}}
```

Optimized output (for the AI Engineer JD):
```latex
\\textbf{{Front-end}} {{: React.js, Next.js, HTML, CSS, JavaScript, Tailwind CSS, Material UI}}\\\\
\\textbf{{Back-end}} {{: Python, FastAPI, REST APIs, WebSockets}}\\\\
\\textbf{{AI/LLM}} {{: OpenAI API, LangChain, Agentic AI Workflows, Model Context Protocol (MCP)}}\\\\
\\textbf{{Database}} {{: SQL (PostgreSQL, MySQL), MongoDB}}\\\\
\\textbf{{Tools \\& Concepts}} {{: Git, GitHub, Docker, OOP, Async Programming}}
```

Note: React.js and JavaScript are validly added because Next.js implies both. REST APIs is valid because FastAPI implies REST. Only add what's implied or already present.

#### 9.4 Post-Optimization Validation (Backend)

After the LLM returns the optimized content, run these automated checks:

```python
class OptimizationValidator:
    def validate(self, original: ParsedResume, optimized_text: str) -> ValidationResult:
        # 1. Extract skills from optimized version
        optimized_skills = extract_skills(optimized_text)
        original_skills = set(original.skills)
        
        # 2. Check for fabricated skills
        # Allow: original skills + implied skills (from IMPLICATION_MAP)
        allowed_skills = original_skills | get_implied_skills(original_skills)
        fabricated = optimized_skills - allowed_skills
        
        # 3. If fabricated skills found, flag them for removal
        if fabricated:
            return ValidationResult(
                valid=False,
                fabricated_skills=list(fabricated),
                message=f"LLM added skills not in original: {fabricated}"
            )
        
        # 4. Check metrics weren't inflated
        original_numbers = extract_numbers(original.raw_text)
        optimized_numbers = extract_numbers(optimized_text)
        # Flag if any number increased
        
        # 5. Re-score the optimized version
        new_score = run_full_analysis(optimized_text, jd_text)
        
        return ValidationResult(
            valid=True,
            original_score=original_score,
            new_score=new_score.overall_score,
            score_delta=new_score.overall_score - original_score
        )
```

**Skill Implication Map** (subset — expand to 200+ mappings):
```python
IMPLICATION_MAP = {
    "next.js": ["react", "react.js", "javascript", "html", "css", "frontend"],
    "fastapi": ["python", "rest api", "restful", "async", "backend"],
    "django": ["python", "oop", "mvc", "backend", "rest api"],
    "flask": ["python", "rest api", "backend"],
    "express": ["node.js", "javascript", "rest api", "backend"],
    "react native": ["react", "javascript", "mobile"],
    "tensorflow": ["python", "machine learning", "deep learning"],
    "pytorch": ["python", "machine learning", "deep learning"],
    "langchain": ["python", "llm", "ai", "rag"],
    "docker": ["containerization", "devops"],
    "kubernetes": ["docker", "containerization", "devops", "orchestration"],
    "postgresql": ["sql", "database"],
    "mongodb": ["nosql", "database"],
    "aws": ["cloud", "cloud services"],
    "git": ["version control"],
    "github": ["git", "version control"],
    # ... extend extensively
}
```

#### 9.5 Response Schema

```python
class OptimizeResponse(BaseModel):
    # Input format
    input_format: str  # "latex"
    
    # Original vs Optimized
    original_text: str              # plain text version
    optimized_text: str             # plain text version (for display/scoring)
    original_latex: str | None      # original .tex source
    optimized_latex: str | None     # complete optimized .tex file ready to compile
    
    # Score Comparison
    original_score: int
    optimized_score: int
    score_delta: int  # positive = improvement
    
    # Detailed Changes
    changes: list[ResumeChange]
    
    # Validation
    validation: ValidationResult
    latex_validation: LatexValidation | None  # LaTeX syntax check results
    fabricated_skills_removed: list[str]
    
    # Keywords
    keywords_added: list[str]
    keywords_impossible: list[KeywordImpossible]
    
    # Sections (plain text versions for display)
    optimized_summary: str
    optimized_skills: str
    optimized_bullets: list[BulletChange]
    
    # LaTeX-specific sections (for copy/paste into .tex file)
    optimized_about_latex: str | None
    optimized_skills_latex: str | None
    optimized_bullets_latex: list[LatexBulletChange] | None


class ResumeChange(BaseModel):
    section: str  # "summary" | "skills" | "experience" | "projects"
    change_type: str  # "rewrite" | "keyword_add" | "restructure"
    original: str
    optimized: str
    original_latex: str | None  # LaTeX version of original
    optimized_latex: str | None  # LaTeX version of optimized
    line_number: int | None  # line in .tex file (for LaTeX input)
    keywords_added: list[str]
    reason: str
    accepted: bool = True  # user can toggle this in frontend


class LatexBulletChange(BaseModel):
    section: str
    entry_index: int
    bullet_index: int
    original_latex: str        # e.g. \\resumeItem{Developed a platform}
    optimized_latex: str       # e.g. \\resumeItem{Developed a full-stack platform using React.js}
    line_number: int           # exact line in .tex file
    keywords_added: list[str]
    reason: str
    accepted: bool = True


class LatexValidation(BaseModel):
    valid: bool
    errors: list[str]  # e.g. ["Unbalanced braces: 47 open, 46 close"]
```

---

## API Endpoints

```
POST   /api/v1/analyze              # Main analysis endpoint
POST   /api/v1/optimize             # Auto-optimize resume against JD
POST   /api/v1/parse/resume         # Parse resume only (returns structured data)
POST   /api/v1/parse/jd             # Parse JD only (returns structured data)
GET    /api/v1/history               # Get past analyses
GET    /api/v1/history/{id}          # Get specific analysis
DELETE /api/v1/history/{id}          # Delete analysis
GET    /api/v1/health                # Health check
```

### Main Analyze Endpoint

```
POST /api/v1/analyze
Content-Type: application/x-www-form-urlencoded

Fields:
- resume_text: string (required, LaTeX source)
- jd_text: string (required)
- include_llm_analysis: boolean (default: true)

Response: ATSAnalysisResponse (JSON)
```

### Optimize Endpoint

```
POST /api/v1/optimize
Content-Type: application/x-www-form-urlencoded

Fields:
- resume_text: string (required, LaTeX source)
- jd_text: string (required)
- analysis_id: string (optional — reuse existing analysis to skip re-scoring)

Response: OptimizeResponse (JSON)

Flow:
1. If analysis_id provided → load existing analysis from DB
2. Else → run full /analyze first
3. Run optimization pipeline (plan → rewrite → validate)
4. Return original vs optimized with score comparison
```

---

## Project Structure

```
resumeRadar/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx              # Main page
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── ui/                   # shadcn components
│   │   │   ├── ResumeUpload.tsx      # Paste LaTeX resume
│   │   │   ├── JDInput.tsx           # JD textarea
│   │   │   ├── ScoreGauge.tsx        # Circular score gauge
│   │   │   ├── RadarChart.tsx        # Skills radar chart
│   │   │   ├── RecruiterView.tsx     # ATS simulation dashboard
│   │   │   ├── KeywordAnalysis.tsx   # Keyword match table
│   │   │   ├── SemanticAnalysis.tsx  # Similarity breakdown
│   │   │   ├── StructureCheck.tsx    # Section checklist
│   │   │   ├── AIRecommendations.tsx # LLM-powered suggestions
│   │   │   ├── AutoOptimize.tsx     # Auto-optimize tab with diff view
│   │   │   ├── BulletRewriter.tsx    # Original vs improved bullets
│   │   │   └── HistoryView.tsx       # Past analyses
│   │   ├── lib/
│   │   │   ├── api.ts               # API client
│   │   │   ├── types.ts             # TypeScript types
│   │   │   └── utils.ts             # Helpers
│   │   └── hooks/
│   │       └── useAnalysis.ts        # Analysis state hook
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── next.config.js
│
├── backend/
│   ├── app/
│   │   ├── main.py                   # FastAPI app entry
│   │   ├── config.py                 # Settings (API keys, model paths)
│   │   ├── models/
│   │   │   ├── schemas.py            # Pydantic models (all request/response)
│   │   │   └── database.py           # SQLAlchemy models for history
│   │   ├── routers/
│   │   │   ├── analyze.py            # /analyze endpoint
│   │   │   ├── optimize.py           # /optimize endpoint
│   │   │   ├── parse.py              # /parse endpoints
│   │   │   └── history.py            # /history endpoints
│   │   ├── services/
│   │   │   ├── resume_parser.py      # Resume text extraction + structuring
│   │   │   ├── latex_parser.py       # LaTeX-aware resume parser (section/bullet extraction with markup)
│   │   │   ├── latex_assembler.py    # Reassemble optimized .tex file from changed blocks
│   │   │   ├── jd_parser.py          # JD parsing + keyword extraction
│   │   │   ├── keyword_matcher.py    # Layer 1: Keyword matching engine
│   │   │   ├── semantic_scorer.py    # Layer 2: Embedding + similarity
│   │   │   ├── structure_scorer.py   # Layer 3: Format/structure checks
│   │   │   ├── llm_analyzer.py       # Gemini API integration
│   │   │   ├── resume_optimizer.py   # Auto-optimize pipeline (plan → rewrite → validate)
│   │   │   ├── optimization_validator.py  # Truthfulness guardrails + fabrication detection
│   │   │   ├── score_aggregator.py   # Combine all scores
│   │   │   └── suggestion_engine.py  # Generate prioritized suggestions
│   │   └── utils/
│   │       ├── text_processing.py    # Text cleaning, normalization
│   │       ├── variations.py         # Keyword variation dictionary
│   │       ├── implication_map.py    # Skill implication mappings (Next.js → React etc.)
│   │       └── constants.py          # Section headers, tech keywords list
│   ├── tests/
│   │   ├── test_keyword_matcher.py
│   │   ├── test_semantic_scorer.py
│   │   ├── test_resume_parser.py
│   │   ├── test_latex_parser.py
│   │   ├── test_optimizer.py
│   │   ├── test_optimization_validator.py
│   │   └── test_api.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── docker-compose.yml
├── README.md
├── REQUIREMENTS.md                    # This file
└── .github/
    └── workflows/
        └── ci.yml
```

---

## Environment Variables

```env
# Backend (.env)
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_CACHE_DIR=./models           # Cache for sentence-transformers model
DATABASE_URL=sqlite:///./ats_history.db
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=info

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Implementation Priority (Build Order)

### Phase 1: Core Engine (MVP)
1. Backend: Resume parser (LaTeX text extraction)
2. Backend: JD parser (KeyBERT keyword extraction)
3. Backend: Layer 1 — Keyword matching with variations + RapidFuzz
4. Backend: Layer 3 — Structure/format scoring
5. Frontend: LaTeX paste UI, basic score display
6. API: `/analyze` endpoint with keyword + structure scores
7. Frontend: Keyword analysis tab, structure check tab

### Phase 2: Semantic Intelligence
8. Backend: Layer 2 — Sentence-transformer embeddings + cosine similarity
9. Backend: Section-level semantic matching
10. Frontend: Semantic analysis tab with similarity bars
11. Frontend: Score gauges + radar chart

### Phase 3: LLM-Powered Insights
12. Backend: Gemini API integration for qualitative analysis
13. Backend: Bullet rewrite suggestions
14. Backend: Gap analysis + improvement recommendations
15. Frontend: AI Recommendations tab
16. Frontend: Bullet rewriter component

### Phase 4: Polish & Extras
17. Frontend: Recruiter simulation view (Greenhouse-style)
18. Backend + Frontend: Analysis history (SQLite + history page)
19. Docker setup
20. Tests
21. GitHub Actions CI
22. README with screenshots

### Phase 5: Auto-Optimize Resume
23. Backend: `latex_parser.py` — LaTeX section/bullet extractor with line number mapping
24. Backend: `latex_assembler.py` — surgical `.tex` file reassembly from optimized blocks
25. Backend: `implication_map.py` — skill implication dictionary (200+ mappings)
26. Backend: `resume_optimizer.py` — LaTeX optimization pipeline
27. Backend: LaTeX-specific Gemini prompt (Prompt B) with LaTeX preservation rules
28. Backend: `optimization_validator.py` — truthfulness guardrails + LaTeX syntax validation
29. Backend: `/optimize` endpoint — runs analyze → optimize → validate → re-score loop
30. Backend: Tests for LaTeX parser, assembler, optimizer, and validator
31. Frontend: `AutoOptimize.tsx` — before/after split view with LaTeX syntax-highlighted diff
32. Frontend: Accept/reject per-change checkboxes + "Apply Selected" merge logic
33. Frontend: Score comparison animation (original → optimized)
34. Frontend: Download `.tex` file + "Copy LaTeX" button (for LaTeX input)
35. Frontend: Download `.tex` file and "Copy LaTeX" button

---

## Key Design Decisions

### Why Hybrid (Keywords + Semantic + LLM)?
- **Keywords alone** miss semantic matches ("built APIs" should match "REST API development")
- **Semantic alone** can't catch exact technical terms (ATS literally searches for "React.js")
- **LLM alone** is slow, expensive, and not reproducible for scoring
- **Hybrid** gives the best of all three: exact keyword matching like real ATS, semantic understanding for nuance, and LLM for actionable human-readable advice

### Why Gemini (not OpenAI)?
- Free tier with generous limits (15 RPM, 1M tokens/day for Flash)
- Fast inference with `gemini-2.5-flash`
- Structured JSON output mode via response_schema
- If user prefers OpenAI, the `llm_analyzer.py` should be designed with a provider abstraction so swapping is trivial

### Why sentence-transformers locally (not API embeddings)?
- Zero cost — runs on CPU, no API calls needed
- `all-MiniLM-L6-v2` is only 80MB, loads in <2 seconds
- Fast inference: <100ms for a full resume + JD
- Works offline
- Proven accuracy for semantic textual similarity tasks

### Why section-level embeddings?
Based on Resume2Vec research (2025): matching entire documents loses granularity. Breaking both resume and JD into sections (skills↔skills, experience↔responsibilities) and matching section-by-section yields up to 15% better accuracy than whole-document comparison.

---

## Performance Targets

- Full analysis (all 3 layers + LLM): **< 8 seconds**
- Analysis without LLM: **< 2 seconds**
- **Auto-optimize (analyze + rewrite + validate + re-score): < 15 seconds**
- Keyword matching: **< 100ms**
- Semantic scoring: **< 300ms**
- Frontend initial load: **< 2 seconds**

---

## Testing Requirements

- **Unit tests** for each scoring layer (keyword, semantic, structure)
- **Test fixtures**: 3-5 sample resumes + JDs with expected scores (include at least 1 LaTeX resume fixture)
- **Edge cases**: Empty resume, empty JD, non-English text, extremely long documents
- **API tests**: FastAPI TestClient for all endpoints
- **LaTeX parser tests**:
  - Section extraction: verify all sections detected from sample `.tex` file
  - Bullet extraction: verify each `\resumeItem{}` is extracted with correct line number
  - Skills parsing: verify `\textbf{Front-end} {: Next.js, Tailwind}` extracts ["Next.js", "Tailwind"]
  - Contact extraction: verify email, phone, LinkedIn extracted from LaTeX header
  - Plain text conversion: verify `latex_to_plain()` strips all commands cleanly
  - Nested commands: verify `\resumeItem{Built a {\href{url}{\myuline{text}}}}` extracts "Built a text"
  - Edge cases: multi-line `\resumeItem`, escaped braces `\{`, comments `% ignored`
- **LaTeX assembler tests**:
  - Verify optimized `.tex` has same number of `\begin{}`/`\end{}` pairs as original
  - Verify brace balancing after assembly
  - Verify preamble is untouched (byte-for-byte comparison)
  - Verify only targeted lines changed (diff original vs optimized)
- **Optimizer tests**:
  - Fabrication detection: feed a resume with only Python skills, JD asking for React — validator must block React from appearing in optimized output
  - Implication validation: resume has Next.js → optimized version adds React.js → validator must allow it
  - Metric preservation: resume says "200% growth" → optimized must not say "500% growth"
  - Score improvement: optimized version must score higher than original (or equal, never lower)
  - Idempotency: running optimize twice on same input should produce consistent results
  - LaTeX round-trip: original `.tex` → optimize → output `.tex` must compile if original compiled
- **Frontend**: Basic component rendering tests (optional)

---

## UI/UX Guidelines

- **Dark theme** (matches developer/tech aesthetic)
- **Mobile responsive** (many users will check on phone)
- **Loading states**: Skeleton loaders during analysis, progress indicator for LLM
- **Animations**: Score gauges should animate from 0 to final score
- **Copy-to-clipboard**: All suggestions, rewritten bullets, optimized skills section
- **Color coding**: Green (80+), Yellow (60-79), Orange (40-59), Red (0-39)
- **No page reloads**: SPA experience, all in one page with tabs

---

## Future Enhancements (Not in MVP)

- **Level 2 Auto-Generate**: Generate an entirely new ATS-optimized resume from scratch (with user skill confirmation step to prevent fabrication)
- **Job URL Scraper**: Paste LinkedIn/Indeed URL → auto-extract JD
- **Resume Builder**: Generate an ATS-optimized resume from scratch
- **Batch Analysis**: Upload multiple JDs, get a compatibility matrix
- **Chrome Extension**: Analyze while browsing job listings
- **Multi-language**: Support non-English resumes (Hindi, Nepali etc.)
- **Fine-tuned model**: Train a custom classifier on labeled resume-JD pairs
- **Real ATS Integration**: Connect to Greenhouse/Lever APIs for actual recruiter data
- **LaTeX/PDF Export**: Generate the optimized resume directly as a formatted PDF using a clean LaTeX template
