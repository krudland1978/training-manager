"""Integration tests for team member import Lambda using moto."""
import base64
import json
import os

import boto3
import pytest
from moto import mock_aws

TABLE_NAME = "TeamMembers"
METADATA_TABLE = "Metadata"


@pytest.fixture(autouse=True)
def aws_env(monkeypatch):
    monkeypatch.setenv("TEAM_MEMBERS_TABLE", TABLE_NAME)
    monkeypatch.setenv("METADATA_TABLE", METADATA_TABLE)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test")


def create_tables():
    ddb = boto3.resource("dynamodb", region_name="eu-west-1")
    ddb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[{"AttributeName": "person_id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "person_id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    ddb.create_table(
        TableName=METADATA_TABLE,
        KeySchema=[{"AttributeName": "key", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "key", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )


VALID_CSV = (
    "person_id,name,email,grade_level,role_id,start_date,grade_start_date,"
    "manager_email,location,active,days_allocated_override,days_remaining,certifications_held\n"
    "P001,Alice Smith,alice@co.com,7,solution_architect,2020-01-01,2022-01-01,"
    "mgr@co.com,London,true,10,10,aws-cp|aws-saa\n"
    "P002,Bob Jones,bob@co.com,5,cloud_engineer,2021-06-01,2021-06-01,"
    "mgr@co.com,Manchester,true,15,15,\n"
)


def _multipart_event(csv_content: str):
    boundary = "boundary123"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="team.csv"\r\n'
        f"Content-Type: text/csv\r\n\r\n"
        f"{csv_content}\r\n"
        f"--{boundary}--\r\n"
    )
    return {
        "headers": {"content-type": f"multipart/form-data; boundary={boundary}"},
        "body": base64.b64encode(body.encode()).decode(),
        "isBase64Encoded": True,
    }


@mock_aws
def test_valid_csv_imports_members():
    create_tables()
    from functions.team_members import import_handler
    import importlib
    importlib.reload(import_handler)

    event = _multipart_event(VALID_CSV)
    response = import_handler.handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert body["imported"] == 2
    assert body["skipped"] == 0


@mock_aws
def test_import_writes_to_dynamodb():
    create_tables()
    from functions.team_members import import_handler
    import importlib
    importlib.reload(import_handler)

    import_handler.handler(_multipart_event(VALID_CSV), None)

    ddb = boto3.resource("dynamodb", region_name="eu-west-1")
    table = ddb.Table(TABLE_NAME)
    item = table.get_item(Key={"person_id": "P001"})["Item"]
    assert item["name"] == "Alice Smith"
    assert item["grade_level"] == "7"


@mock_aws
def test_missing_required_field_counted_as_error():
    create_tables()
    from functions.team_members import import_handler
    import importlib
    importlib.reload(import_handler)

    bad_csv = (
        "person_id,name,email,grade_level,role_id,start_date,grade_start_date,"
        "manager_email,location,active,days_allocated_override,days_remaining,certifications_held\n"
        ",Alice,,7,solution_architect,2020-01-01,2020-01-01,mgr@co.com,London,true,10,10,\n"
    )
    response = import_handler.handler(_multipart_event(bad_csv), None)
    body = json.loads(response["body"])
    assert body["skipped"] == 1
    assert len(body["errors"]) == 1


@mock_aws
def test_marks_plans_stale_after_import():
    create_tables()
    from functions.team_members import import_handler
    import importlib
    importlib.reload(import_handler)

    import_handler.handler(_multipart_event(VALID_CSV), None)

    ddb = boto3.resource("dynamodb", region_name="eu-west-1")
    meta = ddb.Table(METADATA_TABLE)
    item = meta.get_item(Key={"key": "META#plans"}).get("Item")
    assert item is not None
    assert item["plans_stale"] is True
