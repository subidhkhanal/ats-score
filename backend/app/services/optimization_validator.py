import re
from app.models.schemas import ValidationResult, LatexValidation
from app.utils.implication_map import get_implied_skills
from app.services.latex_parser import validate_latex_syntax


def extract_skills_from_text(text: str) -> set[str]:
    tech_pattern = r"\b(?:React|Angular|Vue|Next\.js|Node\.js|Python|Java|JavaScript|TypeScript|Go|Rust|Ruby|PHP|Swift|Kotlin|C\+\+|C#|SQL|NoSQL|MongoDB|PostgreSQL|MySQL|Redis|Docker|Kubernetes|AWS|Azure|GCP|Git|GitHub|FastAPI|Django|Flask|Express|Spring|TensorFlow|PyTorch|Pandas|NumPy|GraphQL|REST|gRPC|Kafka|RabbitMQ|Elasticsearch|Terraform|Ansible|Jenkins|HTML|CSS|Sass|Tailwind|Bootstrap|Webpack|Vite|Jest|Cypress|Selenium|Playwright|Firebase|Supabase|Prisma|Sequelize|LangChain|OpenAI|Figma|Linux|Bash|Nginx|Apache|Celery|Airflow|Spark|Hadoop|Snowflake|Databricks|D3|Three\.js|Flutter|Ionic|Electron|Svelte|Remix|Gatsby|Nuxt|Redux|MobX|Zustand|Storybook|dbt|Power BI|Tableau|scikit-learn|BERT|GPT|LLM|NLP|ML|AI|RAG|MCP|CI\/CD|OOP|Agile|Scrum|Microservices|WebSocket|OAuth|JWT)\b"

    found = re.findall(tech_pattern, text, re.IGNORECASE)
    return {s.lower() for s in found}


def extract_numbers(text: str) -> list[str]:
    return re.findall(r"\b\d+(?:\.\d+)?%?\b", text)


def validate_optimization(
    original_text: str,
    optimized_text: str,
    original_skills: set[str],
) -> ValidationResult:
    optimized_skills = extract_skills_from_text(optimized_text)
    allowed_skills = original_skills | get_implied_skills(original_skills)
    allowed_lower = {s.lower() for s in allowed_skills}

    fabricated = optimized_skills - allowed_lower - {s.lower() for s in original_skills}

    if fabricated:
        return ValidationResult(
            valid=False,
            fabricated_skills=list(fabricated),
            message=f"LLM added skills not in original: {fabricated}",
        )

    return ValidationResult(valid=True, message="Validation passed")


def validate_latex_output(tex_content: str) -> LatexValidation:
    result = validate_latex_syntax(tex_content)
    return LatexValidation(valid=result["valid"], errors=result["errors"])
