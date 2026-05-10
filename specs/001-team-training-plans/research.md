# Research: Team Training Plan Manager

**Branch**: `001-team-training-plans` | **Date**: 2026-05-10

## Decision Log

### 1. Authentication

**Decision**: AWS Cognito User Pools with API Gateway authoriser.

**Rationale**: Cognito is a fully managed AWS service, aligns with the cloud-native
constraint, and integrates natively with API Gateway via a Cognito authoriser — no custom
auth Lambda needed. The manager-only access model maps cleanly to a single Cognito User
Pool with one user group.

**Alternatives considered**:
- Custom JWT auth Lambda — more code to maintain, no benefit over Cognito for this use case.
- AWS IAM auth — appropriate for service-to-service, not manager browser logins.

---

### 2. Primary Data Store

**Decision**: DynamoDB (on-demand capacity) as the sole domain data store.

**Rationale**: Data volumes are small (≤200 members, ~50 certs, ~40 requirement rules).
All access patterns are key-based lookups or full-table scans within a bounded set —
no complex ad-hoc queries. DynamoDB on-demand eliminates capacity planning and is
cost-effective at this scale. Plan generation joins happen in Python in Lambda, not at
the database layer.

**Alternatives considered**:
- RDS Aurora Serverless v2 — better for complex joins, but adds VPC complexity, cold-start
  latency, and operational overhead for data volumes this small.
- S3 + Athena — appropriate for analytics, not transactional reads/writes.

---

### 3. CSV Import Mechanism

**Decision**: HTTP multipart upload via API Gateway → Lambda → parse in-memory → write
to DynamoDB.

**Rationale**: Files are small (≤200 rows). Parsing in Lambda avoids S3 event trigger
complexity. API Gateway supports up to 10MB payloads, well within the expected file size.
Response includes a structured import summary (accepted, rejected, reasons).

**Alternatives considered**:
- S3 presigned URL upload → S3 event → Lambda — better for large files, unnecessary
  complexity here given file size constraints.

---

### 4. Training Plan Generation Algorithm

**Decision**: Synchronous Lambda invocation returning a JSON response.

**Rationale**: Generating plans for 200 members requires: load all members, load all
certs, load requirements matrix, compute gap per member. At this scale this completes
well within Lambda's 29s API Gateway timeout. No async queue needed.

**Algorithm**:
1. Load all team members from DynamoDB.
2. Load all certifications (indexed by cert_id).
3. Load requirements matrix (all role/grade rules).
4. For each active team member:
   a. Find matching requirement rule (role_id + grade_level within grade band).
   b. Determine required cert_ids for that rule.
   c. Subtract certs already held by the member.
   d. For each outstanding cert, look up study days
      (`typical_study_days × difficulty_multiplier`).
   e. Sum study days for all outstanding certs; compare to `days_remaining`.
   f. Set `days_warning = True` if total study days > days_remaining.
   g. Order outstanding certs by certification level
      (foundational → associate → professional → specialty).
5. Write generated plans to DynamoDB.
6. Return summary to caller.

**Certification level ordering** (ascending):
`foundational (1) → associate (2) → professional (3) → specialty (4)`

---

### 5. Export Format

**Decision**: CSV export generated in Lambda, returned as a downloadable file via API
Gateway with `Content-Disposition: attachment`.

**Rationale**: CSV meets the "no specialist software" requirement and is the stated
default. Lambda generates the CSV in-memory and streams it back; for ≤200 rows this is
well within Lambda payload limits.

**PDF stretch goal**: Not in scope for this version. Deferred to a future iteration.

---

### 6. Infrastructure as Code

**Decision**: AWS CDK (Python).

**Rationale**: CDK uses the same language as the backend (Python), reducing context
switching. CDK constructs for Lambda, API Gateway, DynamoDB, Cognito, S3, and CloudFront
are mature and well-documented.

**Alternatives considered**:
- Terraform — language mismatch with Python backend; no strong benefit at this scale.
- SAM — simpler for pure Lambda projects but less capable for the full stack (CloudFront,
  Cognito) compared to CDK.

---

### 7. Grade Band Matching

**Decision**: When a team member's grade falls within a rule's `[grade_min, grade_max]`
inclusive range, that rule applies. If no exact band match exists, apply the rule with
the highest `grade_max` that is still ≤ the member's grade. Flag the member if no rule
covers their grade.

**Rationale**: Consistent, deterministic behaviour for edge cases. Aligns with the spec
edge case: "apply the nearest lower requirement and flag the gap".

---

### 8. Retired Certifications

**Decision**: Retired certifications (`retired: true`) are excluded from new training
plans. If a team member already holds a retired cert, it is still counted as held and
subtracted from their gap. The `superseded_by_cert_id` field is used to suggest the
replacement cert in the plan where applicable.

**Rationale**: Matches spec assumption: "Certifications already held remain valid even
if the awarding course is later removed from the catalogue."
