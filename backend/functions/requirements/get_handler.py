import os

from aws_lambda_powertools import Logger
from lib.utils.dynamodb import scan_all
from lib.utils.response import success

logger = Logger()

REQUIREMENT_RULES_TABLE = os.environ.get("REQUIREMENT_RULES_TABLE", "RequirementRules")


@logger.inject_lambda_context
def handler(event, context):
    items = scan_all(REQUIREMENT_RULES_TABLE)
    rules = sorted(items, key=lambda r: (r.get("role_id", ""), r.get("grade_min", 0)))
    return success({"rules": rules, "total": len(rules)})
