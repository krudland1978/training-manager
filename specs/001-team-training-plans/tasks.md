---
description: "Task list for Team Training Plan Manager"
---

# Tasks: Team Training Plan Manager

**Input**: Design documents from `specs/001-team-training-plans/`
**Prerequisites**: plan.md ✅, spec.md ✅, data-model.md ✅, contracts/api.md ✅, research.md ✅

**Tests**: Included. Required by constitution §II (Testing Standards) — 80% coverage floor,
tests written alongside implementation, CI gate before merge.

**Organization**: Tasks are grouped by user story to enable independent implementation
and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in all task descriptions

## Path Conventions

- Backend Lambda functions: `backend/functions/{domain}/{handler}.py`
- Shared backend logic: `backend/lib/{models|services|utils}/{file}.py`
- Frontend pages: `frontend/src/pages/{Name}Page.jsx`
- Frontend components: `frontend/src/components/{Name}.jsx`
- Frontend services: `frontend/src/services/{name}.js`
- Infrastructure: `infrastructure/cdk/stacks/{name}_stack.py`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialisation and directory structure.

- [X] T001 Create project directory structure: `backend/functions/`, `backend/lib/`, `backend/tests/`, `frontend/src/`, `infrastructure/cdk/` per plan.md
- [X] T002 Initialise Python backend project: `backend/requirements.txt` (boto3, pydantic, aws-lambda-powertools) and `backend/requirements-dev.txt` (pytest, moto, ruff)
- [X] T003 [P] Initialise React frontend project with Vite in `frontend/` (`npm create vite@latest frontend -- --template react`)
- [X] T004 [P] Initialise AWS CDK project in `infrastructure/cdk/app.py` with Python runtime; add `infrastructure/requirements.txt` (aws-cdk-lib, constructs)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared infrastructure and utilities that ALL user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Define DynamoDB stacks for all four tables (TeamMembers, Certifications, RequirementRules, TrainingPlans) with GSI definitions in `infrastructure/cdk/stacks/database_stack.py` per data-model.md
- [X] T006 [P] Define Cognito User Pool and API Gateway REST API with Cognito authoriser in `infrastructure/cdk/stacks/auth_stack.py` and `infrastructure/cdk/stacks/api_stack.py`
- [X] T007 [P] Define S3 bucket and CloudFront distribution for frontend SPA in `infrastructure/cdk/stacks/frontend_stack.py`
- [X] T008 Create shared DynamoDB helper utilities (get_item, put_item, scan, batch_write) in `backend/lib/utils/dynamodb.py`
- [X] T009 [P] Create CSV parsing utility with header validation and row-level error collection in `backend/lib/utils/csv_parser.py`
- [X] T010 [P] Create Lambda response formatter (success, error, CSV attachment) in `backend/lib/utils/response.py`
- [X] T011 [P] Create Pydantic model for TeamMember with field validation in `backend/lib/models/team_member.py` per data-model.md
- [X] T012 [P] Create Pydantic model for Certification with level_order enum in `backend/lib/models/certification.py` per data-model.md
- [X] T013 [P] Create Pydantic model for RequirementRule with grade band validation in `backend/lib/models/requirement_rule.py` per data-model.md
- [X] T014 [P] Create Pydantic model for TrainingPlan and OutstandingCert in `backend/lib/models/training_plan.py` per data-model.md
- [X] T015 Create frontend API client with Cognito JWT injection in `frontend/src/services/api.js`
- [X] T016 [P] Create frontend Cognito auth service (login, logout, token management) in `frontend/src/services/auth.js`
- [X] T017 Deploy foundational CDK stacks and confirm outputs: `cdk deploy DatabaseStack AuthStack FrontendStack`

**Checkpoint**: Foundation ready — all user story phases can now begin.

---

## Phase 3: User Story 1 — Upload Team and Course Data (Priority: P1) 🎯 MVP

**Goal**: Manager can upload team roster and certification catalogue via CSV and receive a
structured import summary.

**Independent Test**: Upload the sample CSVs from `specs/001-team-training-plans/spec.md`
and confirm the import summary shows 6 team members and 15 certifications accepted, with
correct handling of retired cert warnings.

### Implementation for User Story 1

- [X] T018 Implement team member import Lambda: parse multipart CSV, validate rows, write to DynamoDB TeamMembers table, return import summary in `backend/functions/team_members/import_handler.py`
- [X] T019 [P] Implement team member list Lambda: scan TeamMembers table with optional `active` and `role_id` query filters in `backend/functions/team_members/list_handler.py`
- [X] T020 Implement certification import Lambda: parse multipart CSV, validate rows, set `level_order`, flag retired certs as warnings (not errors), write to Certifications table in `backend/functions/certifications/import_handler.py`
- [X] T021 [P] Implement certification list Lambda: scan Certifications table with optional `retired` and `domain` query filters in `backend/functions/certifications/list_handler.py`
- [X] T022 Register `POST /team-members/import` and `GET /team-members` endpoints in `infrastructure/cdk/stacks/api_stack.py` (Lambda integrations with Cognito authoriser)
- [X] T023 [P] Register `POST /certifications/import` and `GET /certifications` endpoints in `infrastructure/cdk/stacks/api_stack.py`
- [X] T024 [P] Build shared FileUpload component (drag-and-drop CSV, file validation, upload state) in `frontend/src/components/FileUpload.jsx`
- [X] T025 [P] Build shared ImportSummary component (accepted/skipped/warnings table) in `frontend/src/components/ImportSummary.jsx`
- [X] T026 Build TeamUploadPage: FileUpload + ImportSummary + team member list preview in `frontend/src/pages/TeamUploadPage.jsx`
- [X] T027 [P] Build CertificationUploadPage: FileUpload + ImportSummary + cert list preview in `frontend/src/pages/CertificationUploadPage.jsx`
- [X] T028 Deploy US1 Lambda functions and test end-to-end via quickstart.md steps 3–4

**Checkpoint**: User Story 1 fully functional — team members and certifications can be
imported and listed independently.

---

## Phase 4: User Story 2 — Define Certification Requirements (Priority: P2)

**Goal**: Manager can save and retrieve the role/grade requirements matrix.

**Independent Test**: POST the full requirements matrix from research.md to
`POST /requirements` and confirm all 24 rules are saved; GET them back and confirm
they match exactly.

### Implementation for User Story 2

- [X] T029 Implement requirements save Lambda: validate all `required_cert_ids` exist in Certifications table, warn on retired certs, replace full matrix, return save summary in `backend/functions/requirements/save_handler.py`
- [X] T030 [P] Implement requirements get Lambda: scan RequirementRules table and return all rules sorted by role_id then grade_min in `backend/functions/requirements/get_handler.py`
- [X] T031 Register `POST /requirements` and `GET /requirements` endpoints in `infrastructure/cdk/stacks/api_stack.py`
- [X] T032 Build RequirementsTable component: editable grid of role/grade band rows with cert picker in `frontend/src/components/RequirementsTable.jsx`
- [X] T033 Build RequirementsPage: load existing matrix, render RequirementsTable, save on submit in `frontend/src/pages/RequirementsPage.jsx`
- [X] T034 Deploy US2 Lambda functions and test end-to-end via API contract in `specs/001-team-training-plans/contracts/api.md`

**Checkpoint**: User Story 2 fully functional — requirements matrix can be saved and
retrieved independently.

---

## Phase 5: User Story 3 — Generate Individualised Training Plans (Priority: P1)

**Goal**: System generates a personalised, ordered training plan for each active team
member, with a days-remaining warning where applicable.

**Independent Test**: With US1 and US2 data in place, call `POST /plans/generate` and
confirm: 6 plans generated, Alice Smith's plan contains only aws-sap (outstanding), Frank
Miller's plan has `days_warning: true` (4 days remaining vs 39 required), Eve Davis's
plan targets aws-dop + aws-scs.

### Implementation for User Story 3

- [X] T035 Implement plan generation service (gap analysis algorithm): load members, certs, rules; compute outstanding certs per member; calculate study days; set days_warning; order by level_order; detect and collect members with incomplete data (missing role_id, grade_level, or unknown role in requirements) into a `generation_errors` list returned in the response in `backend/lib/services/plan_generator.py` per research.md decision 4
- [X] T036 Implement plan generation Lambda: invoke plan_generator service, write all plans to TrainingPlans table, return generation summary in `backend/functions/plans/generate_handler.py`
- [X] T037 [P] Implement plan list Lambda: scan TrainingPlans table with optional `role_id` and `days_warning` filters in `backend/functions/plans/list_handler.py`
- [X] T038 [P] Implement plan get Lambda: fetch single plan by person_id, return 404 if not found in `backend/functions/plans/get_handler.py`
- [X] T039 Register `POST /plans/generate`, `GET /plans`, and `GET /plans/{person_id}` endpoints in `infrastructure/cdk/stacks/api_stack.py`
- [X] T040 [P] Build DaysWarningBadge component: amber warning indicator with days shortfall message in `frontend/src/components/DaysWarningBadge.jsx`
- [X] T041 [P] Build MemberPlanDetail component: required certs, certs held, outstanding cert list with study days, days warning in `frontend/src/components/MemberPlanDetail.jsx`
- [X] T042 [P] Build TeamPlansList component: table of all members with plan status, outstanding count, days warning indicator in `frontend/src/components/TeamPlansList.jsx`
- [X] T043 Build PlanGenerationPage: generate button, generation summary, link to plans dashboard in `frontend/src/pages/PlanGenerationPage.jsx`
- [X] T044 Deploy US3 Lambda functions and test end-to-end via quickstart.md steps 6–8

**Checkpoint**: User Story 3 fully functional — training plans generated, visible per
member, days warnings surfaced.

---

## Phase 6: User Story 4 — View and Export Training Plans (Priority: P3)

**Goal**: Manager can view all plans in a filterable dashboard and export them as CSV.

**Independent Test**: Open the dashboard, filter by `role_id = solution_architect`, confirm
only Alice Smith appears; click Export and confirm CSV opens in a spreadsheet with all
6 members and their plans.

### Implementation for User Story 4

- [X] T045 Implement plan export Lambda: scan TrainingPlans table, format as CSV (columns per contracts/api.md), return with `Content-Disposition: attachment` in `backend/functions/plans/export_handler.py`
- [X] T046 Register `GET /plans/export` endpoint in `infrastructure/cdk/stacks/api_stack.py`
- [X] T047 [P] Build PlanFilter component: dropdowns for role_id and days_warning filter, triggers parent re-fetch in `frontend/src/components/PlanFilter.jsx`
- [X] T048 [P] Build ExportButton component: calls GET /plans/export, triggers browser file download in `frontend/src/components/ExportButton.jsx`
- [X] T049 Build PlansDashboardPage: PlanFilter + TeamPlansList + ExportButton; clicking a row opens MemberPlanDetail in `frontend/src/pages/PlansDashboardPage.jsx`
- [X] T050 Deploy US4 Lambda and test end-to-end via quickstart.md step 9

**Checkpoint**: All user stories independently functional and testable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that apply across all user stories.

- [X] T051 Add structured error logging (aws-lambda-powertools Logger) to all 9 Lambda handlers
- [X] T052 [P] Add loading states, empty states, and error banners to all 5 frontend pages
- [X] T053 [P] Add React Router navigation and top-nav menu in `frontend/src/App.jsx` (routes: /team, /certifications, /requirements, /generate, /plans)
- [X] T054 [P] Configure GitHub Actions CI pipeline: lint (ruff) → pytest --cov with 80% minimum threshold → npm test → cdk synth; fail build if coverage drops below 80% for `backend/lib/` in `.github/workflows/ci.yml`
- [X] T055 Run full quickstart.md end-to-end validation and fix any failures
- [X] T056 [P] Update `specs/001-team-training-plans/checklists/requirements.md` to mark all items complete

---

## Phase 8: Test Suite (Constitution §II Compliance)

**Purpose**: Unit and integration tests required by constitution. Write tests as each
corresponding implementation task completes — do not defer to end.

### Foundational / Shared

- [X] T057 [P] Write unit tests for CSV parser (valid CSV, missing columns, malformed rows) in `backend/tests/unit/test_csv_parser.py`
- [X] T058 [P] Write unit tests for all Pydantic models (valid data, validation failures, edge values) in `backend/tests/unit/test_models.py`

### User Story 1 Tests

- [X] T059 [US1] Write integration tests for team member import Lambda: valid CSV, missing fields, duplicate person_id, updated records using moto DynamoDB in `backend/tests/integration/test_team_members_import.py`
- [X] T060 [P] [US1] Write integration tests for certification import Lambda: valid CSV, retired cert warnings, duplicate cert_id using moto in `backend/tests/integration/test_certifications_import.py`
- [X] T061 [P] [US1] Write Jest component tests for FileUpload and ImportSummary components in `frontend/tests/components/FileUpload.test.jsx` and `frontend/tests/components/ImportSummary.test.jsx`

### User Story 2 Tests

- [X] T062 [US2] Write integration tests for requirements save Lambda: valid matrix, unknown cert_id rejected, retired cert warned, full replace behaviour using moto in `backend/tests/integration/test_requirements.py`

### User Story 3 Tests

- [X] T063 [US3] Write unit tests for plan_generator service covering: member already certified (requirement_met), member with gap, days_warning trigger, incomplete member detection, retired cert exclusion, grade band nearest-lower matching in `backend/tests/unit/test_plan_generator.py`
- [X] T064 [P] [US3] Write integration tests for plan generation Lambda: end-to-end with seeded moto data matching the 6-person sample team in `backend/tests/integration/test_plans_generate.py`
- [X] T065 [P] [US3] Write Jest component tests for MemberPlanDetail and DaysWarningBadge in `frontend/tests/components/MemberPlanDetail.test.jsx`

### User Story 4 Tests

- [X] T066 [US4] Write integration tests for plan export Lambda: CSV output contains all members, correct columns, correct Content-Disposition header using moto in `backend/tests/integration/test_plans_export.py`

---

## Phase 9: FR-010 Stale Plans & SC-004 Quick Lookup

**Purpose**: Address two gaps found during analysis — stale plan detection (FR-010) and
member quick-lookup (SC-004).

### FR-010: Stale Plans Indicator (H1)

- [X] T067 Add a `plans_stale` flag to a DynamoDB metadata item (key: `META#plans`) that is set to `true` after any successful team member import, certification import, or requirements save in `backend/lib/utils/metadata.py`; update T018, T020, T029 handlers to call this after writing data
- [X] T068 [P] Build StalePlansBanner component: reads `plans_stale` status from `GET /meta/plans-status` endpoint; displays an amber banner "Plans are outdated — click Regenerate" with a direct link to PlanGenerationPage in `frontend/src/components/StalePlansBanner.jsx`
- [X] T069 [P] Add `GET /meta/plans-status` Lambda and API Gateway endpoint returning `{ "plans_stale": true/false }` in `backend/functions/meta/status_handler.py` and `infrastructure/cdk/stacks/api_stack.py`
- [X] T070 Add StalePlansBanner to PlansDashboardPage and PlanGenerationPage; clear `plans_stale` flag after successful `POST /plans/generate` in `frontend/src/pages/PlansDashboardPage.jsx` and `backend/functions/plans/generate_handler.py`

### SC-004: Member Quick Lookup (M2)

- [X] T071 [P] Add member name search input to PlansDashboardPage that filters the TeamPlansList client-side by name (no additional API call needed — plans already loaded); search clears when role filter changes in `frontend/src/pages/PlansDashboardPage.jsx`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — no dependency on US2, US3, US4
- **US2 (Phase 4)**: Depends on Foundational — no dependency on US1 (but US3 needs US1 + US2 data)
- **US3 (Phase 5)**: Depends on Foundational — requires US1 and US2 data to be populated before testing
- **US4 (Phase 6)**: Depends on US3 (plans must exist to view/export)
- **Polish (Phase 7)**: Depends on all user stories complete
- **Test Suite (Phase 8)**: Tasks written alongside corresponding story phase; T063/T064 require T035 complete
- **FR-010 / SC-004 (Phase 9)**: T067–T070 depend on T018/T020/T029; T071 depends on T049

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational — independent
- **US2 (P2)**: Can start after Foundational — independent (but populate US1 data first for meaningful testing)
- **US3 (P1)**: Can start after Foundational — needs US1 + US2 data loaded to validate end-to-end
- **US4 (P3)**: Depends on US3 plans existing

### Within Each User Story

- Pydantic models → Lambda handlers → API Gateway wiring → Frontend components → Frontend page
- Backend and frontend components marked [P] within a story can run in parallel
- Deploy step always last within each story

### Parallel Opportunities

- T003, T004 (Setup): frontend and CDK init in parallel
- T006, T007 (Foundational): auth/API and frontend stacks in parallel
- T008–T016 (Foundational): all utilities and models in parallel after T005
- T018–T021 (US1): team and cert Lambdas in parallel pairs
- T024, T025, T027 (US1): frontend components in parallel
- T035 (US3 core algorithm) must complete before T036, but T037 and T038 can run in parallel with T036

---

## Parallel Example: Foundational Phase

```bash
# Run in parallel after T005:
Task: "Create DynamoDB helpers in backend/lib/utils/dynamodb.py"         # T008
Task: "Create CSV parser in backend/lib/utils/csv_parser.py"             # T009
Task: "Create response formatter in backend/lib/utils/response.py"       # T010
Task: "Create TeamMember model in backend/lib/models/team_member.py"     # T011
Task: "Create Certification model in backend/lib/models/certification.py" # T012
Task: "Create RequirementRule model in backend/lib/models/requirement_rule.py" # T013
Task: "Create TrainingPlan model in backend/lib/models/training_plan.py"  # T014
Task: "Create API client in frontend/src/services/api.js"                # T015
Task: "Create auth service in frontend/src/services/auth.js"             # T016
```

---

## Implementation Strategy

### MVP First (US1 Only — Team and Cert Import)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (**CRITICAL** — blocks all stories)
3. Complete Phase 3: US1
4. **STOP and VALIDATE**: Upload sample team list and cert catalogue; confirm import summary
5. Demo if ready

### Incremental Delivery

1. Setup + Foundational → infrastructure ready
2. US1 → team and cert data can be managed (MVP!)
3. US2 → requirements matrix can be defined
4. US3 → training plans generated per member
5. US4 → plans viewable, filterable, exportable
6. Polish → CI, error handling, navigation

### Parallel Team Strategy

With multiple developers after Foundational is complete:
- Developer A: US1 backend (T018–T021) + US1 infrastructure (T022–T023)
- Developer B: US1 frontend (T024–T027)
- Once US1 is done, split US2 and US3 similarly

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks in the same phase
- [Story] label maps each task to its user story for traceability
- Deploy step at the end of each story phase — do not skip
- Retired certifications (aws-das, aws-dbs, aws-pas) must not appear as outstanding requirements
- Days warning is a non-blocking UI indicator only — never prevents plan generation or viewing
- Grade band matching: apply nearest lower rule if exact match missing (research.md decision 7)
