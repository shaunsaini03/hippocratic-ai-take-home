from session import StorySessionManager, get_arc_from_session, persist_session, clear_sessions
from arc_selector import select_arc
from context_builder import build_story_context
from story_teller import generate_story
from judge import evaluate_story
from summarizer import summarize_story
from guardrails import is_relevant_story_prompt


"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

Response:
If I had two additional hours, I would focus on two main improvements. 

First, I would fix the guardrails at the input boundary. My implementation here is very naive, just checking if the text
contains words relevant to the prompt, a more sophisticated way to do this would be guardrails that can quantify relevance
and redirect if below a given threshold. Similarly, I would also refine some of the deterministic heuristics used for routing decisions,
such as expanding the keyword signals used for arc selection. 

Second, I would introduce a lightweight user actions layer to explicitly route user intent. 
At the start of the program I would have a prompt, with options; would you like to write a story, would you like to clear past history.
After this either fails or succeeds, the user would be prompted to try again on failure, or make changes / continue the story on success
I would also like to also have some guardrails for this user actions layer to keep relevance to the prompts and make sure the
language/intent is safe. 


"""

MAX_RETRIES = 3

def prompt_clear_sessions() -> None:
    response = input(
        "Do you want to clear previous story sessions? (y/N): "
    ).strip().lower()

    if response == "y":
        clear_sessions()
        print("Previous sessions cleared.\n")


def main():
    prompt_clear_sessions()
    session_manager = StorySessionManager()

    user_input = input("What kind of story do you want to hear?")

    if not is_relevant_story_prompt(user_input):
        print("Please enter a short description of a children's story you'd like to hear.")
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
    


if __name__ == "__main__":
    main()