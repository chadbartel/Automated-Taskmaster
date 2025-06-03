# Standard Library
import os

# Third Party
from fastapi import APIRouter

# Local Modules
from automated_taskmaster.routers import summon, documentation

# Create a router instance with a default prefix
router = APIRouter(prefix=f"/{os.getenv('API_PREFIX', 'api/v1')}")

# Include other routers
router.include_router(summon.router)
router.include_router(documentation.router)
