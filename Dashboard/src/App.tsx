import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import OverviewSection from './components/sections/OverviewSection';
import AgentPerformanceSection from './components/sections/AgentPerformanceSection';
import ConversationQualitySection from './components/sections/ConversationQualitySection';
import CustomerExperienceSection from './components/sections/CustomerExperienceSection';
import OperationsSection from './components/sections/OperationsSection';
import apiClient from './api/client';
import type { Interaction, DashboardMetrics, AgentPerformance } from './types/dashboard';

function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [dashboardMetrics, setDashboardMetrics] = useState<DashboardMetrics | null>(null);
  const [agentPerformance, setAgentPerformance] = useState<AgentPerformance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch data on component mount and when active tab changes
  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch interactions data
      const interactionsRes = await apiClient.getInteractions(100, 0);
      const interactionsData: Interaction[] =
        (interactionsRes as any)?.items ??
        (interactionsRes as any)?.data?.items ??
        [];

      setInteractions(interactionsData);

      // Fetch summary statistics
      const statsRes = await apiClient.getStatisticsSummary();
      
      // Calculate dashboard metrics from interactions
      const metrics = calculateDashboardMetrics(interactionsData, statsRes);
      setDashboardMetrics(metrics);

      // Calculate agent performance
      const agents = calculateAgentPerformance(interactionsData);
      setAgentPerformance(agents);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateDashboardMetrics = (interactions: Interaction[], stats: any): DashboardMetrics => {
    const total = stats?.total_interactions ?? interactions.length ?? 1;

    const completed =
      stats?.completed_interactions ??
      interactions.filter(i => i.status === 'completed').length;

    const handoffs =
      stats?.total_handoffs ??
      interactions.filter(i => i.is_handoff).length;

    const avgResponseTime =
      stats?.avg_execution_time ??
      (interactions.reduce((sum, i) => sum + (i.execution_time_ms ?? 0), 0) / (interactions.length || 1));

    const feedbackCount = interactions.filter(
      i => i.satisfaction_score === 1 || i.satisfaction_score === 2
    ).length;

    const satisfiedCount = interactions.filter(i => i.satisfaction_score === 1).length;

    const satisfactionRatePct = feedbackCount ? (satisfiedCount / feedbackCount) * 100 : 0;


    // active issues by urgency from the fetched list (best we can do unless we add a backend query)
    const activeIssues = interactions.filter(i => i.status !== 'completed' && i.status !== 'failed');

    return {
      totalInteractions: total,
      successRate: total ? (completed / total) * 100 : 0,
      handoffRate: total ? (handoffs / total) * 100 : 0,
      avgResponseTime: avgResponseTime ?? 0,
      customerSatisfaction: satisfactionRatePct,
      activeIssues: {
        low: activeIssues.filter(i => i.urgency === 'low').length,
        medium: activeIssues.filter(i => i.urgency === 'medium').length,
        high: activeIssues.filter(i => i.urgency === 'high').length,
        critical: activeIssues.filter(i => i.urgency === 'critical').length,
      },
    };
  };



  const calculateAgentPerformance = (interactions: Interaction[]): AgentPerformance[] => {
    const map = new Map<string, Interaction[]>();

    // group by intent (bot capability)
    for (const it of interactions) {
      const key = it.intent || 'unknown_intent';
      const arr = map.get(key) ?? [];
      arr.push(it);
      map.set(key, arr);
    }

    return Array.from(map.entries()).map(([intent, items]) => {
      const total = items.length || 1;

      // "resolution" = successful interactions
      // prefer success boolean if present, fallback to status
      const resolvedCount = items.filter(i =>
        typeof i.success === 'boolean' ? i.success : i.status === 'completed'
      ).length;

      const withTime = items.filter(i => typeof i.resolution_time_seconds === 'number');
      const avgResolutionTime = withTime.length
        ? withTime.reduce((s, i) => s + (i.resolution_time_seconds ?? 0), 0) / withTime.length
        : 0;

      // satisfaction_score: 1 satisfied, 2 unsatisfied
      const feedback = items.filter(i => i.satisfaction_score === 1 || i.satisfaction_score === 2);
      const satisfied = feedback.filter(i => i.satisfaction_score === 1).length;

      const satisfiedRatePct = feedback.length ? (satisfied / feedback.length) * 100 : 0;
      const feedbackRatePct = items.length ? (feedback.length / items.length) * 100 : 0;

      // keep handoff reasons (optional)
      const handoffReasons = items
        .filter(i => i.is_handoff && i.handoff_reason)
        .reduce((acc, i) => {
          const r = i.handoff_reason!;
          acc[r] = (acc[r] || 0) + 1;
          return acc;
        }, {} as Record<string, number>);

      return {
        agent_name: intent, // <- IMPORTANT: agent_name now stores intent
        interactions_handled: items.length,
        resolution_rate: (resolvedCount / total) * 100,
        avg_resolution_time: avgResolutionTime,
        customer_satisfaction: satisfiedRatePct, // keep existing field for compatibility
        satisfied_rate_pct: satisfiedRatePct,
        feedback_rate_pct: feedbackRatePct,
        top_handoff_reasons: Object.entries(handoffReasons)
          .map(([reason, count]) => ({ reason, count }))
          .sort((a, b) => b.count - a.count)
          .slice(0, 3),
      };
    });
  };

  const renderActiveSection = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-ink-500">Loading dashboard data...</div>
        </div>
      );
    }

    if (error) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-negative">Error: {error}</div>
        </div>
      );
    }

    switch (activeTab) {
      case 'overview':
        return dashboardMetrics ? <OverviewSection metrics={dashboardMetrics} /> : null;
      case 'agents':
        return <AgentPerformanceSection agentData={agentPerformance} interactions={interactions} />;
      case 'conversations':
        return <ConversationQualitySection interactions={interactions} />;
      case 'experience':
        return <CustomerExperienceSection interactions={interactions} />;
      case 'operations':
        return <OperationsSection interactions={interactions} />;
      default:
        return dashboardMetrics ? <OverviewSection metrics={dashboardMetrics} /> : null;
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
