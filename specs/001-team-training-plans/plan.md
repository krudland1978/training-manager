# Implementation Plan: Team Training Plan Manager

**Branch**: `001-team-training-plans` | **Date**: 2026-05-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-team-training-plans/spec.md`

## Summary

Build a web application that allows a team manager to import team rosters and AWS
certification catalogues, define role/grade certification requirements, and automatically
generate individualised training plans for each team member. Built on AWS using Lambda
(Python) for all backend logic, React.js for the frontend SPA, DynamoDB for persistent
storage, and API Gateway for the HTTP interface.

## Technical Context

**Language/Version**: Python 3.12 (backend Lambda), Node.js 20 (frontend build toolchain)
**Primary Dependencies**: AWS Lambda, API Gateway, DynamoDB, S3, CloudFront, Cognito,
  AWS CDK (Python) for infrastructure; React.js 18, Vite (frontend)
**Storage**: DynamoDB (all domain data); S3 (CSV exports, frontend static assets)
**Testing**: pytest + moto (backend unit/integration); Jest + React Testing Library (frontend)
**Target Platform**: AWS (Lambda, API Gateway, DynamoDB, S3, CloudFront, Cognito)
**Project Type**: Web application — React SPA + serverless REST API
**Performance Goals**: API responses <200ms p95; plan generation for 200 members <30s;
  UI interactions acknowledged <100ms
**Constraints**: Lambda cold-start budget included in p95 target; DynamoDB on-demand
  pricing; max team size 200 members
**Scale/Scope**: Up to 200 team members, ~50 certifications, ~10 roles, ~40 requirement rules

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality | ✅ PASS | Python + React both enforce single-responsibility via Lambda functions and React components |
| II. Testing Standards | ✅ PASS | pytest + moto for backend; Jest + RTL for frontend; 80% coverage gate in CI |
| III. UX Consistency | ✅ PASS | React component library enforces consistent patterns; all states handled |
| IV. Performance Requirements | ✅ PASS | DynamoDB + Lambda meet <200ms p95; plan generation is async-eligible |
| Platform (AWS) | ✅ PASS | All services are AWS-native |
| Backend (Lambda + Python) | ✅ PASS | All logic in Python Lambda functions; stateless by design |
| Frontend (React SPA) | ✅ PASS | React 18 SPA served via S3 + CloudFront |
| Data Storage (Managed AWS) | ✅ PASS | DynamoDB + S3 only; no self-hosted databases |
| API Layer (API Gateway + Auth) | ✅ PASS | All endpoints behind API Gateway; Cognito auth on every route |

**No violations. Gate passed. Proceeding to Phase 0.**

## Project Structure

### Documentation (this feature)

```text
specs/001-team-training-plans/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api.md
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
backend/
├── functions/
│   ├── team_members/
│   │   ├── import_handler.py    # POST /team-members/import
│   │   └── list_handler.py      # GET /team-members
│   ├── certifications/
│   │   ├── import_handler.py    # POST /certifications/import
│   │   └── list_handler.py      # GET /certifications
│   ├── requirements/
│   │   ├── save_handler.py      # POST /requirements
│   │   └── get_handler.py       # GET /requirements
│   └── plans/
│       ├── generate_handler.py  # POST /plans/generate
│       ├── list_handler.py      # GET /plans
│       ├── get_handler.py       # GET /plans/{person_id}
│       └── export_handler.py    # GET /plans/export
├── lib/
│   ├── models/                  # Pydantic data models
│   ├── services/                # Business logic (plan generation algorithm)
│   └── utils/                   # CSV parsing, DynamoDB helpers
└── tests/
    ├── unit/
    ├── integration/
    └── contract/

frontend/
├── src/
│   ├── components/              # Shared UI components
│   ├── pages/                   # Route-level page components
│   └── services/                # API client functions
└── tests/

infrastructure/
└── cdk/
    ├── app.py                   # CDK entry point
    └── stacks/                  # Lambda, API Gateway, DynamoDB, Cognito, CloudFront stacks
```

**Structure Decision**: Web application layout (Option 2) with an additional
`infrastructure/` directory for CDK. Backend is split by Lambda function to keep each
handler independently deployable and testable.

## Complexity Tracking

> No constitution violations identified. Table left intentionally empty.
