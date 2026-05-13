"""Integration tests for plan generation Lambda using moto with 6-person sample team."""
import json

import boto3
import pytest
from moto import mock_aws

MEMBERS_TABLE = "TeamMembers"
CERTS_TABLE = "Certifications"
RULES_TABLE = "RequirementRules"
PLANS_TABLE = "TrainingPlans"
METADATA_TABLE = "Metadata"


@pytest.fixture(autouse=True)
def aws_env(monkeypatch):
    for k, v in {
        "TEAM_MEMBERS_TABLE": MEMBERS_TABLE,
        "CERTIFICATIONS_TABLE": CERTS_TABLE,
        "REQUIREMENT_RULES_TABLE": RULES_TABLE,
        "TRAINING_PLANS_TABLE": PLANS_TABLE,
        "METADATA_TABLE": METADATA_TABLE,
        "AWS_DEFAULT_REGION": "eu-west-1",
        "AWS_ACCESS_KEY_ID": "test",
        "AWS_SECRET_ACCESS_KEY": "test",
    }.items():
        monkeypatch.setenv(k, v)


def create_tables():
    ddb = boto3.resource("dynamodb", region_name="eu-west-1")
    configs = [
        (MEMBERS_TABLE, "person_id"),
        (CERTS_TABLE, "cert_id"),
        (RULES_TABLE, "rule_id"),
        (PLANS_TABLE, "person_id"),
        (METADATA_TABLE, "key"),
    ]
    for name, pk in configs:
        ddb.create_table(
            TableName=name,
            KeySchema=[{"AttributeName": pk, "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": pk, "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )


def seed_data():
    ddb = boto3.resource("dynamodb", region_name="eu-west-1")

    certs = [
        {"cert_id": "aws-cp",  "name": "Cloud Practitioner",  "level": "foundational", "level_order": 1, "typical_study_days": "3",  "difficulty_multiplier": "1.0", "retired": False},
        {"cert_id": "aws-saa", "name": "SAA",                  "level": "associate",    "level_order": 2, "typical_study_days": "8",  "difficulty_multiplier": "1.5", "retired": False},
        {"cert_id": "aws-sap", "name": "SAP",                  "level": "professional", "level_order": 3, "typical_study_days": "14", "difficulty_multiplier": "2.5", "retired": False},
        {"cert_id": "aws-dop", "name": "DevOps Professional",  "level": "professional", "level_order": 3, "typical_study_days": "14", "difficulty_multiplier": "2.5", "retired": False},
        {"cert_id": "aws-scs", "name": "Security Specialty",   "level": "specialty",    "level_order": 4, "typical_study_days": "12", "difficulty_multiplier": "2.0", "retired": False},
    ]
    for c in certs:
        ddb.Table(CERTS_TABLE).put_item(Item=c)

    rules = [
        {"rule_id": "solution_architect#7#8",   "role_id": "solution_architect", "grade_min": 7, "grade_max": 8, "required_cert_ids": ["aws-sap"]},
        {"rule_id": "devops_engineer#4#6",       "role_id": "devops_engineer",    "grade_min": 4, "grade_max": 6, "required_cert_ids": ["aws-dop"]},
        {"rule_id": "security_engineer#4#12",    "role_id": "security_engineer",  "grade_min": 4, "grade_max": 12, "required_cert_ids": ["aws-scs"]},
    ]
    for r in rules:
        ddb.Table(RULES_TABLE).put_item(Item=r)

    members = [
        {"person_id": "P001", "name": "Alice Smith",  "role_id": "solution_architect", "grade_level": 7, "active": True,  "certifications_held": ["aws-cp", "aws-saa"], "days_remaining": 10},
        {"person_id": "P002", "name": "Bob Jones",    "role_id": "solution_architect", "grade_level": 5, "active": True,  "certifications_held": [],                    "days_remaining": 15},
        {"person_id": "P003", "name": "Carol White",  "role_id": "devops_engineer",    "grade_level": 4, "active": True,  "certifications_held": [],                    "days_remaining": 20},
        {"person_id": "P004", "name": "Dave Brown",   "role_id": "devops_engineer",    "grade_level": 4, "active": True,  "certifications_held": ["aws-dop"],            "days_remaining": 5},
        {"person_id": "P005", "name": "Eve Davis",    "role_id": "security_engineer",  "grade_level": 6, "active": True,  "certifications_held": [],                    "days_remaining": 30},
        {"person_id": "P006", "name": "Frank Miller", "role_id": "solution_architect", "grade_level": 7, "active": True,  "certifications_held": [],                    "days_remaining": 4},
    ]
    for m in members:
        ddb.Table(MEMBERS_TABLE).put_item(Item=m)


def _reload_handler():
    from functions.plans import generate_handler
    import importlib
    importlib.reload(generate_handler)
    return generate_handler


@mock_aws
def test_six_plans_generated():
    create_tables()
    seed_data()
    handler = _reload_handler()
    response = handler.handler({}, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["generated"] == 6


@mock_aws
def test_alice_has_one_outstanding_cert():
    create_tables()
    seed_data()
    handler = _reload_handler()
    handler.handler({}, None)

    ddb = boto3.resource("dynamodb", region_name="eu-west-1")
    plan = ddb.Table(PLANS_TABLE).get_item(Key={"person_id": "P001"})["Item"]
    outstanding = plan["outstanding_certs"]
    assert len(outstanding) == 1
    assert outstanding[0]["cert_id"] == "aws-sap"


@mock_aws
def test_dave_requirement_met():
    create_tables()
    seed_data()
    handler = _reload_handler()
    handler.handler({}, None)

    ddb = boto3.resource("dynamodb", region_name="eu-west-1")
    plan = ddb.Table(PLANS_TABLE).get_item(Key={"person_id": "P004"})["Item"]
    assert plan["requirement_met"] is True


@mock_aws
def test_frank_has_days_warning():
    create_tables()
    seed_data()
    handler = _reload_handler()
    handler.handler({}, None)

    ddb = boto3.resource("dynamodb", region_name="eu-west-1")
    plan = ddb.Table(PLANS_TABLE).get_item(Key={"person_id": "P006"})["Item"]
    # aws-sap: 14 * 2.5 = 35 days; only 4 remaining → warning
    assert plan["days_warning"] is True


@mock_aws
def test_no_certs_returns_409():
    create_tables()
    handler = _reload_handler()
    response = handler.handler({}, None)
    assert response["statusCode"] == 409


@mock_aws
def test_plans_marked_fresh_after_generation():
    create_tables()
    seed_data()

    # First mark stale
    ddb = boto3.resource("dynamodb", region_name="eu-west-1")
    ddb.Table(METADATA_TABLE).put_item(Item={"key": "META#plans", "plans_stale": True})

    handler = _reload_handler()
    handler.handler({}, None)

    item = ddb.Table(METADATA_TABLE).get_item(Key={"key": "META#plans"}).get("Item")
    assert item["plans_stale"] is False
