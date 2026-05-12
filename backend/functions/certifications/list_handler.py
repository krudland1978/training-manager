import os
from aws_lambda_powertools import Logger
from lib.utils.dynamodb import scan_all
from lib.utils.response import success

logger = Logger()
TABLE = os.environ.get("CERTIFICATIONS_TABLE", "Certifications")


@logger.inject_lambda_context
def handler(event, context):
    params = event.get("queryStringParameters") or {}
    include_retired = params.get("retired", "false").lower() == "true"
    domain_filter = params.get("domain")

    items = scan_all(TABLE)

    if not include_retired:
        items = [i for i in items if not i.get("retired")]
    if domain_filter:
        items = [i for i in items if i.get("domain", "").lower() == domain_filter.lower()]

    return success({"certifications": items, "total": len(items)})
