# Third Party
from fastapi import APIRouter, Depends
from aws_lambda_powertools import Logger

# Local Modules
from automated_taskmaster.helpers.utils import verify_client_id_address
from automated_taskmaster.models.monster import (
    MonsterSummonRequest,
    MonsterSummonResponse,
)
from automated_taskmaster.helpers.monster_summoner import find_monsters

# Initialize a logger
logger = Logger(service="at-api-summon")


# Define the FastAPI router
router = APIRouter(prefix="/summon-monster", tags=["summoner"])


@router.post(
    "",
    response_model=MonsterSummonResponse,
    dependencies=[Depends(verify_client_id_address)],
)
async def summon_monster_endpoint(
    request_params: MonsterSummonRequest,
) -> MonsterSummonResponse:
    """Endpoint to summon monsters based on the provided parameters."""
    # Log the request parameters
    logger.info(
        "Summon monster request received.",
        extra=request_params.model_dump(mode="json"),
    )

    # Find monsters based on the request parameters
    monsters_found = find_monsters(request_params)

    # Log the number of monsters found
    logger.info(
        f"Monsters found: {len(monsters_found)}",
        extra={
            "monsters": [
                monster.model_dump(mode="json") for monster in monsters_found
            ]
        },
    )

    return MonsterSummonResponse(
        query_parameters=request_params,
        summoned_monsters=monsters_found,
        count=len(monsters_found),
    )
