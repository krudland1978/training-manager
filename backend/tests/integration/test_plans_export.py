"""Integration tests for plan export Lambda using moto."""
import csv
import io

import boto3
import pytest
from moto import mock_aws

PLANS_TABLE = "TrainingPlans"


@pytest.fixture(autouse=True)
def aws_env(monkeypatch):
    monkeypatch.setenv("TRAINING_PLANS_TABLE", PLANS_TABLE)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test")


def create_table():
    ddb = boto3.resource("dynamodb", region_name="eu-west-1")
    ddb.create_table(
        TableName=PLANS_TABLE,
        KeySchema=[{"AttributeName": "person_id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "person_id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )


SAMPLE_PLANS = [
    {
        "person_id": "P001", "name": "Alice Smith",  "role_id": "solution_architect", "grade_level": 7,
        "required_cert_ids": ["aws-sap"], "certs_held": ["aws-saa"],
        "outstanding_certs": [{"cert_id": "aws-sap", "name": "SAP", "level": "professional", "level_order": 3, "effective_study_days": 35}],
        "total_study_days_required": 35, "days_remaining": 10,
        "days_warning": True, "requirement_met": False, "no_requirement": False,
        "generated_at": "2026-05-10T10:00:00Z",
    },
    {
        "person_id": "P002", "name": "Bob Jones",    "role_id": "cloud_engineer",    "grade_level": 5,
        "required_cert_ids": ["aws-saa"], "certs_held": ["aws-saa"],
        "outstanding_certs": [],
        "total_study_days_required": 0, "days_remaining": 15,
        "days_warning": False, "requirement_met": True, "no_requirement": False,
        "generated_at": "2026-05-10T10:00:00Z",
    },
]


def _reload_handler():
    from functions.plans import export_handler
    import importlib
    importlib.reload(export_handler)
    return export_handler


@mock_aws
def test_export_returns_csv_content_type():
    create_table()
    ddb = boto3.resource("dynamodb", region_name="eu-west-1")
    for p in SAMPLE_PLANS:
        ddb.Table(PLANS_TABLE).put_item(Item=p)

    handler = _reload_handler()
    response = handler.handler({}, None)

    assert response["statusCode"] == 200
    assert "text/csv" in response["headers"]["Content-Type"]


@mock_aws
def test_export_has_content_disposition():
    create_table()
    ddb = boto3.resource("dynamodb", region_name="eu-west-1")
    for p in SAMPLE_PLANS:
        ddb.Table(PLANS_TABLE).put_item(Item=p)

    handler = _reload_handler()
    response = handler.handler({}, None)

    assert "attachment" in response["headers"]["Content-Disposition"]
    assert "training-plans" in response["headers"]["Content-Disposition"]


@mock_aws
def test_export_csv_contains_all_members():
    create_table()
    ddb = boto3.resource("dynamodb", region_name="eu-west-1")
    for p in SAMPLE_PLANS:
        ddb.Table(PLANS_TABLE).put_item(Item=p)

    handler = _reload_handler()
    response = handler.handler({}, None)
    reader = csv.DictReader(io.StringIO(response["body"]))
    rows = list(reader)

    assert len(rows) == 2
    names = {r["name"] for r in rows}
    assert "Alice Smith" in names
    assert "Bob Jones" in names


@mock_aws
def test_export_csv_correct_columns():
    create_table()
    ddb = boto3.resource("dynamodb", region_name="eu-west-1")
    for p in SAMPLE_PLANS:
        ddb.Table(PLANS_TABLE).put_item(Item=p)

    handler = _reload_handler()
    response = handler.handler({}, None)
    reader = csv.DictReader(io.StringIO(response["body"]))
    expected = {"person_id", "name", "role_id", "grade_level", "required_certs",
                "certs_held", "outstanding_certs", "total_study_days_required",
                "days_remaining", "days_warning", "requirement_met", "no_requirement", "generated_at"}
    assert set(reader.fieldnames) == expected
