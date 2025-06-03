# Standard Library
from typing import Dict, Any

# Third Party
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from ip_authorizer.utils import get_allowed_ip_from_ssm

# Initialize logger
logger = Logger()


@logger.inject_lambda_context(log_event=False)
def lambda_handler(
    event: Dict[str, Any], context: LambdaContext
) -> Dict[str, Any]:
    """Lambda Authorizer for API Gateway HTTP API.

    Validates the source IP of the request against an IP stored in SSM
    Parameter Store. The API Gateway authorizer cache TTL should be set to 0
    for this to be checked on every request.

    Parameters
    ----------
    event : Dict[str, Any]
        The event data passed to the Lambda function, which includes the
        request context containing the source IP.
    context : LambdaContext
        The context object provided by AWS Lambda, containing metadata about
        the invocation, function, and execution environment.

    Returns
    -------
    Dict[str, Any]
        A dictionary indicating whether the request is authorized or not.
        If the source IP matches the allowed IP from SSM, returns
        `{"isAuthorized": True}`, otherwise returns `{"isAuthorized": False}`.
    """
    logger.info("IP Authorizer invoked.")

    # For HTTP API Lambda Authorizer of type 'REQUEST', the source IP is typically in:
    # event['requestContext']['http']['sourceIp']
    source_ip = event.get("requestContext", {}).get("http", {}).get("sourceIp")

    # Check if source IP is present in the event
    if not source_ip:
        logger.warning("Source IP not found in the event. Denying request.")
        return {"isAuthorized": False}

    # Log the source IP for debugging purposes
    logger.append_keys(source_ip=source_ip)

    # Fetch the allowed IP from SSM on every invocation (as per "0 second cache" for the value)
    allowed_ip = get_allowed_ip_from_ssm()

    # Check if the allowed IP was retrieved successfully
    if not allowed_ip:
        logger.error(
            "Could not retrieve allowed IP from SSM. Denying request."
        )
        return {"isAuthorized": False}

    # Log the allowed IP for debugging purposes
    if source_ip == allowed_ip:
        logger.info(
            f"Authorization successful for source IP: {source_ip} "
            f"(matches SSM value: {allowed_ip})"
        )
        return {"isAuthorized": True}
    # If the source IP does not match the allowed IP, deny the request
    else:
        logger.warning(
            f"Authorization denied. Source IP {source_ip} does not match "
            f"allowed IP {allowed_ip} from SSM."
        )
        return {"isAuthorized": False}
