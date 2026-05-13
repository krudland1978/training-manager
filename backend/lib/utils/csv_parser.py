import csv
import io
from dataclasses import dataclass


@dataclass
class ParseResult:
    rows: list[dict]
    errors: list[dict]


def parse_csv(content: bytes, required_columns: list[str]) -> ParseResult:
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    headers = reader.fieldnames or []

    missing = [c for c in required_columns if c not in headers]
    if missing:
        raise ValueError(f"CSV missing required columns: {', '.join(missing)}")

    rows, errors = [], []
    for i, row in enumerate(reader, start=2):
        missing_values = [c for c in required_columns if not row.get(c, "").strip()]
        if missing_values:
            errors.append({"row": i, "reason": f"Missing required field(s): {', '.join(missing_values)}", "data": dict(row)})
        else:
            rows.append({k: v.strip() for k, v in row.items() if v is not None})
    return ParseResult(rows=rows, errors=errors)


def parse_pipe_list(value: str) -> list[str]:
    if not value or not value.strip():
        return []
    return [v.strip() for v in value.split("|") if v.strip()]
