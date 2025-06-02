# Standard Library
import os

# Third Party
from fastapi import Request, HTTPException
from aws_lambda_powertools import Logger

# Initialize a logger
logger = Logger(service="at-utils")

# Set static variables
API_PREFIX = os.getenv("API_PREFIX", "api/v1")
ALLOWED_IPS_STR = os.environ.get("ALLOWED_IPS", "")
ALLOWED_IPS = [
    ip.strip() for ip in ALLOWED_IPS_STR.split(",") if ip.strip()
]


def verify_client_id_address(request: Request) -> bool:
    """Verify the client's IP address against allowed IPs for API access.

    Parameters
    ----------
    request : Request
        The FastAPI request object containing client information.

    Returns
    -------
    bool
        True if the client's IP is allowed, otherwise raises HTTPException.

    Raises
    ------
    HTTPException
        If the client's IP is not in the allowed list or if the allowed list is empty.
    """
    # Initialize the source IP to None
    source_ip = None

    # Check if the request is from AWS Lambda and extract the source IP
    if "aws.event" in request.scope and request.scope["aws.event"].get(
        "requestContext", {}
    ).get("http"):
        source_ip = request.scope["aws.event"]["requestContext"]["http"].get(
            "sourceIp"
        )
    elif request.client:
        source_ip = request.client.host

    # Log the source IP and allowed IPs for debugging
    logger.debug(
        f"Docs access attempt from IP: {source_ip}. Allowed: {ALLOWED_IPS}"
    )

    # Check if the source IP is None or not in the allowed list
    if not ALLOWED_IPS:
        logger.warning(
            "WARN: ALLOWED_IPS is not set. Denying docs access."
        )
        raise HTTPException(
            status_code=403, detail="Documentation access is disabled."
        )
    if source_ip not in ALLOWED_IPS:
        logger.warning(f"WARN: Forbidden docs access for IP: {source_ip}")
        raise HTTPException(
            status_code=403, detail="Access to documentation is restricted."
        )

    return True
