import aws_cdk as cdk
from aws_cdk import aws_cognito as cognito
from constructs import Construct


class AuthStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.user_pool = cognito.UserPool(
            self, "ManagerPool",
            user_pool_name="training-manager-pool",
            self_sign_up_enabled=False,
            sign_in_aliases=cognito.SignInAliases(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=12,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True,
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        self.user_pool_client = self.user_pool.add_client(
            "ManagerClient",
            auth_flows=cognito.AuthFlow(user_password=True, user_srp=True),
            generate_secret=False,
        )

        cdk.CfnOutput(self, "UserPoolId", value=self.user_pool.user_pool_id)
        cdk.CfnOutput(self, "UserPoolClientId", value=self.user_pool_client.user_pool_client_id)
