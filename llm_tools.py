"""Two tools to expose to any LLM/agent framework (local model, ADK, LangChain, MCP server, ...).

    query_db(sql)      read-only SQL against mhr.sqlite (for lookups / questions)
    optimize(request)  CP-SAT build search (see optimizer.py docstring for request fields)

The LLM answers questions with query_db and turns build goals into an optimize() request.
It should never try to search armor combinations itself.
"""
import json
import sqlite3
from pathlib import Path

import optimizer

DB_PATH = Path(__file__).with_name("mhr.sqlite")


def _ro():
    return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)


def query_db(sql: str, max_rows: int = 200) -> str:
    """Run a read-only SQL query. Returns JSON rows (capped)."""
    with _ro() as db:
        cur = db.execute(sql)
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchmany(max_rows)]
    return json.dumps(rows, ensure_ascii=False)


def optimize(request: dict) -> str:
    """Find armor + decoration builds meeting skill targets. Returns JSON results."""
    with _ro() as db:
        return json.dumps(optimizer.solve(db, request), ensure_ascii=False)


TOOL_SPECS = [
    {
        "name": "query_db",
        "description": "Read-only SQLite query over MH Rise: Sunbreak equipment. Tables: skill, skill_level, "
                       "decoration, armor_piece, armor_piece_skill, weapon, charm; views: armor_flat, weapon_flat, "
                       "decoration_flat. Use exact skill names from the skill table.",
        "parameters": {"type": "object", "properties": {"sql": {"type": "string"}}, "required": ["sql"]},
    },
    {
        "name": "optimize",
        "description": "Search all armor + decoration combinations for builds that meet skill targets. Fields: "
                       "skills {name: level} (required), rank, min_rarity, weapon (id or name) or weapon_slots, "
                       "charm {skills, slots}, exclude, require, min_resist, objective "
                       "(defense|free_slots|bonus_skills), bonus_skills {name: weight}, top.",
        "parameters": {"type": "object", "properties": {"request": {"type": "object"}}, "required": ["request"]},
    },
]
