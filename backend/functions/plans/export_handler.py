import csv
import io
import os
from datetime import date

from aws_lambda_powertools import Logger
from lib.utils.dynamodb import scan_all
from lib.utils.response import csv_attachment

logger = Logger()

TRAINING_PLANS_TABLE = os.environ.get("TRAINING_PLANS_TABLE", "TrainingPlans")

COLUMNS = [
    "person_id", "name", "role_id", "grade_level",
    "required_certs", "certs_held", "outstanding_certs",
    "total_study_days_required", "days_remaining", "days_warning",
    "requirement_met", "no_requirement", "generated_at",
]


@logger.inject_lambda_context
def handler(event, context):
    items = scan_all(TRAINING_PLANS_TABLE)
    items.sort(key=lambda p: p.get("name", ""))

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=COLUMNS, extrasaction="ignore")
    writer.writeheader()

    for item in items:
        outstanding = item.get("outstanding_certs", [])
        writer.writerow({
            "person_id": item.get("person_id", ""),
            "name": item.get("name", ""),
            "role_id": item.get("role_id", ""),
            "grade_level": item.get("grade_level", ""),
            "required_certs": "|".join(item.get("required_cert_ids", [])),
            "certs_held": "|".join(item.get("certs_held", [])),
            "outstanding_certs": "|".join(c.get("cert_id", "") for c in outstanding),
            "total_study_days_required": item.get("total_study_days_required", 0),
            "days_remaining": item.get("days_remaining", ""),
            "days_warning": item.get("days_warning", False),
            "requirement_met": item.get("requirement_met", False),
            "no_requirement": item.get("no_requirement", False),
            "generated_at": item.get("generated_at", ""),
        })

    filename = f"training-plans-{date.today().isoformat()}.csv"
    return csv_attachment(buf.getvalue(), filename)
