"""Parse downloaded mhrice.info pages into a normalized SQLite database.

Usage: python3 -I parse_mhrice.py <pages_dir> <out.sqlite>
Source: http://mhrise.mhrice.info (data extracted from MH Rise: Sunbreak game files, v16).
"""
import html
import json
import re
import sqlite3
import sys
from pathlib import Path

PAGES = Path(sys.argv[1])
OUT = Path(sys.argv[2])

PART_BY_ICON = {"000": "head", "001": "chest", "002": "arms", "003": "waist", "004": "legs"}
WEAPON_TYPE = {
    "GreatSword": "Great Sword", "LongSword": "Long Sword", "ShortSword": "Sword & Shield",
    "DualBlades": "Dual Blades", "Hammer": "Hammer", "Horn": "Hunting Horn", "Lance": "Lance",
    "GunLance": "Gunlance", "SlashAxe": "Switch Axe", "ChargeAxe": "Charge Blade",
    "InsectGlaive": "Insect Glaive", "LightBowgun": "Light Bowgun", "HeavyBowgun": "Heavy Bowgun",
    "Bow": "Bow",
}
SHARP_COLORS = ["red", "orange", "yellow", "green", "blue", "white", "purple"]
SHARP_SCALE = 4  # bar width % * 4 = sharpness points (bar = 400 points)


def en_only(t: str) -> str:
    t = re.sub(r'<span class="mh-lang" lang="(?!en")[^"]*"><span>.*?</span></span>', "", t, flags=re.S)
    return t


def text(s: str) -> str:
    s = re.sub(r"<img[^>]*alt=\"([^\"]*)\"[^>]*>", r" \1 ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def section(t: str, sid: str) -> str:
    m = re.search(rf'<section id="{sid}">(.*?)</section>', t, re.S)
    return m.group(1) if m else ""


def kv(stat_html: str) -> dict:
    return {k: v for k, v in re.findall(r'<p class="mh-kv"><span>(.*?)</span><span>(.*?)</span></p>', stat_html, re.S)}


def slots(s: str) -> list:
    return [int(x) for x in re.findall(r'alt="A level-(\d) slot"', s)]


def rows(table_html: str) -> list:
    body = re.search(r"<tbody>(.*?)</tbody>", table_html, re.S)
    if not body:
        return []
    out = []
    for tr in re.findall(r"<tr>(.*?)</tr>", body.group(1), re.S):
        out.append(re.findall(r"<td>(.*?)</td>(?=<td>|$)", tr, re.S))
    return out


def rank_of(rarity: int) -> str:
    return "LR" if rarity <= 3 else ("HR" if rarity <= 7 else "MR")


def skills_in(cell: str) -> list:
    out = []
    for href, rest in re.findall(r'href="skill/(PlayerSkill_\d+)\.html".*?</a></div>\s*\+\s*(\d+)', cell, re.S):
        out.append((href, int(rest)))
    return out


db = sqlite3.connect(OUT)
db.executescript(open(Path(__file__).with_name("schema.sql")).read())

# ---------------- skills + decorations ----------------
for f in sorted(PAGES.glob("skill_PlayerSkill_*.html")):
    sid = f.stem.replace("skill_", "")
    t = en_only(f.read_text())
    name = text(re.search(r"<h1>(.*?)</h1>", t, re.S).group(1))
    desc_sec = section(t, "s-description")
    m = re.search(r"<pre>(.*?)</pre>", desc_sec, re.S)
    desc = text(m.group(1)) if m else ""
    levels = re.findall(r"<li><span>Level (\d+): </span><span>(.*?)</span></li>", desc_sec, re.S)
    db.execute("INSERT INTO skill VALUES (?,?,?,?)", (sid, name, len(levels), desc))
    for lv, d in levels:
        db.execute("INSERT INTO skill_level VALUES (?,?,?)", (sid, int(lv), text(d)))
    for r in rows(section(t, "s-decoration")):
        dname = text(r[0])
        slot_lv = int(re.search(r"(\d)$", dname).group(1))
        db.execute(
            "INSERT INTO decoration VALUES (?,?,?,?,?,?)",
            (dname, slot_lv, sid, int(text(r[1])), text(r[2]), text(r[4])),
        )

# ---------------- armor ----------------
for f in sorted(PAGES.glob("armor_*.html")):
    raw = f.read_text()
    t = en_only(raw)
    series_id = f.stem.replace("armor_", "")
    series = text(re.search(r"<h1>(.*?)</h1>", t, re.S).group(1))
    stat = section(t, "s-stat")
    if not stat:
        continue
    # upgrade table -> per-level defense gain and max level
    upg = section(t, "s-upgrade")
    max_level, def_gain = 1, []
    for r in rows(upg):
        cells = [text(c) for c in r]
        m = re.match(r"Up to (\d+)", cells[0]) if cells else None
        if m:
            top = int(m.group(1))
            def_gain.append((top, int(cells[2])))
            max_level = max(max_level, top)
    for r in rows(stat):
        if len(r) < 10:
            continue
        icon = re.search(r"resources/equip/(\d{3})\.r\.png", r[0])
        part = PART_BY_ICON.get(icon.group(1)) if icon else None
        rar = int(re.search(r"mh-rarity-color-(\d+)", r[0]).group(1))
        name = text(r[0])
        base_def = int(text(r[2]))
        # walk levels 2..max_level adding per-level gain for the bracket
        max_def, lvl = base_def, 1
        for top, gain in def_gain:
            while lvl < top:
                lvl += 1
                max_def += gain
        sl = slots(r[8])
        cur = db.execute(
            "INSERT INTO armor_piece (name,series_id,series,part,rarity,rank,base_defense,max_defense,max_level,"
            "fire,water,ice,thunder,dragon,slots,slots_lv1,slots_lv2,slots_lv3,slots_lv4,usable) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (name, series_id, series, part, rar, rank_of(rar), base_def, max_def, max_level,
             *[int(text(r[i])) for i in range(3, 8)], json.dumps(sl),
             *[sl.count(i) for i in (1, 2, 3, 4)], bool(name) and base_def > 0),
        )
        pid = cur.lastrowid
        for sk, lv in skills_in(r[9]):
            db.execute("INSERT INTO armor_piece_skill VALUES (?,?,?)", (pid, sk, lv))

# ---------------- weapons ----------------
for f in sorted(PAGES.glob("weapon_*.html")):
    raw = f.read_text()
    t = en_only(raw)
    wid = f.stem.replace("weapon_", "")
    wtype = WEAPON_TYPE[wid.split("_")[0]]
    main = t[t.find("<main>"):]
    name = text(re.search(r"<h1>(.*?)</h1>", main, re.S).group(1))
    rar = int(re.search(r"mh-rarity-color-(\d+)", main).group(1))
    st = kv(section(t, "s-stat"))
    sl = slots(st["Slot"])
    rsl = slots(st["Rampage Slot"])
    elems = []
    if "Element" in st:
        ev = text(st["Element"])
        elems = re.findall(r"(Fire|Water|Thunder|Ice|Dragon|Poison|Blast|Paralyze|Sleep) (\d+)", ev)
        elems = [(e, int(v)) for e, v in elems[::1]]
        # text() keeps both alt and label text -> each element appears as "Fire Fire 19"; de-dup
    sharp = {}
    if "Sharpness" in st:
        bars = re.findall(r'mh-sharpness mh-sharpness-color-(\d)" style="left:[\d.]+%;width:([\d.]+)%', st["Sharpness"])
        half = re.findall(r'mh-sharpness-color-(\d) mh-sharpness-half" style="left:[\d.]+%;width:([\d.]+)%', st["Sharpness"])
        base = [0] * 7
        for c, w in bars:
            base[int(c)] = round(float(w) * SHARP_SCALE)
        hc = [0] * 7
        for c, w in half:
            if int(c) < 7:
                hc[int(c)] = round(float(w) * SHARP_SCALE)
        mx = [b + h for b, h in zip(base, hc)]
        sharp = {"base": base, "max": mx}
    extra = {}
    for k in ["Phial", "Shelling", "Insect level", "Deviation", "Reload", "Recoil", "Cluster bomb type",
              "Special ammo", "Default charge lv", "Charge shot", "Arc shot"]:
        if k in st:
            extra[k.lower().replace(" ", "_")] = text(st[k])
    if "/" in text(st["Affinity"]):
        extra["affinity_note"] = text(st["Affinity"])
    ammo = section(t, "s-ammo")
    if ammo:
        extra["ammo"] = [
            {"ammo": text(r[0]), "capacity": int(text(r[1]) or 0), "shot_type": text(r[2])}
            for r in rows(ammo) if text(r[0]) != "<None>"
        ]
    mel = section(t, "s-melody")
    if mel:
        extra["melody"] = [x for x in (text(li) for li in re.findall(r"<li>(.*?)</li>", mel, re.S)) if x]
    ramp = section(t, "s-rampage")
    ramp_skills = [text(li) for li in re.findall(r"<li>(.*?)</li>", ramp, re.S)]
    craft = section(t, "s-crafting") + section(t, "s-upgrade")
    obtainable = bool(re.search(r"\d+z", text(craft)))
    rejected = "#Rejected#" in text(section(t, "s-description")) or name.startswith("#Rejected#")
    usable = bool(name) and not rejected and int(text(st["Attack"])) > 1
    db.execute(
        "INSERT INTO weapon (id,name,type,rarity,rank,attack,affinity,defense,element1,element1_value,element2,"
        "element2_value,slots,slots_lv1,slots_lv2,slots_lv3,slots_lv4,rampage_slot_level,sharpness_base,"
        "sharpness_max,sharp_red,sharp_orange,sharp_yellow,sharp_green,sharp_blue,sharp_white,sharp_purple,"
        "sharp_max_white,sharp_max_purple,rampage_skills,type_details,obtainable,usable) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (wid, name, wtype, rar, rank_of(rar), int(text(st["Attack"])), int(re.match(r"-?\d+", text(st["Affinity"])).group(0)),
         int(text(st["Defense"])),
         elems[0][0] if elems else None, elems[0][1] if elems else None,
         elems[1][0] if len(elems) > 1 else None, elems[1][1] if len(elems) > 1 else None,
         json.dumps(sl), *[sl.count(i) for i in (1, 2, 3, 4)], rsl[0] if rsl else None,
         json.dumps(sharp.get("base")) if sharp else None, json.dumps(sharp.get("max")) if sharp else None,
         *(sharp["base"] if sharp else [None] * 7),
         sharp["max"][5] if sharp else None, sharp["max"][6] if sharp else None,
         json.dumps(ramp_skills), json.dumps(extra), obtainable, usable),
    )

db.commit()
print({t: db.execute(f"select count(*) from {t}").fetchone()[0]
       for t in ["skill", "skill_level", "decoration", "armor_piece", "armor_piece_skill", "weapon"]})
