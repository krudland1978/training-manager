<!-- sync-impact-report
Version Change: N/A → 1.0.0 (initial ratification)
Modified Principles: None (first-time fill)
Added Sections:
  - Core Principles (I–IV): Code Quality, Testing Standards, UX Consistency, Performance Requirements
  - Development Workflow
  - Quality Gates
  - Governance
Removed Sections: None
Templates Requiring Updates:
  ✅ .specify/templates/plan-template.md — Constitution Check references principles dynamically; no structural change required
  ✅ .specify/templates/spec-template.md — Success Criteria & Requirements align with performance/UX principles; no structural change required
  ✅ .specify/templates/tasks-template.md — Testing-first discipline already enforced; no structural change required
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

**Version**: 1.0.0 | **Ratified**: 2026-05-10 | **Last Amended**: 2026-05-10
