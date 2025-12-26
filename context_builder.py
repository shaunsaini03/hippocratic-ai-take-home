from typing import Dict
from session import StorySession



def build_story_context(
    session: StorySession,
    arc: Dict,
    user_input: str,
    is_continuation: bool
) -> Dict:
    """
    Build a unified context object for the storyteller.
    """

    if is_continuation:
        mode = "continuation"
        story_state = {
            "characters": session.characters,
            "setting": session.setting,
            "summary": session.summary,
            "arc_stage": session.arc_stage,
        }
    else:
        mode = "new_story"
        story_state = None

    context = {
        "mode": mode,
        "arc": arc,
        "feedback": "",
        "story_state": story_state,
        "user_input": user_input,
    }

    return context

