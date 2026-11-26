# MH Rise: Sunbreak equipment DB + build optimizer

Everything runs locally: SQLite (built into Python) + Google OR-Tools CP-SAT (open source, `pip install ortools`).
No cloud services, no API keys. Optimizer solves typical requests in under a second on a laptop.

## Files
| File | What it is |
|---|---|
| `mhr.sqlite` | Normalized database (source of truth) |
| `optimizer.py` | CP-SAT set builder (CLI + importable) |
| `llm_tools.py` | `query_db()` + `optimize()` wrappers and tool specs for an agent |
| `CLAUDE.md` | How Claude should use this repo |
| `data/player_state.json` | Current progress, talisman, owned gear and jewel limits |
| `data/progress/*.json` | Armor/decoration exclusion lists by progression point |
| `data/csv/` | Flat exports for spreadsheets / pasting into prompts |
| `data/mhr_dump.sql` | Full text dump (`sqlite3 new.sqlite < data/mhr_dump.sql`) |
| `data/reference/` | Decoration recipes and afflicted-material drop monsters |
| `scripts/` | `parse_mhrice.py` + `schema.sql` (rebuild from mhrice pages), `load_cheatsheet.py`, `q.py` |
| `sources/` | Cheat sheet image used for transcription |

## Coverage (game version 16, final Sunbreak update)
- 3,925 usable weapons (all 14 types, LR/HR/MR) — attack, affinity, defense, element(s), slots, rampage slot,
  sharpness (base and Handicraft max, points out of 400), rampage skills, and type details
  (phial, shelling, kinsect level, bow charge/arc shots, bowgun ammo table/recoil/reload, horn melodies).
- 1,366 usable armor pieces — base and max defense, resistances, slots, skills.
- 147 skills with per-level effects; 244 decorations (slot size, skill points).
- `usable = 0` rows are unnamed placeholders, `#Rejected#` unused game entries, or layered-only armor.

## Source and validation
Data extracted from game files by the mhrice project (mhrise.mhrice.info, by wwylele; please credit it).
Cross-checks: all 1,860 base-game weapons matched an independent Kiranico scrape on attack, defense,
slots, rarity and sharpness (1 affinity and 3 dual-element ordering differences); 542 of 547 MR armor
pieces matched Kiranico-derived data exactly (Risen Mizuha defense differs, 125 vs 120, likely a later patch).
`max_defense` is computed from each series' upgrade table.

## Optimizer
```
python3 optimizer.py mhr.sqlite '{"weapon":"Titanfeller","skills":{"Weakness Exploit":3,"Critical Boost":3,"Attack Boost":4},"top":3}'
```
Model: one binary per armor piece (≤1 per body part), integer count per decoration, and slot capacity
enforced as "decorations needing size ≥ k fit in slots of size ≥ k" for k = 1..4 (exact for nested slot sizes).
Objectives: max defense, max free slot levels, or weighted bonus skills. `top` returns distinct armor combos.

Not modelled yet: rampage decorations, qurious crafting / armor augments, your talisman inventory
(pass a charm inline, or fill the `charm` table and extend the request).

## Added tables (Nov 2026)
| Table | Source |
|---|---|
| `afflicted_material` | TU3 anomaly infographic (levels) + game data (monsters) |
| `anomaly_monster` | Sljm8D cheat sheet: rank, XP, HP range, rampage species ("anti_deco"), weakness |
| `qurious_material_upgrade` | Sljm8D cheat sheet: material -> augment points and the weapon augment it unlocks |
| `qurious_upgrade`, `qurious_upgrade_cost` | Sljm8D cheat sheet: augment slots used and material options per augment |
| `cheatsheet_note` | Sheet notes plus transcription notes (2 label typos resolved) |

Chaotic Gore Magala weapons: `affinity` is the base (negative) value; `type_details.affinity_after_overcoming_frenzy` holds the positive one.
Optimizer gained `exclude_decorations` and `max_decorations` (jewel inventory limits).
`load_cheatsheet.py` rebuilds the cheat-sheet tables; `mhr_dump.sql` is a full text dump (`sqlite3 new.sqlite < mhr_dump.sql`).
