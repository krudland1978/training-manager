# Quickstart: Team Training Plan Manager

**Branch**: `001-team-training-plans` | **Date**: 2026-05-10

## Prerequisites

- Python 3.12
- Node.js 20
- AWS CLI configured with appropriate credentials
- AWS CDK CLI: `npm install -g aws-cdk`

## Local Development

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Run unit tests
pytest tests/unit/

# Run integration tests (uses moto to mock AWS)
pytest tests/integration/
```

### Frontend

```bash
cd frontend
npm install
npm run dev       # Start Vite dev server at http://localhost:5173
npm test          # Run Jest + React Testing Library
npm run build     # Production build to frontend/dist/
```

### Running Against a Real AWS Environment

1. Deploy infrastructure (see Deployment below).
2. Copy the API Gateway URL and Cognito details from CDK outputs.
3. Create `frontend/.env.local`:
   ```
   VITE_API_URL=https://{api-id}.execute-api.{region}.amazonaws.com/prod
   VITE_COGNITO_USER_POOL_ID={user-pool-id}
   VITE_COGNITO_CLIENT_ID={client-id}
   ```
4. `npm run dev` — the frontend will call the real AWS backend.

## Deployment

```bash
cd infrastructure/cdk
pip install -r requirements.txt

# First time only
cdk bootstrap

# Deploy all stacks
cdk deploy --all
```

CDK outputs the API URL, CloudFront domain, and Cognito User Pool details after deploy.

## End-to-End Validation

Once deployed, validate the golden path:

1. **Create a manager account** in the Cognito User Pool (AWS Console or CLI).
2. **Log in** to the frontend and obtain a JWT.
3. **Import team members**: upload `specs/001-team-training-plans/examples/team-list.csv`.
4. **Import certifications**: upload `specs/001-team-training-plans/examples/certifications.csv`.
5. **Save requirements matrix**: `POST /requirements` with the role/grade rules.
6. **Generate plans**: `POST /plans/generate` — expect `generated: 6`.
7. **View plans**: `GET /plans` — confirm all 6 members appear.
8. **Check a days warning**: `GET /plans/P006` (Frank Miller, 4 days remaining) —
   expect `days_warning: true`.
9. **Export**: `GET /plans/export` — open CSV and confirm all members are present.

## Teardown

```bash
cd infrastructure/cdk
cdk destroy --all
```
