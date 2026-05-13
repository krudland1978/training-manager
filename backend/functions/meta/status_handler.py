from aws_lambda_powertools import Logger
from lib.utils.metadata import get_plans_stale
from lib.utils.response import success

logger = Logger()


@logger.inject_lambda_context
def handler(event, context):
    return success({"plans_stale": get_plans_stale()})
