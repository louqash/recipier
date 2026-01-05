import { MealPlanProvider } from './hooks/useMealPlan.jsx'
import MealsLibrary from './components/MealsLibrary/MealsLibrary'
import CalendarView from './components/Calendar/CalendarView'
import MealConfigModal from './components/MealModal/MealConfigModal'
import ActionBar from './components/ActionBar/ActionBar'
import ShoppingManager from './components/ShoppingManager/ShoppingManager'

function App() {
  return (
    <MealPlanProvider>
      <div className="h-screen flex flex-col bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="px-6 py-4 flex items-center gap-6">
            <h1 className="text-2xl font-bold text-gray-900">
              🍳 Recipier
            </h1>
            <ActionBar />
          </div>
        </header>

        {/* Main Layout */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 flex overflow-hidden">
            {/* Sidebar - Meals Library */}
            <aside className="w-80 flex-shrink-0">
              <MealsLibrary />
            </aside>

            {/* Main Content - Calendar */}
            <main className="flex-1 p-4 overflow-auto">
              <CalendarView />
            </main>
          </div>

          {/* Shopping Manager - Bottom Panel */}
          <ShoppingManager />
        </div>

        {/* Modal */}
        <MealConfigModal />
      </div>
    </MealPlanProvider>
  )
}

export default App
