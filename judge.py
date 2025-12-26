import json
from typing import Dict
from call_model import call_model


PROMPTS_DIR = "prompts"


ALLOWED_FAILURE_REASONS = {
    "age_inappropriate",
    "arc_misalignment",
    "unclear_prompt",
    "low_creativity"
}

def build_judge_prompt(story: Dict, arc: Dict) -> str:
    with open(f"{PROMPTS_DIR}/judge.txt", "r", encoding="utf-8") as f:
        template = f.read()

    return template.format(
        arc_theme=arc["theme"],
        arc_description=arc["description"],
        arc_stage=story["metadata"]["current_stage"],
        story_text=story["story_text"],
        allowed_failure_reasons=", ".join(sorted(ALLOWED_FAILURE_REASONS))
    )



def parse_judge_output(output: str) -> Dict:
    try:
        data = json.loads(output)
    except json.JSONDecodeError as e:
        raise ValueError(f"Judge output is not valid JSON: {e}")

    if not isinstance(data, dict):
        raise ValueError("Judge output must be a JSON object")

    scores = data.get("scores")
    if not isinstance(scores, dict):
        raise ValueError("scores must be an object")

    required_scores = ["age_appropriateness", "arc_alignment", "creativity"]
    for key in required_scores:
        if key not in scores:
            raise ValueError(f"Missing score: {key}")
        if not isinstance(scores[key], int) or not (1 <= scores[key] <= 5):
            raise ValueError(f"Score '{key}' must be an integer between 1 and 5")

    overall_pass = data.get("overall_pass")
    if not isinstance(overall_pass, bool):
        raise ValueError("overall_pass must be a boolean")

    failure_reason = data.get("failure_reason", None)
    if failure_reason is not None:
        if not isinstance(failure_reason, str):
            raise ValueError("failure_reason must be a string or null")
        if failure_reason not in ALLOWED_FAILURE_REASONS:
            raise ValueError(f"Invalid failure_reason: {failure_reason}")

    feedback = data.get("feedback", None)
    if overall_pass:
        if feedback not in (None, "") and not isinstance(feedback, str):
            raise ValueError("feedback must be a string, null, or empty when overall_pass is true")
        if failure_reason is not None:
            raise ValueError("failure_reason must be null when overall_pass is true")
    else:
        if not isinstance(feedback, str) or not feedback.strip():
            raise ValueError("feedback must be a non-empty string when overall_pass is false")

    min_score = min(scores.values())
    if min_score < 3 and overall_pass:
        raise ValueError("overall_pass cannot be true when any score is below 3")

    return {
        "scores": scores,
        "overall_pass": overall_pass,
        "feedback": feedback,
        "failure_reason": failure_reason,
    }





def evaluate_story(
    story: Dict,
    arc: Dict,
) -> Dict:
    """
    Returns:
    {
      "accept": bool,
      "feedback": str,
      "scores": dict,
      "failure_reason": str (optional)
    }
    """
    prompt = build_judge_prompt(story, arc)
    raw_output = call_model(prompt)

    result = parse_judge_output(raw_output)

    if result["overall_pass"]:
        return {
            "accept": True,
            "feedback": "",
            "scores": result["scores"],
            "failure_reason": result['failure_reason']
        }
    return {
        "accept": False,
        "scores": result["scores"],
        "feedback": result["feedback"],
        "failure_reason": result['failure_reason']
    }

