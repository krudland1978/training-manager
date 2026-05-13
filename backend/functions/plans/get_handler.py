import os

from aws_lambda_powertools import Logger
from lib.utils.dynamodb import get_item
from lib.utils.response import error, success

logger = Logger()

TRAINING_PLANS_TABLE = os.environ.get("TRAINING_PLANS_TABLE", "TrainingPlans")


@logger.inject_lambda_context
def handler(event, context):
    person_id = (event.get("pathParameters") or {}).get("person_id")
    if not person_id:
        return error("person_id path parameter is required")

    item = get_item(TRAINING_PLANS_TABLE, {"person_id": person_id})
    if item is None:
        return error(f"No plan found for person_id {person_id}", status=404)

    return success(item)
