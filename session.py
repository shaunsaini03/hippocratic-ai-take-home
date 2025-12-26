from dataclasses import dataclass
from typing import Optional, Dict
import uuid
import time
import json
import os
import re
from arc_selector import load_arcs

DATA_DIR = "data"
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")




@dataclass
class StorySession:
    session_id: str
    created_at: float
    last_updated: float

    # Optionally include arc story was generated from
    arc_id: Optional[str]
    arc_stage: Optional[str]

    characters: Dict[str, str] # character name to description
    setting: str    # story setting description
    summary: str  # brief summary of the story so far





def load_sessions() -> dict:
    """
    Load saved story sessions from disk.
    Returns a dict with structure: { "sessions": { ... } }
    """
    if not os.path.exists(SESSIONS_FILE):
        return {"sessions": {}}

    with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    
def save_sessions(data: dict) -> None:
    """
    Persist sessions to disk.
    """
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)



def persist_session(session: StorySession, story: Dict, summary: str, arc: Dict) -> None:
    data = load_sessions()

    data["sessions"][session.session_id] = {
        "updated_at": time.time(),
        "created_at": session.created_at,
        "arc_id": arc["theme"],
        "arc_stage": story['metadata']['current_stage'],
        "characters": story['metadata']['characters'],
        "setting": story['metadata']['setting'],
        "summary": summary,
    }
    save_sessions(data)

def clear_sessions() -> None:
    """
    Reset all saved sessions.
    """
    data = {
        "sessions": {}
        }
    save_sessions(data)


def build_character_index(sessions: dict) -> dict[str, set[str]]:
    index = {}
    for session_id, session in sessions.items():
        for char in session.get("characters", {}).keys():
            index.setdefault(char.lower(), set()).add(session_id)
    return index


def find_candidate_session_ids(
    user_input: str,
    character_index: dict[str, set[str]]
) -> set[str]:
    """
    Return session IDs whose character names appear in the user input.
    """
    text = user_input.lower()
    candidate_ids: set[str] = set()

    for character, session_ids in character_index.items():
        # word-boundary match to avoid partial matches
        if re.search(rf"\b{re.escape(character)}\b", text):
            candidate_ids |= session_ids

    return candidate_ids




def get_arc_from_session(session: StorySession) -> Optional[Dict]:
    # Fail Safe
    if session.arc_id is None:
        return None
    
    arcs_data = load_arcs()
    arc = arcs_data["arcs"][session.arc_id]
    return arc


def prompt_for_session_choice(
    candidate_ids: set[str],
    sessions: dict
) -> str | None:
    """
    Prompt user to choose an existing session or start new.
    Returns chosen session_id or None if starting new.
    """
    print("\nI found existing stories that may match:\n")

    candidates = list(candidate_ids)

    for i, session_id in enumerate(candidates, start=1):
        summary = sessions[session_id].get("summary", "No summary available.")
        print(f"{i}. Session {session_id}")
        print(f"   Summary: {summary}\n")

    print("0. Start a new story")

    while True:
        choice = input("\nChoose a number: ").strip()

        if choice == "0":
            return None

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(candidates):
                return candidates[idx]

        print("Invalid choice. Please try again.")





class StorySessionManager:
    def __init__(self):
        self.current_session: Optional[StorySession] = None

    def handle_user_input(self, user_input: str) -> tuple[StorySession, bool]:
        """
        Returns (session, is_continuation)
        """

        data = load_sessions()
        sessions = data["sessions"]

        
        index = build_character_index(sessions)
        candidate_ids = find_candidate_session_ids(user_input, index)
        if candidate_ids:
            chosen_id = prompt_for_session_choice(candidate_ids, sessions)
            if chosen_id:
                session = self._set_chosen_session(sessions, chosen_id)
                return session, True


        session = self._create_new_session()
        return session, False


    def _set_chosen_session(self, sessions: dict, chosen_id: str) -> StorySession:
        session = StorySession(
            session_id=chosen_id,
            created_at=sessions[chosen_id]["created_at"],
            last_updated=sessions[chosen_id].get("last_updated", sessions[chosen_id]["created_at"]),
            arc_id=sessions[chosen_id].get("arc_id"),
            arc_stage=sessions[chosen_id].get("arc_stage"),
            characters=sessions[chosen_id].get("characters", {}),
            setting=sessions[chosen_id].get("setting", ""),
            summary=sessions[chosen_id].get("summary", ""),
        )
        self.current_session = session
        return session


    def _create_new_session(self) -> StorySession:
        session = StorySession(
            session_id=str(uuid.uuid4()),
            created_at=time.time(),
            last_updated=time.time(),
            characters={},
            setting="",
            arc_id=None,
            arc_stage=None,
            summary="",
        )
        self.current_session = session
        return session
