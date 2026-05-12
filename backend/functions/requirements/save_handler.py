import json
import os
from datetime import datetime, timezone

from aws_lambda_powertools import Logger
from lib.models.requirement_rule import RequirementRule
from lib.utils.dynamodb import scan_all, batch_write, delete_item
from lib.utils.metadata import mark_plans_stale
from lib.utils.response import error, success

logger = Logger()
REQUIREMENT_RULES_TABLE = os.environ.get("REQUIREMENT_RULES_TABLE", "RequirementRules")
CERTIFICATIONS_TABLE = os.environ.get("CERTIFICATIONS_TABLE", "Certifications")


@logger.inject_lambda_context
def handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return error("Invalid JSON body")

    rules_input = body.get("rules")
    if not isinstance(rules_input, list):
        return error("Request body must contain a 'rules' list")

    # Load all known certs for validation
    cert_items = scan_all(CERTIFICATIONS_TABLE)
    cert_map = {c["cert_id"]: c for c in cert_items}

    now = datetime.now(timezone.utc).isoformat()
    validation_errors = []
    warnings = []
    parsed_rules = []

    for i, rule_input in enumerate(rules_input):
        role_id = rule_input.get("role_id", "")
        grade_min = rule_input.get("grade_min")
        grade_max = rule_input.get("grade_max")
        required_cert_ids = rule_input.get("required_cert_ids", [])

        if not role_id or grade_min is None or grade_max is None:
            rule_label = f"rule[{i}]"
            validation_errors.append({"rule_id": rule_label, "reason": "role_id, grade_min, and grade_max are required"})
            continue

        rule_id = RequirementRule.make_rule_id(role_id, int(grade_min), int(grade_max))

        for cert_id in required_cert_ids:
            if cert_id not in cert_map:
                validation_errors.append({"rule_id": rule_id, "reason": f"cert_id {cert_id} does not exist"})
            elif cert_map[cert_id].get("retired"):
                warnings.append({"rule_id": rule_id, "reason": f"cert_id {cert_id} is retired and will not appear in new plans"})

        if any(e["rule_id"] == rule_id for e in validation_errors):
            continue

        try:
            rule = RequirementRule(
                rule_id=rule_id,
                role_id=role_id,
                grade_min=int(grade_min),
                grade_max=int(grade_max),
                required_cert_ids=required_cert_ids,
                notes=rule_input.get("notes"),
                updated_at=now,
            )
            parsed_rules.append(rule)
        except Exception as exc:
            validation_errors.append({"rule_id": rule_id, "reason": str(exc)})

    if validation_errors:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Validation failed", "details": validation_errors}),
        }

    # Replace full matrix: delete all existing rules then write new ones
    existing = scan_all(REQUIREMENT_RULES_TABLE)
    for item in existing:
        delete_item(REQUIREMENT_RULES_TABLE, {"rule_id": item["rule_id"]})

    if parsed_rules:
        batch_write(REQUIREMENT_RULES_TABLE, [r.to_dynamo() for r in parsed_rules])

    mark_plans_stale()

    logger.info("Requirements saved", extra={"saved": len(parsed_rules), "warnings": len(warnings)})
    return success({"saved": len(parsed_rules), "warnings": warnings})
