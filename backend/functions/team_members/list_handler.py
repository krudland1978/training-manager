import os
from aws_lambda_powertools import Logger
from lib.utils.dynamodb import scan_all, query_gsi
from lib.utils.response import success

logger = Logger()
TABLE = os.environ.get("TEAM_MEMBERS_TABLE", "TeamMembers")


@logger.inject_lambda_context
def handler(event, context):
    params = event.get("queryStringParameters") or {}
    role_id = params.get("role_id")
    active_filter = params.get("active")

    if role_id:
        items = query_gsi(TABLE, "ByRole", "role_id", role_id)
    else:
        items = scan_all(TABLE)

    if active_filter is not None:
        want_active = active_filter.lower() == "true"
        items = [i for i in items if i.get("active") == want_active]

    return success({"members": items, "total": len(items)})
