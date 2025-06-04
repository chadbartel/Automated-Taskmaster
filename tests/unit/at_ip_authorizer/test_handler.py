# Standard Library
from typing import Generator, Any, Dict
from unittest.mock import MagicMock, patch

# Third Party
import pytest

# My Modules
from tests.conftest import import_handler


@pytest.fixture
def handler_module():
    """Import and return the at-ip-authorizer handler module."""
    return import_handler("at-ip-authorizer")


@pytest.fixture
def mock_logger(handler_module: MagicMock) -> Generator[MagicMock, None, None]:
    """Mock the logger instance in the handler."""
    with patch.object(handler_module, "logger") as mock_log:
        yield mock_log


@pytest.fixture
def mock_get_allowed_ip(
    handler_module: MagicMock,
) -> Generator[MagicMock, None, None]:
    """Mock the get_allowed_ip_from_ssm function."""
    with patch.object(
        handler_module, "get_allowed_ip_from_ssm"
    ) as mock_get_ip:
        yield mock_get_ip


@pytest.fixture
def sample_lambda_context() -> MagicMock:
    """Return a sample Lambda context object."""
    context = MagicMock()
    context.function_name = "test_authorizer_lambda"
    context.memory_limit_in_mb = 256
    context.aws_request_id = "test-authorizer-request-id"
    context.invoked_function_arn = (
        "arn:aws:lambda:us-east-1:123456789012:function:test_authorizer"
    )
    return context


@pytest.fixture
def sample_api_gateway_event() -> Dict[str, Any]:
    """Return a sample API Gateway HTTP API event."""
    return {
        "version": "2.0",
        "type": "REQUEST",
        "routeArn": "arn:aws:execute-api:us-east-1:123456789012:abcdef123/test/GET/resource",
        "identitySource": ["$request.header.Authorization"],
        "routeKey": "GET /resource",
        "rawPath": "/resource",
        "rawQueryString": "",
        "headers": {
            "accept": "application/json",
            "content-length": "0",
            "host": "api.example.com",
            "user-agent": "test-client/1.0",
        },
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "abcdef123",
            "domainName": "api.example.com",
            "http": {
                "method": "GET",
                "path": "/resource",
                "protocol": "HTTP/1.1",
                "sourceIp": "192.168.1.100",
                "userAgent": "test-client/1.0",
            },
            "requestId": "test-request-id",
            "routeKey": "GET /resource",
            "stage": "test",
            "time": "01/Jan/2023:12:00:00 +0000",
            "timeEpoch": 1672574400000,
        },
    }


class TestIPAuthorizerHandler:
    """Test class for the IP authorizer handler."""

    def test_lambda_handler_success_authorization(
        self,
        handler_module: MagicMock,
        mock_logger: MagicMock,
        mock_get_allowed_ip: MagicMock,
        sample_api_gateway_event: Dict[str, Any],
        sample_lambda_context: MagicMock,
    ):
        """Test successful authorization with matching IP address."""
        # Arrange
        source_ip = "192.168.1.100"
        mock_get_allowed_ip.return_value = source_ip

        # Act
        result = handler_module.lambda_handler(
            sample_api_gateway_event, sample_lambda_context
        )

        # Assert
        assert result == {"isAuthorized": True}
        mock_logger.info.assert_any_call("IP Authorizer invoked.")
        mock_logger.append_keys.assert_called_once_with(source_ip=source_ip)
        mock_logger.info.assert_any_call(
            f"Authorization successful for source IP: {source_ip} "
            f"(matches SSM value: {source_ip})"
        )
        mock_get_allowed_ip.assert_called_once()

    def test_lambda_handler_denied_different_ip(
        self,
        handler_module: MagicMock,
        mock_logger: MagicMock,
        mock_get_allowed_ip: MagicMock,
        sample_api_gateway_event: Dict[str, Any],
        sample_lambda_context: MagicMock,
    ):
        """Test authorization denied when source IP doesn't match allowed IP."""
        # Arrange
        source_ip = "192.168.1.100"
        allowed_ip = "10.0.0.1"
        mock_get_allowed_ip.return_value = allowed_ip

        # Act
        result = handler_module.lambda_handler(
            sample_api_gateway_event, sample_lambda_context
        )

        # Assert
        assert result == {"isAuthorized": False}
        mock_logger.warning.assert_called_once_with(
            f"Authorization denied. Source IP {source_ip} does not match "
            f"allowed IP {allowed_ip} from SSM."
        )
        mock_get_allowed_ip.assert_called_once()

    def test_lambda_handler_denied_missing_source_ip(
        self,
        handler_module: MagicMock,
        mock_logger: MagicMock,
        mock_get_allowed_ip: MagicMock,
        sample_lambda_context: MagicMock,
    ):
        """Test authorization denied when source IP is missing from event."""
        # Arrange
        event_without_source_ip = {"requestContext": {"http": {}}}

        # Act
        result = handler_module.lambda_handler(
            event_without_source_ip, sample_lambda_context
        )

        # Assert
        assert result == {"isAuthorized": False}
        mock_logger.warning.assert_called_once_with(
            "Source IP not found in the event. Denying request."
        )
        mock_get_allowed_ip.assert_not_called()

    def test_lambda_handler_denied_missing_request_context(
        self,
        handler_module: MagicMock,
        mock_logger: MagicMock,
        mock_get_allowed_ip: MagicMock,
        sample_lambda_context: MagicMock,
    ):
        """Test authorization denied when requestContext is missing."""
        # Arrange
        event_without_context = {}

        # Act
        result = handler_module.lambda_handler(
            event_without_context, sample_lambda_context
        )

        # Assert
        assert result == {"isAuthorized": False}
        mock_logger.warning.assert_called_once_with(
            "Source IP not found in the event. Denying request."
        )
        mock_get_allowed_ip.assert_not_called()

    def test_lambda_handler_denied_missing_http_context(
        self,
        handler_module: MagicMock,
        mock_logger: MagicMock,
        mock_get_allowed_ip: MagicMock,
        sample_lambda_context: MagicMock,
    ):
        """Test authorization denied when http context is missing."""
        # Arrange
        event_without_http = {"requestContext": {}}

        # Act
        result = handler_module.lambda_handler(
            event_without_http, sample_lambda_context
        )

        # Assert
        assert result == {"isAuthorized": False}
        mock_logger.warning.assert_called_once_with(
            "Source IP not found in the event. Denying request."
        )
        mock_get_allowed_ip.assert_not_called()

    def test_lambda_handler_denied_ssm_retrieval_failure(
        self,
        handler_module: MagicMock,
        mock_logger: MagicMock,
        mock_get_allowed_ip: MagicMock,
        sample_api_gateway_event: Dict[str, Any],
        sample_lambda_context: MagicMock,
    ):
        """Test authorization denied when SSM parameter retrieval fails."""
        # Arrange
        source_ip = "192.168.1.100"
        mock_get_allowed_ip.return_value = None

        # Act
        result = handler_module.lambda_handler(
            sample_api_gateway_event, sample_lambda_context
        )

        # Assert
        assert result == {"isAuthorized": False}
        mock_logger.append_keys.assert_called_once_with(source_ip=source_ip)
        mock_logger.error.assert_called_once_with(
            "Could not retrieve allowed IP from SSM. Denying request."
        )
        mock_get_allowed_ip.assert_called_once()

    def test_lambda_handler_denied_empty_allowed_ip(
        self,
        handler_module: MagicMock,
        mock_logger: MagicMock,
        mock_get_allowed_ip: MagicMock,
        sample_api_gateway_event: Dict[str, Any],
        sample_lambda_context: MagicMock,
    ):
        """Test authorization denied when allowed IP is empty string."""
        # Arrange
        source_ip = "192.168.1.100"
        mock_get_allowed_ip.return_value = ""

        # Act
        result = handler_module.lambda_handler(
            sample_api_gateway_event, sample_lambda_context
        )

        # Assert
        assert result == {"isAuthorized": False}
        mock_logger.error.assert_called_once_with(
            "Could not retrieve allowed IP from SSM. Denying request."
        )

    @pytest.mark.parametrize(
        "source_ip,allowed_ip,should_authorize",
        [
            ("192.168.1.100", "192.168.1.100", True),
            ("10.0.0.1", "10.0.0.1", True),
            ("127.0.0.1", "127.0.0.1", True),
            ("203.0.113.1", "203.0.113.1", True),
            ("192.168.1.100", "192.168.1.101", False),
            ("10.0.0.1", "192.168.1.1", False),
            ("127.0.0.1", "10.0.0.1", False),
            ("192.168.1.100", "203.0.113.1", False),
        ],
    )
    def test_lambda_handler_parametrized_ip_authorization(
        self,
        handler_module: MagicMock,
        mock_logger: MagicMock,
        mock_get_allowed_ip: MagicMock,
        sample_api_gateway_event: Dict[str, Any],
        sample_lambda_context: MagicMock,
        source_ip: str,
        allowed_ip: str,
        should_authorize: bool,
    ):
        """Test various IP authorization scenarios with parameterized inputs."""
        # Arrange
        sample_api_gateway_event["requestContext"]["http"][
            "sourceIp"
        ] = source_ip
        mock_get_allowed_ip.return_value = allowed_ip

        # Act
        result = handler_module.lambda_handler(
            sample_api_gateway_event, sample_lambda_context
        )

        # Assert
        assert result == {"isAuthorized": should_authorize}
        mock_logger.append_keys.assert_called_once_with(source_ip=source_ip)

    def test_lambda_handler_logging_context_injection(
        self,
        handler_module: MagicMock,
        mock_get_allowed_ip: MagicMock,
        sample_api_gateway_event: Dict[str, Any],
        sample_lambda_context: MagicMock,
    ):
        """Test that the lambda_handler has proper logging context injection."""
        # Arrange
        mock_get_allowed_ip.return_value = "192.168.1.100"

        # Act
        handler_func = handler_module.lambda_handler

        # Assert - Check if the function has the inject_lambda_context decorator
        assert hasattr(handler_func, "__wrapped__")

        # Act - Call the function to verify it works
        result = handler_module.lambda_handler(
            sample_api_gateway_event, sample_lambda_context
        )

        # Assert - Verify basic functionality
        assert "isAuthorized" in result
        assert isinstance(result["isAuthorized"], bool)

    def test_lambda_handler_with_none_source_ip_in_http(
        self,
        handler_module: MagicMock,
        mock_logger: MagicMock,
        mock_get_allowed_ip: MagicMock,
        sample_lambda_context: MagicMock,
    ):
        """Test authorization denied when sourceIp is None in http context."""
        # Arrange
        event_with_none_source_ip = {
            "requestContext": {"http": {"sourceIp": None}}
        }

        # Act
        result = handler_module.lambda_handler(
            event_with_none_source_ip, sample_lambda_context
        )

        # Assert
        assert result == {"isAuthorized": False}
        mock_logger.warning.assert_called_once_with(
            "Source IP not found in the event. Denying request."
        )
        mock_get_allowed_ip.assert_not_called()

    def test_lambda_handler_with_empty_string_source_ip(
        self,
        handler_module: MagicMock,
        mock_logger: MagicMock,
        mock_get_allowed_ip: MagicMock,
        sample_lambda_context: MagicMock,
    ):
        """Test authorization denied when sourceIp is empty string."""
        # Arrange
        event_with_empty_source_ip = {
            "requestContext": {"http": {"sourceIp": ""}}
        }

        # Act
        result = handler_module.lambda_handler(
            event_with_empty_source_ip, sample_lambda_context
        )

        # Assert
        assert result == {"isAuthorized": False}
        mock_logger.warning.assert_called_once_with(
            "Source IP not found in the event. Denying request."
        )
        mock_get_allowed_ip.assert_not_called()
