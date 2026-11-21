import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import JourneyPlanner from './pages/JourneyPlanner';
import NetworkExplorer from './pages/NetworkExplorer';
import OperatorAnalytics from './pages/OperatorAnalytics';
import CrowdShift from './pages/CrowdShift';
import Methodology from './pages/Methodology';

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
      case 'operator-analytics':
        return <OperatorAnalytics />;
      case 'crowd-shift':
        return <CrowdShift />;
      case 'methodology':
        return <Methodology />;
      default:
        return <Overview onNavigateToJourney={() => setActivePage('journey-planner')} />;
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex font-sans">
      {/* Sleek Fixed Sidebar */}
      <Sidebar activePage={activePage} setActivePage={setActivePage} />

      {/* Main Content Area */}
      <div className="flex-1 ml-60 flex flex-col min-h-screen">
        <main className="flex-1">
          {renderActivePage()}
        </main>
      </div>
    </div>
  );
}
