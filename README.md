# Recipier - Meal Planning to Todoist

A modular Python system for converting meal plans into organized Todoist tasks. Plan your meals with an LLM, then automatically create shopping and cooking tasks with properly categorized ingredients.

## Features

- **Structured meal planning** with JSON schema for LLM consistency
- **Automatic task generation** for shopping, prep, and cooking
- **Ingredient organization** by category (produce, meat, dairy, etc.)
- **Subtasks for ingredients** with labels and descriptions
- **Organized sections** - Shopping, Prep, and Cooking tasks in separate sections
- **Configurable** categories, formatting, and priorities
- **Modular architecture** - use as CLI, MCP server, or web app

## Quick Start

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

### 3. Create Your Meals Database

Create a library of recipes in `meals_database.json` (see `meals_database_schema.json`):
- Each recipe has base ingredient amounts per serving
- Define base serving sizes for each person (e.g., Lukasz: 1.5x, Gaba: 1.0x)

### 4. Create a Meal Plan

Create `meal_plan.json` referencing meals from your database:
- Schedule when to cook each meal
- Specify how many servings per person
- Plan shopping trips

See `meal_plan_schema.json` and example files.

### 5. Generate Tasks

```bash
uv run recipier meal_plan.json meals_database.json
```

Optional: Use a custom configuration file:

```bash
uv run recipier meal_plan.json meals_database.json --config my_config.json
```

## File Structure

```
recipier/
├── meals_database_schema.json  # Schema for meals database
├── meal_plan_schema.json       # Schema for meal plans
├── meals_database.json         # Example meals database
├── meal_plan.json              # Example meal plan
├── config.py                   # Configuration dataclass
├── meal_planner.py             # Core business logic
├── todoist_adapter.py          # Todoist API integration
├── create_meal_tasks.py        # CLI script
└── README.md                   # This file
```

## Architecture

The system is designed to be modular:

### Core Components

1. **`meal_planner.py`** - Platform-independent meal planning logic
   - Generates `Task` objects from meal plan data
   - Handles ingredient grouping and ordering
   - No direct dependency on Todoist

2. **`todoist_adapter.py`** - Todoist-specific integration
   - Converts `Task` objects to Todoist tasks
   - Handles API calls and project management
   - Can be swapped for other task management systems

3. **`config.py`** - Configuration management
   - Customizable categories and display names
   - Formatting options
   - Task priorities

4. **`create_meal_tasks.py`** - CLI interface
   - Command-line tool for standalone use

### Using as a Library

You can import and use the components in your own code:

```python
from meal_planner import MealPlanner
from todoist_adapter import TodoistAdapter
from config import TaskConfig

# Create custom configuration
config = TaskConfig(
    shopping_categories=['produce', 'meat', 'dairy', 'pantry'],
    use_emojis=True,
    use_category_labels=True
)

# Generate tasks
planner = MealPlanner(config=config)
meal_plan = planner.load_meal_plan('my_plan.json')
tasks = planner.generate_all_tasks(meal_plan)

# Create in Todoist
adapter = TodoistAdapter(api_token='your_token', config=config)
adapter.create_tasks(tasks)
```

### For MCP Server

The modular design makes it easy to create an MCP server:

```python
from meal_planner import MealPlanner
from todoist_adapter import TodoistAdapter

# In your MCP server endpoint
def create_meal_tasks_endpoint(meal_plan_json: str, api_token: str):
    planner = MealPlanner()
    meal_plan = planner.parse_meal_plan(meal_plan_json)
    tasks = planner.generate_all_tasks(meal_plan)

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
    api_token = data['api_token']

    planner = MealPlanner()
    tasks = planner.generate_all_tasks(meal_plan)

    adapter = TodoistAdapter(api_token)
    adapter.create_tasks(tasks)

    return jsonify({"success": True, "tasks": len(tasks)})
```

## Configuration

### Default Configuration

The default configuration includes:

- **Categories**: produce, meat, dairy, pantry, frozen, bakery, beverages, other
- **Emojis**: Enabled (🛒 for shopping, 👨‍🍳 for cooking, 🥘 for prep)
- **Labels**: Category labels on ingredient subtasks
- **Format**: `{quantity}{unit} {name}`
- **Priorities**: Shopping (2/high), Prep (2/high), Cooking (3/normal)
- **Sections**: Enabled (Shopping, Prep, Cooking)

### Custom Configuration

Create a JSON file with your preferences:

```json
{
  "shopping_categories": ["produce", "meat", "dairy", "pantry", "other"],
  "use_emojis": true,
  "use_category_labels": true,
  "ingredient_format": "{quantity}{unit} {name}",
  "shopping_priority": 2,
  "prep_priority": 2,
  "cooking_priority": 3,
  "project_name": "Meal Planning",
  "use_sections": true,
  "shopping_section_name": "Shopping",
  "prep_section_name": "Prep",
  "cooking_section_name": "Cooking"
}
```

Then use it:

```bash
python create_meal_tasks.py meal_plan.json --config config.json
```

## Meal Plan Schema

### Required Fields

Each meal plan must have:

- **meals**: Array of meal objects
  - `meal_id`: Unique identifier (e.g., "meal_001")
  - `name`: Meal name
  - `date`: Cooking date (YYYY-MM-DD)
  - `meal_type`: breakfast, lunch, dinner, or snack
  - `assigned_cook`: "Lukasz", "Gaba", or "both"
  - `ingredients`: Array of ingredient objects
    - `name`: Ingredient name
    - `quantity`: Amount
    - `unit`: Unit of measurement
    - `category`: Shopping category
    - `notes` (optional): Additional notes (appears in subtask description)
  - `prep_tasks` (optional): Array of prep task objects
  - `notes` (optional): Meal notes

- **shopping_trips**: Array of shopping trip objects
  - `date`: Shopping date (YYYY-MM-DD)
  - `meal_ids`: Array of meal IDs this trip covers

### Example

See `example_meal_plan.json` for a complete example with 4 meals and 2 shopping trips.

## Task Structure

### Shopping Tasks

- **Title**: 🛒 Shopping for: [Meal Names]
- **Description**: "Shopping list"
- **Due Date**: Shopping trip date
- **Subtasks**: Each ingredient as a subtask (TOTAL amounts)
  - Title: Formatted ingredient (e.g., "400g spaghetti")
  - Description: Ingredient notes if any
  - Label: Category (e.g., "pantry")

### Cooking Tasks

- **Title**: 👨‍🍳 Cook: [Meal Name]
- **Description**: Meal type, date, assigned cook, and meal notes
- **Due Date**: Cooking date
- **Subtasks**: Per-person portions (creates subtasks only for people who eat this meal)
  - Title: "Portion for [Person]"
  - Description: Markdown checklist of ingredients with quantities for that person
  - Example:
    ```
    - [ ] 240g spaghetti
    - [ ] 120g bacon
    - [ ] 2.5 pieces eggs
    ```

### Prep Tasks

- **Title**: 🥘 Prep for [Meal Name]: [Task Description]
- **Description**: Meal name, cooking date, assigned person
- **Due Date**: Calculated from `days_before`

## Tips for LLM Integration

Send the `meal_planning_schema.json` to an LLM with a prompt like:

```
I need you to create a meal plan for me and my fiancée Gaba for the next week.
Please follow this JSON schema exactly: [paste schema]

Important notes about portions:
- Lukasz needs approximately 3000kcal/day (larger portions)
- Gaba needs approximately 1800kcal/day (smaller portions)
- Use a 60:40 ratio (Lukasz:Gaba) or 3:2 as a guideline
- For each ingredient, provide:
  * "quantity" and "unit": TOTAL amount to buy (for shopping)
  * "per_person": breakdown for each person (for cooking portions)

Include:
- 7 dinners (varied cuisine)
- 2 weekend breakfasts
- 2 shopping trips (one mid-week, one weekend)
- Assign cooking duties between "Lukasz" and "Gaba"

Make sure all ingredient quantities are specific and categories are correct.
```

The schema ensures consistent output that can be directly used with this system.

### Example Ingredient Formats

**Both people eat (different portions)**:
```json
{
  "name": "spaghetti",
  "quantity": 400,
  "unit": "g",
  "category": "pantry",
  "per_person": {
    "Lukasz": {"quantity": 240, "unit": "g", "portions": 1},
    "Gaba": {"quantity": 160, "unit": "g", "portions": 1}
  }
}
```
Creates:
- **Shopping**: "400g spaghetti"
- **Cooking**: Two subtasks for Lukasz and Gaba (1 portion each)

**Only one person eats**:
```json
{
  "name": "chicken breast",
  "quantity": 300,
  "unit": "g",
  "category": "meat",
  "per_person": {
    "Lukasz": {"quantity": 300, "unit": "g", "portions": 1}
  }
}
```
Creates:
- **Shopping**: "300g chicken breast"
- **Cooking**: Only one subtask for Lukasz (1 portion)

**Multiple portions - Meal Prep** (cook once, 3 portions):

Meal level:
```json
{
  "name": "Meal Prep Rice Bowls",
  "cooking_dates": ["2026-01-06"]
}
```

Ingredient:
```json
{
  "name": "rice",
  "quantity": 600,
  "unit": "g",
  "category": "pantry",
  "per_person": {
    "Lukasz": {"quantity": 600, "unit": "g", "portions": 3}
  }
}
```

Creates:
- **Shopping**: "600g rice" (total)
- **Cooking** (Jan 6): One task with "600g rice" for all 3 portions

**Multiple portions - Cook Separately** (cook 3 times, 1 portion each):

Meal level:
```json
{
  "name": "Fresh Rice Bowl",
  "cooking_dates": ["2026-01-06", "2026-01-08", "2026-01-10"]
}
```

Ingredient:
```json
{
  "name": "rice",
  "quantity": 600,
  "unit": "g",
  "category": "pantry",
  "per_person": {
    "Lukasz": {"quantity": 600, "unit": "g", "portions": 3}
  }
}
```

Creates:
- **Shopping**: "600g rice" (total)
- **Cooking** (Jan 6): Task with "200g rice" (session 1 of 3)
- **Cooking** (Jan 8): Task with "200g rice" (session 2 of 3)
- **Cooking** (Jan 10): Task with "200g rice" (session 3 of 3)

## License

MIT

## Contributing

This is a personal project, but feel free to fork and adapt for your needs!
