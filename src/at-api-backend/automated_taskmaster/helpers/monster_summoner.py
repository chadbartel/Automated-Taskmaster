# Standard Library
import os
import json
from functools import lru_cache
from typing import List, Dict, Any

# Third Party
from aws_lambda_powertools import Logger

# Local Modules
from automated_taskmaster.models.monster import Monster, MonsterSummonRequest

# Initialize a logger
logger = Logger(service="at-monster-summoner")

# Static variables
_MONSTER_DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "monsters.json"
)
_MONSTERS_CACHE: List[Monster] = []


@lru_cache(maxsize=1)
def load_monsters_cached() -> List[Monster]:
    """Load monsters with caching to avoid repeated file I/O.

    Returns
    -------
    List[Monster]
        A list of `Monster` objects loaded from the JSON file.
    """
    # Set up a global cache for monsters
    global _MONSTERS_CACHE

    # If the cache is empty, load the data from the JSON file
    if _MONSTERS_CACHE is None:
        with open(_MONSTER_DATA_FILE, "r") as f:
            data = json.load(f)
        _MONSTERS_CACHE = [Monster(**monster) for monster in data]
    return _MONSTERS_CACHE


def _convert_cr_to_float(cr: Any) -> float:
    """Convert Challenge Rating (CR) to a float.
    This function handles various formats of CR, including integers,
    floats, and strings (including fractions).

    Parameters
    ----------
    cr : Any
        The Challenge Rating to convert, which can be an int, float, or str.

    Returns
    -------
    float
        The converted Challenge Rating as a float, or -1 if conversion fails.
    """
    # Check if CR is already a float or int
    if isinstance(cr, (int, float)):
        return float(cr)
    # Check if CR is a string and handle fractions or numeric strings
    if isinstance(cr, str):
        if "/" in cr:
            try:
                num, den = map(float, cr.split("/"))
                return num / den
            except ValueError:
                return -1  # Handle malformed fractions
        try:
            return float(cr)
        except ValueError:
            return -1

    # If CR is not a recognized type, return -1
    return -1


def find_monsters(params: MonsterSummonRequest) -> List[Monster]:
    """Find monsters based on the provided parameters.
    This function filters the loaded monster data based on the Challenge Rating
    (CR) range and environment specified in the `params`. It returns a list of
    `Monster` objects that match the criteria.

    Parameters
    ----------
    params : MonsterSummonRequest
        The parameters for filtering monsters, including CR range and
        environment.

    Returns
    -------
    List[Monster]
        A list of `Monster` objects that match the specified criteria.
    """
    # Load cached monster data
    monsters = load_monsters_cached()

    # Initialize an empty list to store the results
    results = []

    # Iterate through the loaded monster data
    for monster in monsters:
        # Dump the monster data to a dictionary
        monster_data: Dict[str, Any] = monster.model_dump(mode="json")
        # Convert CR to float for comparison
        monster_cr_float = _convert_cr_to_float(monster_data.get("cr", -1))
        # Skip monsters with CR below the minimum specified
        if params.cr_min is not None and monster_cr_float < params.cr_min:
            continue
        # Skip monsters with CR above the maximum specified
        if params.cr_max is not None and monster_cr_float > params.cr_max:
            continue
        # Skip monsters without an environment if one is specified
        if params.environment:
            env_match = any(
                params.environment.lower() in env.lower()
                for env in monster_data.get("environment", [])
            )
            if not env_match:
                continue

        # Ensure all required fields for Monster model are present or have defaults
        try:
            results.append(Monster(**monster_data))
        except Exception as e:  # Catch Pydantic validation error or others
            logger.warning(
                f"Error creating Monster object from data: {monster_data}. Error: {e}"
            )
            continue  # Skip this monster if data is incompatible

        # Check if we have reached the limit of results
        if len(results) >= params.limit:
            break

    return results
