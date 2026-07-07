#!/usr/bin/env python3
"""Build the Enchanting data foundation for The Artisan's Ledger.

This utility is intentionally repeatable and side-effect safe: it only writes the
JSON and browser-friendly JavaScript files requested by the caller, defaulting
to data/enchanting-data.json and data/enchanting-data.js when run from the
repository root.

How to update later
-------------------
1. Add or correct source entries in SOURCE_NOTES.
2. Update POTENCY_GROUPS, ESSENCE_RUNES, ASPECT_RUNES, PRAXIS_PLANS, or
   MATERIALS_SEED with vetted data only.
3. Run: python tools/build_enchanting_data.py
4. Review the generated JSON and JS diffs before wiring them into script.js.

Design choice
-------------
ESO glyphs are formula-based: one Potency rune + one Essence rune + one Aspect
rune. The app should not hand-maintain thousands of recipe rows. This script
keeps compact source tables, then generates deterministic recipe records for
script.js or any later import step.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional

SCHEMA_VERSION = "0.1.0"
PROFESSION = "Enchanting"
DEFAULT_OUTPUT = Path("data/enchanting-data.json")
DEFAULT_JS_OUTPUT = Path("data/enchanting-data.js")
JS_GLOBAL_NAME = "window.ARTISAN_ENCHANTING_DATA"

SOURCE_NOTES: List[Dict[str, str]] = [
    {
        "id": "uesp-runestones",
        "label": "UESP: Online:Runestones",
        "url": "https://en.uesp.net/wiki/Online:Runestones",
        "notes": "Primary reference for ESO runestone types, rune translations, glyph construction, and aspect quality notes.",
    },
    {
        "id": "uesp-furnishing-schematics",
        "label": "UESP: Online:Furnishing Schematics",
        "url": "https://en.uesp.net/wiki/Online:Furnishing_Schematics",
        "notes": "Primary seed reference for Enchanting furnishing Praxes. UESP marks the page incomplete after Blackwood, so Praxis data here is a starting seed, not a complete catalog.",
    },
    {
        "id": "benevolentbowd-enchanting",
        "label": "BenevolentBowD: ESO Enchanting Rune and Glyph List",
        "url": "https://benevolentbowd.ca/games/esotu/eso-enchanting-rune-and-glyph-list/",
        "notes": "Cross-check reference for potency prefixes, rune translations, essence effects, aspect rune levels, and common glyph naming.",
    },
    {
        "id": "eso-hub-enchanting",
        "label": "ESO-Hub: ESO Enchantments, Glyphs and Runes",
        "url": "https://eso-hub.com/en/enchanting-runes-and-glyphs",
        "notes": "Cross-check reference for glyph categories and Enchanting skill unlock ranges.",
    },
]


def slugify(value: str) -> str:
    """Make a stable app-friendly id from a display name."""
    keep: List[str] = []
    previous_dash = False
    for char in value.strip().lower():
        if char.isalnum():
            keep.append(char)
            previous_dash = False
        elif not previous_dash:
            keep.append("-")
            previous_dash = True
    return "".join(keep).strip("-")


def level_range(kind: str, minimum: int, maximum: Optional[int], label: str) -> Dict[str, Any]:
    return {"kind": kind, "min": minimum, "max": maximum, "label": label}


# Each group produces one additive and one subtractive potency rune. The
# glyph_prefix is the name contribution used before "Glyph of ...".
POTENCY_GROUPS: List[Dict[str, Any]] = [
    {
        "glyph_prefix": "Trifling",
        "level_range": level_range("level", 1, 10, "Level 1-10"),
        "potency_improvement_rank": 1,
        "additive": {"name": "Jora", "translation": "Develop"},
        "subtractive": {"name": "Jode", "translation": "Reduce"},
    },
    {
        "glyph_prefix": "Inferior",
        "level_range": level_range("level", 5, 15, "Level 5-15"),
        "potency_improvement_rank": 1,
        "additive": {"name": "Porade", "translation": "Add"},
        "subtractive": {"name": "Notade", "translation": "Subtract"},
    },
    {
        "glyph_prefix": "Petty",
        "level_range": level_range("level", 10, 20, "Level 10-20"),
        "potency_improvement_rank": 2,
        "additive": {"name": "Jera", "translation": "Increase"},
        "subtractive": {"name": "Ode", "translation": "Shrink"},
    },
    {
        "glyph_prefix": "Slight",
        "level_range": level_range("level", 15, 25, "Level 15-25"),
        "potency_improvement_rank": 2,
        "additive": {"name": "Jejora", "translation": "Raise"},
        "subtractive": {"name": "Tade", "translation": "Decrease"},
    },
    {
        "glyph_prefix": "Minor",
        "level_range": level_range("level", 20, 30, "Level 20-30"),
        "potency_improvement_rank": 3,
        "additive": {"name": "Odra", "translation": "Gain"},
        "subtractive": {"name": "Jayde", "translation": "Deduct"},
    },
    {
        "glyph_prefix": "Lesser",
        "level_range": level_range("level", 25, 35, "Level 25-35"),
        "potency_improvement_rank": 3,
        "additive": {"name": "Pojora", "translation": "Supplement"},
        "subtractive": {"name": "Edode", "translation": "Lower"},
    },
    {
        "glyph_prefix": "Moderate",
        "level_range": level_range("level", 30, 40, "Level 30-40"),
        "potency_improvement_rank": 4,
        "additive": {"name": "Edora", "translation": "Boost"},
        "subtractive": {"name": "Pojode", "translation": "Diminish"},
    },
    {
        "glyph_prefix": "Average",
        "level_range": level_range("level", 35, 45, "Level 35-45"),
        "potency_improvement_rank": 4,
        "additive": {"name": "Jaera", "translation": "Advance"},
        "subtractive": {"name": "Rekude", "translation": "Weaken"},
    },
    {
        "glyph_prefix": "Strong",
        "level_range": level_range("level", 40, 50, "Level 40-50"),
        "potency_improvement_rank": 5,
        "additive": {"name": "Pora", "translation": "Augment"},
        "subtractive": {"name": "Hade", "translation": "Lessen"},
    },
    {
        "glyph_prefix": "Major",
        "level_range": level_range("champion_points", 10, 30, "Champion Point 10-30"),
        "potency_improvement_rank": 5,
        "additive": {"name": "Denara", "translation": "Strengthen"},
        "subtractive": {"name": "Idode", "translation": "Impair"},
        "notes": "Some tables label this row as CP10; skill-rank summaries group it through CP30.",
    },
    {
        "glyph_prefix": "Greater",
        "level_range": level_range("champion_points", 30, 50, "Champion Point 30-50"),
        "potency_improvement_rank": 6,
        "additive": {"name": "Rera", "translation": "Exaggerate"},
        "subtractive": {"name": "Pode", "translation": "Remove"},
    },
    {
        "glyph_prefix": "Grand",
        "level_range": level_range("champion_points", 50, 70, "Champion Point 50-70"),
        "potency_improvement_rank": 7,
        "additive": {"name": "Derado", "translation": "Empower"},
        "subtractive": {"name": "Kedeko", "translation": "Drain"},
    },
    {
        "glyph_prefix": "Splendid",
        "level_range": level_range("champion_points", 70, 90, "Champion Point 70-90"),
        "potency_improvement_rank": 8,
        "additive": {"name": "Rekura", "translation": "Magnify", "aliases": ["Recura"]},
        "subtractive": {"name": "Rede", "translation": "Deprive"},
        "notes": "Some third-party tables spell Rekura as Recura; current in-game/common spelling is Rekura.",
    },
    {
        "glyph_prefix": "Monumental",
        "level_range": level_range("champion_points", 100, 140, "Champion Point 100-140"),
        "potency_improvement_rank": 9,
        "additive": {"name": "Kura", "translation": "Intensify", "aliases": ["Cura"]},
        "subtractive": {"name": "Kude", "translation": "Negate"},
        "notes": "Some older tables spell Kura as Cura.",
    },
    {
        "glyph_prefix": "Superb",
        "level_range": level_range("champion_points", 150, 150, "Champion Point 150"),
        "potency_improvement_rank": 10,
        "additive": {"name": "Rejera", "translation": "Amplify"},
        "subtractive": {"name": "Jehade", "translation": "Divest"},
    },
    {
        "glyph_prefix": "Truly Superb",
        "level_range": level_range("champion_points", 160, 160, "Champion Point 160"),
        "potency_improvement_rank": 10,
        "additive": {"name": "Repora", "translation": "Reinforce"},
        "subtractive": {"name": "Itade", "translation": "Plunder"},
        "notes": "Highest standard gear tier. Some tables split the prefix into 'Truly' / 'Superb'; app display uses the familiar 'Truly Superb'.",
    },
]

ESSENCE_RUNES: List[Dict[str, Any]] = [
    {
        "name": "Dekeipa",
        "translation": "Frost",
        "effect": "Frost",
        "glyph_results": {
            "additive": {"glyph_name": "Glyph of Frost", "category": "weapon", "effect": "Frost Damage"},
            "subtractive": {"glyph_name": "Glyph of Frost Resist", "category": "jewelry", "effect": "Frost Resistance"},
        },
    },
    {
        "name": "Deni",
        "translation": "Stamina",
        "effect": "Stamina",
        "glyph_results": {
            "additive": {"glyph_name": "Glyph of Stamina", "category": "armor", "effect": "Maximum Stamina"},
            "subtractive": {"glyph_name": "Glyph of Absorb Stamina", "category": "weapon", "effect": "Absorb Stamina"},
        },
    },
    {
        "name": "Denima",
        "translation": "Stamina Regeneration",
        "effect": "Stamina Recovery",
        "glyph_results": {
            "additive": {"glyph_name": "Glyph of Stamina Recovery", "category": "jewelry", "effect": "Stamina Recovery"},
            "subtractive": {"glyph_name": "Glyph of Reduce Feat Cost", "category": "jewelry", "effect": "Reduce Stamina Ability Cost"},
        },
    },
    {
        "name": "Deteri",
        "translation": "Armor",
        "effect": "Armor / Damage Shield",
        "glyph_results": {
            "additive": {"glyph_name": "Glyph of Hardening", "category": "weapon", "effect": "Damage Shield"},
            "subtractive": {"glyph_name": "Glyph of Crushing", "category": "weapon", "effect": "Reduce Target Spell and Physical Resistance"},
        },
    },
    {
        "name": "Hakeijo",
        "translation": "Prismatic Defense",
        "effect": "Prismatic Defense / Prismatic Onslaught",
        "glyph_results": {
            "additive": {"glyph_name": "Glyph of Prismatic Defense", "category": "armor", "effect": "Maximum Magicka, Health, and Stamina"},
            "subtractive": {"glyph_name": "Glyph of Prismatic Onslaught", "category": "weapon", "effect": "Magic Damage to Undead and Daedra"},
        },
        "notes": "Imperial City source; often obtained from glowing trove scamps, special chests, or Tel Var merchants.",
    },
    {
        "name": "Haoko",
        "translation": "Disease",
        "effect": "Disease",
        "glyph_results": {
            "additive": {"glyph_name": "Glyph of Foulness", "category": "weapon", "effect": "Disease Damage"},
            "subtractive": {"glyph_name": "Glyph of Disease Resist", "category": "jewelry", "effect": "Disease Resistance"},
        },
    },
    {
        "name": "Indeko",
        "translation": "Prismatic Recovery",
        "effect": "Prismatic Recovery / Reduced Skill Cost",
        "glyph_results": {
            "additive": {"glyph_name": "Glyph of Prismatic Recovery", "category": "jewelry", "effect": "Health, Magicka, and Stamina Recovery"},
            "subtractive": {"glyph_name": "Glyph of Reduce Skill Cost", "category": "jewelry", "effect": "Reduced Skill Cost"},
        },
        "notes": "Antiquity-related rune source; keep source field open for future app filters.",
    },
    {
        "name": "Kaderi",
        "translation": "Bracing",
        "effect": "Bash / Block",
        "glyph_results": {
            "additive": {"glyph_name": "Glyph of Bashing", "category": "jewelry", "effect": "Bash Damage"},
            "subtractive": {"glyph_name": "Glyph of Bracing", "category": "jewelry", "effect": "Reduce Bash Cost and Blocking Cost"},
        },
    },
    {
        "name": "Kuoko",
        "translation": "Poison",
        "effect": "Poison",
        "glyph_results": {
            "additive": {"glyph_name": "Glyph of Poison", "category": "weapon", "effect": "Poison Damage"},
            "subtractive": {"glyph_name": "Glyph of Poison Resist", "category": "jewelry", "effect": "Poison Resistance"},
        },
    },
    {
        "name": "Makderi",
        "translation": "Spell Harm",
        "effect": "Spell Damage / Spell Resistance",
        "glyph_results": {
            "additive": {"glyph_name": "Glyph of Increase Magical Harm", "category": "jewelry", "effect": "Increase Spell Damage"},
            "subtractive": {"glyph_name": "Glyph of Decrease Spell Harm", "category": "jewelry", "effect": "Spell Resistance"},
        },
    },
    {
        "name": "Makko",
        "translation": "Magicka",
        "effect": "Magicka",
        "glyph_results": {
            "additive": {"glyph_name": "Glyph of Magicka", "category": "armor", "effect": "Maximum Magicka"},
            "subtractive": {"glyph_name": "Glyph of Absorb Magicka", "category": "weapon", "effect": "Absorb Magicka"},
        },
    },
    {
        "name": "Makkoma",
        "translation": "Magicka Regeneration",
        "effect": "Magicka Recovery",
        "glyph_results": {
            "additive": {"glyph_name": "Glyph of Magicka Recovery", "category": "jewelry", "effect": "Magicka Recovery"},
            "subtractive": {"glyph_name": "Glyph of Reduce Spell Cost", "category": "jewelry", "effect": "Reduce Magicka Ability Cost"},
        },
    },
    {
        "name": "Meip",
        "translation": "Shock",
        "effect": "Shock",
        "glyph_results": {
            "additive": {"glyph_name": "Glyph of Shock", "category": "weapon", "effect": "Shock Damage"},
            "subtractive": {"glyph_name": "Glyph of Shock Resist", "category": "jewelry", "effect": "Shock Resistance"},
        },
    },
    {
        "name": "Oko",
        "translation": "Health",
        "effect": "Health",
        "glyph_results": {
            "additive": {"glyph_name": "Glyph of Health", "category": "armor", "effect": "Maximum Health"},
            "subtractive": {"glyph_name": "Glyph of Absorb Health", "category": "weapon", "effect": "Absorb Health"},
        },
    },
    {
        "name": "Okoma",
        "translation": "Health Regeneration",
        "effect": "Health Recovery / Oblivion Damage",
        "glyph_results": {
            "additive": {"glyph_name": "Glyph of Health Recovery", "category": "jewelry", "effect": "Health Recovery"},
            "subtractive": {"glyph_name": "Glyph of Decrease Health", "category": "weapon", "effect": "Unresistable / Oblivion Damage"},
        },
    },
    {
        "name": "Okori",
        "translation": "Power",
        "effect": "Weapon Damage / Weakening",
        "glyph_results": {
            "additive": {"glyph_name": "Glyph of Weapon Damage", "category": "weapon", "effect": "Increase Weapon Damage"},
            "subtractive": {"glyph_name": "Glyph of Weakening", "category": "weapon", "effect": "Reduce Target Weapon and Spell Damage"},
        },
    },
    {
        "name": "Oru",
        "translation": "Alchemist",
        "effect": "Potion Duration / Potion Cooldown",
        "glyph_results": {
            "additive": {"glyph_name": "Glyph of Potion Boost", "category": "jewelry", "effect": "Increase Potion Duration"},
            "subtractive": {"glyph_name": "Glyph of Potion Speed", "category": "jewelry", "effect": "Reduce Potion Cooldown"},
        },
    },
    {
        "name": "Rakeipa",
        "translation": "Fire",
        "effect": "Fire",
        "glyph_results": {
            "additive": {"glyph_name": "Glyph of Flame", "category": "weapon", "effect": "Fire Damage"},
            "subtractive": {"glyph_name": "Glyph of Flame Resist", "category": "jewelry", "effect": "Fire Resistance"},
        },
    },
    {
        "name": "Taderi",
        "translation": "Physical Harm",
        "effect": "Physical Damage / Physical Resistance",
        "glyph_results": {
            "additive": {"glyph_name": "Glyph of Increase Physical Harm", "category": "jewelry", "effect": "Increase Weapon Damage"},
            "subtractive": {"glyph_name": "Glyph of Decrease Physical Harm", "category": "jewelry", "effect": "Physical Resistance"},
        },
    },
]

ASPECT_RUNES: List[Dict[str, Any]] = [
    {
        "name": "Ta",
        "translation": "Base",
        "quality": "Common",
        "quality_color": "White",
        "aspect_improvement_rank": 1,
        "notes": "Base/common quality aspect rune.",
    },
    {
        "name": "Jejota",
        "translation": "Fine",
        "quality": "Fine",
        "quality_color": "Green",
        "aspect_improvement_rank": 1,
        "notes": "Fine quality aspect rune.",
    },
    {
        "name": "Denata",
        "translation": "Superior",
        "quality": "Superior",
        "quality_color": "Blue",
        "aspect_improvement_rank": 2,
        "notes": "Superior quality aspect rune.",
    },
    {
        "name": "Rekuta",
        "translation": "Artifact",
        "quality": "Artifact / Epic",
        "quality_color": "Purple",
        "aspect_improvement_rank": 3,
        "notes": "Purple artifact/epic quality aspect rune.",
    },
    {
        "name": "Kuta",
        "translation": "Legendary",
        "quality": "Legendary",
        "quality_color": "Gold",
        "aspect_improvement_rank": 4,
        "notes": "Gold legendary quality aspect rune.",
    },
]

# Seed list for the Praxis tracker. known defaults to False by design; this is
# user-state data that the app will persist separately or merge later.
PRAXIS_PLANS: List[Dict[str, Any]] = [
    {
        "plan_name": "Praxis: Alinor Archway, Tall",
        "category": "Structures",
        "subcategory": "Doorways",
        "materials": {"Mundane Rune": 9, "Denata": 6, "Ochre": 5, "Regulus": 5, "Culanda Lacquer": 1},
        "source_notes": "UESP Furnishing Schematics seed entry; Summerset/Alinor themed furnishing.",
    },
    {
        "plan_name": "Praxis: Alinor Archway, Timeworn",
        "category": "Structures",
        "subcategory": "Doorways",
        "materials": {"Mundane Rune": 10, "Alchemical Resin": 7, "Denata": 6, "Culanda Lacquer": 1},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Bench, Marble",
        "category": "Dining",
        "subcategory": "Benches",
        "materials": {"Mundane Rune": 9, "Denata": 6, "Alchemical Resin": 5, "Ochre": 5, "Culanda Lacquer": 1},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Bookcase Wall, Timeworn",
        "category": "Library",
        "subcategory": "Shelves",
        "materials": {"Mundane Rune": 13, "Alchemical Resin": 9, "Decorative Wax": 6, "Ochre": 6, "Rekuta": 3, "Culanda Lacquer": 2},
        "source_notes": "UESP Furnishing Schematics seed entry; page note says material listing may need later audit.",
    },
    {
        "plan_name": "Praxis: Alinor Bowl, Shallow Limestone",
        "category": "Courtyard",
        "subcategory": "Yard Ornaments",
        "materials": {"Jejota": 9, "Mundane Rune": 6, "Culanda Lacquer": 1},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Bowl, Stemmed Limestone",
        "category": "Courtyard",
        "subcategory": "Yard Ornaments",
        "materials": {"Jejota": 9, "Mundane Rune": 7, "Culanda Lacquer": 1},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Column, Heavy Timeworn",
        "category": "Structures",
        "subcategory": "Building Components",
        "materials": {"Jejota": 9, "Mundane Rune": 7, "Alchemical Resin": 5, "Culanda Lacquer": 1},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Column, Slender Timeworn",
        "category": "Structures",
        "subcategory": "Building Components",
        "materials": {"Mundane Rune": 9, "Alchemical Resin": 6, "Denata": 6, "Culanda Lacquer": 1},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Column, Timeworn",
        "category": "Structures",
        "subcategory": "Building Components",
        "materials": {"Mundane Rune": 10, "Alchemical Resin": 7, "Denata": 6, "Culanda Lacquer": 1},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Display Stand, Marble",
        "category": "Gallery",
        "subcategory": "Display",
        "materials": {"Mundane Rune": 10, "Alchemical Resin": 6, "Decorative Wax": 6, "Denata": 6, "Culanda Lacquer": 1},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Display Stand, Marble Wide",
        "category": "Gallery",
        "subcategory": "Display",
        "materials": {"Mundane Rune": 9, "Decorative Wax": 6, "Denata": 6, "Alchemical Resin": 5, "Culanda Lacquer": 1},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Fence, Tall",
        "category": "Structures",
        "subcategory": "Walls and Fences",
        "materials": {"Mundane Rune": 8, "Denata": 6, "Regulus": 5, "Culanda Lacquer": 1},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Fence, Tall Long",
        "category": "Structures",
        "subcategory": "Walls and Fences",
        "materials": {"Mundane Rune": 9, "Denata": 6, "Regulus": 6, "Culanda Lacquer": 1},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Fireplace, Ornate",
        "category": "Structures",
        "subcategory": "Building Components",
        "materials": {"Mundane Rune": 12, "Alchemical Resin": 8, "Decorative Wax": 8, "Rekuta": 3, "Culanda Lacquer": 2},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Floor, Ballroom Timeworn",
        "category": "Structures",
        "subcategory": "Platforms",
        "materials": {"Mundane Rune": 10, "Denata": 6, "Alchemical Resin": 5, "Ochre": 5, "Culanda Lacquer": 1},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Fountain, Four-Way Timeworn",
        "category": "Courtyard",
        "subcategory": "Fountains",
        "materials": {"Mundane Rune": 13, "Alchemical Resin": 8, "Decorative Wax": 7, "Ochre": 7, "Rekuta": 3, "Culanda Lacquer": 2},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Fountain, Timeworn",
        "category": "Courtyard",
        "subcategory": "Fountains",
        "materials": {"Mundane Rune": 10, "Decorative Wax": 6, "Denata": 6, "Alchemical Resin": 5, "Ochre": 5, "Culanda Lacquer": 1},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Gaming Table, Punctilious Conflict",
        "category": "Parlor",
        "subcategory": "Tea Tables",
        "materials": {"Heartwood": 15, "Alchemical Resin": 13, "Decorative Wax": 11, "Ochre": 11, "Culanda Lacquer": 2, "Kuta": 1},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Pedestal, Timeworn",
        "category": "Gallery",
        "subcategory": "Display",
        "materials": {"Jejota": 9, "Mundane Rune": 6, "Alchemical Resin": 4, "Culanda Lacquer": 1},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Plinth, Sarcophagus",
        "category": "Undercroft",
        "subcategory": "Grave Goods",
        "materials": {"Mundane Rune": 8, "Denata": 6, "Alchemical Resin": 5, "Ochre": 5, "Culanda Lacquer": 1},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Post, Stone Wall",
        "category": "Structures",
        "subcategory": "Walls and Fences",
        "materials": {"Jejota": 9, "Mundane Rune": 5, "Culanda Lacquer": 1},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Pot, Limestone",
        "category": "Courtyard",
        "subcategory": "Yard Ornaments",
        "materials": {"Jejota": 9, "Mundane Rune": 7, "Culanda Lacquer": 1},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Sarcophagus, Peaked",
        "category": "Undercroft",
        "subcategory": "Grave Goods",
        "materials": {"Mundane Rune": 13, "Alchemical Resin": 9, "Ochre": 8, "Rekuta": 3, "Culanda Lacquer": 2},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
    {
        "plan_name": "Praxis: Alinor Statue, Kinlord",
        "category": "Courtyard",
        "subcategory": "Statues",
        "materials": {"Mundane Rune": 13, "Alchemical Resin": 7, "Decorative Wax": 7, "Ochre": 7, "Rekuta": 3, "Culanda Lacquer": 2},
        "source_notes": "UESP Furnishing Schematics seed entry.",
    },
]

MATERIALS_SEED: List[Dict[str, Any]] = [
    {"name": "Mundane Rune", "type": "furnishing_material", "crafting_profession": "Enchanting", "notes": "Common Enchanting furnishing material used by many Praxes."},
    {"name": "Alchemical Resin", "type": "furnishing_material", "crafting_profession": "Alchemy", "notes": "Reusable furnishing material that appears in Praxis recipes."},
    {"name": "Bast", "type": "furnishing_material", "crafting_profession": "Clothing", "notes": "General furnishing material; included for later Praxis expansion."},
    {"name": "Clean Pelt", "type": "furnishing_material", "crafting_profession": "Clothing", "notes": "General furnishing material; included for later Praxis expansion."},
    {"name": "Decorative Wax", "type": "furnishing_material", "crafting_profession": "Provisioning", "notes": "Reusable furnishing material that appears in Praxis recipes."},
    {"name": "Heartwood", "type": "furnishing_material", "crafting_profession": "Woodworking", "notes": "Reusable furnishing material that appears in Praxis recipes."},
    {"name": "Ochre", "type": "furnishing_material", "crafting_profession": "Jewelry Crafting", "notes": "Reusable furnishing material that appears in Praxis recipes."},
    {"name": "Regulus", "type": "furnishing_material", "crafting_profession": "Blacksmithing", "notes": "Reusable furnishing material that appears in Praxis recipes."},
    {"name": "Culanda Lacquer", "type": "style_material", "crafting_profession": None, "notes": "Altmer/Summerset style material found in the Alinor Praxis seed list."},
]


def build_potency_runes() -> List[Dict[str, Any]]:
    potency: List[Dict[str, Any]] = []
    for group in POTENCY_GROUPS:
        for polarity in ("additive", "subtractive"):
            seed = group[polarity]
            entry: Dict[str, Any] = {
                "id": slugify(seed["name"]),
                "name": seed["name"],
                "translation": seed["translation"],
                "polarity": polarity,
                "glyph_prefix": group["glyph_prefix"],
                "level_range": deepcopy(group["level_range"]),
                "potency_improvement_rank": group["potency_improvement_rank"],
                "aliases": seed.get("aliases", []),
                "notes": group.get("notes", seed.get("notes", "")),
                "sources": ["uesp-runestones", "benevolentbowd-enchanting", "eso-hub-enchanting"],
            }
            potency.append(entry)
    return potency


def normalize_essence_runes() -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for rune in ESSENCE_RUNES:
        entry = deepcopy(rune)
        entry.setdefault("notes", "")
        entry["id"] = slugify(entry["name"])
        entry["sources"] = ["uesp-runestones", "benevolentbowd-enchanting", "eso-hub-enchanting"]
        entries.append(entry)
    return entries


def normalize_aspect_runes() -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for rune in ASPECT_RUNES:
        entry = deepcopy(rune)
        entry["id"] = slugify(entry["name"])
        entry["sources"] = ["uesp-runestones", "benevolentbowd-enchanting"]
        entries.append(entry)
    return entries


def display_glyph_name(prefix: str, base_name: str) -> str:
    """Combine a potency prefix with a base glyph name."""
    return f"{prefix} {base_name}".strip()


def generate_glyph_recipes(
    potency_runes: Iterable[Mapping[str, Any]],
    essence_runes: Iterable[Mapping[str, Any]],
    aspect_runes: Iterable[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    recipes: List[Dict[str, Any]] = []
    for potency in potency_runes:
        polarity = str(potency["polarity"])
        for essence in essence_runes:
            result = essence["glyph_results"][polarity]
            for aspect in aspect_runes:
                recipes.append(
                    {
                        "id": slugify(f"{potency['name']}-{essence['name']}-{aspect['name']}"),
                        "potency_rune": potency["name"],
                        "essence_rune": essence["name"],
                        "aspect_rune": aspect["name"],
                        "resulting_glyph_name": display_glyph_name(str(potency["glyph_prefix"]), str(result["glyph_name"])),
                        "base_glyph_name": result["glyph_name"],
                        "level_range": deepcopy(potency["level_range"]),
                        "quality": aspect["quality"],
                        "quality_color": aspect["quality_color"],
                        "effect": result["effect"],
                        "category": result["category"],
                        "polarity": polarity,
                        "source_notes": "Generated from vetted Potency + Essence + Aspect rune tables; not hand-entered.",
                    }
                )
    return recipes


def normalize_praxis_plans() -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for plan in PRAXIS_PLANS:
        entry = deepcopy(plan)
        entry["id"] = slugify(entry["plan_name"].replace("Praxis:", ""))
        entry.setdefault("category", "")
        entry.setdefault("subcategory", "")
        entry.setdefault("materials", {})
        entry.setdefault("source_notes", "")
        entry["known"] = False
        entry["sources"] = ["uesp-furnishing-schematics"]
        entries.append(entry)
    return entries


def build_materials(praxis_plans: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    materials: Dict[str, Dict[str, Any]] = {}
    for seed in MATERIALS_SEED:
        entry = deepcopy(seed)
        entry["id"] = slugify(entry["name"])
        entry.setdefault("notes", "")
        entry["sources"] = ["uesp-furnishing-schematics"]
        materials[entry["name"]] = entry

    # Include any missing material names used by Praxis seed data. This keeps the
    # JSON internally usable even while the Praxis catalog is still growing.
    for plan in praxis_plans:
        for material_name in plan.get("materials", {}).keys():
            materials.setdefault(
                material_name,
                {
                    "id": slugify(material_name),
                    "name": material_name,
                    "type": "unknown_or_rune_material",
                    "crafting_profession": None,
                    "notes": "Auto-added because a Praxis seed entry uses this material; classify on the next data audit.",
                    "sources": ["uesp-furnishing-schematics"],
                },
            )

    return sorted(materials.values(), key=lambda item: item["name"])


def build_data() -> Dict[str, Any]:
    potency = build_potency_runes()
    essence = normalize_essence_runes()
    aspect = normalize_aspect_runes()
    praxis = normalize_praxis_plans()
    materials = build_materials(praxis)
    glyph_recipes = generate_glyph_recipes(potency, essence, aspect)

    data: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "profession": PROFESSION,
        "private_branch_note": "Built for private feature/enchanting branch. No HTML/CSS/JS release changes are included.",
        "sources": SOURCE_NOTES,
        "design_notes": [
            "Glyph recipes are generated because ESO Enchanting is formula-based: Potency + Essence + Aspect.",
            "Praxis plans are a starting tracker seed. User known/unknown state defaults to false and should be persisted separately or merged carefully.",
            "Unknown future values should remain null or empty strings until verified; do not invent plan materials or sources.",
        ],
        "runes": {
            "potency": potency,
            "essence": essence,
            "aspect": aspect,
        },
        "recipe_logic": {
            "formula": "One Potency Rune + one Essence Rune + one Aspect Rune creates one glyph.",
            "potency_role": "Determines glyph prefix/name contribution, additive/subtractive polarity, and usable item level or Champion Point range.",
            "essence_role": "Determines glyph effect and item category result for each polarity.",
            "aspect_role": "Determines glyph quality and quality color.",
            "result_name_template": "{potency.glyph_prefix} {essence.glyph_results[potency.polarity].glyph_name}",
        },
        "glyph_recipes": glyph_recipes,
        "praxis_furnishing_plans": praxis,
        "materials": materials,
        "counts": {
            "potency_runes": len(potency),
            "essence_runes": len(essence),
            "aspect_runes": len(aspect),
            "generated_glyph_recipes": len(glyph_recipes),
            "praxis_seed_plans": len(praxis),
            "materials": len(materials),
        },
    }
    validate_data(data)
    return data


def assert_unique_ids(section_name: str, records: Iterable[Mapping[str, Any]]) -> None:
    seen: set[str] = set()
    for record in records:
        record_id = str(record.get("id", ""))
        if not record_id:
            raise ValueError(f"{section_name} contains a record without an id: {record!r}")
        if record_id in seen:
            raise ValueError(f"{section_name} contains duplicate id: {record_id}")
        seen.add(record_id)


def validate_data(data: Mapping[str, Any]) -> None:
    runes = data["runes"]
    assert len(runes["potency"]) == 32, "Expected 32 potency runes."
    assert len(runes["essence"]) == 19, "Expected 19 essence runes."
    assert len(runes["aspect"]) == 5, "Expected 5 aspect runes."
    assert len(data["glyph_recipes"]) == 32 * 19 * 5, "Generated glyph recipe count is wrong."

    assert_unique_ids("potency runes", runes["potency"])
    assert_unique_ids("essence runes", runes["essence"])
    assert_unique_ids("aspect runes", runes["aspect"])
    assert_unique_ids("glyph recipes", data["glyph_recipes"])
    assert_unique_ids("praxis plans", data["praxis_furnishing_plans"])
    assert_unique_ids("materials", data["materials"])

    for plan in data["praxis_furnishing_plans"]:
        if plan["known"] is not False:
            raise ValueError(f"Praxis plan {plan['plan_name']} must default known=false.")

    known_categories = {"weapon", "armor", "jewelry", "other"}
    for recipe in data["glyph_recipes"]:
        if recipe["category"] not in known_categories:
            raise ValueError(f"Unexpected glyph category: {recipe['category']}")


def serialize_data(data: Mapping[str, Any]) -> str:
    """Return the canonical pretty JSON payload used by both outputs."""
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False)


def write_json(data: Mapping[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(serialize_data(data) + "\n", encoding="utf-8")
    return output_path


def write_js(data: Mapping[str, Any], output_path: Path) -> Path:
    """Write browser-friendly Enchanting data without imports, npm, fetch, or build tools."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    js = (
        "// Generated by tools/build_enchanting_data.py. Do not edit by hand.\n"
        "// Browser global for The Artisan's Ledger Enchanting data.\n"
        f"{JS_GLOBAL_NAME} = {serialize_data(data)};\n"
    )
    output_path.write_text(js, encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Enchanting JSON and browser JS data for The Artisan's Ledger.")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Output JSON path, relative to the current working directory. Default: data/enchanting-data.json",
    )
    parser.add_argument(
        "--js-output",
        default=str(DEFAULT_JS_OUTPUT),
        help="Output JavaScript path, relative to the current working directory. Default: data/enchanting-data.js",
    )
    parser.add_argument(
        "--pretty-counts",
        action="store_true",
        help="Print record counts after writing the file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = build_data()
    output_path = write_json(data, Path(args.output))
    js_output_path = write_js(data, Path(args.js_output))
    print(f"Wrote {output_path}")
    print(f"Wrote {js_output_path}")
    if args.pretty_counts:
        print(json.dumps(data["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
