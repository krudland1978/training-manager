import os

from aws_lambda_powertools import Logger
from boto3.dynamodb.conditions import Attr
from lib.utils.dynamodb import scan_all
from lib.utils.response import success

logger = Logger()

TRAINING_PLANS_TABLE = os.environ.get("TRAINING_PLANS_TABLE", "TrainingPlans")


@logger.inject_lambda_context
def handler(event, context):
    params = (event.get("queryStringParameters") or {})
    role_id = params.get("role_id")
    days_warning_param = params.get("days_warning")

    filter_expr = None
    if role_id:
        filter_expr = Attr("role_id").eq(role_id)
    if days_warning_param is not None:
        want_warning = days_warning_param.lower() == "true"
        dw_filter = Attr("days_warning").eq(want_warning)
        filter_expr = dw_filter if filter_expr is None else filter_expr & dw_filter

    items = scan_all(TRAINING_PLANS_TABLE, filter_expression=filter_expr)

    plans = []
    for item in items:
        plans.append({
            "person_id": item.get("person_id"),
            "name": item.get("name", ""),
            "role_id": item.get("role_id"),
            "grade_level": item.get("grade_level"),
            "requirement_met": item.get("requirement_met", False),
            "no_requirement": item.get("no_requirement", False),
            "outstanding_count": len(item.get("outstanding_certs", [])),
            "total_study_days_required": item.get("total_study_days_required", 0),
            "days_remaining": item.get("days_remaining"),
            "days_warning": item.get("days_warning", False),
            "generated_at": item.get("generated_at"),
        })

    plans.sort(key=lambda p: p.get("name", ""))
    return success({"plans": plans, "total": len(plans)})
