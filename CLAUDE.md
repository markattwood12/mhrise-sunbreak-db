# MH Rise: Sunbreak equipment DB — instructions for Claude

This repo is Mark's personal Monster Hunter Rise: Sunbreak data + build optimizer. Everything runs locally (SQLite + OR-Tools); no cloud services.

## Setup in a fresh session
```
pip install --break-system-packages -q ortools   # or: pip install -r requirements.txt
```

## How to answer questions
- Lookups (stats, skills, recipes, drops): query `mhr.sqlite` with SQL (`python3 scripts/q.py mhr.sqlite "select ..."` or `llm_tools.query_db`). Prefer the views `weapon_flat`, `armor_flat`, `decoration_flat`. Filter `usable = 1` on base tables.
- Builds: never hand-search armor combinations. Call `optimizer.solve(db, request)` (see the docstring in `optimizer.py`). Start from `data/player_state.json`: its talisman, owned armor (`require`), decoration limits (`max_decorations`), and the pool filters (`exclude` / `exclude_decorations` from the JSON files it names).
- Verify any build the optimizer returns by recounting skills and slot fit before presenting it, and present it as a slot-by-slot table.

## Data caveats
- Source: mhrice (game files, v16). Base-game weapons and MR armor were cross-checked against Kiranico-derived data.
- `armor_piece.max_defense` is computed from the upgrade table.
- Chaotic Gore weapons: `affinity` is the base (negative) value; the Frenzy value is in `type_details`.
- Decoration recipes/materials are in `data/reference/deco_materials.json`; afflicted material drop monsters in `data/reference/afflicted_sources.json`.
- Anomaly/qurious tables come from community sources (TU3 infographic, Sljm8D cheat sheet); level ranges may differ in the final game version.
- Not modelled by the optimizer: rampage decorations, qurious armor augments.

## Keeping it current
When Mark reports progress (rank, research level, new gear or jewels), update `data/player_state.json` and the `data/progress/` filters, and commit.
