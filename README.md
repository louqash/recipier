# Recipier - Meal Planning to Todoist

A modular meal planning system that converts meal plans into organized Todoist tasks. Available as both a Python CLI tool and a modern web interface. Features a reusable meals database, drag-and-drop meal scheduling, and automatic task creation with personalized portion scaling.

## Features

- **Web Interface & CLI** - Modern drag-and-drop web app + powerful command-line tools
- **Meals Database System** - Store reusable recipes separately from meal scheduling
- **Interactive Planning** - Drag meals onto calendar, configure portions visually
- **Personalized Portion Scaling** - Automatic quantity calculation based on person-specific servings
- **Ingredient-Level Overrides** - Fine-tune portions for specific ingredients
- **Automatic Task Generation** - Creates shopping, prep (per cooking session), and cooking tasks
- **Multi-Language Support** - Polish and English localization (instant switching)
- **Ingredient Organization** - Grouped by category (produce, meat, dairy, etc.)
- **Flexible Cooking Modes** - Meal prep (cook once) or separate cooking sessions
- **Modular Architecture** - Adapter pattern for different task management systems

## Quick Start

### Docker (Easiest)

Run the complete application with Docker:

```bash
# Production mode (single container)
docker build -t recipier .
docker run -d -p 8000:8000 -e TODOIST_API_TOKEN='your_token' recipier

# Or use Docker Compose
export TODOIST_API_TOKEN='your_token'
docker-compose up -d

# Access at http://localhost:8000
```

See [DOCKER.md](./DOCKER.md) for detailed Docker instructions, development setup, and deployment guide.

### Web Interface (Local Development)

The web interface provides a visual, drag-and-drop experience for meal planning:

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Start the backend:**
   ```bash
   uv run recipier-backend
   ```

3. **Start the frontend** (in a new terminal):
   ```bash
   uv run recipier-frontend
   ```

4. **Open** http://localhost:5173

5. **Configure Todoist token:**
   - Click the ⚙️ Settings button
   - Get your token from [Todoist Developer Settings](https://todoist.com/app/settings/integrations/developer)
   - Paste it and save

6. **Plan your meals:**
   - Drag meals from the library onto the calendar
   - Configure portions, dates, and who's cooking
   - Create shopping trips and assign meals to them
   - Click "Generate Tasks" to create everything in Todoist

7. **Switch language:**
   - Click the EN/PL button to toggle between English and Polish
   - All text, including calendar dates, updates instantly

**Features:**
- ✨ Drag-and-drop meal scheduling with unique instance IDs
- 📅 Visual calendar with FullCalendar
- 🗑️ Delete meals from calendar (auto-removes from shopping trips)
- 🛒 Shopping trip management with smart duplicate prevention
- 📆 Smart date handling (new cooking dates default to next day)
- 💾 Save/load meal plans as JSON
- 🌍 Instant language switching (EN/PL)
- 📱 Responsive design
- 🔢 Automatic multipliers in shopping tasks (x2, x3) for multiple cooking sessions

See [Web Interface Documentation](./docs/WEB_INTERFACE.md) for detailed information.

### CLI Tools

### 1. Install Dependencies

```bash
uv sync
```

### 2. Get Todoist API Token

1. Go to [Todoist Settings → Integrations → Developer](https://todoist.com/app/settings/integrations/developer)
2. Copy your API token
3. Set it as an environment variable:

```bash
export TODOIST_API_TOKEN='your_token_here'
```

### 3. Create Meals Database

Create `meals_database.json` with your recipe library (see `meals_database_schema.json`):

```json
{
  "meals": [
    {
      "meal_id": "spaghetti_carbonara",
      "name": "Spaghetti Carbonara",
      "base_servings": {
        "Lukasz": 1.5,
        "Gaba": 1.0
      },
      "ingredients": [
        {
          "name": "spaghetti",
          "quantity": 100,
          "unit": "g",
          "category": "pantry"
        }
      ]
    }
  ]
}
```

**Key Concepts:**
- `base_servings`: Person-specific multipliers (e.g., Lukasz eats 1.5x a standard serving)
- `quantity`: Base amount per **1 serving**
- Recipes are type-agnostic (same recipe can be breakfast, lunch, or dinner)

### 4. Generate Meal Plan Interactively

```bash
uv run recipier-generate
```

This launches an interactive CLI that:
- Shows fuzzy-searchable meal selection from your database
- Guides you through portions, cooking dates, meal types
- Collects shopping trip information
- Saves to `data/YYYY-MM-DD.json` (named by earliest cooking date)
- Optionally creates Todoist tasks immediately

### 5. Or Use Existing Meal Plan

Create `meal_plan.json` manually:

```json
{
  "scheduled_meals": [
    {
      "id": "sm_1735920000000",
      "meal_id": "spaghetti_carbonara",
      "cooking_dates": ["2026-01-06"],
      "servings_per_person": {
        "Lukasz": 2,
        "Gaba": 1
      },
      "meal_type": "dinner",
      "assigned_cook": "Lukasz"
    }
  ],
  "shopping_trips": [
    {
      "shopping_date": "2026-01-05",
      "scheduled_meal_ids": ["sm_1735920000000"]
    }
  ]
}
```

**Schema changes:**
- `scheduled_meals` (not `meals`) - each has unique `id` field (format: `sm_{timestamp}`)
- Shopping trips use `shopping_date` (not `date`) and `scheduled_meal_ids` (not `meal_ids`)
- Meal names inferred from database using `meal_id` (no `meal_name` field needed)

Then generate tasks:

```bash
uv run recipier meal_plan.json meals_database.json
```

## Commands

### `recipier` - Create Tasks from Meal Plan

```bash
# Basic usage
uv run recipier meal_plan.json meals_database.json

# With custom configuration
uv run recipier meal_plan.json meals_database.json --config my_config.json
```

### `recipier-generate` - Interactive Meal Plan Generator

```bash
uv run recipier-generate
```

Features:
- Fuzzy search for meal selection
- Interactive prompts for all meal details
- Meal prep vs. separate cooking selection
- Shopping trip scheduling
- Automatic task creation option

## File Structure

```
recipier/
├── backend/                    # FastAPI backend
│   ├── main.py                # API entry point
│   ├── routers/               # API endpoints
│   │   ├── meals.py           # Meals database API
│   │   ├── meal_plans.py      # Meal plan save/load/validate
│   │   └── tasks.py           # Todoist task generation
│   └── models/                # Pydantic schemas
├── frontend/                   # React + Vite web interface
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── ActionBar/     # Save/Load/Generate buttons
│   │   │   ├── Calendar/      # FullCalendar with drag-drop
│   │   │   ├── MealsLibrary/  # Draggable meal cards
│   │   │   ├── MealModal/     # Meal configuration
│   │   │   ├── ShoppingManager/ # Shopping trips
│   │   │   └── Settings/      # Todoist token config
│   │   ├── hooks/             # React hooks
│   │   │   ├── useMealPlan.jsx  # Central state management
│   │   │   └── useTranslation.js # Localization hook
│   │   ├── localization/      # Frontend translations
│   │   │   └── translations.js
│   │   └── api/               # API client
│   └── package.json
├── data/                       # Generated meal plans
│   └── YYYY-MM-DD.json        # Daily meal plans
├── docs/                       # Documentation
│   └── WEB_INTERFACE.md       # Web interface guide
├── meals_database.json         # Recipe library
├── meals_database_schema.json  # Schema for recipes
├── meal_plan_schema.json       # Schema for meal plans
├── config.py                   # Configuration dataclass
├── localization.py             # Python translations
├── meal_planner.py             # Core business logic
├── todoist_adapter.py          # Todoist API integration
├── create_meal_tasks.py        # CLI for task creation
├── generate_meal_plan.py       # Interactive meal plan generator
└── README.md                   # This file
```

## Architecture

### Adapter Pattern

The codebase uses an adapter pattern to separate business logic from external integrations:

```
meal_planner.py (core logic) → Task objects → todoist_adapter.py (Todoist API)
```

This allows reuse with different task management systems (MCP servers, web apps, Google Tasks, etc.).

### Core Components

**`meal_planner.py`** - Platform-independent meal planning logic
- Defines the `Task` dataclass (platform-agnostic task representation)
- `MealPlanner` class handles:
  - Loading and expanding meal plans with database lookups
  - Calculating ingredient quantities: `base_qty × base_servings × servings_per_person`
  - Generating shopping, prep (per session), and cooking tasks
  - Grouping ingredients by category
  - Dividing ingredients for multiple cooking sessions

**`todoist_adapter.py`** - Todoist-specific integration
- `TodoistAdapter` class converts `Task` objects to Todoist API calls
- Handles project and section management
- Maps user names to Todoist user IDs for task assignment
- Can be swapped for other adapters

**`config.py`** - Configuration management
- `TaskConfig` dataclass for customizable settings
- Shopping categories, emojis, priorities, project/section names
- User mapping for task assignment
- Language setting for localization

**`localization.py`** - Multi-language support
- `Localizer` class for managing translations
- Supports Polish (default) and English
- Translates CLI prompts and Todoist task content

**`create_meal_tasks.py`** - CLI for task creation
- Command-line tool that orchestrates the flow
- Validates environment (API token)
- Displays progress and statistics

**`generate_meal_plan.py`** - Interactive meal plan generator
- Interactive CLI using questionary
- Fuzzy search for meal selection
- Guides through meal details and shopping trips
- Saves to JSON and optionally creates tasks

## Data Flow: Meals Database System

### Two-File Approach

**1. Meals Database** (`meals_database.json`):
- Stores reusable recipes with base ingredient quantities **per serving**
- Defines `base_servings` for each person (meal-level multipliers)
- Recipes are type-agnostic (same recipe can be any meal type)

**2. Meal Plan** (`meal_plan.json` or `data/YYYY-MM-DD.json`):
- References meals by `meal_id` from database (meal names inferred dynamically)
- Each scheduled meal has unique `id` (format: `sm_{timestamp}`) for instance tracking
- Specifies `servings_per_person` (how many servings each person gets)
- Defines `cooking_dates`, `meal_type`, and `assigned_cook`
- Shopping trips reference scheduled meal instances by their unique IDs
- Same recipe can be scheduled multiple times (e.g., Spaghetti Week 1 and Week 3)

### Portion Calculation

```
Final Quantity = base_ingredient_qty × base_servings[person] × servings_per_person[person]
```

**Example:**
- Base recipe: 100g spaghetti per serving
- Lukasz `base_servings`: 1.5 (eats 1.5x standard portion)
- Meal plan `servings_per_person`: 2 (Lukasz gets 2 servings)
- **Result**: 100g × 1.5 × 2 = 300g for Lukasz

### Ingredient-Level Overrides

Use `base_servings_override` to adjust specific ingredients:

```json
{
  "name": "Hummus",
  "quantity": 20,
  "unit": "g",
  "category": "pantry",
  "base_servings_override": {
    "Lukasz": 3.0
  },
  "notes": "Using full 160g package"
}
```

**Why?**
- Use full product packages to avoid waste
- Adjust calories for specific ingredients
- Person-specific preferences

### Multiple Cooking Sessions

**Meal Prep (1 cooking date):**
```json
{
  "cooking_dates": ["2026-01-06"]
}
```
- Cook once for multiple portions
- Shows full quantities in cooking task

**Separate Cooking (multiple dates):**
```json
{
  "cooking_dates": ["2026-01-06", "2026-01-08", "2026-01-10"]
}
```
- Cook separately for each date
- Divides ingredients evenly across sessions
- Creates prep tasks for each cooking session

**Validation:** Total portions must equal number of cooking dates (for multi-session meals)

## Task Generation

### Shopping Tasks

- **Title**: 🛒 Zakupy na: [Meal Names] (Polish) / Shopping for: [Meal Names] (English)
  - Automatically adds multipliers for multiple cooking sessions: "Spaghetti x3, Pizza x2"
  - Counts total cooking sessions across all scheduled meal instances
- **Description**: Lista zakupów / Shopping list
- **Subtasks**: Ingredients grouped by category, showing TOTAL quantities
- **Labels**: Category labels (produce, meat, dairy, etc.)
- **Order**: Categories follow `TaskConfig.shopping_categories` order

**Example titles:**
- Single meal, single session: "🛒 Shopping for: Spaghetti"
- Single meal, multiple sessions: "🛒 Shopping for: Spaghetti x3"
- Multiple meals: "🛒 Shopping for: Spaghetti x2, Pizza, Salad x3"

### Prep Tasks (Per Cooking Session)

- **Title**: 🥘 Przygotowania do [Meal] / Prep for [Meal]
- **Description**:
  - Prep task description
  - Cooking date for this session
- **Due Date**: Calculated from cooking date minus `days_before`
- **Assignment**: Can differ from cook (e.g., one person preps, another cooks)
- **Note**: Creates separate prep task for each cooking date

### Cooking Tasks

- **Title**: 🍳 Gotowanie: [Meal] / Cook: [Meal]
- **Description**:
  - Meal type (Śniadanie/Breakfast, Obiad/Dinner, etc.)
  - Cooking date
  - Portions info
  - Cooking session X of Y (if multiple sessions)
- **Subtasks**: Per-person portions showing individual quantities
  - For meal prep: Full quantities
  - For multiple sessions: Divided quantities

## Configuration

### Default Configuration

```python
TaskConfig(
    shopping_categories=['produce', 'meat', 'dairy', 'pantry', 'frozen', 'bakery', 'beverages', 'other'],
    use_emojis=True,
    use_category_labels=True,
    ingredient_format="{quantity}{unit} {name}",
    shopping_priority=2,  # High
    prep_priority=2,      # High
    cooking_priority=3,   # Normal
    project_name="Meal Planning",
    use_sections=True,
    shopping_section_name="Shopping",
    prep_section_name="Prep",
    cooking_section_name="Cooking",
    user_mapping={},
    language="polish"  # or "english"
)
```

### Custom Configuration

Create a JSON file:

```json
{
  "use_emojis": true,
  "shopping_priority": 2,
  "prep_priority": 2,
  "cooking_priority": 3,
  "project_name": "My Meals",
  "language": "english",
  "user_mapping": {
    "Lukasz": "lukasz_todoist",
    "Gaba": "gaba_todoist"
  }
}
```

Use it:

```bash
uv run recipier meal_plan.json meals_database.json --config config.json
```

### Localization

Set language in config:
- `"language": "polish"` (default)
- `"language": "english"`

Affects:
- CLI prompts in `recipier-generate`
- Todoist task titles and descriptions
- Meal type names

To add a new language:
1. Add translation dictionary to `localization.py`
2. Update `Localizer.__init__()` to support it

## Using as a Library

### Generate and Create Tasks

```python
from meal_planner import MealPlanner
from todoist_adapter import TodoistAdapter
from config import TaskConfig

# Custom configuration
config = TaskConfig(
    language="english",
    use_emojis=True
)

# Load and expand meal plan
planner = MealPlanner(config=config)
meal_plan = planner.load_meal_plan('meal_plan.json', 'meals_database.json')
expanded_plan = planner.expand_meal_plan(meal_plan)

# Generate tasks
tasks = planner.generate_all_tasks(expanded_plan)

# Create in Todoist
adapter = TodoistAdapter(api_token='your_token', config=config)
created_tasks = adapter.create_tasks(tasks)

print(f"Created {len(created_tasks)} tasks")
```

### For MCP Server

```python
from meal_planner import MealPlanner
from todoist_adapter import TodoistAdapter

def create_meal_tasks_endpoint(meal_plan_path: str, database_path: str, api_token: str):
    planner = MealPlanner()
    meal_plan = planner.load_meal_plan(meal_plan_path, database_path)
    expanded_plan = planner.expand_meal_plan(meal_plan)
    tasks = planner.generate_all_tasks(expanded_plan)

    adapter = TodoistAdapter(api_token)
    adapter.create_tasks(tasks)

    return {"status": "success", "tasks_created": len(tasks)}
```

### For Web Interface

```python
from flask import Flask, request, jsonify
from meal_planner import MealPlanner
from todoist_adapter import TodoistAdapter

app = Flask(__name__)

@app.route('/create-tasks', methods=['POST'])
def create_tasks():
    data = request.json
    meal_plan = data['meal_plan']
    meals_database = data['meals_database']
    api_token = data['api_token']

    planner = MealPlanner()
    # Parse JSON directly
    import json
    meal_plan_dict = json.loads(meal_plan)
    meals_db_dict = json.loads(meals_database)

    # Merge databases
    for meal in meal_plan_dict['meals']:
        db_meal = next(m for m in meals_db_dict['meals'] if m['meal_id'] == meal['meal_id'])
        meal.update(db_meal)

    expanded_plan = planner.expand_meal_plan(meal_plan_dict)
    tasks = planner.generate_all_tasks(expanded_plan)

    adapter = TodoistAdapter(api_token)
    adapter.create_tasks(tasks)

    return jsonify({"success": True, "tasks": len(tasks)})
```

## Tips for LLM Integration

The schemas (`meals_database_schema.json` and `meal_plan_schema.json`) are designed for LLM-based meal planning.

### Creating Meals Database with LLM

```
Create recipes for a meals database following this schema: [paste meals_database_schema.json]

Important guidelines:
- Each ingredient quantity is for 1 BASE SERVING
- Set base_servings: Lukasz 1.5, Gaba 1.0 (Lukasz eats 50% more)
- Use ingredient-level base_servings_override when needed:
  * To use full product packages (avoid waste)
  * To adjust specific ingredients for calorie balance
  * For person-specific preferences

Categories: produce, meat, dairy, pantry, frozen, bakery, beverages, other

Include diverse recipes: pasta, rice bowls, stir-fries, salads, breakfasts, etc.
```

### Creating Meal Plans with LLM

```
Create a meal plan for me (Lukasz) and my fiancée Gaba for this week.
Follow this schema: [paste meal_plan_schema.json]

Context:
- Lukasz: ~3000kcal/day (larger portions)
- Gaba: ~1800kcal/day (smaller portions)
- We have these meals in our database: [list meal_ids]

Requirements:
- 7 dinners (varied cuisine)
- 2 weekend breakfasts
- Set servings_per_person based on meal size (typically 1-2 servings)
- Choose meal_type: breakfast, second_breakfast, dinner, supper, or snack
- Assign cooking between "Lukasz" and "Gaba"
- Plan 2 shopping trips (dates: [dates])

For meal prep (cook once for multiple days):
- Use 1 cooking date
- Increase servings_per_person for portions

For separate cooking (cook fresh each time):
- Use multiple cooking dates
- servings_per_person should be 1 or 2

Include prep_tasks if needed (marinades, overnight oats, etc.)
```

## Example: Meal Prep vs. Separate Cooking

### Meal Prep Example (Cook Once, Eat 3 Times)

**In Meals Database:**
```json
{
  "meal_id": "chicken_rice_bowl",
  "name": "Chicken Rice Bowl",
  "base_servings": {
    "Lukasz": 1.5,
    "Gaba": 1.0
  },
  "ingredients": [
    {
      "name": "chicken breast",
      "quantity": 150,
      "unit": "g",
      "category": "meat"
    },
    {
      "name": "rice",
      "quantity": 80,
      "unit": "g",
      "category": "pantry"
    }
  ]
}
```

**In Meal Plan:**
```json
{
  "meal_id": "chicken_rice_bowl",
  "servings_per_person": {
    "Lukasz": 3
  },
  "cooking_dates": ["2026-01-06"],
  "meal_type": "dinner",
  "assigned_cook": "Lukasz"
}
```

**Calculation:**
- Chicken: 150g × 1.5 (base_servings) × 3 (servings_per_person) = **675g**
- Rice: 80g × 1.5 × 3 = **360g**

**Tasks Created:**
- **Shopping**: 675g chicken breast, 360g rice
- **Cooking (Jan 6)**: One task with full quantities for 3 portions

### Separate Cooking Example (Cook Fresh 3 Times)

**In Meal Plan:**
```json
{
  "meal_id": "chicken_rice_bowl",
  "servings_per_person": {
    "Lukasz": 3
  },
  "cooking_dates": ["2026-01-06", "2026-01-08", "2026-01-10"],
  "meal_type": "dinner",
  "assigned_cook": "Lukasz"
}
```

**Tasks Created:**
- **Shopping**: 675g chicken breast, 360g rice (same total)
- **Prep (Jan 5)**: For Jan 6 cooking
- **Cooking (Jan 6)**: 225g chicken, 120g rice (session 1 of 3)
- **Prep (Jan 7)**: For Jan 8 cooking
- **Cooking (Jan 8)**: 225g chicken, 120g rice (session 2 of 3)
- **Prep (Jan 9)**: For Jan 10 cooking
- **Cooking (Jan 10)**: 225g chicken, 120g rice (session 3 of 3)

## License

MIT

## Contributing

This is a personal project, but feel free to fork and adapt for your needs!
