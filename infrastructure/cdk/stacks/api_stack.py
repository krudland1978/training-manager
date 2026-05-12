import aws_cdk as cdk
from aws_cdk import (
    aws_apigateway as apigw,
    aws_lambda as lambda_,
    aws_cognito as cognito,
    aws_iam as iam,
)
from constructs import Construct
import os

BACKEND_DIR = os.path.join(os.path.dirname(__file__), "../../../../backend")
LAMBDA_ENV_BASE = {
    "POWERTOOLS_SERVICE_NAME": "training-manager",
    "LOG_LEVEL": "INFO",
}


def _lambda(scope, id_, handler_path: str, env: dict, tables) -> lambda_.Function:
    fn = lambda_.Function(
        scope, id_,
        runtime=lambda_.Runtime.PYTHON_3_12,
        handler=handler_path,
        code=lambda_.Code.from_asset(BACKEND_DIR),
        environment={**LAMBDA_ENV_BASE, **env},
        timeout=cdk.Duration.seconds(30),
    )
    for table in tables:
        table.grant_read_write_data(fn)
    return fn


class ApiStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, database, auth, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        db = database
        env = {
            "TEAM_MEMBERS_TABLE": db.team_members_table.table_name,
            "CERTIFICATIONS_TABLE": db.certifications_table.table_name,
            "REQUIREMENT_RULES_TABLE": db.requirement_rules_table.table_name,
            "TRAINING_PLANS_TABLE": db.training_plans_table.table_name,
            "METADATA_TABLE": db.metadata_table.table_name,
        }
        all_tables = [db.team_members_table, db.certifications_table,
                      db.requirement_rules_table, db.training_plans_table,
                      db.metadata_table]

        api = apigw.RestApi(self, "Api", rest_api_name="training-manager-api",
                             default_cors_preflight_options=apigw.CorsOptions(
                                 allow_origins=apigw.Cors.ALL_ORIGINS,
                                 allow_methods=apigw.Cors.ALL_METHODS,
                             ))

        authorizer = apigw.CognitoUserPoolsAuthorizer(
            self, "Authorizer", cognito_user_pools=[auth.user_pool])
        auth_opts = apigw.MethodOptions(
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        def lam(id_, path, tables=None):
            return _lambda(self, id_, path, env, tables or all_tables)

        def add(resource, method, fn):
            resource.add_method(method, apigw.LambdaIntegration(fn), **auth_opts.__dict__ if False else {"authorizer": authorizer, "authorization_type": apigw.AuthorizationType.COGNITO})

        # Team members
        tm = api.root.add_resource("team-members")
        tm_import = tm.add_resource("import")
        tm_import.add_method("POST", apigw.LambdaIntegration(
            lam("TmImport", "functions.team_members.import_handler.handler")),
            authorizer=authorizer, authorization_type=apigw.AuthorizationType.COGNITO)
        tm.add_method("GET", apigw.LambdaIntegration(
            lam("TmList", "functions.team_members.list_handler.handler")),
            authorizer=authorizer, authorization_type=apigw.AuthorizationType.COGNITO)

        # Certifications
        certs = api.root.add_resource("certifications")
        certs_import = certs.add_resource("import")
        certs_import.add_method("POST", apigw.LambdaIntegration(
            lam("CertImport", "functions.certifications.import_handler.handler")),
            authorizer=authorizer, authorization_type=apigw.AuthorizationType.COGNITO)
        certs.add_method("GET", apigw.LambdaIntegration(
            lam("CertList", "functions.certifications.list_handler.handler")),
            authorizer=authorizer, authorization_type=apigw.AuthorizationType.COGNITO)

        # Requirements
        reqs = api.root.add_resource("requirements")
        reqs.add_method("POST", apigw.LambdaIntegration(
            lam("ReqSave", "functions.requirements.save_handler.handler")),
            authorizer=authorizer, authorization_type=apigw.AuthorizationType.COGNITO)
        reqs.add_method("GET", apigw.LambdaIntegration(
            lam("ReqGet", "functions.requirements.get_handler.handler")),
            authorizer=authorizer, authorization_type=apigw.AuthorizationType.COGNITO)

        # Plans
        plans = api.root.add_resource("plans")
        plans_gen = plans.add_resource("generate")
        plans_gen.add_method("POST", apigw.LambdaIntegration(
            lam("PlansGenerate", "functions.plans.generate_handler.handler")),
            authorizer=authorizer, authorization_type=apigw.AuthorizationType.COGNITO)
        plans_export = plans.add_resource("export")
        plans_export.add_method("GET", apigw.LambdaIntegration(
            lam("PlansExport", "functions.plans.export_handler.handler")),
            authorizer=authorizer, authorization_type=apigw.AuthorizationType.COGNITO)
        plans.add_method("GET", apigw.LambdaIntegration(
            lam("PlansList", "functions.plans.list_handler.handler")),
            authorizer=authorizer, authorization_type=apigw.AuthorizationType.COGNITO)
        plan_id = plans.add_resource("{person_id}")
        plan_id.add_method("GET", apigw.LambdaIntegration(
            lam("PlanGet", "functions.plans.get_handler.handler")),
            authorizer=authorizer, authorization_type=apigw.AuthorizationType.COGNITO)

        # Meta
        meta = api.root.add_resource("meta")
        meta_status = meta.add_resource("plans-status")
        meta_status.add_method("GET", apigw.LambdaIntegration(
            lam("MetaStatus", "functions.meta.status_handler.handler")),
            authorizer=authorizer, authorization_type=apigw.AuthorizationType.COGNITO)

        self.api_url = api.url
        cdk.CfnOutput(self, "ApiUrl", value=api.url)
