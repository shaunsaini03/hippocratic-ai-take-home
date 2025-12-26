from user_actions import user_actions


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



def main():
    user_actions()


if __name__ == "__main__":
    main()