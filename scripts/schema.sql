-- Monster Hunter Rise: Sunbreak equipment database (source: mhrise.mhrice.info, game v16)
DROP TABLE IF EXISTS skill;
CREATE TABLE skill (
  id TEXT PRIMARY KEY,          -- e.g. PlayerSkill_001
  name TEXT NOT NULL UNIQUE,
  max_level INTEGER NOT NULL,
  description TEXT
);
DROP TABLE IF EXISTS skill_level;
CREATE TABLE skill_level (
  skill_id TEXT REFERENCES skill(id),
  level INTEGER,
  effect TEXT,
  PRIMARY KEY (skill_id, level)
);
DROP TABLE IF EXISTS decoration;
CREATE TABLE decoration (
  name TEXT PRIMARY KEY,        -- e.g. "Challenger Jewel+ 4"
  slot_level INTEGER NOT NULL,  -- size of slot it needs (1-4)
  skill_id TEXT REFERENCES skill(id),
  skill_level INTEGER NOT NULL, -- skill points granted (Lv4 "+" jewels give 2)
  unlock TEXT,
  cost TEXT
);
DROP TABLE IF EXISTS armor_piece;
CREATE TABLE armor_piece (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  series_id TEXT,
  series TEXT,
  part TEXT CHECK (part IN ('head','chest','arms','waist','legs')),
  rarity INTEGER,
  rank TEXT,                    -- LR (1-3) / HR (4-7) / MR (8-10)
  base_defense INTEGER,
  max_defense INTEGER,          -- computed from the series upgrade table
  max_level INTEGER,
  fire INTEGER, water INTEGER, ice INTEGER, thunder INTEGER, dragon INTEGER,
  slots TEXT,                   -- JSON list, e.g. [4,1]
  slots_lv1 INTEGER, slots_lv2 INTEGER, slots_lv3 INTEGER, slots_lv4 INTEGER,
  usable INTEGER                -- 0 = unnamed placeholder or layered-only (no defense)
);
DROP TABLE IF EXISTS armor_piece_skill;
CREATE TABLE armor_piece_skill (
  piece_id INTEGER REFERENCES armor_piece(id),
  skill_id TEXT REFERENCES skill(id),
  level INTEGER,
  PRIMARY KEY (piece_id, skill_id)
);
DROP TABLE IF EXISTS weapon;
CREATE TABLE weapon (
  id TEXT PRIMARY KEY,          -- mhrice id, e.g. LongSword_301
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  rarity INTEGER, rank TEXT,
  attack INTEGER, affinity INTEGER, defense INTEGER,
  element1 TEXT, element1_value INTEGER,
  element2 TEXT, element2_value INTEGER,
  slots TEXT,
  slots_lv1 INTEGER, slots_lv2 INTEGER, slots_lv3 INTEGER, slots_lv4 INTEGER,
  rampage_slot_level INTEGER,   -- Sunbreak rampage decoration slot (null if none)
  sharpness_base TEXT,          -- JSON [red..purple], points out of 400
  sharpness_max TEXT,           -- with Handicraft 5
  sharp_red INTEGER, sharp_orange INTEGER, sharp_yellow INTEGER, sharp_green INTEGER,
  sharp_blue INTEGER, sharp_white INTEGER, sharp_purple INTEGER,
  sharp_max_white INTEGER, sharp_max_purple INTEGER,
  rampage_skills TEXT,          -- JSON list (base-game weapons)
  type_details TEXT,            -- JSON: phial, shelling, kinsect, bow/bowgun stats, ammo, melody
  obtainable INTEGER,           -- 1 if it has a craft/upgrade cost
  usable INTEGER                -- 0 = unnamed, #Rejected# (unused) or attack <= 1
);

-- User-owned talismans (charms): fill in your own. Slots as counts by level.
DROP TABLE IF EXISTS charm;
CREATE TABLE charm (
  id INTEGER PRIMARY KEY,
  label TEXT,
  skill1_id TEXT REFERENCES skill(id), skill1_level INTEGER,
  skill2_id TEXT REFERENCES skill(id), skill2_level INTEGER,
  slots TEXT,
  slots_lv1 INTEGER DEFAULT 0, slots_lv2 INTEGER DEFAULT 0, slots_lv3 INTEGER DEFAULT 0, slots_lv4 INTEGER DEFAULT 0
);

-- Flat, human/LLM-readable views
DROP VIEW IF EXISTS armor_flat;
CREATE VIEW armor_flat AS
SELECT p.id, p.name, p.series, p.part, p.rank, p.rarity, p.base_defense, p.max_defense,
       p.fire, p.water, p.ice, p.thunder, p.dragon, p.slots,
       (SELECT group_concat(s.name || ' ' || ps.level, '; ')
          FROM armor_piece_skill ps JOIN skill s ON s.id = ps.skill_id WHERE ps.piece_id = p.id) AS skills
FROM armor_piece p WHERE p.usable = 1;

DROP VIEW IF EXISTS weapon_flat;
CREATE VIEW weapon_flat AS
SELECT id, name, type, rank, rarity, attack, affinity, defense,
       element1, element1_value, element2, element2_value, slots, rampage_slot_level,
       sharp_red, sharp_orange, sharp_yellow, sharp_green, sharp_blue, sharp_white, sharp_purple,
       sharp_max_white, sharp_max_purple, rampage_skills, type_details
FROM weapon WHERE usable = 1;

DROP VIEW IF EXISTS decoration_flat;
CREATE VIEW decoration_flat AS
SELECT d.name, d.slot_level, s.name AS skill, d.skill_level, s.max_level AS skill_max_level, d.unlock
FROM decoration d JOIN skill s ON s.id = d.skill_id;
