from aws_cdk import aws_ecr as ecr, RemovalPolicy
from constructs import Construct


class CustomEcrRepository(Construct):
    def __init__(
        self, scope: Construct, id: str, name: str, stack_suffix: str, **kwargs
    ) -> None:
        """Custom ECR Repository Construct for AWS CDK.

        Parameters
        ----------
        scope : Construct
            The scope in which this construct is defined.
        id : str
            The ID of the construct.
        name : str
            The name of the ECR repository.
        stack_suffix : str
            Suffix to append to the ECR repository name.
        """
        super().__init__(scope, id, **kwargs)

        # Append stack suffix to name if provided
        if stack_suffix:
            name = f"{name}{stack_suffix}"

        # Create the ECR repository
        self.repository = ecr.Repository(
            self,
            "EcrRepository",
            repository_name=name,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_images=True,
        )
