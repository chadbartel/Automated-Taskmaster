# Standard Library
import os
from typing import Optional

# Third Party
import boto3
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger

# Initialize logger
logger = Logger(service="at-ip-authorizer-utils")

# Get SSM parameter name from environment variable (set by CDK)
HOME_IP_SSM_PARAMETER_NAME = os.environ.get("HOME_IP_SSM_PARAMETER_NAME")


def get_ssm_client() -> Optional[boto3.client]:
    """Initializes and returns a Boto3 SSM client.

    Returns
    -------
    Optional[boto3.client]
        The initialized SSM client or None if initialization fails.
    """
    try:
        ssm_client = boto3.client("ssm")
    except Exception as e:
        logger.exception(f"Failed to initialize Boto3 SSM client: {e}")
        ssm_client = None
    return ssm_client


def get_allowed_ip_from_ssm() -> Optional[str]:
    """Fetches the allowed IP address from SSM Parameter Store.

    This function retrieves the IP address stored in the SSM parameter defined
    by the environment variable `HOME_IP_SSM_PARAMETER_NAME`. It returns the IP
    address as a string if found, otherwise returns None.

    Returns
    -------
    Optional[str]
        The allowed IP address as a string if found, otherwise None.
    """
    ssm_client = get_ssm_client()
    if not ssm_client or not HOME_IP_SSM_PARAMETER_NAME:
        logger.error("SSM client or parameter name not configured.")
        return None
    try:
        logger.debug(
            f"Fetching IP from SSM parameter: {HOME_IP_SSM_PARAMETER_NAME}"
        )
        parameter = ssm_client.get_parameter(
            Name=HOME_IP_SSM_PARAMETER_NAME, WithDecryption=False
        )
        ip_address = parameter.get("Parameter", {}).get("Value")
        if ip_address:
            logger.info(
                f"Successfully fetched allowed IP from SSM: {ip_address}"
            )
            return ip_address
        else:
            logger.error("SSM parameter value is empty or not found.")
            return None
    except ClientError as e:
        logger.exception(
            f"Error fetching IP from SSM parameter '{HOME_IP_SSM_PARAMETER_NAME}': {e}"
        )
        return None
    except Exception as e:
        # Catch any other unexpected errors
        logger.exception(f"Unexpected error fetching IP from SSM: {e}")
        return None
