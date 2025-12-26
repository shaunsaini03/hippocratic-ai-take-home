

def is_relevant_story_prompt(text: str) -> bool:
    if not text or len(text.strip()) < 5:
        return False

    text = text.lower()

    story_indicators = [
        "story", "tell", "about", "adventure", "once upon",
        "dog", "cat", "bear", "child", "kid", "animal",
        "friend", "journey"
    ]

    return any(word in text for word in story_indicators)
