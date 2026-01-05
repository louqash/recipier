# Recipier Web Interface Documentation

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Frontend Components](#frontend-components)
- [Backend API](#backend-api)
- [State Management](#state-management)
- [Localization](#localization)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)

## Overview

The Recipier web interface provides a visual, user-friendly way to create meal plans through drag-and-drop interactions. It consists of:

- **FastAPI Backend**: RESTful API serving meals database and handling task generation
- **React Frontend**: Interactive UI with calendar, meal library, and shopping trip management
- **Shared Business Logic**: 100% reuse of existing Python modules (meal_planner.py, todoist_adapter.py, localization.py)

### Key Features

- **Drag-and-drop meal planning**: Drag meals from library onto calendar dates
- **Visual calendar**: Week/month view with color-coded meal types
- **Meal configuration**: Customize portions, cooking dates, meal types, and assigned cooks
- **Shopping trip management**: Organize meals into shopping trips with click-based interface
- **Bilingual support**: Instant switching between Polish and English
- **Save/Load**: Client-side JSON export/import for meal plans
- **Todoist integration**: Generate tasks directly from the web interface

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend (Port 3000)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ MealsLibrary │  │ CalendarView │  │ShoppingManager│     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │                                │
│                    ┌───────▼────────┐                       │
│                    │  useMealPlan   │ (Context API)         │
│                    │  useTranslation│                       │
│                    └───────┬────────┘                       │
└────────────────────────────┼────────────────────────────────┘
                             │ HTTP (Vite Proxy)
┌────────────────────────────▼────────────────────────────────┐
│                  FastAPI Backend (Port 8000)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ meals.py     │  │meal_plans.py │  │  tasks.py    │     │
│  └──────┬───────┘  └──────────────┘  └──────┬───────┘     │
│         │                                     │             │
│         └─────────────────┬───────────────────┘             │
│                           │                                 │
│                   ┌───────▼────────┐                        │
│                   │ meal_planner.py│ (Existing Logic)       │
│                   │todoist_adapter │                        │
│                   │ localization.py│                        │
│                   └────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Load Meals**: Frontend fetches meals database from `GET /api/meals`
2. **Schedule Meal**: User drags meal to calendar → Opens config modal → Saves to React state
3. **Organize Shopping**: User clicks ➕ on shopping trip → Selects meals from dropdown
4. **Generate Tasks**: Frontend sends meal plan to `POST /api/tasks/generate` → Backend uses meal_planner.py → Tasks created in Todoist

### Technology Stack

**Backend**:
- FastAPI (async Python web framework)
- Pydantic (data validation)
- uvicorn (ASGI server)

**Frontend**:
- React 18 (UI library)
- Vite (build tool, dev server)
- Tailwind CSS (styling)
- FullCalendar (calendar component)
- React Context API (state management)

**Development**:
- CORS enabled for cross-origin requests
- Vite proxy for /api requests
- Hot module replacement (HMR)
- Auto-reload on file changes

## Getting Started

### Prerequisites

- Python >= 3.10
- Node.js >= 18
- Todoist API token (get from https://todoist.com/app/settings/integrations/developer)

### Installation

1. Install Python dependencies:
```bash
uv sync
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

3. Set up environment:
```bash
export TODOIST_API_TOKEN='your_token_here'
```

### Running in Development Mode

**Terminal 1 - Backend**:
```bash
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

Open browser at: http://localhost:3000

### Production Build

```bash
# Build frontend
cd frontend
npm run build

# Run backend (serves frontend static files)
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Open browser at: http://localhost:8000

## Frontend Components

### Component Hierarchy

```
App.jsx
├── MealPlanProvider (Context)
│   ├── ActionBar
│   │   └── SettingsModal
│   ├── Main Layout
│   │   ├── MealsLibrary
│   │   │   └── MealCard (draggable)
│   │   └── CalendarView (FullCalendar)
│   ├── ShoppingManager
│   └── MealConfigModal
```

### Core Components

#### `App.jsx`

Root component that sets up the layout and context providers.

**Location**: `frontend/src/App.jsx`

**Key features**:
- Wraps app in MealPlanProvider
- Defines grid layout (sidebar, main, bottom panel)
- Renders all top-level components
- Manages MealConfigModal visibility

#### `MealsLibrary.jsx`

Sidebar component displaying all available meals from the database.

**Location**: `frontend/src/components/MealsLibrary/MealsLibrary.jsx`

**Key features**:
- Fetches meals from `GET /api/meals`
- Search functionality (filters by meal name)
- Renders draggable MealCard components
- Shows loading and empty states

**State**:
- `meals`: Array of meal objects from database
- `loading`: Boolean for loading state
- `searchQuery`: String for search filter

#### `MealCard.jsx`

Individual meal card component with drag functionality.

**Location**: `frontend/src/components/MealsLibrary/MealCard.jsx`

**Key features**:
- Displays meal name, base servings, ingredient count
- Shows prep indicator if meal requires prep
- Sets `data-meal-data` attribute for drag-and-drop
- CSS class `meal-card` makes it draggable (FullCalendar Draggable)

**Props**:
- `meal`: Meal object from database

**Data format**:
```json
{
  "meal_id": "jajecznica",
  "name": "Jajecznica z warzywami",
  "base_servings": {"Lukasz": 1.5, "Gaba": 1.0},
  "ingredients": [...],
  "prep_tasks": [...]
}
```

#### `CalendarView.jsx`

Main calendar component using FullCalendar library.

**Location**: `frontend/src/components/Calendar/CalendarView.jsx`

**Key features**:
- Week/month view toggle
- Drop zone for meals from MealsLibrary
- Color-coded events by meal type
- Click to edit meal configuration
- Polish/English locale support

**Calendar configuration**:
- `droppable: true` - Accepts external drops
- `drop` handler - Opens MealConfigModal when meal dropped
- `eventClick` handler - Opens MealConfigModal with existing config
- `events` - Transforms scheduledMeals into FullCalendar format

**Event structure**:
```javascript
{
  id: 'meal_id_date_index',
  title: 'Meal Name',
  start: '2026-01-05',
  allDay: true,
  backgroundColor: MEAL_TYPE_COLORS[meal.meal_type],
  extendedProps: {
    mealIndex, meal_id, meal_type, assigned_cook,
    servings_per_person, cooking_dates, session_number
  }
}
```

**Meal type colors**:
- Breakfast: `#fef3c7` (light yellow)
- Second Breakfast: `#dbeafe` (light blue)
- Dinner: `#fecaca` (light red)
- Supper: `#d1fae5` (light green)
- Snack: `#e9d5ff` (light purple)

#### `MealConfigModal.jsx`

Modal for configuring meal details when dropped on calendar.

**Location**: `frontend/src/components/MealConfigModal/MealConfigModal.jsx`

**Key features**:
- Cooking dates selection (multiple dates supported)
- Servings per person (number inputs with +/- buttons)
- Meal type dropdown (breakfast, second_breakfast, dinner, supper)
- Assigned cook selection
- Prep assignment (if meal has prep tasks)
- Validation: portions must equal cooking dates for multi-session meals

**Configuration object**:
```javascript
{
  meal_id: 'jajecznica',
  meal_name: 'Jajecznica z warzywami',
  cooking_dates: ['2026-01-05', '2026-01-07'],
  servings_per_person: {Lukasz: 2, Gaba: 2},
  meal_type: 'breakfast',
  assigned_cook: 'Lukasz'
}
```

**Validation rules**:
- At least one cooking date required
- For multiple cooking dates: `servings_per_person[person] === cooking_dates.length`
- Example: 3 cooking dates → Lukasz: 3 portions, Gaba: 3 portions

#### `ShoppingManager.jsx`

Bottom panel for managing shopping trips.

**Location**: `frontend/src/components/ShoppingManager/ShoppingManager.jsx`

**Key features**:
- Create new shopping trips with date picker
- Add meals to trips via ➕ button (opens dropdown selector)
- Display meals assigned to each trip
- Remove meals from trips
- Delete entire shopping trips

**Shopping trip structure**:
```javascript
{
  shopping_date: '2026-01-04',
  meal_ids: ['jajecznica', 'spaghetti']
}
```

**User interaction**:
1. Click "Add Shopping Trip" → Opens date picker
2. Click ➕ on shopping trip → Opens meal selector dropdown
3. Select meals to add (grayed out if already added)
4. Remove meals with × button

#### `ActionBar.jsx`

Top action bar with save, load, generate tasks, and settings buttons.

**Location**: `frontend/src/components/ActionBar/ActionBar.jsx`

**Key features**:
- **Save button**: Downloads meal plan as JSON file
- **Load button**: Uploads JSON file and loads meal plan
- **Generate Tasks button**: Creates Todoist tasks
- **Language toggle**: Switches between Polish (PL) and English (EN)
- **Settings button**: Opens SettingsModal

**Save functionality**:
- Creates Blob from meal plan JSON
- Downloads with filename `meal-plan-{earliest_date}.json`
- Client-side only (no server interaction)

**Load functionality**:
- Hidden file input with accept=".json"
- Validates JSON structure
- Loads into state via `loadMealPlan()`

**Generate Tasks**:
- Validates Todoist token exists
- Sends POST to `/api/tasks/generate`
- Shows success message with task count
- Displays errors if token missing or API fails

#### `SettingsModal.jsx`

Modal for configuring Todoist API token.

**Location**: `frontend/src/components/Settings/SettingsModal.jsx`

**Key features**:
- Text input for Todoist API token
- Stores token in sessionStorage
- Link to Todoist developer settings
- Save button with confirmation

**Storage**:
```javascript
sessionStorage.setItem('todoist_token', token);
```

## Backend API

### Base URL

Development: `http://localhost:8000`

All endpoints are prefixed with `/api`

### Endpoints

#### `GET /api/meals`

Get all meals from the database.

**Response**:
```json
[
  {
    "meal_id": "jajecznica",
    "name": "Jajecznica z warzywami",
    "base_servings": {"Lukasz": 1.5, "Gaba": 1.0},
    "ingredients": [
      {
        "name": "eggs",
        "quantity": 2,
        "unit": "pcs",
        "category": "dairy"
      }
    ],
    "prep_tasks": []
  }
]
```

**Implementation**: `backend/routers/meals.py`

#### `GET /api/meals/{meal_id}`

Get single meal by ID.

**Parameters**:
- `meal_id` (path): Meal identifier

**Response**: Single meal object (same structure as above)

**Errors**:
- 404 if meal not found

#### `POST /api/tasks/generate`

Generate Todoist tasks from meal plan.

**Request body**:
```json
{
  "meal_plan": {
    "scheduled_meals": [
      {
        "meal_id": "jajecznica",
        "meal_name": "Jajecznica",
        "cooking_dates": ["2026-01-05"],
        "servings_per_person": {"Lukasz": 1, "Gaba": 1},
        "meal_type": "breakfast",
        "assigned_cook": "Lukasz"
      }
    ],
    "shopping_trips": [
      {
        "shopping_date": "2026-01-04",
        "meal_ids": ["jajecznica"]
      }
    ]
  },
  "todoist_token": "your_api_token_here",
  "config": {
    "language": "polish"
  }
}
```

**Response**:
```json
{
  "tasks_created": 3,
  "message": "Successfully created tasks in Todoist"
}
```

**Errors**:
- 400 if meal plan validation fails
- 500 if Todoist API fails

**Implementation**: `backend/routers/tasks.py`

**Process**:
1. Load configuration (from request or my_config.json)
2. Load meals database
3. Expand meal plan (calculate quantities)
4. Generate Task objects via meal_planner.py
5. Create tasks in Todoist via todoist_adapter.py

#### API Models

**Pydantic models** (backend/models/schemas.py):

```python
class MealPlanRequest(BaseModel):
    meal_plan: dict
    todoist_token: str
    config: Optional[dict] = None

class TaskGenerateResponse(BaseModel):
    tasks_created: int
    message: str
```

## State Management

### React Context: `useMealPlan`

Central state management using React Context API.

**Location**: `frontend/src/hooks/useMealPlan.jsx`

### State Variables

```javascript
{
  // Meal plan data
  scheduledMeals: [],      // Array of meal configurations
  shoppingTrips: [],       // Array of shopping trip objects

  // UI state
  configModalOpen: false,  // Boolean for modal visibility
  currentMealData: null,   // Meal object being configured
  currentMealConfig: null, // Existing config (if editing)

  // Settings
  language: 'polish',      // 'polish' or 'english'
  todoistToken: ''         // From sessionStorage
}
```

### Actions

#### Meal Actions

**`addScheduledMeal(mealConfig)`**
- Adds new meal to scheduledMeals array
- Called after user saves MealConfigModal

**`updateScheduledMeal(index, updates)`**
- Updates existing meal at index
- Merges updates with existing config

**`removeScheduledMeal(index)`**
- Removes meal from scheduledMeals
- Used when user deletes a meal

**`findScheduledMeal(mealId, date)`**
- Finds index of meal by ID and date
- Returns -1 if not found

#### Shopping Trip Actions

**`addShoppingTrip(trip)`**
- Adds new shopping trip
- Trip format: `{shopping_date: '2026-01-04', meal_ids: []}`

**`updateShoppingTrip(index, updates)`**
- Updates shopping trip at index

**`removeShoppingTrip(index)`**
- Removes shopping trip

**`addMealToTrip(tripIndex, mealId)`**
- Adds meal_id to shopping trip's meal_ids array
- Prevents duplicates

#### Modal Actions

**`openConfigModal(mealId, date, existingConfig)`**
- Fetches full meal data from API
- Opens modal with initial values
- Async function

**`closeConfigModal()`**
- Closes modal
- Clears currentMealData and currentMealConfig

#### Meal Plan Actions

**`clearMealPlan()`**
- Resets scheduledMeals and shoppingTrips to empty arrays

**`loadMealPlan(mealPlanData)`**
- Loads meal plan from JSON file
- Validates structure

**`getMealPlanJSON()`**
- Returns meal plan as JSON object for saving

#### Settings Actions

**`setLanguage(language)`**
- Sets language ('polish' or 'english')
- Triggers re-render of all localized components

**`updateTodoistToken(token)`**
- Sets token in state
- Saves to sessionStorage

#### Validation

**`validateMealConfig(config)`**
- Validates cooking dates and portions
- Returns `{valid: boolean, errors: string[]}`
- Rules:
  - At least one cooking date
  - For multiple dates: portions must equal dates
  - Portions must be non-negative

### Usage Example

```javascript
import { useMealPlan } from '../hooks/useMealPlan';

function MyComponent() {
  const {
    scheduledMeals,
    addScheduledMeal,
    openConfigModal,
    language
  } = useMealPlan();

  const handleAddMeal = (mealConfig) => {
    addScheduledMeal(mealConfig);
  };

  return (
    <div>
      <p>Meals: {scheduledMeals.length}</p>
      <button onClick={() => openConfigModal('jajecznica', '2026-01-05')}>
        Add Meal
      </button>
    </div>
  );
}
```

## Localization

### Overview

The application supports Polish and English with instant language switching. Translations are managed separately for frontend and backend.

### Frontend Localization

**Translation files**:
- `frontend/src/localization/translations.js` - All translations
- `frontend/src/hooks/useTranslation.js` - Hook for accessing translations

#### Translation Structure

```javascript
export const translations = {
  polish: {
    app_title: 'Recipier',
    save: 'Zapisz',
    load: 'Wczytaj',
    // ... 70+ keys
  },
  english: {
    app_title: 'Recipier',
    save: 'Save',
    load: 'Load',
    // ... 70+ keys
  }
};
```

#### Polish Pluralization

Polish has three plural forms:
1. Singular (1): "1 posiłek"
2. Plural 2-4 (ends in 2-4, not 12-14): "2 posiłki"
3. Many (5+, or 12-14): "5 posiłków"

**Implementation**:
```javascript
export function getMealCountText(language, count) {
  const lang = language === 'english' ? 'english' : 'polish';

  if (lang === 'polish') {
    if (count === 1) return `${count} posiłek`;
    if (count % 10 >= 2 && count % 10 <= 4 &&
        (count % 100 < 10 || count % 100 >= 20)) {
      return `${count} posiłki`;
    }
    return `${count} posiłków`;
  } else {
    return count === 1 ? `${count} meal` : `${count} meals`;
  }
}
```

#### Using Translations

```javascript
import { useTranslation } from '../hooks/useTranslation';

function MyComponent() {
  const { t, mealCount, ingredientCount } = useTranslation();

  return (
    <div>
      <h1>{t('app_title')}</h1>
      <button>{t('save')}</button>
      <p>{mealCount(5)}</p>  {/* "5 posiłków" or "5 meals" */}
      <p>{ingredientCount(3)}</p>  {/* "3 składniki" or "3 ingredients" */}
    </div>
  );
}
```

### Backend Localization

**Location**: `localization.py` (root directory)

Used for:
- CLI prompts in `generate_meal_plan.py`
- Todoist task titles and descriptions

**Configuration**:
```python
from localization import Localizer

loc = Localizer(language='polish')  # or 'english'
print(loc.t('shopping_task_title'))
```

### FullCalendar Localization

Calendar UI is localized using FullCalendar's built-in locale support:

```javascript
import plLocale from '@fullcalendar/core/locales/pl';

<FullCalendar
  locale={language === 'polish' ? plLocale : 'en'}
  // ... other props
/>
```

This localizes:
- Day names (Poniedziałek vs Monday)
- Month names (Styczeń vs January)
- Button labels (Dziś vs Today)

## Development Workflow

### Project Structure

```
recipier/
├── backend/
│   ├── main.py                    # FastAPI app setup
│   ├── routers/
│   │   ├── meals.py               # Meals endpoints
│   │   └── tasks.py               # Task generation
│   └── models/
│       └── schemas.py             # Pydantic models
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── MealsLibrary/
│   │   │   ├── Calendar/
│   │   │   ├── MealConfigModal/
│   │   │   ├── ShoppingManager/
│   │   │   ├── ActionBar/
│   │   │   └── Settings/
│   │   ├── hooks/
│   │   │   ├── useMealPlan.jsx
│   │   │   └── useTranslation.js
│   │   ├── localization/
│   │   │   └── translations.js
│   │   └── api/
│   │       └── client.js          # API client
│   ├── public/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── meal_planner.py                # Core logic (unchanged)
├── todoist_adapter.py             # Todoist API (unchanged)
├── localization.py                # Backend translations
├── meals_database.json
└── my_config.json
```

### Adding a New Component

1. Create component file in `frontend/src/components/`
2. Import `useTranslation` for localized text
3. Import `useMealPlan` for state access
4. Add translations to `translations.js`
5. Import and use in `App.jsx`

Example:
```javascript
// frontend/src/components/NewComponent/NewComponent.jsx
import { useTranslation } from '../../hooks/useTranslation';
import { useMealPlan } from '../../hooks/useMealPlan';

export default function NewComponent() {
  const { t } = useTranslation();
  const { scheduledMeals } = useMealPlan();

  return (
    <div>
      <h2>{t('my_new_component_title')}</h2>
      <p>{scheduledMeals.length}</p>
    </div>
  );
}
```

### Adding a Translation

1. Add key to both Polish and English in `translations.js`:
```javascript
export const translations = {
  polish: {
    my_new_key: 'Mój nowy tekst',
  },
  english: {
    my_new_key: 'My new text',
  }
};
```

2. Use in component:
```javascript
const { t } = useTranslation();
<span>{t('my_new_key')}</span>
```

### Adding a Backend Endpoint

1. Create or update router file in `backend/routers/`
2. Define Pydantic models in `backend/models/schemas.py`
3. Register router in `backend/main.py`
4. Add API client function in `frontend/src/api/client.js`

Example:
```python
# backend/routers/new_router.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/new-endpoint")
async def get_new_data():
    return {"data": "value"}
```

```python
# backend/main.py
from backend.routers import new_router

app.include_router(new_router.router, prefix="/api", tags=["new"])
```

```javascript
// frontend/src/api/client.js
export const newAPI = {
  async getData() {
    const response = await fetch('/api/new-endpoint');
    if (!response.ok) throw new Error('Failed to fetch');
    return response.json();
  }
};
```

### Testing

#### Manual Testing Checklist

- [ ] Drag meal from library to calendar
- [ ] Configure meal (portions, dates, type, cook)
- [ ] Edit existing meal by clicking calendar event
- [ ] Create shopping trip
- [ ] Add meals to shopping trip via ➕ button
- [ ] Remove meals from shopping trip
- [ ] Delete shopping trip
- [ ] Save meal plan (downloads JSON)
- [ ] Load meal plan (uploads JSON)
- [ ] Generate Todoist tasks
- [ ] Switch language (all text changes)
- [ ] Configure Todoist token in settings

#### Testing Multi-Session Meals

1. Drag meal to calendar
2. Add 3 cooking dates
3. Set portions: Lukasz: 3, Gaba: 3
4. Save (should succeed)
5. Try setting portions: Lukasz: 2, Gaba: 2
6. Should show validation error

#### Testing Shopping Trips

1. Create shopping trip for 2026-01-04
2. Schedule 3 meals on different dates
3. Click ➕ on shopping trip
4. Add all 3 meals
5. Verify meals show in shopping trip
6. Try adding same meal again (should be disabled)

### Common Development Tasks

#### Update Meal Type Colors

Edit `CalendarView.jsx`:
```javascript
const MEAL_TYPE_COLORS = {
  breakfast: '#fef3c7',
  // ... add or modify colors
};
```

#### Change Default Language

Edit `useMealPlan.jsx`:
```javascript
const [language, setLanguage] = useState('english'); // Changed from 'polish'
```

#### Modify Task Generation Logic

Edit `meal_planner.py` (existing file) - changes automatically available to web interface via API.

## Troubleshooting

### Frontend Issues

#### "Failed to fetch meals"

**Symptoms**: Empty meals library, console error

**Causes**:
- Backend not running
- CORS misconfiguration
- Vite proxy not working

**Solutions**:
1. Verify backend is running: `curl http://localhost:8000/api/meals`
2. Check Vite proxy in `vite.config.js`:
```javascript
server: {
  proxy: {
    '/api': 'http://localhost:8000'
  }
}
```
3. Check FastAPI CORS config in `backend/main.py`

#### "Drop doesn't work on calendar"

**Symptoms**: Dragging meal to calendar does nothing

**Causes**:
- MealCard missing `data-meal-data` attribute
- FullCalendar droppable not enabled
- JavaScript error preventing modal open

**Solutions**:
1. Verify MealCard has correct attribute:
```jsx
<div data-meal-data={JSON.stringify({meal_id, meal_name})}>
```
2. Check FullCalendar config:
```jsx
<FullCalendar droppable={true} drop={handleDrop} />
```
3. Check browser console for errors

#### "Language doesn't change"

**Symptoms**: Some text doesn't translate

**Causes**:
- Missing translation key
- Component not using `useTranslation`
- Hardcoded strings

**Solutions**:
1. Add missing key to both Polish and English in `translations.js`
2. Import and use hook:
```jsx
const { t } = useTranslation();
<span>{t('my_key')}</span>
```
3. Replace all hardcoded strings with `t()` calls

### Backend Issues

#### "500 Internal Server Error" when generating tasks

**Symptoms**: Generate tasks button fails, 500 error in console

**Causes**:
- Missing meals_database.json
- Invalid meal_id in meal plan
- Todoist API token invalid
- Missing my_config.json

**Solutions**:
1. Verify meals_database.json exists in root directory
2. Check all meal_ids exist in database
3. Test Todoist token:
```bash
curl -X GET https://api.todoist.com/rest/v2/projects \
  -H "Authorization: Bearer YOUR_TOKEN"
```
4. Create my_config.json or use default config

#### "Todoist tasks created but don't appear"

**Symptoms**: Success message but no tasks in Todoist

**Causes**:
- Wrong project ID in config
- User mapping incorrect
- Tasks created in archived project

**Solutions**:
1. Check project ID in my_config.json:
```json
{
  "project_name": "Posiłki"
}
```
2. Verify user_mapping:
```json
{
  "user_mapping": {
    "Lukasz": "lukasz_username",
    "Gaba": "gaba_username"
  }
}
```
3. Check Todoist app for archived projects

#### "Portions must equal cooking dates" error

**Symptoms**: Validation error when saving meal

**Cause**: For multiple cooking dates, portions per person must equal number of dates

**Solution**: If you have 3 cooking dates, set:
- Lukasz: 3 portions
- Gaba: 3 portions

This is by design - each date cooks one fresh portion per person.

### Configuration Issues

#### Todoist Token Not Persisted

**Behavior**: Token disappears after page reload

**Cause**: sessionStorage is cleared on browser close

**Solution**: This is intentional for security. Users must re-enter token each session. To change:

Edit `useMealPlan.jsx` to use localStorage:
```javascript
const [todoistToken, setTodoistToken] = useState(
  localStorage.getItem('todoist_token') || '' // Changed from sessionStorage
);

const updateTodoistToken = useCallback((token) => {
  setTodoistToken(token);
  localStorage.setItem('todoist_token', token); // Changed from sessionStorage
}, []);
```

#### Language Resets to Polish

**Behavior**: Language doesn't persist across sessions

**Cause**: No localStorage persistence

**Solution**: Edit `useMealPlan.jsx`:
```javascript
const [language, setLanguage] = useState(
  localStorage.getItem('language') || 'polish'
);

const handleSetLanguage = useCallback((lang) => {
  setLanguage(lang);
  localStorage.setItem('language', lang);
}, []);
```

### Performance Issues

#### Slow meal library loading

**Cause**: Large meals database

**Solution**: Implement pagination or virtualization
- Use `react-window` for virtual scrolling
- Add pagination to backend endpoint

#### Calendar lags when dragging

**Cause**: Too many events or complex render function

**Solutions**:
1. Simplify `renderEventContent`
2. Use `useMemo` for events array (already implemented)
3. Reduce number of visible weeks

### Data Issues

#### Meal plan won't save

**Cause**: No scheduled meals

**Solution**: Add at least one meal to calendar before saving

#### Loaded meal plan appears empty

**Causes**:
- Invalid JSON format
- Wrong schema version

**Solutions**:
1. Validate JSON structure:
```json
{
  "scheduled_meals": [...],
  "shopping_trips": [...]
}
```
2. Check browser console for parsing errors

## API Reference

See [Backend API](#backend-api) section for endpoint details.

### Quick Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/meals` | Get all meals |
| GET | `/api/meals/{id}` | Get single meal |
| POST | `/api/tasks/generate` | Generate Todoist tasks |

## Contributing

When contributing to the web interface:

1. **Don't modify core Python modules** (meal_planner.py, todoist_adapter.py, localization.py)
2. **Add translations** for both Polish and English
3. **Use existing hooks** (useMealPlan, useTranslation)
4. **Follow naming conventions**:
   - Components: PascalCase
   - Files: Match component name
   - Functions: camelCase
   - CSS classes: Tailwind utilities
5. **Test in both languages**
6. **Document new features** in this file

## Further Reading

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [FullCalendar Documentation](https://fullcalendar.io/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Todoist API Documentation](https://developer.todoist.com/rest/v2/)
