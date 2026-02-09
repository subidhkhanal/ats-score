import re


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines).strip()


def extract_emails(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)


def extract_phones(text: str) -> list[str]:
    patterns = [
        r"\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
        r"\+\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}",
    ]
    phones = []
    for p in patterns:
        phones.extend(re.findall(p, text))
    return phones


def extract_urls(text: str) -> dict[str, list[str]]:
    urls = re.findall(r"https?://[^\s,)>\]]+", text)
    result: dict[str, list[str]] = {"linkedin": [], "github": [], "portfolio": [], "other": []}
    for url in urls:
        url_lower = url.lower()
        if "linkedin.com" in url_lower:
            result["linkedin"].append(url)
        elif "github.com" in url_lower:
            result["github"].append(url)
        else:
            result["other"].append(url)
    return result


def count_words(text: str) -> int:
    return len(text.split())


def estimate_pages(word_count: int) -> int:
    if word_count <= 500:
        return 1
    elif word_count <= 1000:
        return 2
    else:
        return max(1, (word_count + 499) // 500)


def normalize_keyword(keyword: str) -> str:
    return keyword.lower().strip().replace("-", " ").replace(".", "").replace("/", " ")
