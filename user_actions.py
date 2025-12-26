from session import StorySessionManager, get_arc_from_session, persist_session, clear_sessions
from arc_selector import select_arc
from context_builder import build_story_context
from story_teller import generate_story
from judge import evaluate_story
from summarizer import summarize_story
from guardrails import is_relevant_story_prompt


MAX_RETRIES = 3

def user_actions() -> None:
    response = input(
        "Do you want to clear previous story sessions, tell a story " \
        "Respond either clear or story: "
    ).strip().lower()


    session_manager = StorySessionManager()
    if response == "clear":
        clear_sessions()
        print("Previous sessions cleared.\n")
        return
    if response == "story":
        user_input = input("What kind of story do you want to hear? Or what story did you want to continue (give description of previous story) and what you want next?: ")
        num_retries = 3
        for i in range(num_retries):
            if is_relevant_story_prompt(user_input):
                break
            user_input = input("Please enter a short description of a children's story you'd like to hear.")
            return
    session, is_continuation = session_manager.handle_user_input(user_input)
    if not is_continuation:
        arc = select_arc(user_input)
    if is_continuation:
        arc = get_arc_from_session(session)
    context = build_story_context(session, arc, user_input, is_continuation)

    for attempt in range(MAX_RETRIES + 1):

        story = generate_story(context)
        judgment = evaluate_story(story, arc)

        if judgment["accept"]:
            break

        context["feedback"] = judgment['feedback']
    
    if not judgment["accept"]:
        print(f"Sorry, we couldn't generate a satisfactory story due to {judgment['failure_reason']}")
        return
    
    else:
        print("Here is your story:")
        print(story["story_text"])
        summary = summarize_story(story['story_text'])
        persist_session(session, story, summary, arc)

        
        


    