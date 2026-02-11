import json
import re


def parse_llm_json(text: str) -> dict:
    """Extract and parse a JSON object from LLM response text."""
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
