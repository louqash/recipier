import { MealPlanProvider } from './hooks/useMealPlan.jsx'
import MealsLibrary from './components/MealsLibrary/MealsLibrary'
import CalendarView from './components/Calendar/CalendarView'
import MealConfigModal from './components/MealModal/MealConfigModal'
import ActionBar from './components/ActionBar/ActionBar'
import ShoppingManager from './components/ShoppingManager/ShoppingManager'
import { useTheme } from './hooks/useTheme.jsx'

function App() {
  const { colors } = useTheme();

  return (
    <MealPlanProvider>
      <div className="h-screen flex flex-col" style={{ backgroundColor: colors.mantle }}>
        {/* Header */}
        <header className="shadow-sm" style={{
          backgroundColor: colors.base,
          borderBottom: `1px solid ${colors.surface0}`
        }}>
          <div className="px-6 py-4 flex items-center gap-6">
            <h1 className="text-2xl font-bold" style={{ color: colors.text }}>
              🍳 Recipier
            </h1>
            <ActionBar />
          </div>
        </header>

        {/* Main Layout */}
        <div className="flex-1 flex overflow-hidden">
          {/* Sidebar - Meals Library (Full Height) */}
          <aside className="w-80 flex-shrink-0 flex flex-col">
            <MealsLibrary />
          </aside>

          {/* Main Content - Calendar and Shopping */}
          <main className="flex-1 flex flex-col overflow-hidden">
            {/* Calendar */}
            <div className="flex-1 p-4 overflow-auto">
              <CalendarView />
            </div>

            {/* Shopping Manager */}
            <ShoppingManager />
          </main>
        </div>

        {/* Modal */}
        <MealConfigModal />
      </div>
    </MealPlanProvider>
  )
}

export default App
