# Standard Library
from typing import Dict, Any

# Third Party
from fastapi import FastAPI
from mangum import Mangum
from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

# Local Modules
from automated_taskmaster.api import router

# Initialize a logger
logger = Logger()

# Create a FastAPI application instance
app = FastAPI(
    title="Automated Taskmaster API",
    version="0.1.0",
    description="Provides TTRPG utilities like monster summoning.",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# Add the API router to the FastAPI app
app.include_router(router)


@logger.inject_lambda_context(
    log_event=True, correlation_id_path=correlation_paths.API_GATEWAY_HTTP
)
def lambda_handler(
    event: Dict[str, Any], context: LambdaContext
) -> Dict[str, Any]:
    """Lambda handler function to adapt the FastAPI app for AWS Lambda.

    Parameters
    ----------
    event : Dict[str, Any]
        The event data passed to the Lambda function.
    context : LambdaContext
        The context object containing runtime information.

    Returns
    -------
    Dict[str, Any]
        The response from the FastAPI application.
    """
    # Create a Mangum handler to adapt FastAPI for AWS Lambda
    handler = Mangum(app)

    # Return the response from the FastAPI application
    return handler(event, context)
