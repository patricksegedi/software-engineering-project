# src/smarterspeaker/movies.py
import json
from pathlib import Path
from typing import List, Dict

# 프로젝트 루트 기준 경로 계산
BASE_DIR = Path(__file__).resolve().parents[2]  # .../software-engineering-project
MOVIES_FILE = BASE_DIR / "movies.json"


def load_movies() -> List[Dict]:
    """Load all movies from movies.json."""
    with open(MOVIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def search_movies(query: str) -> List[Dict]:
    """
    Return movies whose title contains the query (case-insensitive).
    If query is empty, return all movies.
    """
    movies = load_movies()
    if not query:
        return movies

    q = query.lower()
    return [m for m in movies if q in m["title"].lower()]
