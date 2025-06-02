# Standard Library
from typing import Optional, List

# Third Party
from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as apigwv2_integrations,
    Duration,
    CfnOutput,
)
from constructs import Construct

# Local Modules
from cdk.custom_constructs.lambda_function import CustomLambdaFromDockerImage
from cdk.custom_constructs.http_api import CustomHttpApiGateway


class AutomatedTaskmasterStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, stack_suffix: str, **kwargs
    ) -> None:
        """Automated Taskmaster stack for AWS CDK.

        Parameters
        ----------
        scope : Construct
            The scope in which this construct is defined.
        construct_id : str
            The ID of the construct.
        stack_suffix : Optional[str], optional
            Suffix to append to resource names for this stack, by default ""
        """
        self.api_prefix = kwargs.pop("api_prefix", "api/v1")
        super().__init__(scope, construct_id, **kwargs)

        # region Stack Suffix and Subdomain Configuration
        self.stack_suffix = (stack_suffix if stack_suffix else "").lower()
        self.base_domain_name = "thatsmidnight.com"
        self.subdomain_part = "automated-taskmaster"
        self.full_domain_name = (
            f"{self.subdomain_part}{self.stack_suffix}.{self.base_domain_name}"
        )
        self.allowed_docs_ips_from_context = (
            self.node.try_get_context("allowed_docs_ips") or "127.0.0.1"
        )
        # endregion

        # region Backend Lambda Function
        taskmaster_backend_lambda = self.create_lambda_function(
            construct_id="TaskmasterBackendLambda",
            src_folder_path="at-api-backend",
            environment={
                "ALLOWED_DOCS_IPS": self.allowed_docs_ips_from_context,
                "API_PREFIX": self.api_prefix,
            },
            memory_size=512,
            timeout=Duration.minutes(30),
            description="Automated Taskmaster backend Lambda function",
        )
        # endregion

        # region HTTP API Gateway
        # Create a custom HTTP API Gateway
        taskmaster_api = CustomHttpApiGateway(
            scope=self,
            id="TaskmasterHttpApi",
            name="automated-taskmaster-api",
            allow_methods=[apigwv2.CorsHttpMethod.ANY],
            allow_headers=["Content-Type", "Authorization", "*"],
            max_age=Duration.days(1),
        ).http_api

        # Create Lambda integration for the API
        taskmaster_integration = apigwv2_integrations.HttpLambdaIntegration(
            "TaskmasterIntegration", handler=taskmaster_backend_lambda
        )

        # Create proxy route for the API
        taskmaster_api.add_routes(
            path="/".join([f"/{self.api_prefix}", "{proxy+}"]),
            methods=[apigwv2.HttpMethod.ANY],
            integration=taskmaster_integration,
        )
        # endregion

        # region Outputs
        CfnOutput(
            self,
            "TaskmasterApiEndpoint",
            value=taskmaster_api.api_endpoint,
            description="Endpoint for Automated Taskmaster API",
            export_name=(
                f"automated-taskmaster-api-endpoint{self.stack_suffix}"
            ),
        )
        CfnOutput(
            self,
            "CustomApiUrlOutput",
            value=f"https://{self.full_domain_name}",
            description="Custom API URL for Automated Taskmaster",
            export_name=(
                f"automated-taskmaster-custom-api-url{self.stack_suffix}"
            ),
        )
        # endregion

    def create_lambda_function(
        self,
        construct_id: str,
        src_folder_path: str,
        environment: Optional[dict] = None,
        memory_size: Optional[int] = 128,
        timeout: Optional[Duration] = Duration.seconds(10),
        initial_policy: Optional[List[iam.PolicyStatement]] = None,
        description: Optional[str] = None,
    ) -> _lambda.Function:
        """Helper method to create a Lambda function.

        Parameters
        ----------
        construct_id : str
            The ID of the construct.
        src_folder_path : str
            The path to the source folder for the Lambda function code.
        environment : Optional[dict], optional
            Environment variables for the Lambda function, by default None
        memory_size : Optional[int], optional
            Memory size for the Lambda function, by default 128
        timeout : Optional[Duration], optional
            Timeout for the Lambda function, by default Duration.seconds(10)
        initial_policy : Optional[List[iam.PolicyStatement]], optional
            Initial IAM policies to attach to the Lambda function, by default None
        description : Optional[str], optional
            Description for the Lambda function, by default None

        Returns
        -------
        _lambda.Function
            The created Lambda function instance.
        """
        custom_lambda = CustomLambdaFromDockerImage(
            scope=self,
            id=construct_id,
            src_folder_path=src_folder_path,
            stack_suffix=self.stack_suffix,
            environment=environment,
            memory_size=memory_size,
            timeout=timeout,
            initial_policy=initial_policy or [],
            description=description,
        )
        return custom_lambda.function
