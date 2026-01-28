import { useState } from 'react';
import Sidebar from './components/Sidebar';
import OverviewSection from './components/sections/OverviewSection';
import AgentPerformanceSection from './components/sections/AgentPerformanceSection';
import ConversationQualitySection from './components/sections/ConversationQualitySection';
import CustomerExperienceSection from './components/sections/CustomerExperienceSection';
import OperationsSection from './components/sections/OperationsSection';
import { mockInteractions, calculateDashboardMetrics, calculateAgentPerformance } from './data/mockData';

function App() {
  const [activeTab, setActiveTab] = useState('overview');

  // Calculate data for dashboard
  const dashboardMetrics = calculateDashboardMetrics(mockInteractions);
  const agentPerformance = calculateAgentPerformance(mockInteractions);

  const renderActiveSection = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewSection metrics={dashboardMetrics} />;
      case 'agents':
        return <AgentPerformanceSection agentData={agentPerformance} />;
      case 'conversations':
        return <ConversationQualitySection interactions={mockInteractions} />;
      case 'experience':
        return <CustomerExperienceSection interactions={mockInteractions} />;
      case 'operations':
        return <OperationsSection interactions={mockInteractions} />;
      default:
        return <OverviewSection metrics={dashboardMetrics} />;
    }
  };

  return (
    <div className="flex h-screen w-screen bg-ink-50">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="flex-1 overflow-y-auto">
        {renderActiveSection()}
      </main>
    </div>
  );
}

export default App;
