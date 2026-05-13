# API Contract: Team Training Plan Manager

**Branch**: `001-team-training-plans` | **Date**: 2026-05-10

## Overview

All endpoints are served via AWS API Gateway (REST API). Every endpoint requires a valid
Cognito JWT in the `Authorization: Bearer <token>` header. Unauthenticated requests
receive `401 Unauthorized`.

**Base URL**: `https://{api-id}.execute-api.{region}.amazonaws.com/prod`

**Content-Type**: `application/json` (except CSV import: `multipart/form-data`)

---

## Team Members

### `POST /team-members/import`

Import team members from a CSV file.

**Request**: `multipart/form-data`
- `file` (required): CSV file with headers matching the team member schema

**Response `200 OK`**:
```json
{
  "imported": 5,
  "skipped": 1,
  "errors": [
    {
      "row": 3,
      "person_id": "P004",
      "reason": "Missing required field: role_id"
    }
  ]
}
```

**Response `400 Bad Request`** (malformed CSV or missing `file` field):
```json
{ "error": "Invalid CSV format", "detail": "Header row missing required column: grade_level" }
```

---

### `GET /team-members`

List all team members.

**Query parameters**:
- `active` (optional, boolean): filter by active status (default: all)
- `role_id` (optional, string): filter by role

**Response `200 OK`**:
```json
{
  "members": [
    {
      "person_id": "P001",
      "name": "Alice Smith",
      "email": "alice.smith@company.com",
      "grade_level": 7,
      "role_id": "solution_architect",
      "location": "London",
      "active": true,
      "days_allocated_override": 10,
      "days_remaining": 10,
      "certifications_held": ["aws-cp", "aws-saa"]
    }
  ],
  "total": 6
}
```

---

## Certifications

### `POST /certifications/import`

Import the certification catalogue from a CSV file.

**Request**: `multipart/form-data`
- `file` (required): CSV file with headers matching the certification schema

**Response `200 OK`**:
```json
{
  "imported": 14,
  "skipped": 1,
  "warnings": [
    {
      "cert_id": "aws-das",
      "reason": "Certification is retired; will not appear in new plans"
    }
  ]
}
```

---

### `GET /certifications`

List all certifications.

**Query parameters**:
- `retired` (optional, boolean): include retired certs (default: `false`)
- `domain` (optional, string): filter by domain

**Response `200 OK`**:
```json
{
  "certifications": [
    {
      "cert_id": "aws-saa",
      "exam_code": "SAA-C03",
      "name": "AWS Certified Solutions Architect - Associate",
      "provider": "aws",
      "level": "associate",
      "level_order": 2,
      "domain": "Architecture",
      "typical_study_days": 8,
      "difficulty_multiplier": 1.5,
      "effective_study_days": 12,
      "validity_years": 3,
      "retired": false,
      "superseded_by_cert_id": null
    }
  ],
  "total": 12
}
```

---

## Requirements Matrix

### `POST /requirements`

Save (replace) the full requirements matrix.

**Request body**:
```json
{
  "rules": [
    {
      "role_id": "solution_architect",
      "grade_min": 7,
      "grade_max": 8,
      "required_cert_ids": ["aws-sap"],
      "notes": "Solutions architect professional"
    }
  ]
}
```

**Response `200 OK`**:
```json
{ "saved": 24, "warnings": [] }
```

**Response `400 Bad Request`** (validation failure):
```json
{
  "error": "Validation failed",
  "details": [
    { "rule_id": "solution_architect#7#8", "reason": "cert_id aws-xyz does not exist" }
  ]
}
```

---

### `GET /requirements`

Retrieve the current requirements matrix.

**Response `200 OK`**:
```json
{
  "rules": [
    {
      "rule_id": "solution_architect#7#8",
      "role_id": "solution_architect",
      "grade_min": 7,
      "grade_max": 8,
      "required_cert_ids": ["aws-sap"],
      "notes": "Solutions architect professional"
    }
  ],
  "total": 24
}
```

---

## Training Plans

### `POST /plans/generate`

Generate (or regenerate) training plans for all active team members.

**Request body**: empty `{}`

**Response `200 OK`**:
```json
{
  "generated": 6,
  "no_requirement": 0,
  "requirement_met": 1,
  "days_warnings": 2,
  "errors": []
}
```

**Response `409 Conflict`** (prerequisites missing):
```json
{ "error": "Cannot generate plans: no certifications loaded" }
```

---

### `GET /plans`

List all training plans.

**Query parameters**:
- `role_id` (optional, string): filter by role
- `days_warning` (optional, boolean): filter to members with a days warning

**Response `200 OK`**:
```json
{
  "plans": [
    {
      "person_id": "P001",
      "name": "Alice Smith",
      "role_id": "solution_architect",
      "grade_level": 7,
      "requirement_met": false,
      "no_requirement": false,
      "outstanding_count": 1,
      "total_study_days_required": 39,
      "days_remaining": 10,
      "days_warning": true,
      "generated_at": "2026-05-10T10:00:00Z"
    }
  ],
  "total": 6
}
```

---

### `GET /plans/{person_id}`

Get the full training plan for a specific team member.

**Response `200 OK`**:
```json
{
  "person_id": "P001",
  "name": "Alice Smith",
  "role_id": "solution_architect",
  "grade_level": 7,
  "required_cert_ids": ["aws-sap"],
  "certs_held": ["aws-cp", "aws-saa"],
  "outstanding_certs": [
    {
      "cert_id": "aws-sap",
      "name": "AWS Certified Solutions Architect - Professional",
      "level": "professional",
      "level_order": 3,
      "effective_study_days": 39,
      "superseded_by": null
    }
  ],
  "total_study_days_required": 39,
  "days_remaining": 10,
  "days_warning": true,
  "requirement_met": false,
  "no_requirement": false,
  "generated_at": "2026-05-10T10:00:00Z"
}
```

**Response `404 Not Found`**:
```json
{ "error": "No plan found for person_id P999" }
```

---

### `GET /plans/export`

Export all training plans as a CSV file.

**Response `200 OK`**:
- `Content-Type: text/csv`
- `Content-Disposition: attachment; filename="training-plans-2026-05-10.csv"`

**CSV columns**:
```
person_id, name, email, role_id, grade_level, required_certs, certs_held,
outstanding_certs, total_study_days_required, days_remaining, days_warning,
requirement_met, no_requirement, generated_at
```

---

## Error Response Format

All error responses follow this structure:

```json
{
  "error": "Human-readable error summary",
  "detail": "Optional additional context"
}
```

| HTTP Status | Meaning |
|-------------|---------|
| 400 | Bad request — validation or parse failure |
| 401 | Unauthorized — missing or invalid Cognito token |
| 404 | Resource not found |
| 409 | Conflict — prerequisites not met |
| 500 | Internal server error |
