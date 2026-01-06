# Recipier Test Suite

Comprehensive pytest test suite for Recipier meal planning system.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and test configuration
├── unit/                    # Unit tests for individual components
│   ├── test_config.py       # Configuration system tests
│   ├── test_localization.py # Translation system tests
│   └── test_meal_planner.py # Core business logic tests
├── api/                     # API endpoint tests
│   ├── test_meals.py        # Meals database API tests
│   └── test_tasks.py        # Task generation API tests
└── integration/             # End-to-end integration tests
    └── test_end_to_end.py   # Full workflow tests
```

## Running Tests

### Install Test Dependencies

```bash
uv sync --dev
```

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=recipier --cov=backend --cov-report=html
```

Open `htmlcov/index.html` to view coverage report.

### Run Specific Test Types

```bash
# Unit tests only
pytest -m unit

# API tests only
pytest -m api

# Integration tests only
pytest -m integration
```

### Run Specific Test Files

```bash
# Test configuration
pytest tests/unit/test_config.py

# Test localization
pytest tests/unit/test_localization.py

# Test meal planner
pytest tests/unit/test_meal_planner.py

# Test API endpoints
pytest tests/api/
```

### Run Specific Test Functions

```bash
pytest tests/unit/test_config.py::TestTaskConfig::test_default_config
pytest tests/unit/test_meal_planner.py::TestMealPlanner::test_quantity_calculation
```

### Verbose Output

```bash
pytest -v
```

### Stop on First Failure

```bash
pytest -x
```

### Show Print Statements

```bash
pytest -s
```

## Test Coverage

Current test coverage includes:

### Unit Tests
- ✅ **Configuration System** - Loading, validation, user mapping, diet profiles
- ✅ **Localization** - Polish/English translations, format placeholders, completeness
- ✅ **Meal Planner** - Quantity calculations, task generation, per-person breakdowns
- ✅ **Task Dataclass** - Task creation, subtasks, labels

### API Tests
- ✅ **Meals API** - Get meals, search, calorie data, meal details
- ✅ **Tasks API** - Task generation, validation, token handling
- ✅ **Config API** - User configuration, environment token status

### Integration Tests
- ✅ **End-to-End Workflow** - Full meal plan to Todoist tasks
- ✅ **Validation Workflow** - Meal plan validation
- ✅ **Save/Load Workflow** - Meal plan persistence
- ✅ **Quantity Calculations** - Multi-person portion scaling
- ✅ **Multi-Cooking Dates** - Meal prep vs. separate cooking
- ✅ **Shopping Trips** - Combining multiple meals

## Fixtures

Common fixtures available in `conftest.py`:

### Test Data
- `sample_meals_database` - Sample meal recipes with ingredients
- `sample_meal_plan` - Sample scheduled meals and shopping trips
- `sample_config` - Sample TaskConfig with user mappings

### Temporary Files
- `temp_meals_database` - Temporary meals database file
- `temp_meal_plan` - Temporary meal plan file
- `temp_config` - Temporary config file

### Components
- `localizer_english` - English localizer instance
- `localizer_polish` - Polish localizer instance
- `mock_todoist_api` - Mocked Todoist API
- `api_client` - FastAPI test client
- `mock_env_token` - Mocked environment token

## Writing New Tests

### Unit Test Example

```python
import pytest
from recipier.config import TaskConfig

@pytest.mark.unit
def test_my_feature(sample_config):
    """Test my new feature."""
    # Arrange
    config = sample_config

    # Act
    result = config.some_method()

    # Assert
    assert result == expected_value
```

### API Test Example

```python
import pytest

@pytest.mark.api
def test_my_endpoint(api_client):
    """Test my API endpoint."""
    response = api_client.get("/api/my-endpoint")

    assert response.status_code == 200
    data = response.json()
    assert "expected_key" in data
```

### Integration Test Example

```python
import pytest

@pytest.mark.integration
def test_my_workflow(sample_meals_database, sample_config, mocker):
    """Test my complete workflow."""
    # Mock external dependencies
    mock_api = mocker.patch("recipier.todoist_adapter.TodoistApi")

    # Execute workflow
    # ... your code here ...

    # Verify results
    assert mock_api.called
```

## Continuous Integration

Tests are designed to run in CI/CD environments:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    uv sync --dev
    pytest --cov --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Troubleshooting

### Import Errors

If you get import errors, make sure you're running tests from the project root:

```bash
cd /path/to/recipier
pytest
```

### Fixture Not Found

If a fixture is not found, check that `conftest.py` is in the `tests/` directory.

### API Tests Failing

API tests require the FastAPI app to find `meals_database.json`. The test fixtures handle this by creating temporary databases.

### Mock Issues

If mocks aren't working, ensure you're patching the correct module path where the object is **used**, not where it's defined.

## Test Markers

Available markers for filtering tests:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.integration` - Integration tests

Use with `-m` flag:
```bash
pytest -m "unit and not integration"
pytest -m "api or integration"
```
