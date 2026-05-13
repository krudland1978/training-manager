import base64
import cgi
import io
import os
from datetime import datetime, timezone

from aws_lambda_powertools import Logger
from lib.models.certification import Certification, CertLevel
from lib.utils.csv_parser import parse_csv
from lib.utils.dynamodb import put_item
from lib.utils.metadata import mark_plans_stale
from lib.utils.response import error, success

logger = Logger()
TABLE = os.environ.get("CERTIFICATIONS_TABLE", "Certifications")
REQUIRED_COLS = ["cert_id", "exam_code", "name", "provider", "level",
                 "domain", "typical_study_days", "difficulty_multiplier",
                 "validity_years", "retired"]


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
    return fs["file"].file.read()


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

    imported, errors, warnings = 0, list(result.errors), []
    now = datetime.now(timezone.utc).isoformat()

    for row in result.rows:
        try:
            level = row["level"].lower()
            level_order = int(CertLevel.from_str(level))
            retired = row["retired"].lower() == "true"
            superseded = row.get("superseded_by_cert_id", "").strip() or None

            cert = Certification(
                cert_id=row["cert_id"],
                exam_code=row["exam_code"],
                name=row["name"],
                provider=row["provider"],
                level=level,
                level_order=level_order,
                domain=row["domain"],
                typical_study_days=int(row["typical_study_days"]),
                difficulty_multiplier=float(row["difficulty_multiplier"]),
                validity_years=int(row["validity_years"]),
                retired=retired,
                superseded_by_cert_id=superseded,
                updated_at=now,
            )
            put_item(TABLE, cert.to_dynamo())
            imported += 1
            if retired:
                warnings.append({"cert_id": row["cert_id"],
                                  "reason": "Certification is retired; will not appear in new plans"})
        except Exception as e:
            errors.append({"cert_id": row.get("cert_id", "?"), "reason": str(e)})

    if imported > 0:
        mark_plans_stale()

    logger.info("Certifications imported", extra={"imported": imported})
    return success({"imported": imported, "skipped": len(errors), "warnings": warnings, "errors": errors})
