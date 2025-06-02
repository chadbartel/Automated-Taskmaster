# Standard Library
from typing import List

# Third Party
from fastapi import Request, HTTPException
from aws_lambda_powertools import Logger

# Initialize a logger
logger = Logger(service="at-utils")


def verify_client_id_address(request: Request, allowed_ips: List[str]) -> bool:
    """Verify the client's IP address against allowed IPs for API access.

    Parameters
    ----------
    request : Request
        The FastAPI request object containing client information.
    allowed_ips : List[str]
        A list of allowed IP addresses for accessing the API.

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
        f"Docs access attempt from IP: {source_ip}. Allowed: {allowed_ips}"
    )

    # Check if the source IP is None or not in the allowed list
    if not allowed_ips:
        logger.warning(
            "WARN: ALLOWED_DOCS_IPS is not set. Denying docs access."
        )
        raise HTTPException(
            status_code=403, detail="Documentation access is disabled."
        )
    if source_ip not in allowed_ips:
        logger.warning(f"WARN: Forbidden docs access for IP: {source_ip}")
        raise HTTPException(
            status_code=403, detail="Access to documentation is restricted."
        )

    return True
