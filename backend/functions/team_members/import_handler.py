import base64
import cgi
import io
import json
import os
from datetime import datetime, timezone

from aws_lambda_powertools import Logger
from lib.models.team_member import TeamMember
from lib.utils.csv_parser import parse_csv, parse_pipe_list
from lib.utils.dynamodb import put_item
from lib.utils.metadata import mark_plans_stale
from lib.utils.response import error, success

logger = Logger()

TABLE = os.environ.get("TEAM_MEMBERS_TABLE", "TeamMembers")
REQUIRED_COLS = ["person_id", "name", "email", "grade_level", "role_id",
                 "start_date", "grade_start_date", "manager_email",
                 "location", "active", "days_allocated_override", "days_remaining"]


def _parse_multipart(event: dict) -> bytes:
    body = event.get("body", "")
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body)
    elif isinstance(body, str):
        body = body.encode()
    content_type = event.get("headers", {}).get("content-type", "")
    environ = {"REQUEST_METHOD": "POST", "CONTENT_TYPE": content_type,
                "CONTENT_LENGTH": str(len(body))}
    fs = cgi.FieldStorage(fp=io.BytesIO(body), environ=environ)
    file_item = fs["file"]
    return file_item.file.read()


@logger.inject_lambda_context
def handler(event, context):
    try:
        content = _parse_multipart(event)
    except Exception as e:
        return error("Invalid multipart request", str(e))

    try:
        result = parse_csv(content, REQUIRED_COLS)
    except ValueError as e:
        return error("Invalid CSV format", str(e))

    imported, errors = 0, list(result.errors)
    now = datetime.now(timezone.utc).isoformat()

    for row in result.rows:
        try:
            member = TeamMember(
                person_id=row["person_id"],
                name=row["name"],
                email=row["email"],
                grade_level=int(row["grade_level"]),
                role_id=row["role_id"],
                start_date=row["start_date"],
                grade_start_date=row["grade_start_date"],
                manager_email=row["manager_email"],
                location=row["location"],
                active=row["active"].upper() == "TRUE",
                days_allocated_override=int(row["days_allocated_override"]),
                days_remaining=int(row["days_remaining"]),
                certifications_held=parse_pipe_list(row.get("certifications_held", "")),
                updated_at=now,
            )
            put_item(TABLE, member.to_dynamo())
            imported += 1
        except Exception as e:
            errors.append({"person_id": row.get("person_id", "?"), "reason": str(e)})

    if imported > 0:
        mark_plans_stale()

    logger.info("Team members imported", extra={"imported": imported, "errors": len(errors)})
    return success({"imported": imported, "skipped": len(errors), "errors": errors})
