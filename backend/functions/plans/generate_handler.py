import os

from aws_lambda_powertools import Logger
from lib.services.plan_generator import generate
from lib.utils.dynamodb import scan_all, batch_write
from lib.utils.metadata import mark_plans_fresh
from lib.utils.response import error, success

logger = Logger()

TRAINING_PLANS_TABLE = os.environ.get("TRAINING_PLANS_TABLE", "TrainingPlans")
CERTIFICATIONS_TABLE = os.environ.get("CERTIFICATIONS_TABLE", "Certifications")
REQUIREMENT_RULES_TABLE = os.environ.get("REQUIREMENT_RULES_TABLE", "RequirementRules")


@logger.inject_lambda_context
def handler(event, context):
    certs = scan_all(CERTIFICATIONS_TABLE)
    if not certs:
        return error("Cannot generate plans: no certifications loaded", status=409)

    rules = scan_all(REQUIREMENT_RULES_TABLE)
    if not rules:
        return error("Cannot generate plans: no requirement rules defined", status=409)

    plans, generation_errors = generate()

    if plans:
        batch_write(TRAINING_PLANS_TABLE, [p.to_dynamo() for p in plans])

    mark_plans_fresh()

    no_requirement = sum(1 for p in plans if p.no_requirement)
    requirement_met = sum(1 for p in plans if p.requirement_met and not p.no_requirement)
    days_warnings = sum(1 for p in plans if p.days_warning)

    logger.info("Plans generated", extra={"generated": len(plans), "errors": len(generation_errors)})
    return success({
        "generated": len(plans),
        "no_requirement": no_requirement,
        "requirement_met": requirement_met,
        "days_warnings": days_warnings,
        "errors": generation_errors,
    })
