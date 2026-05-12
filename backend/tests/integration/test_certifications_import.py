"""Integration tests for certification import Lambda using moto."""
import base64
import json

import boto3
import pytest
from moto import mock_aws

TABLE_NAME = "Certifications"
METADATA_TABLE = "Metadata"


@pytest.fixture(autouse=True)
def aws_env(monkeypatch):
    monkeypatch.setenv("CERTIFICATIONS_TABLE", TABLE_NAME)
    monkeypatch.setenv("METADATA_TABLE", METADATA_TABLE)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test")


def create_tables():
    ddb = boto3.resource("dynamodb", region_name="eu-west-1")
    ddb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[{"AttributeName": "cert_id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "cert_id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    ddb.create_table(
        TableName=METADATA_TABLE,
        KeySchema=[{"AttributeName": "key", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "key", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )


VALID_CSV = (
    "cert_id,exam_code,name,provider,level,domain,typical_study_days,difficulty_multiplier,validity_years,retired,superseded_by_cert_id\n"
    "aws-cp,CLF-C02,AWS Cloud Practitioner,aws,foundational,General,3,1.0,3,false,\n"
    "aws-saa,SAA-C03,AWS SAA,aws,associate,Architecture,8,1.5,3,false,\n"
    "aws-das,DAS-C01,AWS Data Analytics (retired),aws,specialty,Data,10,2.0,3,true,\n"
)


def _multipart_event(csv_content: str):
    boundary = "boundary123"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="certs.csv"\r\n'
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
def test_valid_csv_imports_certs():
    create_tables()
    from functions.certifications import import_handler
    import importlib
    importlib.reload(import_handler)

    response = import_handler.handler(_multipart_event(VALID_CSV), None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert body["imported"] == 3


@mock_aws
def test_retired_cert_flagged_as_warning_not_error():
    create_tables()
    from functions.certifications import import_handler
    import importlib
    importlib.reload(import_handler)

    response = import_handler.handler(_multipart_event(VALID_CSV), None)
    body = json.loads(response["body"])

    assert body["skipped"] == 0
    warnings = body.get("warnings", [])
    warning_cert_ids = [w["cert_id"] for w in warnings]
    assert "aws-das" in warning_cert_ids


@mock_aws
def test_duplicate_cert_id_is_upserted():
    create_tables()
    from functions.certifications import import_handler
    import importlib
    importlib.reload(import_handler)

    import_handler.handler(_multipart_event(VALID_CSV), None)

    updated_csv = (
        "cert_id,exam_code,name,provider,level,domain,typical_study_days,difficulty_multiplier,validity_years,retired,superseded_by_cert_id\n"
        "aws-cp,CLF-C02,AWS Cloud Practitioner Updated,aws,foundational,General,4,1.0,3,false,\n"
    )
    import_handler.handler(_multipart_event(updated_csv), None)

    ddb = boto3.resource("dynamodb", region_name="eu-west-1")
    item = ddb.Table(TABLE_NAME).get_item(Key={"cert_id": "aws-cp"})["Item"]
    assert item["name"] == "AWS Cloud Practitioner Updated"
    assert item["typical_study_days"] == "4"
