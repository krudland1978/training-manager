# Feature Specification: Team Training Plan Manager

**Feature Branch**: `001-team-training-plans`
**Created**: 2026-05-10
**Status**: Draft

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload Team and Certification Data (Priority: P1)

A team manager uploads a roster of team members (with their roles, seniority grades, and
existing certifications held) and a catalogue of available certifications. The system
accepts this input and stores it ready for plan generation.

**Why this priority**: Without team data and course catalogue, no training plans can be
generated. This is the foundational data entry flow — everything else depends on it.

**Independent Test**: Manager can upload a team list and certification catalogue and receive
confirmation that the data has been accepted and displays a summary of team members and
certifications recognised.

**Acceptance Scenarios**:

1. **Given** a manager has a team roster and a certification catalogue, **When** they submit both,
   **Then** the system confirms successful import and displays a summary of team members
   and certifications recognised.
2. **Given** a manager submits a team roster with missing required fields (e.g., no role
   assigned), **When** the system processes it, **Then** it reports which records are
   incomplete and does not generate plans for those individuals until corrected.
3. **Given** a manager submits an updated team roster (new starters, leavers, promotions),
   **When** the system processes it, **Then** it updates existing records and flags any
   changes that affect training plan requirements.

---

### User Story 2 - Define Certification Requirements by Role and Grade (Priority: P2)

A team manager specifies which certification level each combination of role and seniority
grade is required to hold. This requirements matrix is the target state against which
individual gaps are calculated.

**Why this priority**: The requirements matrix drives plan generation. Without it the
system cannot determine what each person needs to achieve.

**Independent Test**: Manager can enter a requirements matrix (role + grade → required
certification level) and view it back to confirm it is correct before generating plans.

**Acceptance Scenarios**:

1. **Given** a manager specifies that "Senior Analyst" must hold "Level 3 Certification",
   **When** they save the requirement, **Then** the system stores the rule and applies it
   to all team members with that role and grade.
2. **Given** a role has no certification requirement defined, **When** plans are generated,
   **Then** team members in that role are flagged as having no training requirement rather
   than being silently skipped.
3. **Given** a manager raises a required certification level for a role, **When** they save
   the change, **Then** affected team members' plans are recalculated to reflect the new
   target.

---

### User Story 3 - Generate Individualised Training Plans (Priority: P1)

The system generates a personalised training plan for each team member based on their
role, seniority grade, and the certifications they already hold. The plan shows which
courses they need to complete — in order — to reach the required certification level for
their role and grade.

**Why this priority**: This is the core value of the application. All other stories exist
to support this one.

**Independent Test**: For a team member with a known role, grade, and existing
certifications, the system produces a plan listing only the courses they still need, in
a logical sequence, to reach their required certification level.

**Acceptance Scenarios**:

1. **Given** a team member holds "Level 1 Certification" and their role requires "Level 3",
   **When** the manager generates plans, **Then** the system produces a plan showing the
   courses needed to progress from Level 1 to Level 3, excluding any already completed.
2. **Given** a team member already holds the required certification level for their role,
   **When** plans are generated, **Then** their plan shows "No training required" rather
   than an empty or missing plan.
3. **Given** a team member changes role or grade, **When** their record is updated and
   plans are regenerated, **Then** their training plan reflects the requirements of the
   new role and grade.
4. **Given** the manager generates plans for the whole team, **When** generation completes,
   **Then** every team member has a plan or an explicit "no requirement" status — no one
   is silently omitted.

---

### User Story 4 - View and Export Training Plans (Priority: P3)

A manager can view all generated training plans in one place — for the whole team or
filtered by individual, role, or grade — and export them for sharing or record-keeping.

**Why this priority**: Plans have no value if they cannot be reviewed and shared. This
story closes the loop from generation to practical use.

**Independent Test**: Manager can view a team member's plan, filter the team view by role,
and export the full team plan list in a format that opens without specialist software.

**Acceptance Scenarios**:

1. **Given** plans have been generated, **When** the manager views the team overview,
   **Then** they see all team members with their plan status and outstanding training
   summarised.
2. **Given** the manager filters by role, **When** the view updates, **Then** only team
   members with that role are shown with their respective plans.
3. **Given** the manager opens an individual's plan, **When** it loads, **Then** they see
   the full list of required courses, the certification target, and courses already held.
4. **Given** the manager requests an export, **When** the export is produced, **Then** it
   contains all team members and their plans in a format openable without specialist
   software.

---

### Edge Cases

- What happens when a course in a team member's existing certifications is removed from
  the course catalogue? The certification is still recognised as held; the course is simply
  no longer available for new completions.
- What happens when two courses lead to the same certification level? The plan presents
  all qualifying options so the manager can select or configure a preference.
- What happens when a team member's grade falls between two defined requirement levels
  (e.g., requirements exist for Grade 3 and Grade 5 but the member is Grade 4)? The
  system applies the nearest lower requirement and flags the gap for the manager to review.
- What happens if the course catalogue is empty when plans are generated? The system
  informs the manager that no courses are available and no plans can be produced.
- What happens when a team member's remaining training days are insufficient to complete
  their required certifications? The system displays a warning on their plan but still
  generates and shows the full plan — the manager decides how to respond (e.g., increase
  allocation or prioritise certifications).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow a manager to submit a list of team members including
  each person's name, role, seniority grade, and current certifications held.
- **FR-002**: The system MUST allow a manager to submit a certification catalogue listing
  available certifications and the certification level each one awards.
- **FR-003**: The system MUST allow a manager to define a requirements matrix specifying
  the certification level required for each role and seniority grade combination.
- **FR-004**: The system MUST generate an individualised training plan for each team
  member listing only the courses they still need to reach their required certification
  level.
- **FR-005**: The system MUST order courses within a training plan in progression order
  (lower certification levels before higher).
- **FR-006**: The system MUST mark team members who already meet their required
  certification level as having no outstanding training requirement.
- **FR-007**: The system MUST flag team members whose data is incomplete rather than
  silently skipping them during plan generation.
- **FR-008**: The system MUST allow a manager to view training plans for the whole team
  or filtered by individual, role, or grade.
- **FR-009**: The system MUST allow training plans to be exported in at least one format
  that does not require specialist software to open.
- **FR-010**: The system MUST recalculate affected training plans when team member data,
  the course catalogue, or the requirements matrix is updated.
- **FR-011**: The system MUST display a warning on a team member's training plan when
  their remaining allocated training days are insufficient to complete all required
  certifications, but MUST NOT prevent the plan from being generated or viewed.

### Key Entities

- **Team Member**: An individual on the team, identified by name, role, seniority grade,
  and the set of certifications they currently hold.
- **Course**: An available training course with a name and the certification level it
  awards upon completion.
- **Certification Level**: A named, ordered level of attainment (e.g., Level 1, Level 2,
  Level 3) that a team member can hold or a course can award.
- **Requirements Matrix**: A mapping of (role, grade) to required certification level,
  defining what each type of team member must achieve.
- **Training Plan**: A personalised, ordered list of courses a specific team member must
  complete to reach their required certification level.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A manager can go from submitting team and certification data to having
  generated training plans for all team members in under 30 seconds for a team of up to
  200 people.
- **SC-002**: Generated training plans are accurate — 100% of plans contain only courses
  the team member does not already hold and that lead toward their required certification
  level.
- **SC-003**: Every person in the submitted roster appears in the output with either a
  training plan or an explicit "no requirement" status — 0% silently omitted.
- **SC-004**: A manager can locate a specific team member's plan within 30 seconds of
  opening the application.
- **SC-005**: Exported plans can be opened and read without additional software by 100%
  of recipients.

## Example Data

### Team List

The following CSV format is used to submit team member data:

```csv
person_id,name,email,grade_level,role_id,start_date,grade_start_date,manager_email,location,active,days_allocated_override,days_remaining,certifications_held
P001,Alice Smith,alice.smith@company.com,7,solution_architect,15/03/2022,01/04/2024,big.manager@company.com,London,TRUE,10,10,aws-cp|aws-saa
P002,Bob Johnson,bob.johnson@company.com,5,software_dev_engineer,10/01/2024,10/01/2024,big.manager@company.com,London,TRUE,10,10,aws-cp
P003,Carol Williams,carol.williams@company.com,9,cloud_devops,01/09/2018,01/04/2023,big.manager@company.com,London,TRUE,10,10,aws-cp|aws-soa|aws-dop
P004,David Brown,david.brown@company.com,3,cloud_engineer,15/09/2025,15/09/2025,big.manager@company.com,Manchester,TRUE,10,5,
P005,Eve Davis,eve.davis@company.com,10,devsecops,01/06/2017,01/01/2024,big.manager@company.com,Edinburgh,TRUE,10,6,aws-cp|aws-soa|aws-dop
P006,Frank Miller,frank.miller@company.com,8,application_architect,01/02/2020,01/04/2024,big.manager@company.com,Bristol,TRUE,10,4,aws-cp|aws-saa
```

**Field notes**:
- `person_id` — unique identifier for each team member
- `grade_level` — numeric seniority grade (higher = more senior)
- `role_id` — machine-readable role identifier (e.g., `solution_architect`, `cloud_devops`)
- `days_allocated_override` — total training days allocated to this person
- `days_remaining` — training days not yet consumed
- `active` — whether the person is currently on the team
- `certifications_held` — pipe-separated list of `cert_id` values already held (empty = none)

### Certification Catalogue

The following CSV format defines available certifications, their study time, difficulty, and domain:

```csv
cert_id,exam_code,name,provider,level,domain,typical_study_days,difficulty_multiplier,validity_years,retired,superseded_by_cert_id
aws-cp,CLF-C02,AWS Certified Cloud Practitioner,aws,foundational,General,3,1.0,3,false,
aws-aip,AIF-C01,AWS Certified AI Practitioner,aws,foundational,AI/ML,4,1.0,3,false,
aws-saa,SAA-C03,AWS Certified Solutions Architect - Associate,aws,associate,Architecture,8,1.5,3,false,
aws-dva,DVA-C02,AWS Certified Developer - Associate,aws,associate,Development,8,1.5,3,false,
aws-soa,SOA-C02,AWS Certified SysOps Administrator - Associate,aws,associate,Operations,9,1.5,3,false,
aws-dea,DEA-C01,AWS Certified Data Engineer - Associate,aws,associate,Data,10,1.6,3,false,
aws-mla,MLA-C01,AWS Certified Machine Learning Engineer - Associate,aws,associate,AI/ML,10,1.6,3,false,
aws-sap,SAP-C02,AWS Certified Solutions Architect - Professional,aws,professional,Architecture,15,2.6,3,false,
aws-dop,DOP-C02,AWS Certified DevOps Engineer - Professional,aws,professional,DevOps,15,2.5,3,false,
aws-ans,ANS-C01,AWS Certified Advanced Networking - Specialty,aws,specialty,Networking,14,2.2,3,false,
aws-scs,SCS-C02,AWS Certified Security - Specialty,aws,specialty,Security,12,2.0,3,false,
aws-mls,MLS-C01,AWS Certified Machine Learning - Specialty,aws,specialty,AI/ML,14,2.1,3,false,
aws-das,DAS-C01,AWS Certified Data Analytics - Specialty,aws,specialty,Data,13,2.0,3,true,
aws-dbs,DBS-C01,AWS Certified Database - Specialty,aws,specialty,Data,13,2.0,3,true,
aws-pas,PAS-C01,AWS Certified SAP on AWS - Specialty,aws,specialty,Workloads,12,2.0,3,true,
```

**Field notes**:
- `cert_id` — unique identifier for the certification
- `exam_code` — official vendor exam code
- `level` — progression tier: `foundational` → `associate` → `professional` → `specialty`
- `domain` — subject area (e.g., Architecture, Security, AI/ML, Data)
- `typical_study_days` — baseline study days required; actual days = `typical_study_days × difficulty_multiplier`
- `difficulty_multiplier` — scales study time for individual circumstances
- `validity_years` — how long the certification remains valid before renewal is needed
- `retired` — if `true`, the certification is no longer offered for new candidates
- `superseded_by_cert_id` — if retired, the replacement certification (if any)

**Certification level ordering** (lowest to highest):
1. `foundational`
2. `associate`
3. `professional`
4. `specialty`

### Role and Grade Requirements Matrix

The following defines the required certification(s) for each role and grade band. Higher
grades require more advanced certifications within the role's domain track.

```csv
role_id,grade_min,grade_max,required_cert_ids,notes
cloud_engineer,1,3,aws-cp,Foundational AWS literacy
cloud_engineer,4,6,aws-soa,Operations associate
cloud_engineer,7,8,aws-sap,Solutions architect professional
cloud_engineer,9,99,aws-sap|aws-ans,Professional + Networking specialty
software_dev_engineer,1,3,aws-cp,Foundational AWS literacy
software_dev_engineer,4,6,aws-dva,Developer associate
software_dev_engineer,7,8,aws-dop,DevOps professional
software_dev_engineer,9,99,aws-dop|aws-mla,Professional + ML associate
solution_architect,1,3,aws-cp,Foundational AWS literacy
solution_architect,4,6,aws-saa,Solutions architect associate
solution_architect,7,8,aws-sap,Solutions architect professional
solution_architect,9,99,aws-sap|aws-scs,Professional + Security specialty
application_architect,1,3,aws-cp,Foundational AWS literacy
application_architect,4,6,aws-saa,Solutions architect associate
application_architect,7,8,aws-sap,Solutions architect professional
application_architect,9,99,aws-sap|aws-ans,Professional + Networking specialty
cloud_devops,1,3,aws-cp,Foundational AWS literacy
cloud_devops,4,6,aws-soa,SysOps associate
cloud_devops,7,8,aws-dop,DevOps professional
cloud_devops,9,99,aws-dop|aws-ans,Professional + Networking specialty
devsecops,1,3,aws-cp,Foundational AWS literacy
devsecops,4,6,aws-soa,SysOps associate (security foundation)
devsecops,7,8,aws-dop,DevOps professional
devsecops,9,99,aws-dop|aws-scs,Professional + Security specialty
```

**Field notes**:
- `grade_min` / `grade_max` — inclusive grade band; use `99` as an open upper bound
- `required_cert_ids` — pipe-separated list of certifications all of which must be held
- Each certification's `typical_study_days × difficulty_multiplier` determines the
  study time needed; this is compared against the team member's `days_remaining`

## Assumptions

- The manager is the sole user of this application; team members do not have their own
  logins or self-service access in this version.
- Certification levels are strictly ordered (Level 1 < Level 2 < Level 3); there are no
  parallel tracks or equivalent levels in this version.
- A team member's existing certifications are provided as part of the input data; the
  system does not connect to external certification registries.
- Certifications already held remain valid even if the awarding course is later removed
  from the catalogue.
- Course progression follows certification level order; no additional prerequisite logic
  beyond level ordering is required in this version.
- The expected team size is up to 200 people.
- Export format defaults to CSV; PDF is a stretch goal.
- Mobile access is out of scope for this version.
