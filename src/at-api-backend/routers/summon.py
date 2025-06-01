from fastapi import APIRouter, Depends  # Added Depends if you want to protect this route too
from models.monster import MonsterSummonRequest, MonsterSummonResponse  # Adjusted import path
from automated_taskmaster.monster_summoner import find_monsters
# from ..handler import verify_ip_for_docs # If you had a generic auth for regular endpoints too

router = APIRouter(
    prefix="/taskmaster",  # Base prefix for all routes in this router
    tags=["summoner"],
)


@router.post("/summon-monster", response_model=MonsterSummonResponse)
async def summon_monster_endpoint(request_params: MonsterSummonRequest):
    """
    Summons monsters based on the provided criteria.
    Filters by Challenge Rating (CR) and environment type.
    """
    print(f"Summon monster request received: {request_params.dict()}") # Replace with logger
    monsters_found = find_monsters(request_params)
    return MonsterSummonResponse(
        query_parameters=request_params,
        summoned_monsters=monsters_found,
        count=len(monsters_found)
    )
