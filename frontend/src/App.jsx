import { useState } from 'react'
import { MealPlanProvider, useMealPlan } from './hooks/useMealPlan.jsx'
import MealsLibrary from './components/MealsLibrary/MealsLibrary'
import CalendarView from './components/Calendar/CalendarView'
import MealConfigModal from './components/MealModal/MealConfigModal'
import ActionBar from './components/ActionBar/ActionBar'
import ShoppingManager from './components/ShoppingManager/ShoppingManager'
import Footer from './components/Footer/Footer'
import { useTheme } from './hooks/useTheme.jsx'

function AppContent() {
  const { colors } = useTheme();
  const { fontSize } = useMealPlan();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Map font size to CSS class
  const fontSizeClass = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg'
  }[fontSize] || 'text-base';

  return (
    <div className={`h-screen flex flex-col ${fontSizeClass}`} style={{ backgroundColor: colors.mantle }}>
      {/* Header */}
      <header className="shadow-sm z-30 relative" style={{
        backgroundColor: colors.base,
        borderBottom: `1px solid ${colors.surface0}`
      }}>
        <div className="px-4 md:px-6 py-3 md:py-4 flex items-center gap-4 md:gap-6">
          {/* Mobile Sidebar Toggle */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="md:hidden p-2 -ml-2 rounded-lg"
            style={{ color: colors.text }}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <h1 className="text-xl md:text-2xl font-bold truncate" style={{ color: colors.text }}>
            🍳 Recipier
          </h1>
          <div className="flex-1 min-w-0">
            <ActionBar />
          </div>
        </div>
      </header>

      {/* Main Layout */}
      <div className="flex-1 flex overflow-hidden min-h-0 relative">
        {/* Sidebar - Meals Library */}
        {/* Mobile: Fixed overlay */}
        {/* Desktop: Static sidebar */}
        <div
          className={`
              fixed inset-y-0 left-0 z-40 w-80 shadow-xl transform transition-transform duration-300 ease-in-out md:relative md:translate-x-0 md:shadow-none md:z-0
              ${sidebarOpen ? 'translate-x-0 mt-[65px] md:mt-0' : '-translate-x-full md:translate-x-0'}
            `}
          style={{ backgroundColor: colors.base }}
        >
          <aside className="h-full flex flex-col">
            <MealsLibrary />
          </aside>
        </div>

        {/* Mobile Sidebar Overlay */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-30 bg-black/50 md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Main Content - Calendar and Shopping */}
        <main className="flex-1 flex flex-col overflow-hidden w-full">
          {/* Calendar */}
          <div className="flex-1 p-2 md:p-4 overflow-auto">
            <CalendarView />
          </div>

          {/* Shopping Manager */}
          <ShoppingManager />
        </main>
      </div>

      {/* Footer */}
      <Footer />

      {/* Modal */}
      <MealConfigModal />
    </div>
  );
}

function App() {
  return (
    <MealPlanProvider>
      <AppContent />
    </MealPlanProvider>
  );
}

export default App
