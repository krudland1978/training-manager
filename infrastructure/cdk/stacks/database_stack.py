import aws_cdk as cdk
from aws_cdk import aws_dynamodb as dynamodb
from constructs import Construct


class DatabaseStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.team_members_table = dynamodb.Table(
            self, "TeamMembers",
            table_name="TeamMembers",
            partition_key=dynamodb.Attribute(name="person_id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
        self.team_members_table.add_global_secondary_index(
            index_name="ByRole",
            partition_key=dynamodb.Attribute(name="role_id", type=dynamodb.AttributeType.STRING),
        )

        self.certifications_table = dynamodb.Table(
            self, "Certifications",
            table_name="Certifications",
            partition_key=dynamodb.Attribute(name="cert_id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        self.requirement_rules_table = dynamodb.Table(
            self, "RequirementRules",
            table_name="RequirementRules",
            partition_key=dynamodb.Attribute(name="rule_id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
        self.requirement_rules_table.add_global_secondary_index(
            index_name="ByRole",
            partition_key=dynamodb.Attribute(name="role_id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="grade_min", type=dynamodb.AttributeType.NUMBER),
        )

        self.training_plans_table = dynamodb.Table(
            self, "TrainingPlans",
            table_name="TrainingPlans",
            partition_key=dynamodb.Attribute(name="person_id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        self.metadata_table = dynamodb.Table(
            self, "Metadata",
            table_name="Metadata",
            partition_key=dynamodb.Attribute(name="key", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
