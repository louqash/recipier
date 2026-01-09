# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Recipier is a modular Python system for converting meal plans into organized Todoist tasks. Available as both a Python CLI tool and a modern React web interface. It uses a meals database system where recipes are stored separately from meal plans, allowing for reusable recipes with personalized portion scaling.

### Project Structure
- **Backend**: FastAPI server providing REST API for meals database, meal plan management, and task generation
- **Frontend**: React + Vite web interface with drag-and-drop calendar, shopping trip management, and bilingual support
- **CLI Tools**: Python command-line tools for task creation and interactive meal plan generation

## Common Commands

### Development Setup
```bash
# Install dependencies
uv sync

# Set Todoist API token (required)
export TODOIST_API_TOKEN='your_token_here'
```

### Running with Docker

```bash
# Production (single container with frontend + backend)
docker build -t recipier .
docker run -d -p 8000:8000 -e TODOIST_API_TOKEN='your_token' recipier

# Production with Docker Compose
docker-compose up -d

# Development (separate containers with hot-reload)
docker-compose -f docker-compose.dev.yml up

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

See [DOCKER.md](./DOCKER.md) for comprehensive Docker documentation.

### Running the Application (Local)
```bash
# Create tasks from meal plan
uv run recipier meal_plan.json meals_database.json

# Create tasks with custom configuration
uv run recipier meal_plan.json meals_database.json --config my_config.json

# Generate new meal plan interactively
uv run recipier-generate
```

### Entry Points
The entry points are defined in `pyproject.toml` as:
- `recipier` - Create Todoist tasks from existing meal plan JSON
- `recipier-generate` - Interactive meal plan generator
- `recipier-backend` - Start the FastAPI backend server
- `recipier-frontend` - Start the React frontend development server

### Web Interface
```bash
# Start backend server
uv run recipier-backend

# Start backend with custom port
uv run recipier-backend --port 3000

# Start backend without auto-reload (production mode)
uv run recipier-backend --no-reload

# Start frontend development server
uv run recipier-frontend

# Build frontend for production
uv run recipier-frontend build

# Preview production build
uv run recipier-frontend preview
```

**Key Features:**
- Drag-and-drop meal scheduling with FullCalendar
- Unique instance IDs for scheduled meals (format: `sm_{timestamp}`)
- Delete meals from calendar (auto-removes from shopping trips)
- Smart duplicate prevention (meals can't be in multiple shopping trips)
- Smart date handling (new cooking dates default to next day after previous)
- Meal names cached and inferred from database (not stored in scheduled meals)
- Bilingual support (Polish/English) with instant language switching
- Shopping trip management with visual meal assignment

## Architecture

### Core Design Pattern: Adapter Pattern

The codebase uses a modular adapter pattern to separate business logic from external integrations:

```
meal_planner.py (core logic) -> Task objects -> todoist_adapter.py (Todoist API)
```

This allows the core meal planning logic to be reused with different task management systems (MCP servers, web apps, other task managers).

### Module Responsibilities

**`meal_planner.py`** - Platform-independent meal planning logic
- Defines the `Task` dataclass (platform-agnostic task representation)
- `MealPlanner` class handles:
  - Loading and expanding meal plans with database lookups
  - Calculating ingredient quantities based on servings and base portion sizes
  - Generating shopping, prep, and cooking tasks
  - Grouping ingredients by category and creating subtasks
  - Dividing ingredients for multiple cooking sessions
- Key methods:
  - `load_meal_plan()`: Loads plan and merges with meals database
  - `expand_meal_plan()`: Calculates quantities based on servings_per_person × base_servings
  - `generate_all_tasks()`: Creates all shopping, prep, and cooking tasks
  - `create_person_portion_subtasks()`: Creates per-person cooking subtasks using `per_person` ingredient data

**`todoist_adapter.py`** - Todoist-specific integration
- `TodoistAdapter` class converts `Task` objects to Todoist API calls
- Handles project and section management
- Maps user names to Todoist user IDs for task assignment
- Can be swapped for other adapters (e.g., Google Tasks, Notion)

**`config.py`** - Configuration management
- `TaskConfig` dataclass for customizable settings
- Shopping categories, emojis, priorities, project/section names
- User mapping for task assignment (maps internal names to Todoist usernames)
- Language setting for localization ("polish" or "english")
- Can be loaded from JSON files

**`localization.py`** - Localization support
- `Localizer` class for managing translations
- Supports Polish and English languages
- Translates CLI prompts, Todoist task titles and descriptions
- Used by `MealPlanner` and `generate_meal_plan.py`
- Set language in `TaskConfig.language` (defaults to "polish")

**`create_meal_tasks.py`** - CLI interface
- Command-line tool that orchestrates the flow
- Validates environment (API token)
- Displays progress and statistics

**`generate_meal_plan.py`** - Interactive meal plan generator
- Interactive CLI for creating new meal plans using questionary
- Features fuzzy search for meal selection from database
- Guides user through: meal selection, portion sizes, cooking dates, meal types, assignments
- Collects shopping trip information
- Saves to JSON file (named by earliest cooking date)
- Optionally creates Todoist tasks immediately after generation

### Data Flow: Meals Database System

The system uses a two-file approach for separation of recipes and scheduling:

1. **Meals Database** (`meals_database.json`):
   - Stores reusable recipes with base ingredient quantities per serving
   - Defines `base_servings` for each person (e.g., high_calorie: 1.67x, low_calorie: 1.0x)
   - Recipes are type-agnostic (same recipe can be used for different meal types)
   - Contains centralized `ingredient_details` dictionary with calories, unit_size, and adjustable flag for all ingredients
   - Ingredients are normalized (e.g., all milk → "Mleko bezlaktozowe 2%")
   - Schema: `meals_database_schema.json`

2. **Meal Plan** (`meal_plan.json`):
   - Contains `scheduled_meals` array (not `meals`) - each has unique `id` (format: `sm_{timestamp}`)
   - References meals by `meal_id` from database (meal names inferred dynamically, not stored)
   - Specifies `servings_per_person` (how many servings each person gets)
   - Defines `cooking_dates` (when to cook), `meal_type` (breakfast/second_breakfast/dinner/supper), and `assigned_cook`
   - `meal_type` is defined here (not in database) so the same recipe can be eaten at different meal times
   - Shopping trips use `shopping_date` (not `date`) and `scheduled_meal_ids` (not `meal_ids`)
   - Same recipe can be scheduled multiple times with different instance IDs
   - Schema: `meal_plan_schema.json`

3. **Expansion Process** (`expand_meal_plan()` in `meal_planner.py`):
   ```
   Final Quantity = base_ingredient_qty × base_servings[person] × servings_per_person[person]
   ```
   - Creates `per_person` breakdown for each ingredient
   - Generates total quantities for shopping
   - Handles meal prep (1 cooking date) vs. separate cooking (multiple dates)

### Task Generation Logic

**Shopping Tasks**:
- Group ingredients from multiple meals by shopping trip
- Task title shows meal names with multipliers (x2, x3) for multiple cooking sessions
  - Example: "Shopping for: Spaghetti x3, Pizza x2"
  - Counts total cooking sessions (sum of cooking_dates across all scheduled meal instances)
- Create subtasks ordered by category (produce, meat, dairy, pantry, etc.)
- Use TOTAL quantities across all people
- Add category labels for organization

**Cooking Tasks**:
- Create per-person portion subtasks showing individual quantities
- For meal prep (1 cooking date): show full quantities
- For multiple cooking dates: divide quantities evenly across sessions
- Validation: portions must equal number of cooking dates for multi-session meals

**Prep Tasks**:
- Schedule based on `days_before` relative to first cooking date
- Support separate prep assignment (can differ from cook)

### Key Data Structures

**Task Dataclass** (`meal_planner.py`):
- Platform-agnostic task representation
- Contains: title, description, priority, assigned_to, due_date, labels, subtasks
- `task_type` field: "shopping", "prep", or "cooking"

**Ingredient with per_person**:
```json
{
  "name": "spaghetti",
  "quantity": 400,  // Total for shopping
  "unit": "g",
  "category": "pantry",
  "per_person": {
    "John": {"quantity": 240, "unit": "g", "portions": 1},
    "Jane": {"quantity": 160, "unit": "g", "portions": 1}
  }
}
```

### Ingredient Details System

**Centralized Ingredient Details**:
- All ingredient data stored in `meals_database.json` under `ingredient_details` key
- Format: `{"ingredient_name": {"calories_per_100g": 165, "unit_size": 40, "adjustable": false}}`
- Single source of truth for 140+ ingredients with:
  - `calories_per_100g`: Calorie content (required)
  - `unit_size`: Package/unit size for rounding in grams/ml (optional)
  - `adjustable`: Whether ingredient can be modified for calorie compensation (defaults to true, auto-false if unit_size set)
- Frontend fetches via `/api/meals/ingredient-details` endpoint and caches in memory
- Calories calculated on-the-fly using ingredient lookups (no redundant data in recipes)

**Package/Unit Size Rounding System**:
- Rounds ingredient quantities to multiples of package/unit sizes (e.g., 40g sachets, 60g tortillas)
- **Meal-plan-level rounding**: Aggregates across ALL shopping trips, rounds total, then distributes
- **Smart distribution**: Uses leftover tracking to minimize purchases (e.g., buying 0 units in Trip2 when Trip1 has surplus)
- **Calorie preservation**: Automatically adjusts "adjustable" ingredients to maintain meal calorie totals (±1 kcal tolerance)
- **Warning system**: Alerts if ingredient changes >50%, suggests portion counts to reduce impact
- **Minimum enforcement**: Always uses at least 1 unit per meal plan
- Example ingredients with unit_size:
  - Budyń waniliowy bez cukru: 40g (powder sachet)
  - Tortilla pełnoziarnista: 60g (individual tortilla)
  - Pudding proteinowy Valio: 90g (individual cup)

**Ingredient Normalization**:
- Ingredients are normalized to canonical names (e.g., "Jajko"/"Jajo" → "Jajka")
- Use `normalize_ingredients.py` script to update database
- Normalization log saved to `ingredient_normalization.log`
- Key normalizations:
  - All lactose-free milk → "Mleko bezlaktozowe 2%" (1.5% quantities adjusted -6%)
  - Granola variants → "Granola proteinowa" (408 kcal/100g)
  - Frozen/fresh variants consolidated (spinach, berries, nuts)

**Calorie Display** (Frontend):
- Meal cards show: `~2850 kcal / ~1700 kcal`
  - First number = high_calorie person (with base_servings multiplier, e.g., 1.67x)
  - Second number = low_calorie person (with base_servings multiplier, e.g., 1.0x)
- Calculation: `sum((quantity/100) × calories_per_100g × base_servings × servings_per_person)`
- Package size indicators shown in meal details modal (e.g., "📦 Package: 40g")

**Updating Ingredient Data**:
1. Edit `meals_database.json` → `ingredient_details` section
2. To add unit size rounding: set `unit_size` to package size in grams/ml and `adjustable: false`
3. Changes instantly apply to frontend (no script needed)
4. Add new ingredients: add to dictionary with all three fields

### Important Implementation Details

**Portion Calculation**:
- Base recipe defines ingredient quantity per 1 serving
- `base_servings` in database defines person-specific multipliers (meal-level)
- `servings_per_person` in meal plan defines how many servings each person gets
- System automatically calculates: base × base_servings × servings_per_person
- For package rounding scenarios, use `unit_size` in `ingredient_details` instead of per-ingredient overrides

**Multiple Cooking Sessions**:
- If `cooking_dates` has 1 date: meal prep (cook once for multiple portions)
- If `cooking_dates` has multiple dates: cook separately (divide ingredients evenly)
- Assertion validates: total portions = number of cooking dates (for multi-session)

**Task Assignment**:
- Uses `user_mapping` in config to map internal names to Todoist usernames
- Fetches collaborator IDs via Todoist API
- Hardcoded project ID for collaborator lookup: '6fgJjvvgQX92XJcf' (in `todoist_adapter.py:61`)

**Category Ordering**:
- Shopping categories are ordered in `TaskConfig.shopping_categories`
- Default order: produce, meat, dairy, pantry, frozen, bakery, beverages, other
- This ordering is used for both shopping subtasks and cooking subtasks

**Localization**:
- Set language in config: `TaskConfig(language="english")` or `TaskConfig(language="polish")`
- Default is Polish
- Affects:
  - CLI prompts in `generate_meal_plan.py` (meal selection, portions, dates, etc.)
  - Todoist task titles and descriptions (shopping, prep, cooking tasks)
  - Meal type names (Breakfast/Śniadanie, Lunch/Obiad, etc.)
- To add a new language:
  1. Add translation dictionary to `localization.py` (e.g., `Translations.SPANISH`)
  2. Update `Localizer.__init__()` to support the new language
  3. All strings are centralized in `localization.py` for easy maintenance

### Extensibility Points

**To add a new task manager integration**:
1. Create new adapter class (e.g., `notion_adapter.py`)
2. Implement methods to convert `Task` objects to target API
3. Follow the pattern in `TodoistAdapter`

**To add new task types**:
1. Add task generation method to `MealPlanner`
2. Update `generate_all_tasks()` to include new type
3. Add section configuration if using sections

**To customize formatting**:
- Modify `TaskConfig` dataclass with new options
- Update `format_ingredient_title()` or relevant methods in `MealPlanner`

## File Organization

### Core Application Files
- `config.py` - Configuration dataclass
- `meal_planner.py` - Core business logic (16KB, most complex)
- `todoist_adapter.py` - Todoist API integration
- `create_meal_tasks.py` - CLI script
- `generate_meal_plan.py` - Interactive meal plan generator
- `localization.py` - Translation support (Polish/English)

### Backend Files
- `backend/main.py` - FastAPI application entry point
- `backend/routers/meals.py` - Meals database API endpoints
- `backend/routers/meal_plans.py` - Meal plan save/load/validate endpoints
- `backend/routers/tasks.py` - Todoist task generation endpoint
- `backend/models/schemas.py` - Pydantic models for validation

### Frontend Files
- `frontend/src/components/Calendar/CalendarView.jsx` - FullCalendar integration, event display
- `frontend/src/components/MealsLibrary/MealsLibrary.jsx` - Draggable meal cards
- `frontend/src/components/MealModal/MealConfigModal.jsx` - Meal configuration form
- `frontend/src/components/ShoppingManager/ShoppingManager.jsx` - Shopping trip management
- `frontend/src/components/ActionBar/ActionBar.jsx` - Save/Load/Generate buttons
- `frontend/src/hooks/useMealPlan.jsx` - Central state management with Context API
- `frontend/src/localization/translations.js` - Frontend translations and formatting helpers

### Schema Files
- `meals_database_schema.json` - Schema for recipes database
- `meal_plan_schema.json` - Schema for weekly meal plans

### Data Files
- `data/*.json` - Meal plan examples (e.g., `2026-01-03.json`)
- `meals_database.json` - Reusable recipe library (in root)
- `meal_plan.json` - Current/example meal plan (in root)
- `my_config.json` - Custom configuration example

### Build Configuration
- `pyproject.toml` - Project metadata, dependencies, entry point
- Uses `hatchling` as build backend
- Packages only the 4 core `.py` files

## Environment Requirements

- Python >= 3.10
- Dependencies: `todoist-api-python>=2.0.0`
- Environment variable: `TODOIST_API_TOKEN`

## Notes for LLM Integration

The schemas (`meals_database_schema.json` and `meal_plan_schema.json`) are designed to be sent to LLMs for generating meal plans. The README contains detailed prompting guidance for:
- Portion size recommendations (John: 3000kcal, Jane: 1800kcal)
- Ingredient format examples
- Distinction between meal prep and separate cooking sessions
