# SaaS Project

# SaaS Project

[![Django CI](https://github.com/bigbums/SaaS_Project/actions/workflows/ci.yml/badge.svg)](https://github.com/bigbums/SaaS_Project/actions/workflows/ci.yml)

[![codecov](https://codecov.io/gh/bigbums/SaaS_Project/branch/main/graph/badge.svg)](https://codecov.io/gh/bigbums/SaaS_Project)



This is a Django + DRF SaaS application with:
- Role-based access control (RBAC)
- Invoice management (tenant and platform)
- Validation and edge case tests
- CI/CD integration with GitHub Actions
- Coverage reporting enforced at 80%

## CI/CD Workflow
The project uses GitHub Actions to:
- Run migrations
- Execute all tests
- Enforce coverage ≥80%
- Upload coverage results to Codecov

## Running Tests Locally
```bash
pytest -vv --cov=saas_app --cov-report=term-missing




---

## 🔎 Step 2: Add Codecov Upload Step
Make sure your `.github/workflows/ci.yml` includes:

```yaml
    - name: Run tests with coverage
      run: |
        pytest --cov=saas_app --cov-report=xml --cov-report=term-missing --cov-fail-under=80 -vv

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v4
      with:
        token: ${{ secrets.CODECOV_TOKEN }} # only needed for private repos
        files: coverage.xml
        fail_ci_if_error: true
