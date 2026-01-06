# Test Suite Fixes

## Major Refactoring: MealPlanner Architecture

**Date**: 2026-01-06

**Problem**: The `MealPlanner` class had inconsistent state management. The `calculate_meal_calories()` method depended on `self.ingredient_calories`, but `expand_meal_plan()` required passing `meals_db` as a parameter and didn't populate `self.ingredient_calories` consistently.

**Solution**: Refactored `MealPlanner` to own the meals database:

```python
# NEW API (after refactoring)
planner = MealPlanner(config, meals_db)  # Pass meals_db to constructor
expanded = planner.expand_meal_plan(meal_plan)  # No meals_db parameter
calories = planner.calculate_meal_calories(meal)  # No ingredient_calories parameter

# File-based API still works
planner = MealPlanner(config)
planner.load_meals_database(meals_db_path)  # Stores in self.meals_db
expanded = planner.load_meal_plan(plan_path, meals_db_path)
```

**Benefits**:
- Clear ownership: MealPlanner manages its own data
- No parameter passing confusion
- State is always consistent
- Cleaner test code

**Files Updated**:
- `recipier/meal_planner.py` - Updated `__init__`, `expand_meal_plan`, `calculate_meal_calories`
- `recipier/generate_meal_plan.py` - Updated MealPlanner initialization
- All test files - Updated to new API
- `backend/routers/tasks.py` - Already compatible (uses file-based API)

---

## Session 2: Integration and API Test Fixes

**Date**: 2026-01-06 (continued)

**Problems**: After MealPlanner refactoring, API and integration tests were failing due to schema mismatches and mock issues.

### Integration Test Fixes

1. **Schema Mismatch in meal_plans.py**:
   - `ScheduledMealRequest` required `meal_name` (not in fixtures) and was missing `id` field
   - `ShoppingTripRequest` used `date` and `meal_ids` instead of correct `shopping_date` and `scheduled_meal_ids`
   - **Fix**: Updated schemas in `backend/routers/meal_plans.py` to match `backend/routers/tasks.py`

2. **Todoist Mock Returns Dicts Instead of Objects**:
   - Mock returned `{"id": "123", "name": "Test"}` but adapter expected objects with `.id` and `.name` attributes
   - Caused `AttributeError: 'dict' object has no attribute 'id'`
   - **Fix**: Used `MagicMock` objects with attributes instead of plain dicts

3. **Module Caching in Full Test Suite**:
   - Test passed individually but failed when running full suite
   - Real Todoist API was being called (401 error)
   - **Fix**: Added module cache clearing at start of test (same pattern as `api_client` fixture)

### API Test Fixes

1. **Database Isolation**:
   - Tests loaded real 31-meal database instead of 2-meal fixture
   - **Fix**: Enhanced `api_client` fixture with `monkeypatch.setattr()` to override `MEALS_DB_PATH`

2. **Date Validation in Tasks Endpoint**:
   - Endpoint accepted invalid meal plans (eating before cooking)
   - **Fix**: Added comprehensive date validation that returns 422 with `validation_errors` list

3. **Task Count Assertions**:
   - Tests had wrong expected counts or used `> 0` instead of exact values
   - **Fix**: Calculated correct task counts (shopping + prep + cooking + eating)

**Result**: All 63 tests passing (39 unit + 18 API + 6 integration)

---

## Issues Fixed

### 1. MealPlanner API Misunderstanding

**Problem**: Tests were calling `MealPlanner(meals_db, config)` but actual API is `MealPlanner(config)`

**Fix**:
```python
# OLD (wrong)
planner = MealPlanner(sample_meals_database, sample_config)

# NEW (correct)
planner = MealPlanner(sample_config)
expanded = planner.expand_meal_plan(sample_meal_plan, sample_meals_database)
```

**Files Fixed**:
- `tests/unit/test_meal_planner.py` - Updated all MealPlanner instantiations
- `tests/integration/test_end_to_end.py` - Updated integration tests

### 2. calculate_meal_calories Signature

**Problem**: Tests were passing `calories_dict` but method doesn't take it

**Actual API**:
```python
def calculate_meal_calories(self, meal: Dict[str, Any]) -> Dict[str, int]:
    # Uses self.ingredient_calories which is set during expand_meal_plan
```

**Fix**: Call `expand_meal_plan` first to populate `ingredient_calories`, then call `calculate_meal_calories`

### 3. Todoist Mock Path

**Problem**: Mocking wrong class name

**Fix**:
```python
# OLD (wrong)
mock_api = mocker.patch("recipier.todoist_adapter.TodoistApi")

# NEW (correct)
mock_api = mocker.patch("todoist_api_python.api.TodoistAPI")
```

### 4. Mock Return Types

**Problem**: `create_tasks()` was mocked to return `int` but actual API returns `list`

**Fix**:
```python
# OLD (wrong)
mock_instance.create_tasks.return_value = 15

# NEW (correct)
mock_instance.create_tasks.return_value = ["task_1", "task_2", "task_3"]
```

### 5. API Test Isolation

**Problem**: API tests were loading real database (31 meals) instead of test fixture (2 meals)

**Fix**: Enhanced `api_client` fixture to:
- Clear cached module imports
- Change to temp directory before importing FastAPI app
- Properly restore directory after tests

## Test Status

### ✅ ALL TESTS PASSING (80/80)

#### Unit Tests (39/39) ✅
- ✅ All config tests (10/10) - 100% coverage
- ✅ All localization tests (14/14) - 100% coverage
- ✅ All meal planner tests (15/15) - 95% coverage
- ✅ All Task dataclass tests (3/3)

#### API Tests (35/35) ✅
- ✅ Meals API tests (13/13) - 98% coverage
- ✅ Tasks API tests (11/11) - 90% coverage
- ✅ Config router tests (5/5) - 100% coverage
- ✅ Meal plans API tests (6/6) - 95% coverage

#### Integration Tests (6/6) ✅
- ✅ Full meal plan to tasks workflow
- ✅ Meal plan validation workflow
- ✅ Save and load meal plan
- ✅ Quantity calculation workflow
- ✅ Multi cooking date workflow
- ✅ Shopping trip with multiple meals

### Coverage Report
```
recipier/config.py           100%
recipier/localization.py     100%
recipier/meal_planner.py      95%
backend/models/schemas.py    100%
backend/routers/config.py    100% ⬆️ (was 90%)
backend/routers/meals.py      98% ⬆️ (was 85%)
backend/routers/tasks.py      90% ⬆️ (was 87%)
backend/routers/meal_plans.py 95% ⬆️ (was 83%)
Overall coverage:             65% (80/80 tests passing) ⬆️ (was 64%)
```

## Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=recipier --cov=backend --cov-report=term-missing

# Run specific test categories
uv run pytest tests/unit/ -v
uv run pytest tests/api/ -v
uv run pytest tests/integration/ -v
```

## Next Steps

1. ✅ ~~Fix remaining 4 meal planner tests~~ **COMPLETE**
2. ✅ ~~Refactor MealPlanner architecture~~ **COMPLETE**
3. ✅ ~~Update API tests to work with isolated test database~~ **COMPLETE**
4. ✅ ~~Fix integration test mocks~~ **COMPLETE**
5. ✅ ~~Update validation tests for correct schema~~ **COMPLETE**
6. ✅ ~~Fix backend routers with new MealPlanner API~~ **COMPLETE**
7. Add more test coverage for edge cases (optional)
8. Consider adding tests for CLI tools (create_meal_tasks.py, generate_meal_plan.py)

---

## Summary

**Status**: ✅ **ALL TESTS PASSING** (80/80)

**Major Achievements**:
1. Refactored MealPlanner to own its data (meals_db and ingredient_calories)
2. Fixed all API test database isolation issues
3. Fixed all integration test mock issues
4. Added comprehensive date validation to tasks endpoint
5. Aligned all schemas across routers
6. Improved test coverage from 32% → 64% → **65%**
7. Achieved 90-100% coverage on all backend routers

**Coverage Breakdown**:
- Core modules (config, localization, meal_planner): 95-100%
- Backend routers: **90-100%** ⬆️ (was 83-87%)
  - config.py: **100%** (was 90%)
  - meals.py: **98%** (was 85%)
  - meal_plans.py: **95%** (was 83%)
  - tasks.py: **90%** (was 87%)
- Integration: 100% (all scenarios covered)
- TodoistAdapter: 72% (tested via integration tests)

**Files Modified** (Session 1 + 2 + 3):
- `recipier/meal_planner.py` - Complete refactoring
- `backend/routers/tasks.py` - Updated API + validation
- `backend/routers/meal_plans.py` - Fixed schemas
- `tests/conftest.py` - Enhanced fixtures
- `tests/api/test_tasks.py` - Fixed mocks + added 3 error case tests
- `tests/api/test_meals.py` - Added 3 error case tests
- `tests/api/test_config_router.py` - **NEW** (5 tests for config endpoints)
- `tests/api/test_meal_plans.py` - **NEW** (6 tests for validation edge cases)
- `tests/integration/test_end_to_end.py` - Fixed mocks and caching
- `recipier/todoist_adapter.py` - Fixed create_from_meal_plan method
- `recipier/generate_meal_plan.py` - Updated to new API
- All test files - Updated to new MealPlanner API
