from __future__ import annotations

import os
import boto3
from boto3.dynamodb.conditions import Key

_dynamodb = None


def _get_resource():
    global _dynamodb
    if _dynamodb is None:
        _dynamodb = boto3.resource("dynamodb", region_name=os.environ.get("AWS_REGION", "eu-west-1"))
    return _dynamodb


def get_table(name: str):
    return _get_resource().Table(name)


def get_item(table_name: str, key: dict) -> dict | None:
    table = get_table(table_name)
    response = table.get_item(Key=key)
    return response.get("Item")


def put_item(table_name: str, item: dict) -> None:
    get_table(table_name).put_item(Item=item)


def delete_item(table_name: str, key: dict) -> None:
    get_table(table_name).delete_item(Key=key)


def scan_all(table_name: str, filter_expression=None) -> list[dict]:
    table = get_table(table_name)
    kwargs = {}
    if filter_expression is not None:
        kwargs["FilterExpression"] = filter_expression
    items = []
    while True:
        response = table.scan(**kwargs)
        items.extend(response.get("Items", []))
        if "LastEvaluatedKey" not in response:
            break
        kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
    return items


def query_gsi(table_name: str, index_name: str, key_name: str, key_value: str) -> list[dict]:
    table = get_table(table_name)
    response = table.query(
        IndexName=index_name,
        KeyConditionExpression=Key(key_name).eq(key_value),
    )
    return response.get("Items", [])


def batch_write(table_name: str, items: list[dict]) -> None:
    table = get_table(table_name)
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)
