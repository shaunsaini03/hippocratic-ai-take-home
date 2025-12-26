import json
import os
from typing import Dict
from call_model import call_model

PROMPTS_DIR = "prompts"


def load_prompt(mode: str) -> str:
    filename = (
        "story_teller_continue.txt"
        if mode == "continuation"
        else "story_teller_new.txt"
    )
    with open(f"{PROMPTS_DIR}/{filename}", "r") as f:
        return f.read()



def build_storyteller_prompt(context: Dict) -> str:
    mode = context["mode"]
    template = load_prompt(mode)

    feedback = context["feedback"]
    feedback_section = (
        f"Judge Feedback (use this to improve the story):\n{feedback}\n"
        if feedback
        else ""
    )

    if mode == "new_story":
        # For new stories, we don't have prior story state
        return template.format(
            arc_theme=context["arc"]["theme"],
            arc_description=context["arc"]["description"],
            arc_stages=", ".join(context["arc"]["stages"]),
            user_input=context["user_input"],
            feedback_section=feedback_section,
        )
    elif mode == "continuation":
        return template.format(
            characters=json.dumps(context["story_state"]["characters"], indent=2),
            setting=context["story_state"]["setting"],
            summary=context["story_state"]["summary"],
            arc_stage=context["story_state"]["arc_stage"],
            arc_theme=context["arc"]["theme"],
            arc_description=context["arc"]["description"],
            arc_stages=", ".join(context["arc"]["stages"]),
            user_input=context["user_input"],
            feedback_section=feedback_section,
        )


def parse_storyteller_output(output: str) -> Dict:
    """
    Parse and validate storyteller JSON output.
    """
    try:
        data = json.loads(output)

        # Top-level validation
        if not isinstance(data, dict):
            raise ValueError("Top-level JSON must be an object")

        if "story_text" not in data or "metadata" not in data:
            raise ValueError("Missing required top-level fields")

        metadata = data["metadata"]
        if not isinstance(metadata, dict):
            raise ValueError("metadata must be an object")

        # Required metadata fields (UPDATED)
        required_metadata_fields = [
            "characters",
            "setting",
            "summary",
            "current_stage",
        ]

        for field in required_metadata_fields:
            if field not in metadata:
                raise ValueError(f"Missing metadata field: {field}")

        # Type checks (defensive, but lightweight)
        if not isinstance(metadata["characters"], dict):
            raise ValueError("characters must be an object")

        if not isinstance(metadata["setting"], str):
            raise ValueError("setting must be a string")

        if not isinstance(metadata["summary"], str):
            raise ValueError("summary must be a string")

        if not isinstance(metadata["current_stage"], str):
            raise ValueError("current_stage must be a string")

        if not isinstance(data["story_text"], str):
            raise ValueError("story_text must be a string")

        return data

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    except Exception as e:
        raise ValueError(f"Invalid storyteller output: {e}")



def generate_story(context: Dict) -> Dict:
    """
    Generate a story and structured metadata.
    This function is intentionally simple:
    - build prompt
    - call LLM
    - parse output
    Judge handles validation and retries.
    """
    prompt = build_storyteller_prompt(context)
    raw_output = call_model(prompt)
    data = parse_storyteller_output(raw_output)
    print(data)
    return data


