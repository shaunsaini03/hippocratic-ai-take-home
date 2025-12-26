import json
import os
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass
import random

DATA_DIR = "data"
ARCS_FILE = os.path.join(DATA_DIR, "arcs.json")



def load_arcs() -> Dict:
    with open(ARCS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


import random
from typing import Dict

ARC_KEYWORDS = {
    "adventure": [
        "adventure", "quest", "journey", "travel", "explore", "dragon",
        "treasure", "forest", "mountain", "castle", "brave", "hero",
        "knight", "pirate", "map"
    ],

    "friendship": [
        "friend", "friends", "friendship", "kind", "kindness",
        "help", "together", "sharing", "team", "caring",
        "nice", "cooperate", "play", "buddy"
    ],

    "exploration": [
        "explore", "exploration", "discover", "discovery",
        "new place", "unknown", "travel", "journey",
        "island", "space", "ocean", "planet", "map"
    ],

    "problem_solving": [
        "problem", "solve", "solution", "figure out",
        "fix", "build", "create", "plan",
        "think", "idea", "puzzle", "challenge"
    ],

    "kindness": [
        "kind", "kindness", "help", "care", "share",
        "gentle", "nice", "smile", "thank",
        "happy", "helpful", "good deed"
    ],
}


def select_predefined_arc(user_input: str, arcs: Dict) -> Dict:
    """
    Select a predefined arc based on keyword heuristics.
    Falls back to random selection if no keywords match.
    """
    text = user_input.lower()

    # score arcs by keyword matches
    arc_scores = {}
    for arc_id, keywords in ARC_KEYWORDS.items():
        if arc_id not in arcs["arcs"]:
            continue
        arc_scores[arc_id] = sum(1 for word in keywords if word in text)

    # choose best match if any score > 0
    if arc_scores:
        best_arc = max(arc_scores, key=arc_scores.get)
        if arc_scores[best_arc] > 0:
            arc_id = best_arc
        else:
            arc_id = 'exploration'
    else:
        arc_id = 'exploration'

    arc = arcs["arcs"][arc_id]

    return arc



def select_arc(user_input: str) -> Dict:
    """
    Main arc selection entry point.
    """
    arcs = load_arcs()

    return select_predefined_arc(user_input, arcs)


