#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.database_stack import DatabaseStack
from stacks.auth_stack import AuthStack
from stacks.api_stack import ApiStack
from stacks.frontend_stack import FrontendStack

app = cdk.App()
env = cdk.Environment(region="eu-west-1")

db = DatabaseStack(app, "DatabaseStack", env=env)
auth = AuthStack(app, "AuthStack", env=env)
api = ApiStack(app, "ApiStack", database=db, auth=auth, env=env)
FrontendStack(app, "FrontendStack", api=api, env=env)

app.synth()
