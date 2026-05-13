# Data Model: Team Training Plan Manager

**Branch**: `001-team-training-plans` | **Date**: 2026-05-10

## Storage: DynamoDB

All domain entities are stored in DynamoDB using on-demand capacity. Each entity type
uses a dedicated table for clarity and independent scaling.

---

## Tables

### Table: `TeamMembers`

Stores all team members uploaded by the manager.

| Attribute | Type | Description |
|-----------|------|-------------|
| `person_id` (PK) | String | Unique identifier (e.g., `P001`) |
| `name` | String | Full name |
| `email` | String | Work email address |
| `grade_level` | Number | Numeric seniority grade (higher = more senior) |
| `role_id` | String | Role identifier (e.g., `solution_architect`) |
| `start_date` | String | Employment start date (ISO 8601) |
| `grade_start_date` | String | Date current grade was assigned (ISO 8601) |
| `manager_email` | String | Manager's email address |
| `location` | String | Office location |
| `active` | Boolean | Whether the member is currently active |
| `days_allocated_override` | Number | Total training days allocated |
| `days_remaining` | Number | Training days not yet consumed |
| `certifications_held` | List\<String\> | List of `cert_id` values the member currently holds |
| `updated_at` | String | ISO 8601 timestamp of last update |

**Validation rules**:
- `person_id` MUST be unique across the table.
- `grade_level` MUST be a positive integer.
- `role_id` MUST match a known role in the requirements matrix.
- `days_remaining` MUST be ≥ 0 and ≤ `days_allocated_override`.
- `active` = `false` members are stored but excluded from plan generation.

**GSI**: `ByRole` — GSI on `role_id` (PK) for filtering plans by role.

---

### Table: `Certifications`

Stores the certification catalogue uploaded by the manager.

| Attribute | Type | Description |
|-----------|------|-------------|
| `cert_id` (PK) | String | Unique identifier (e.g., `aws-saa`) |
| `exam_code` | String | Official vendor exam code (e.g., `SAA-C03`) |
| `name` | String | Full certification name |
| `provider` | String | Certification provider (e.g., `aws`) |
| `level` | String | Tier: `foundational`, `associate`, `professional`, `specialty` |
| `level_order` | Number | Numeric sort order: foundational=1, associate=2, professional=3, specialty=4 |
| `domain` | String | Subject area (e.g., `Architecture`, `Security`, `AI/ML`) |
| `typical_study_days` | Number | Baseline study days required |
| `difficulty_multiplier` | Number | Scales study time; effective days = `typical_study_days × difficulty_multiplier` |
| `validity_years` | Number | Years before renewal is required |
| `retired` | Boolean | If `true`, excluded from new plans |
| `superseded_by_cert_id` | String \| null | Replacement cert_id if retired |
| `updated_at` | String | ISO 8601 timestamp of last update |

**Validation rules**:
- `cert_id` MUST be unique.
- `level` MUST be one of: `foundational`, `associate`, `professional`, `specialty`.
- `typical_study_days` MUST be a positive integer.
- `difficulty_multiplier` MUST be > 0.
- `retired = true` certs MUST NOT appear in generated training plans as outstanding
  requirements, but MUST be recognised if already held.

---

### Table: `RequirementRules`

Stores the role/grade certification requirements matrix defined by the manager.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rule_id` (PK) | String | Composite key: `{role_id}#{grade_min}#{grade_max}` |
| `role_id` | String | Role this rule applies to |
| `grade_min` | Number | Minimum grade (inclusive) |
| `grade_max` | Number | Maximum grade (inclusive); use `99` for open upper bound |
| `required_cert_ids` | List\<String\> | All certs that MUST be held (all required, not one-of) |
| `notes` | String \| null | Optional human-readable description |
| `updated_at` | String | ISO 8601 timestamp of last update |

**Validation rules**:
- Grade bands for the same `role_id` MUST NOT overlap.
- `required_cert_ids` MUST reference cert_ids that exist in the Certifications table.
- Retired certs MUST NOT be added to `required_cert_ids` (warn on import if attempted).

**GSI**: `ByRole` — GSI on `role_id` (PK) for efficient rule lookup during plan generation.

---

### Table: `TrainingPlans`

Stores generated training plans, one per active team member.

| Attribute | Type | Description |
|-----------|------|-------------|
| `person_id` (PK) | String | References `TeamMembers.person_id` |
| `generated_at` | String | ISO 8601 timestamp of plan generation |
| `role_id` | String | Role at time of generation |
| `grade_level` | Number | Grade at time of generation |
| `required_cert_ids` | List\<String\> | All certs required for this member's role/grade |
| `certs_held` | List\<String\> | Certs already held at time of generation |
| `outstanding_certs` | List\<Object\> | Ordered list of certs still needed (see below) |
| `total_study_days_required` | Number | Sum of effective study days for outstanding certs |
| `days_remaining` | Number | Training days remaining at time of generation |
| `days_warning` | Boolean | `true` if `total_study_days_required > days_remaining` |
| `no_requirement` | Boolean | `true` if no rule applies to this member's role/grade |
| `requirement_met` | Boolean | `true` if all required certs are already held |

**`outstanding_certs` item structure**:

```json
{
  "cert_id": "aws-sap",
  "name": "AWS Certified Solutions Architect - Professional",
  "level": "professional",
  "level_order": 3,
  "effective_study_days": 39,
  "superseded_by": null
}
```

**State transitions**:

```
[member imported] → [plan generated] → [plan regenerated on data change]
                                     ↘ [exported to CSV]
```

---

## Entity Relationships

```
TeamMember ──── (role_id, grade_level) ──→ RequirementRule
TeamMember ──── (certifications_held) ──→ Certification
RequirementRule ─── (required_cert_ids) ──→ Certification
TrainingPlan ──── (person_id) ──────────→ TeamMember
TrainingPlan ──── (outstanding_certs) ──→ Certification
```

---

## S3 Storage

| Bucket / Prefix | Contents |
|-----------------|----------|
| `training-manager-exports/plans/{timestamp}.csv` | CSV exports of training plans |
| `training-manager-frontend/` | React SPA static assets (served via CloudFront) |
