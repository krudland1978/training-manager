<!-- sync-impact-report
Version Change: 1.0.0 → 1.1.0 (MINOR — new Architectural Constraints section added)
Modified Principles: None
Added Sections:
  - Architectural Constraints (platform, backend, frontend, data storage)
Removed Sections: None
Templates Requiring Updates:
  ✅ .specify/templates/plan-template.md — Technical Context section already captures language/platform; no structural change required
  ✅ .specify/templates/spec-template.md — Spec remains technology-agnostic by design; no change required
  ✅ .specify/templates/tasks-template.md — Task path conventions already reflect backend/frontend split; no change required
Deferred TODOs: None
-->

# Training Manager Constitution

## Core Principles

### I. Code Quality

Every line of code MUST be clean, readable, and maintainable. Functions MUST have a
single responsibility. Modules MUST be cohesive and loosely coupled. Code duplication
MUST be eliminated through well-named abstractions. Public interfaces MUST be
self-documenting through clear naming — inline comments are reserved for non-obvious
invariants and hidden constraints only. No dead code, commented-out blocks, or
speculative abstractions MUST be merged.

**Rationale**: Readable code reduces onboarding time, lowers defect rates, and enables
confident refactoring as requirements evolve.

### II. Testing Standards

Tests MUST be written before or alongside implementation — never after. Unit tests MUST
cover all business logic. Integration tests MUST cover all critical user paths and
service boundaries. The test suite MUST pass in CI before any merge to main. Coverage
MUST NOT regress below 80% for core modules. Tests MUST be deterministic — flaky tests
MUST be fixed or deleted immediately, never muted. Test data MUST be isolated per test
and MUST NOT rely on shared mutable state.

**Rationale**: A reliable test suite is the primary mechanism for safe, continuous
delivery and confident change. Tests that pass by accident are worse than no tests.

### III. User Experience Consistency

All user-facing interfaces MUST follow established design patterns and the project's
component and style system. Interaction flows MUST be predictable and consistent across
the entire application — equivalent actions MUST behave equivalently in every context.
Error messages MUST be actionable, plain-language, and human-readable. Loading, empty,
and error states MUST be handled gracefully in every UI context. No feature MUST ship
without having been tested on the golden path and primary edge cases in a real browser
or device.

**Rationale**: Consistent UX reduces cognitive load, builds user trust, and lowers
support burden. Inconsistency is a form of technical debt visible to every user.

### IV. Performance Requirements

API responses MUST complete within 200ms at p95 under normal load. UI interactions MUST
render or acknowledge within 100ms to feel instantaneous. Background jobs MUST NOT
degrade user-facing response times. Database queries MUST be indexed and MUST NOT
produce full-table scans on large datasets. Performance regressions MUST be caught in CI
via benchmarks or load tests before reaching production. Every feature plan MUST declare
explicit performance goals and constraints before implementation begins.

**Rationale**: Performance is a feature. Users abandon slow applications, and regressions
compound silently if not gated at the boundary.

## Architectural Constraints

These constraints are non-negotiable. Any deviation MUST be explicitly justified in the
plan's Complexity Tracking table and approved before implementation begins.

### Platform

The application MUST be deployed on AWS. Cloud-native, managed AWS services MUST be
preferred over self-managed alternatives at every layer. Introducing a self-managed
component where an equivalent managed AWS service exists requires explicit justification.

### Backend

All backend logic MUST be implemented as AWS Lambda functions. Python MUST be used as
the sole backend language. Lambda functions MUST be stateless — no local disk writes or
in-memory state that persists across invocations. Shared business logic MUST be packaged
as Lambda Layers or internal Python modules, not duplicated across functions.

**Rationale**: Lambda eliminates server management overhead, scales automatically with
demand, and aligns with the cloud-native platform constraint.

### Frontend

The user interface MUST be built with React.js. The frontend MUST be a single-page
application (SPA) served via a managed static hosting service (e.g., S3 + CloudFront).
No server-side rendering frameworks that require persistent compute MUST be introduced.

**Rationale**: React.js provides a mature component model and ecosystem. Serving a static
SPA via CloudFront minimises operational overhead and aligns with the managed-services
principle.

### Data Storage

Persistent data MUST be stored in managed AWS storage services (e.g., DynamoDB, RDS,
S3). The choice of storage service for each feature MUST be justified in the plan based
on access patterns, consistency requirements, and cost. No self-hosted databases MUST be
run on EC2 or ECS unless no managed equivalent exists.

### API Layer

Backend functions MUST be exposed to the frontend via API Gateway. All API endpoints
MUST require authentication. Direct Lambda invocation from the frontend is not permitted.

## Development Workflow

All changes MUST be made on feature branches and reviewed via pull request before merge
to main. PRs MUST reference a spec or tracked issue. No direct commits to main are
permitted. The Constitution Check in each plan MUST be completed and passing before
implementation begins. Complexity violations — any deviation from these principles —
MUST be explicitly justified in the plan's Complexity Tracking table with a specific
reason and an explanation of why the simpler alternative was rejected.

## Quality Gates

Every PR MUST pass the following gates before merge:

- All tests passing in CI (unit, integration, contract)
- No new linting or type errors introduced
- Test coverage for core modules at or above 80%
- Performance benchmarks within declared thresholds (no regressions)
- Peer review approval from at least one other contributor
- Constitution Check completed and documented in plan.md

## Governance

This constitution supersedes all other project practices and conventions. When any
practice conflicts with these principles, the constitution wins. Amendments require a
documented rationale, team discussion, and a version-bumped update to this file.

Amendment versioning policy:
- **MAJOR**: Removal or backward-incompatible redefinition of an existing principle
- **MINOR**: New principle or section added, or material expansion of existing guidance
- **PATCH**: Clarification, wording improvement, or non-semantic refinement

All pull requests and code reviews MUST verify compliance with the principles above.
When in doubt, choose the simpler, more testable, more consistent approach.

**Version**: 1.1.0 | **Ratified**: 2026-05-10 | **Last Amended**: 2026-05-10
