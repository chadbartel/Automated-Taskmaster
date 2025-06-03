# Third Party
from fastapi import APIRouter

# Local Modules
from automated_taskmaster.routers import summon

# Create a router instance with a default prefix
router = APIRouter()

# Include other routers
router.include_router(summon.router)
