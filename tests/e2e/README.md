# E2E API Contract Tests

Run the full API contract test suite to verify the Token Trail backend against the documented contract.

## Prerequisites

- Docker stack running: `docker compose up -d` (from repo root)
- Python 3 with dev deps: `pip install -r requirements-dev.txt`

## Run

From the **repo root**:

```bash
pytest tests/e2e/ -v
```

With print output:

```bash
pytest tests/e2e/ -v -s
```

Single test:

```bash
pytest tests/e2e/test_api_contract.py::test_health_returns_ok -v
```

## Optional: Custom API URL

Override the base URL (default `http://localhost:8000`):

```bash
API_BASE_URL=http://localhost:8000 pytest tests/e2e/ -v
```

## Test Change Report Template

When adding or changing tests, include:

1. **What changed (per file)**: Added/Changed/Removed test names
2. **Why each test exists**: Type (validation/defect/boundary), Protects, Would catch, Key assertions
3. **Weak-test check per test**: Hardcoded return would pass? No-op would pass?
4. **How to run**: `pytest tests/e2e/ -v`; pass/fail summary
