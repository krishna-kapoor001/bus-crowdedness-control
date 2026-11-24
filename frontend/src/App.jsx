import React, { useState, Component } from 'react';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import JourneyPlanner from './pages/JourneyPlanner';
import NetworkExplorer from './pages/NetworkExplorer';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 max-w-xl mx-auto my-12 bg-white rounded-2xl border border-rose-200 shadow-sm text-center">
          <div className="w-12 h-12 rounded-full bg-rose-50 text-rose-600 flex items-center justify-center mx-auto mb-4 font-bold text-xl">
            !
          </div>
          <h2 className="text-lg font-bold text-slate-900 mb-2">Something went wrong</h2>
          <p className="text-sm text-slate-600 mb-6">
            {this.state.error?.message || "An unexpected error occurred while rendering this page."}
          </p>
          <button
            onClick={() => {
              this.setState({ hasError: false, error: null });
              window.location.reload();
            }}
            className="px-4 py-2 bg-slate-900 text-white rounded-lg text-sm font-semibold hover:bg-slate-800 transition-colors"
          >
            Reload Page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  const [activePage, setActivePage] = useState('overview');

  const renderActivePage = () => {
    switch (activePage) {
      case 'overview':
        return <Overview onNavigateToJourney={() => setActivePage('journey-planner')} />;
      case 'journey-planner':
        return <JourneyPlanner />;
      case 'network-explorer':
        return <NetworkExplorer />;
      default:
        return <Overview onNavigateToJourney={() => setActivePage('journey-planner')} />;
    }
  };

  return (
    <div className="min-h-screen bg-[#FBFBFD] flex font-sans">
      {/* Sleek Fixed Sidebar */}
      <Sidebar activePage={activePage} setActivePage={setActivePage} />

      {/* Main Content Area */}
      <div className="flex-1 ml-72 flex flex-col min-h-screen">
        <main className="flex-1">
          <ErrorBoundary>
            {renderActivePage()}
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
}
