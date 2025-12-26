import json
from typing import Dict
from call_model import call_model

PROMPTS_DIR = "prompts"


def build_summarize_prompt(story_text: str) -> str:
    with open(f"{PROMPTS_DIR}/summarizer.txt", "r", encoding="utf-8") as f:
        template = f.read()

    return template.format(
        story_text=story_text,
    )


def parse_summary_output(output: str) -> str:
    """
    Parse and validate summarizer JSON output.
    Expected format:
    {
      "summary": "1–2 sentence summary"
    }
    """
    try:
        data = json.loads(output)

        if "summary" not in data:
            raise ValueError("Missing 'summary' field")

        if not isinstance(data["summary"], str):
            raise ValueError("'summary' must be a string")

        summary = data["summary"].strip()
        if not summary:
            raise ValueError("'summary' cannot be empty")

        return summary

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from summarizer: {e}")

    except Exception as e:
        raise ValueError(f"Invalid summarizer output: {e}")


def summarize_story(story_text: str ) -> str:
    """
    Generate a compact, structured summary for long-term memory.
    """
    prompt = build_summarize_prompt(story_text)
    raw_output = call_model(prompt)
    return parse_summary_output(raw_output)
