**Production Style Template for Casablanca Insight**

---

## 1. Git Branching Strategy
Adopt a GitFlow-like model to manage features, releases, and hotfixes cleanly:

- **main**: Production-ready code; every commit here is deployed automatically.
- **develop**: Integration branch for upcoming releases; merges from feature and hotfix branches.
- **feature/xxx**: Branch off `develop` for new features; named `feature/<short-description>`.
- **release/vX.Y.Z**: Branch off `develop` when preparing a new release; used for QA, version bump, and release notes.
- **hotfix/vX.Y.Z**: Branch off `main` to address critical production issues; merge back into both `main` and `develop`.

### Branch Naming Conventions
- **Features**: `feature/market-data-widget`, `feature/portfolio-import`
- **Releases**: `release/1.0.0`, `release/1.1.0`
- **Hotfixes**: `hotfix/1.0.1`, `hotfix/1.0.2`

## 2. Environment Configuration
Maintain separate configurations per environment with sample templates committed and actual secrets in CI/CD or secret store.

| Environment | Env File               | Purpose                         |
|-------------|------------------------|---------------------------------|
| Development | `.env.development`     | Local dev keys and endpoints    |
| Staging     | `.env.staging`         | Pre-production testing          |
| Production  | `.env.production`      | Live deployment settings        |

**Sample Template (`example.env.development`):**
```env
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
API_URL=http://localhost:8000
OPENAI_API_KEY=
STRIPE_SECRET_KEY=
SENDGRID_API_KEY=
```

## 3. Docker & Compose Setup
Use Docker Compose with overrides for local, staging, and production:

- **docker-compose.yml**: Base definitions (Postgres, Redis, backend, frontend)
- **docker-compose.override.yml**: Local overrides (volumes, host ports)
- **docker-compose.staging.yml**: Staging-specific images and env files
- **docker-compose.prod.yml**: Production images, no volumes, stricter resource limits

## 4. CI/CD Pipeline Templates
### GitHub Actions Workflows

#### 4.1 Pull Request Validation (`pr-check.yml`)
```yaml
name: PR Validation
on: [pull_request]
jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with: { node-version: '18' }
      - name: Install
        run: npm install --workspaces
      - name: Lint & Type-Check
        run: npm run lint && npm run type-check
      - name: Unit Tests
        run: npm test
```

#### 4.2 Deploy to Staging (`deploy-develop.yml`)
```yaml
name: Deploy Staging
on:
  push:
    branches: [ develop ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Staging
        run: |
          docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d --build
```

#### 4.3 Deploy to Production (`deploy-main.yml`)
```yaml
name: Deploy Production
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Production
        run: |
          docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

## 5. Release Process
1. **Feature Complete**: Merge all `feature/*` branches into `develop`.
2. **Create Release Branch**: `git checkout -b release/1.0.0 develop`.
3. **Test & QA**: Validate on staging; bump version and update changelog.
4. **Merge to main**: `git checkout main && git merge --no-ff release/1.0.0 && git tag v1.0.0`.
5. **Merge back to develop**: `git checkout develop && git merge --no-ff main`.
6. **Deploy**: CI/CD triggers for `main`.

---

*This template ensures consistent branching, environment segregation, and automated deployments for a robust production workflow.*