"""Transcription of 'Afflicted Materials Cheat Sheet (final update)' by Sljm8D (r/MHRise).
Source image: https://i.redd.it/i7yl1cui3f9b1.png  (copy in sources/)
Usage: python3 load_cheatsheet.py mhr.sqlite
"""
import sqlite3, sys
db = sqlite3.connect(sys.argv[1])

# rank, group, xp_low, xp_high, monster, hp_min, hp_max, anti_deco (species), weakness
M = [
("A1",1,180,324,"Volvidon",45220,48260,"Fanged Beast","Water"),
("A1",1,180,324,"Arzuros",46860,49560,"Fanged Beast","Fire"),
("A1",1,180,324,"Lagombi",50040,52560,"Fanged Beast","Fire"),
("A1",2,180,324,"Kulu-Ya-Ku",54450,57750,"Wyvern","Water"),
("A1",2,180,324,"Great Baggi",55500,58500,"Wyvern","Fire"),
("A1",2,180,324,"Great Izuchi",55500,58500,"Wyvern","Thunder"),
("A1",2,180,324,"Great Wroggi",55500,58500,"Wyvern","Ice"),
("A2",3,220,374,"Basarios",48260,51300,"Wyvern; Aerial","Fire/Dragon"),
("A2",3,220,374,"Barroth",51120,54000,"Wyvern","Water/Fire"),
("A2",3,220,374,"Royal Ludroth",59770,62780,"Wyvern; Aquatic","Fire"),
("A2",3,220,374,"Aknosom",60750,63900,"Wyvern; Aerial","Water"),
("A2",4,220,374,"Khezu",50040,52560,"Wyvern; Aerial","Fire"),
("A2",4,220,374,"Daimyo Hermitaur",54450,57750,"Aquatic","Thunder/Fire"),
("A2",4,220,374,"Bishaten",56700,59640,"Fanged Beast","Ice"),
("A2",4,220,374,"Tetranadon",58950,62550,"Aquatic","Thunder"),
("A3",5,270,432,"Anjanath",60000,64000,"Wyvern","Water"),
("A3",5,270,432,"Pukei-Pukei",71750,75850,"Wyvern; Aerial","Thunder"),
("A3",5,270,432,"Tobi-Kadachi",75920,80600,"Wyvern","Water"),
("A3",5,270,432,"Rathian",78750,83250,"Wyvern; Aerial","Dragon"),
("A3",6,270,432,"Shogun Ceanataur",60000,64000,"Aquatic","Thunder/Fire"),
("A3",6,270,432,"Blood Orange Bishaten",61320,65100,"Fanged Beast","Water"),
("A3",6,270,432,"Jyuratodus",65700,69750,"Wyvern; Aquatic","Water/Thunder"),
("A3",6,270,432,"Somnacanth",65700,69750,"Wyvern; Aquatic","Thunder"),
("A4",7,320,480,"Nargacuga",61320,65100,"Wyvern; Aerial","Thunder"),
("A4",7,320,480,"Garangolm",61500,65600,"Fanged Beast","Thunder"),
("A4",7,320,480,"Barioth",63000,67200,"Wyvern; Aerial","Fire"),
("A4",7,320,480,"Magnamalo",65700,69750,"Wyvern","Water"),
("A4",8,320,480,"Almudron",64500,68800,"Wyvern; Aquatic","Fire"),
("A4",8,320,480,"Aurora Somnacanth",65700,69750,"Wyvern; Aquatic","Fire"),
("A4",8,320,480,"Goss Harag",70080,74400,"Fanged Beast","Fire"),
("A4",8,320,480,"Rakna-Kadaki",75920,80600,"None","Ice"),
("A5",9,380,532,"Seregios",61200,64600,"Wyvern; Aerial","Thunder"),
("A5",9,380,532,"Zinogre",77550,82250,"Wyvern","Ice"),
("A5",9,380,532,"Diablos",81000,85500,"Wyvern; Aerial","Ice"),
("A5",10,380,532,"Tigrex",81000,85500,"Wyvern; Aerial","Thunder"),
("A5",10,380,532,"Lunagaron",86400,91200,"Wyvern","Fire"),
("A5",10,380,532,"Magma Almudron",86400,91200,"Wyvern; Aquatic","Water"),
("A5",11,380,532,"Astalos",81000,85500,"Wyvern; Aerial","Ice"),
("A5",11,380,532,"Mizutsune",86400,91200,"Wyvern; Aquatic","Thunder"),
("A5",11,380,532,"Rathalos",88200,93100,"Wyvern; Aerial","Dragon"),
("A6",12,440,572,"Espinas",74000,76000,"Wyvern; Aerial","Ice"),
("A6",12,440,572,"Gore Magala",83250,87750,"Aerial","Fire"),
("A6",12,440,572,"Bazelgeuse",85100,89700,"Wyvern; Aerial","Thunder"),
("A6",13,440,572,"Rajang",74375,78625,"Fanged Beast","Ice"),
("A6",13,440,572,"Pyre Rakna-Kadaki",85000,90000,"None","Water"),
("A7",14,500,650,"Gold Rathian",87750,92250,"Wyvern; Aerial","Thunder"),
("A7",14,500,650,"Silver Rathalos",87750,92250,"Wyvern; Aerial","Water"),
("A7",15,500,650,"Flaming Espinas",81900,86100,"Wyvern; Aerial","Water"),
("A7",15,500,650,"Chaotic Gore Magala",92250,96750,"Aerial","Fire/Dragon"),
("A7",15,500,650,"Seething Bazelgeuse",93600,98400,"Wyvern; Aerial","Ice"),
("A7",16,500,650,"Furious Rajang",74000,78000,"Fanged Beast","Ice"),
("A7",16,500,650,"Scorned Magnamalo",91650,96350,"Wyvern","Water"),
("A8",17,560,728,"Risen Teostra",68800,73100,"Aerial","Water"),
("A8",17,560,728,"Risen Chameleos",72000,76500,"Aerial","Fire"),
("A8",17,560,728,"Risen Kushala",72000,76500,"Aerial","Thunder"),
("A9",18,620,806,"Risen Shagaru Magala",76500,81000,"Aerial","Dragon"),
("A9",18,620,806,"Risen Valstrax",79900,84600,"Aerial","Not Dragon"),
]

# group, level range, material (sheet short name), augment points, upgrade it unlocks, qty
Q = [
(1,"1-30","Bone",2,"Elemental Boost Lv 1",3),(1,"31-100","Hardbone",8,"Status Effect Boost Lv 1",2),(1,"101-200","Slogbone",15,"Elemental Boost Lv 4",2),
(2,"1-30","Pelt",2,"Attack Boost Lv 1",3),(2,"31-100","Hide+",8,"Affinity Boost Lv 1",2),(2,"101-200","Thickhide",15,"Attack Boost Lv 3",2),
(3,"11-30","Monster Bone",4,"Affinity Boost Lv 1",2),(3,"31-100","Monster Hardbone",10,"Elemental Boost Lv 2",2),(3,"101-200","Monster Slogbone",20,"Status Effect Boost Lv 2",2),
(4,"11-30","Blood",4,"Status Effect Boost Lv 1",2),(4,"31-100","Dragon Blood",10,"Add Anomaly Slot Lv 1",2),(4,"101-200","Pure Blood",20,"Elemental Boost Lv 4",2),
(5,"21-30","Scale",6,"Elemental Boost Lv 2",2),(5,"31-100","Scale+",12,"Sharpness Boost Lv 1",2),(5,"101-200","Shard",25,"Add Anomaly Slot Lv 3",2),
(6,"21-30","Shell",6,"Add Anomaly Slot Lv 1",2),(6,"31-100","Carapace",12,"Elemental Boost Lv 3",2),(6,"101-200","Cortex",25,"Elemental Boost Lv 4",2),
(7,"31-31","Fang",8,"Attack Boost Lv 2",2),(7,"31-100","Fang+",16,"Attack Boost Lv 2",2),(7,"101-200","Hardfang",30,"Add Anomaly Slot Lv 3",2),
(8,"31-31","Claw",8,"Elemental Boost Lv 3",2),(8,"31-100","Claw+",16,"Sharpness Boost Lv 1",2),(8,"101-200","Hardclaw",30,"Elemental Boost Lv 5",2),
(9,"51-100","Dire Horn",20,"Elemental Boost Lv 3",2),(9,"101-160","Dire Horn+",40,"Attack Boost Lv 3",2),(9,"161-200","Dire Hardhorn",50,"Add Anomaly Slot Lv 4",2),
(10,"51-100","Dire Bone",20,"Rampage Slot Upgrade Lv 1",3),(10,"101-160","Dire Hardbone",40,"Status Effect Boost Lv 2",2),
(10,"161-200","Dire Slogbone",50,"Add Anomaly Slot Lv 5",2),(10,"161-200","Dire Slogbone",50,"Elemental Boost Lv 6",3),
(11,"51-100","Dire Scale",20,"Add Anomaly Slot Lv 2",3),(11,"101-160","Dire Scale+",40,"Elemental Boost Lv 5",2),(11,"161-200","Dire Shard",50,"Sharpness Boost Lv 2",2),
(12,"71-110","Dire Shell",30,"Attack Boost Lv 3",2),(12,"111-180","Dire Carapace",50,"Elemental Boost Lv 5",2),
(12,"181-200","Dire Cortex",70,"Add Anomaly Slot Lv 5",2),(12,"181-200","Dire Cortex",70,"Shelling Level Boost Lv 2",2),
(13,"71-110","Dire Claw",30,"Status Effect Boost Lv 2",2),(13,"111-180","Dire Claw+",50,"Add Anomaly Slot Lv 3",2),
(13,"181-200","Dire Hardclaw",70,"Sharpness Boost Lv 2",2),(13,"181-200","Dire Hardclaw",70,"Shelling Level Boost Lv 2",2),
(14,"91-140","Dire Wing",40,"Affinity Boost Lv 2",2),(14,"141-200","Dire Wing+",60,"Add Anomaly Slot Lv 4",2),(14,"201-220","Dire Fellwing",90,"Sharpness Boost Lv 3",2),
(15,"91-140","Dire Blood",40,"Attack Boost Lv 4",2),(15,"141-200","Dire Dragon Blood",60,"Add Anomaly Slot Lv 5",2),(15,"141-200","Dire Dragon Blood",60,"Shelling Level Boost Lv 1",2),
(15,"201-220","Dire Darkblood",90,"Rampage Slot Upgrade Lv 2",2),
(16,"91-140","Dire Fang",40,"Affinity Boost Lv 2",2),(16,"141-200","Dire Fang+",60,"Attack Boost Lv 4",2),(16,"141-200","Dire Fang+",60,"Shelling Level Boost Lv 1",2),
(16,"201-220","Dire Hardfang",90,"Add Anomaly Slot Lv 6",2),
(17,"111-160","Risen Dragonbone",80,"Add Anomaly Slot Lv 6",2),(17,"111-160","Risen Dragonbone",80,"Affinity Boost Lv 3",3),
(17,"111-160","Risen Dragonbone",80,"Status Effect Boost Lv 3",3),(17,"111-160","Risen Dragonbone",80,"Sharpness Boost Lv 3",2),
(17,"161-220","Risen Dragonbone+",120,"Elemental Boost Lv 7",3),(17,"161-220","Risen Dragonbone+",120,"Rampage Slot Upgrade Lv 2",2),
(17,"221-300","Risen Slogbone",160,"Sharpness Boost Lv 4",2),(17,"221-300","Risen Slogbone",160,"Add Anomaly Slot Lv 7",2),
(18,"131-200","Risen Dragon Blood",100,"Status Effect Boost Lv 4",3),
(18,"201-240","Risen Dragon Pureblood",150,"Elemental Boost Lv 8",3),(18,"201-240","Risen Dragon Pureblood",150,"Sharpness Boost Lv 4",2),
(18,"241-300","Risen Dragon Thickblood",200,"Add Anomaly Slot Lv 7",2),
]

# upgrade, augment slots used, (rank, levels, material, qty) options -- from the "by upgrade" table
U = [
("Add Anomaly Slot Lv 1",4,[("A3","21-30","Shell",2),("A2","31-100","Dragon Blood",2)]),
("Add Anomaly Slot Lv 2",5,[("A5","51-100","Dire Scale",3)]),
("Add Anomaly Slot Lv 3",6,[("A3","101-200","Shard",2),("A4","101-200","Hardfang",2),("A6","111-180","Dire Claw+",2)]),
("Add Anomaly Slot Lv 4",7,[("A7","141-200","Dire Wing+",2),("A5","161-200","Dire Hardhorn",2)]),
("Add Anomaly Slot Lv 5",8,[("A7","141-200","Dire Dragon Blood",2),("A5","161-200","Dire Slogbone",2),("A6","181-200","Dire Cortex",2)]),
("Add Anomaly Slot Lv 6",9,[("A8","111-160","Risen Dragonbone",2),("A7","201-220","Dire Hardfang",2)]),
("Add Anomaly Slot Lv 7",10,[("A8","161-220","Risen Slogbone",2),("A9","241-300","Risen Dragon Thickblood",2)]),
("Attack Boost Lv 1",2,[("A1","1-30","Pelt",3)]),
("Attack Boost Lv 2",4,[("A4","31-31","Fang",2),("A4","31-100","Fang+",2)]),
("Attack Boost Lv 3",6,[("A6","71-110","Dire Shell",2),("A5","101-160","Dire Horn+",2),("A1","101-200","Thickhide",2)]),
("Attack Boost Lv 4",8,[("A7","91-140","Dire Blood",2),("A7","141-200","Dire Fang+",2)]),
("Affinity Boost Lv 1",3,[("A2","11-30","Monster Bone",2),("A1","31-100","Hide+",2)]),
("Affinity Boost Lv 2",6,[("A7","91-140","Dire Wing",2),("A7","91-140","Dire Fang",2)]),
("Affinity Boost Lv 3",8,[("A8","111-160","Risen Dragonbone",3)]),
("Elemental Boost Lv 1",1,[("A1","1-30","Bone",3)]),
("Elemental Boost Lv 2",2,[("A3","21-30","Scale",2),("A2","31-100","Monster Hardbone",2)]),
("Elemental Boost Lv 3",3,[("A4","31-31","Claw",2),("A3","31-100","Carapace",2),("A5","51-100","Dire Horn",2)]),
("Elemental Boost Lv 4",4,[("A1","101-200","Slogbone",2),("A2","101-200","Pure Blood",2),("A3","101-200","Cortex",2)]),
("Elemental Boost Lv 5",5,[("A5","101-160","Dire Scale+",2),("A4","101-200","Hardclaw",2),("A6","111-180","Dire Carapace",2)]),
("Elemental Boost Lv 6",6,[("A5","161-200","Dire Slogbone",3)]),
("Elemental Boost Lv 7",7,[("A8","161-220","Risen Dragonbone+",3)]),
("Elemental Boost Lv 8",8,[("A9","201-240","Risen Dragon Pureblood",3)]),
("Status Effect Boost Lv 1",2,[("A2","11-30","Blood",2),("A1","31-100","Hardbone",2)]),
("Status Effect Boost Lv 2",4,[("A6","71-110","Dire Claw",2),("A5","101-160","Dire Hardbone",2),("A2","101-200","Monster Slogbone",2)]),
("Status Effect Boost Lv 3",6,[("A8","111-160","Risen Dragonbone",3)]),
("Status Effect Boost Lv 4",8,[("A9","131-200","Risen Dragon Blood",3)]),
("Sharpness Boost Lv 1",3,[("A3","31-100","Scale+",2),("A4","31-100","Claw+",2)]),
("Sharpness Boost Lv 2",5,[("A5","161-200","Dire Shard",2),("A6","181-200","Dire Hardclaw",2)]),
("Sharpness Boost Lv 3",7,[("A8","111-160","Risen Dragonbone",2),("A7","201-220","Dire Fellwing",2)]),
("Sharpness Boost Lv 4",9,[("A8","221-300","Risen Slogbone",2),("A9","201-240","Risen Dragon Pureblood",2)]),
("Shelling Level Boost Lv 1",2,[("A7","141-200","Dire Dragon Blood",2),("A7","141-200","Dire Fang+",2)]),
("Shelling Level Boost Lv 2",3,[("A6","181-200","Dire Cortex",2),("A6","181-200","Dire Hardclaw",2)]),
("Rampage Slot Upgrade Lv 1",4,[("A5","51-100","Dire Bone",3)]),
("Rampage Slot Upgrade Lv 2",7,[("A8","161-220","Risen Dragonbone+",2),("A7","201-220","Dire Darkblood",2)]),
]
NOTES = [
"Qurio node breaks damage the monster by about 1% of max HP. Monster will nova after about 90s if you don't deal enough damage.",
"HP values are the range for the Quest version. Increasing Investigation level increases HP further.",
"Daimyo Hermitaur and Shogun Ceanataur are weakest to Thunder on head/body, Fire on their claws, equal otherwise.",
"Barroth and Jyuratodus are weak to Water on mud-covered parts, and weak to their second element otherwise.",
"Basarios is weakest to Dragon, but Fire weapons soften its hide.",
"Chaotic Gore Magala is weaker to Dragon on its right wingarm and head, but weaker to Fire everywhere else. Classified as A8 for XP and Quest/Investigation unlocks, but drops A7 materials.",
"Transcriber notes: the by-upgrade table labels the Risen Dragonbone x3 row 'Affinity Boost Lv 2 (8 slots)' and the Risen Slogbone/Pureblood row 'Sharpness Boost Lv 3 (9 slots)'; the by-material table says Lv 3 and Lv 4, so those are recorded as Lv 3 / Lv 4. The by-upgrade table lists Risen Slogbone at 161-220 for Add Anomaly Slot Lv 7; the by-material table says 221-300.",
]

def lv(r):
    a, b = r.split("-"); return int(a), int(b)
def full(m):
    return m if m.startswith("Risen") else "Afflicted " + m

db.executescript("""
DROP TABLE IF EXISTS anomaly_monster; DROP TABLE IF EXISTS qurious_material_upgrade;
DROP TABLE IF EXISTS qurious_upgrade_cost; DROP TABLE IF EXISTS qurious_upgrade; DROP TABLE IF EXISTS cheatsheet_note;
CREATE TABLE anomaly_monster (monster TEXT PRIMARY KEY, anomaly_rank TEXT, material_group INTEGER,
  xp_low INTEGER, xp_high INTEGER, hp_min INTEGER, hp_max INTEGER, anti_deco TEXT, weakness TEXT);
CREATE TABLE qurious_material_upgrade (material_group INTEGER, level_min INTEGER, level_max INTEGER,
  material TEXT, augment_points INTEGER, upgrade TEXT, qty INTEGER);
CREATE TABLE qurious_upgrade (upgrade TEXT PRIMARY KEY, category TEXT, level INTEGER, augment_slots INTEGER);
CREATE TABLE qurious_upgrade_cost (upgrade TEXT REFERENCES qurious_upgrade(upgrade), anomaly_rank TEXT,
  level_min INTEGER, level_max INTEGER, material TEXT, qty INTEGER);
CREATE TABLE cheatsheet_note (id INTEGER PRIMARY KEY, note TEXT);
""")
db.executemany("INSERT INTO anomaly_monster VALUES (?,?,?,?,?,?,?,?,?)",
               [(m[4], m[0], m[1], m[2], m[3], m[5], m[6], m[7], m[8]) for m in M])
db.executemany("INSERT INTO qurious_material_upgrade VALUES (?,?,?,?,?,?,?)",
               [(g, *lv(r), full(m), p, u, q) for g, r, m, p, u, q in Q])
for up, slots, opts in U:
    cat, n = up.rsplit(" Lv ", 1)
    db.execute("INSERT INTO qurious_upgrade VALUES (?,?,?,?)", (up, cat, int(n), slots))
    for rk, r, m, q in opts:
        db.execute("INSERT INTO qurious_upgrade_cost VALUES (?,?,?,?,?,?)", (up, rk, *lv(r), full(m), q))
db.executemany("INSERT INTO cheatsheet_note (note) VALUES (?)", [(n,) for n in NOTES])
db.commit()
print({t: db.execute(f"select count(*) from {t}").fetchone()[0] for t in
       ["anomaly_monster","qurious_material_upgrade","qurious_upgrade","qurious_upgrade_cost","cheatsheet_note"]})
