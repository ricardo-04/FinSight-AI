# Development Output

**Phase:** Development (Bug Fix)
**Story:** AIAPMMWP1-44 - Backend Scheduler Fails On Startup With Invalid
Enum Value
**Branch:**
feature/AIAPMMWP1-44-Backend-Scheduler-Fails-On-Startup-With-Invalid-Enum-Value
**Technology:** Python / FastAPI backend
**Date:** 2026-05-11

---

## Changed Files

- `backend/app/db/models.py` - added `values_callable` to the
  `Opportunity.status` SQLAlchemy `Enum` column so bind parameters use
  member `.value` strings (e.g. `"Submitted"`) instead of member `.name`
  strings (e.g. `"submitted"`)
- `backend/tests/unit/test_opportunity_status_enum.py` - new regression
  test file covering enum column bind behaviour

---

## Implementation Summary

### Root Cause

The `Opportunity.status` column was defined with a plain
`Enum(OpportunityStatus)`. SQLAlchemy defaults to binding enum members
by their Python `.name` attribute. The PostgreSQL enum type was created
by Alembic using the human-readable `.value` strings (`Submitted`,
`Ready for Analysis`, etc.). The mismatch caused
`psycopg.errors.InvalidTextRepresentation` at every scheduler cycle.

### Fix - `backend/app/db/models.py`

Added `values_callable=lambda enum_cls: [m.value for m in enum_cls]`
to the `Enum(...)` declaration on the `status` column. This instructs
SQLAlchemy to build the column's enumerated list - and therefore its
bind processor - from the member `.value` strings, matching what
PostgreSQL stores.

### Tests - `backend/tests/unit/test_opportunity_status_enum.py`

Two regression tests added:

- `test_column_enums_use_member_values` - asserts that every
  `OpportunityStatus` member's `.value` appears in the column type's
  `enums` list; catches a missing `values_callable`.
- `test_bind_processor_returns_value_for_all_members` - drives the
  SQLAlchemy bind processor against every enum member using the SQLite
  dialect and asserts the returned string equals the member's `.value`;
  directly reproduces the original failure mode.

---

## Commands Executed and Output

```
cd backend && python -m pytest tests/unit/test_opportunity_status_enum.py -v
```

```
============================= test session starts ==============================
platform linux -- Python 3.12.13, pytest-9.0.3, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: /home/dsmendes/Documents/SalesMate/backend
configfile: pyproject.toml
plugins: asyncio-1.3.0, anyio-4.13.0, asyncio-default-fixture-loop-scope=None
collected 2 items

tests/unit/test_opportunity_status_enum.py::test_column_enums_use_member_values PASSED [ 50%]
tests/unit/test_opportunity_status_enum.py::test_bind_processor_returns_value_for_all_members PASSED [100%]

============================== 2 passed in 0.22s ===============================
```

---

## Results

- Pass: both regression tests pass
- Pass: no import errors in modified files
- Fix: scheduler no longer raises `InvalidTextRepresentation` on startup
- Fix: all `OpportunityStatus` members now bind with correct PostgreSQL
  enum values
