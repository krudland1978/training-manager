"""Integration tests for requirements save/get Lambdas using moto."""
import json

import boto3
import pytest
from moto import mock_aws

RULES_TABLE = "RequirementRules"
CERTS_TABLE = "Certifications"
METADATA_TABLE = "Metadata"


@pytest.fixture(autouse=True)
def aws_env(monkeypatch):
    monkeypatch.setenv("REQUIREMENT_RULES_TABLE", RULES_TABLE)
    monkeypatch.setenv("CERTIFICATIONS_TABLE", CERTS_TABLE)
    monkeypatch.setenv("METADATA_TABLE", METADATA_TABLE)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test")


def create_tables():
    ddb = boto3.resource("dynamodb", region_name="eu-west-1")
    for name, pk in [(RULES_TABLE, "rule_id"), (CERTS_TABLE, "cert_id"), (METADATA_TABLE, "key")]:
        ddb.create_table(
            TableName=name,
            KeySchema=[{"AttributeName": pk, "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": pk, "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )


def seed_cert(cert_id="aws-sap", retired=False):
    ddb = boto3.resource("dynamodb", region_name="eu-west-1")
    ddb.Table(CERTS_TABLE).put_item(Item={"cert_id": cert_id, "name": cert_id, "retired": retired})


VALID_RULES = [
    {"role_id": "solution_architect", "grade_min": 7, "grade_max": 8, "required_cert_ids": ["aws-sap"]},
    {"role_id": "solution_architect", "grade_min": 4, "grade_max": 6, "required_cert_ids": ["aws-sap"]},
]


@mock_aws
def test_save_valid_rules():
    create_tables()
    seed_cert("aws-sap")
    from functions.requirements import save_handler
    import importlib
    importlib.reload(save_handler)

    event = {"body": json.dumps({"rules": VALID_RULES})}
    response = save_handler.handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert body["saved"] == 2


@mock_aws
def test_save_unknown_cert_id_returns_400():
    create_tables()
    from functions.requirements import save_handler
    import importlib
    importlib.reload(save_handler)

    rules = [{"role_id": "solution_architect", "grade_min": 7, "grade_max": 8, "required_cert_ids": ["aws-xyz"]}]
    event = {"body": json.dumps({"rules": rules})}
    response = save_handler.handler(event, None)

    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "Validation failed" in body["error"]


@mock_aws
def test_save_retired_cert_adds_warning():
    create_tables()
    seed_cert("aws-das", retired=True)
    from functions.requirements import save_handler
    import importlib
    importlib.reload(save_handler)

    rules = [{"role_id": "solution_architect", "grade_min": 7, "grade_max": 8, "required_cert_ids": ["aws-das"]}]
    event = {"body": json.dumps({"rules": rules})}
    response = save_handler.handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert body["saved"] == 1
    assert len(body["warnings"]) == 1


@mock_aws
def test_save_replaces_existing_matrix():
    create_tables()
    seed_cert("aws-sap")
    seed_cert("aws-saa")
    from functions.requirements import save_handler
    import importlib
    importlib.reload(save_handler)

    save_handler.handler({"body": json.dumps({"rules": VALID_RULES})}, None)

    new_rules = [{"role_id": "cloud_engineer", "grade_min": 1, "grade_max": 8, "required_cert_ids": ["aws-saa"]}]
    save_handler.handler({"body": json.dumps({"rules": new_rules})}, None)

    ddb = boto3.resource("dynamodb", region_name="eu-west-1")
    items = ddb.Table(RULES_TABLE).scan()["Items"]
    assert len(items) == 1
    assert items[0]["role_id"] == "cloud_engineer"


@mock_aws
def test_get_returns_sorted_rules():
    create_tables()
    seed_cert("aws-sap")
    seed_cert("aws-saa")
    from functions.requirements import save_handler, get_handler
    import importlib
    importlib.reload(save_handler)
    importlib.reload(get_handler)

    save_handler.handler({"body": json.dumps({"rules": VALID_RULES})}, None)

    response = get_handler.handler({}, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert body["total"] == 2
    grades = [r["grade_min"] for r in body["rules"]]
    assert grades == sorted(grades)
