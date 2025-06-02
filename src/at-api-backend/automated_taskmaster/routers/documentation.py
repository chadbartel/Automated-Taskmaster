# Standard Library
from typing import Dict, Any

# Third Party
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from aws_lambda_powertools import Logger

# Local Modules
from automated_taskmaster.utils import verify_client_id_address

# Initialize a logger
logger = Logger(service="at-api-documentation")

# Define the FastAPI router
router = APIRouter(tags=["documentation"])


@router.get(
    "/openapi.json",
    include_in_schema=False,
    dependencies=[Depends(verify_client_id_address)],
)
async def custom_openapi_endpoint() -> Dict[str, Any]:
    """Custom OpenAPI endpoint with IP verification.

    Returns
    -------
    Dict[str, Any]
        The OpenAPI schema for the application.
    """
    return get_openapi(
        title=router.app.title,
        version=router.app.version,
        description=router.app.description,
        routes=router.app.routes,
    )


@router.get(
    "/docs",
    include_in_schema=False,
    dependencies=[Depends(verify_client_id_address)],
)
async def custom_swagger_ui_html() -> HTMLResponse:
    """Custom Swagger UI endpoint with IP verification.

    Returns
    -------
    HTMLResponse
        The HTML response for the Swagger UI documentation.
    """
    return get_swagger_ui_html(
        openapi_url="/openapi.json", title=router.app.title + " - Swagger UI"
    )


@router.get(
    "/redoc",
    include_in_schema=False,
    dependencies=[Depends(verify_client_id_address)],
)
async def custom_redoc_html() -> HTMLResponse:
    """Custom ReDoc endpoint with IP verification.

    Returns
    -------
    HTMLResponse
        The HTML response for the ReDoc documentation.
    """
    return get_redoc_html(
        openapi_url="/openapi.json", title=router.app.title + " - ReDoc"
    )
