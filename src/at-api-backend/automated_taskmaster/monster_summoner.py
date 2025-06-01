import json
import os
from typing import List, Dict, Any
from models.monster import Monster, MonsterSummonRequest  # Assuming models.py is directly under models/

# Path to monsters.json relative to this file's location in app_logic/
# The `src/automated-taskmaster/` will be the root inside the Docker container's /app
_MONSTER_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'monsters.json')
_MONSTERS: List[Dict[str, Any]] = []


def _load_monsters():
    global _MONSTERS
    if not _MONSTERS:
        try:
            with open(_MONSTER_DATA_FILE, 'r') as f:
                _MONSTERS = json.load(f)
            print(f"Successfully loaded monster data from: {_MONSTER_DATA_FILE}") # Replace with logger
        except FileNotFoundError:
            print(f"ERROR: Monster data file not found at {_MONSTER_DATA_FILE}")
            _MONSTERS = []
        except json.JSONDecodeError:
            print(f"ERROR: Could not decode monster data from {_MONSTER_DATA_FILE}")
            _MONSTERS = []
_load_monsters()


def _convert_cr_to_float(cr: Any) -> float:
    if isinstance(cr, (int, float)): return float(cr)
    if isinstance(cr, str):
        if "/" in cr:
            try: num, den = map(float, cr.split('/')); return num / den
            except ValueError: return -1 # Handle malformed fractions
        try: return float(cr)
        except ValueError: return -1
    return -1


def find_monsters(params: MonsterSummonRequest) -> List[Monster]:
    if not _MONSTERS: _load_monsters() # Attempt to reload if empty
    if not _MONSTERS: return []

    results = []
    for m_data in _MONSTERS:
        monster_cr_float = _convert_cr_to_float(m_data.get("cr", -1))
        if params.cr_min is not None and monster_cr_float < params.cr_min: continue
        if params.cr_max is not None and monster_cr_float > params.cr_max: continue
        if params.environment:
            env_match = any(params.environment.lower() in env.lower() for env in m_data.get("environment", []))
            if not env_match: continue
        
        # Ensure all required fields for Monster model are present or have defaults
        try:
            results.append(Monster(**m_data))
        except Exception as e: # Catch Pydantic validation error or others
            print(f"Error creating Monster object from data: {m_data}. Error: {e}") # Replace with logger
            continue # Skip this monster if data is incompatible
        
        if len(results) >= params.limit: break
    return results
