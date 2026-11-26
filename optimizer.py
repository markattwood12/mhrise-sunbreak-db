"""MH Rise: Sunbreak build optimizer (OR-Tools CP-SAT, runs locally, no cloud).

Usage:
    python3 optimizer.py mhr.sqlite request.json
    python3 optimizer.py mhr.sqlite '{"skills": {"Weakness Exploit": 3}}'

Request fields (all optional except skills):
    skills          {"Skill Name": min_level, ...}   required skill levels
    rank            "MR" | "HR" | "LR"               armor rank pool (default "MR")
    min_rarity      int                              armor rarity floor
    weapon          weapon id or exact name          supplies its deco slots + defense
    weapon_slots    [4, 2]                           if no weapon given
    charm           {"skills": {"Name": lvl}, "slots": [2, 1]}
    exclude         ["piece or series name", ...]
    exclude_decorations ["Expert Jewel+ 4", ...]   decorations you can't craft yet
    max_decorations {"Sprinter Jewel+ 4": 1}       how many of a decoration you own
    require         ["piece name", ...]
    min_resist      {"fire": 0, "dragon": 5, ...}    minimum total resistance
    objective       "defense" (default) | "free_slots" | "bonus_skills"
    bonus_skills    {"Skill Name": weight}           used by objective "bonus_skills"
    top             int                              number of distinct armor combos (default 3)
    time_limit      seconds per solve (default 20)

Not modelled: rampage decorations, qurious crafting / armor augments, set-bonus activation
thresholds beyond plain skill levels (they are reported in the skill effect text).
"""
import json
import sqlite3
import sys

from ortools.sat.python import cp_model

PARTS = ["head", "chest", "arms", "waist", "legs"]
RES = ["fire", "water", "ice", "thunder", "dragon"]


def load(db, req):
    q = lambda sql, *a: db.execute(sql, a).fetchall()
    skills = {n: (sid, mx) for sid, n, mx in q("select id, name, max_level from skill")}
    sid_name = {sid: n for n, (sid, _) in skills.items()}
    for n in list(req.get("skills", {})) + list(req.get("bonus_skills", {})) + list(req.get("charm", {}).get("skills", {})):
        if n not in skills:
            close = [k for k in skills if n.lower() in k.lower()]
            raise SystemExit(f"Unknown skill '{n}'. Did you mean: {close[:5]}")

    rank = req.get("rank", "MR")
    pieces = q("select id,name,series,part,rarity,max_defense,fire,water,ice,thunder,dragon,"
               "slots_lv1,slots_lv2,slots_lv3,slots_lv4,slots from armor_piece where usable=1 and rank=? and rarity>=?",
               rank, req.get("min_rarity", 0))
    excl = {e.lower() for e in req.get("exclude", [])}
    pieces = [p for p in pieces if p[1].lower() not in excl and (p[2] or "").lower() not in excl]
    pskills = {}
    for pid, sid, lv in q("select piece_id, skill_id, level from armor_piece_skill"):
        pskills.setdefault(pid, {})[sid_name[sid]] = lv
    decos = q("select d.name, d.slot_level, s.name, d.skill_level from decoration d join skill s on s.id=d.skill_id")
    xd = set(req.get("exclude_decorations", []))
    decos = [d for d in decos if d[0] not in xd]

    weapon = None
    if "weapon" in req:
        w = q("select id,name,defense,slots from weapon where usable=1 and (id=? or name=?)", req["weapon"], req["weapon"])
        if not w:
            raise SystemExit(f"Weapon not found: {req['weapon']}")
        weapon = {"id": w[0][0], "name": w[0][1], "defense": w[0][2], "slots": json.loads(w[0][3])}
    return skills, pieces, pskills, decos, weapon


def solve(db, req):
    skills, pieces, pskills, decos, weapon = load(db, req)
    targets = req.get("skills", {})
    bonus = req.get("bonus_skills", {})
    charm = req.get("charm", {"skills": {}, "slots": []})
    fixed_slots = (weapon["slots"] if weapon else req.get("weapon_slots", [])) + charm.get("slots", [])
    relevant = set(targets) | set(bonus)

    # prune: pieces/decos that touch no relevant skill only matter for slots/defense -> keep all pieces
    decos = [d for d in decos if d[2] in relevant]

    results, cuts = [], []
    for _ in range(req.get("top", 3)):
        m = cp_model.CpModel()
        x = {p[0]: m.NewBoolVar(f"p{p[0]}") for p in pieces}
        for part in PARTS:
            m.Add(sum(x[p[0]] for p in pieces if p[3] == part) <= 1)
        for name in req.get("require", []):
            ids = [p[0] for p in pieces if p[1] == name]
            if not ids:
                raise SystemExit(f"Required piece not in pool: {name}")
            m.Add(sum(x[i] for i in ids) == 1)
        cap = req.get("max_decorations", {})
        y = {d[0]: m.NewIntVar(0, cap.get(d[0], 20), f"d{i}") for i, d in enumerate(decos)}

        # slot capacity: for each size k, decos needing >= k must fit in slots of size >= k
        for k in (1, 2, 3, 4):
            cap_fixed = sum(1 for s in fixed_slots if s >= k)
            cap_armor = sum(sum(p[11 + j] for j in range(k - 1, 4)) * x[p[0]] for p in pieces)
            m.Add(sum(y[d[0]] for d in decos if d[1] >= k) <= cap_fixed + cap_armor)

        eff = {}
        for sk in relevant:
            total = (sum(pskills.get(p[0], {}).get(sk, 0) * x[p[0]] for p in pieces if sk in pskills.get(p[0], {}))
                     + sum(d[3] * y[d[0]] for d in decos if d[2] == sk) + charm["skills"].get(sk, 0))
            mx = skills[sk][1]
            raw = m.NewIntVar(0, 60, f"raw_{sk}")
            m.Add(raw == total)
            e = m.NewIntVar(0, mx, f"eff_{sk}")
            m.AddMinEquality(e, [raw, mx])
            eff[sk] = e
            if sk in targets:
                m.Add(raw >= min(targets[sk], mx))
        for r, v in req.get("min_resist", {}).items():
            i = 6 + RES.index(r)
            m.Add(sum(p[i] * x[p[0]] for p in pieces) >= v)
        for cut in cuts:
            m.Add(sum(x[i] for i in cut) <= len(cut) - 1)

        defense = sum(p[5] * x[p[0]] for p in pieces)
        used = sum(d[1] * y[d[0]] for d in decos)
        total_cap = sum(sum((j + 1) * p[11 + j] for j in range(4)) * x[p[0]] for p in pieces)
        obj = req.get("objective", "defense")
        if obj == "free_slots":
            m.Maximize((total_cap - used) * 1000 + defense)
        elif obj == "bonus_skills":
            m.Maximize(sum(int(w * 1000) * eff[s] for s, w in bonus.items()) + defense)
        else:
            m.Maximize(defense * 1000 - used)  # tie-break: fewer deco slot-levels used

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = req.get("time_limit", 20)
        solver.parameters.num_workers = 8
        st = solver.Solve(m)
        if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            break
        chosen = [p for p in pieces if solver.Value(x[p[0]])]
        cuts.append([p[0] for p in chosen])
        totals = {}
        for p in chosen:
            for sk, lv in pskills.get(p[0], {}).items():
                totals[sk] = totals.get(sk, 0) + lv
        dec_used = {d[0]: solver.Value(y[d[0]]) for d in decos if solver.Value(y[d[0]])}
        for d in decos:
            if d[0] in dec_used:
                totals[d[2]] = totals.get(d[2], 0) + d[3] * dec_used[d[0]]
        for sk, lv in charm["skills"].items():
            totals[sk] = totals.get(sk, 0) + lv
        all_slots = sorted(fixed_slots + [s for p in chosen for s in json.loads(p[15])], reverse=True)
        results.append({
            "status": "optimal" if st == cp_model.OPTIMAL else "feasible (time limit)",
            "weapon": weapon["name"] if weapon else None,
            "armor": {p[3]: p[1] for p in chosen},
            "max_defense": sum(p[5] for p in chosen) + (weapon["defense"] if weapon else 0),
            "resistances": {r: sum(p[6 + i] for p in chosen) for i, r in enumerate(RES)},
            "decorations": dec_used,
            "slots_total": all_slots,
            "slot_levels_free": sum(all_slots) - sum(d[1] * n for d in decos for k, n in dec_used.items() if k == d[0]),
            "skills": {k: f"{min(v, skills[k][1])}/{skills[k][1]}" + (f" (+{v - skills[k][1]} over)" if v > skills[k][1] else "")
                       for k, v in sorted(totals.items(), key=lambda kv: -kv[1])},
        })
    if not results:
        return {"status": "infeasible", "hint": "No combination reaches the targets; relax a skill, add a charm, or change rank."}
    return results


if __name__ == "__main__":
    db = sqlite3.connect(sys.argv[1])
    arg = sys.argv[2]
    req = json.loads(arg) if arg.lstrip().startswith("{") else json.load(open(arg))
    print(json.dumps(solve(db, req), indent=2, ensure_ascii=False))
