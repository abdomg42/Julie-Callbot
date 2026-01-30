import React, { useMemo } from 'react';
import type { AgentPerformance, Interaction } from '../../types/dashboard';
import Chart from '../Chart';
import { CheckCircle, TrendingUp } from 'lucide-react';

interface AgentPerformanceSectionProps {
  agentData: AgentPerformance[];      // now: metrics by intent
  interactions: Interaction[];        // needed for the latest conversations leaderboard
}

const AgentPerformanceSection: React.FC<AgentPerformanceSectionProps> = ({ agentData, interactions }) => {
  const formatTime = (seconds: number): string => {
    if (!Number.isFinite(seconds) || seconds <= 0) return '—';
    if (seconds < 60) return `${Math.round(seconds)}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
  };

  const prettyIntent = (s: string) => (s || 'unknown_intent').replaceAll('_', ' ');

  // empty state to avoid Chart crashing
  if (!agentData || agentData.length === 0) {
    return (
      <div className="px-8 py-6 bg-ink-50 min-h-screen">
        <div className="mb-8">
          <h1 className="text-display text-ink-900">Agent Performance</h1>
          <p className="text-body text-ink-500 mt-1">
            No intent metrics yet (need interactions with intent).
          </p>
        </div>

        <div className="bg-white border border-ink-200 rounded-xl p-6 shadow-sm">
          <p className="text-ink-700 font-medium">Nothing to show yet.</p>
        </div>
      </div>
    );
  }

  // sort intents by resolution rate (desc)
  const sortedIntents = useMemo(() => {
    return [...agentData].sort((a, b) => (b.resolution_rate ?? 0) - (a.resolution_rate ?? 0));
  }, [agentData]);

  const chartLabels = useMemo(
    () => sortedIntents.map(a => prettyIntent(a.agent_name)),
    [sortedIntents]
  );

  // ✅ ONE chart: Resolution + Satisfaction
  const combinedChartData = useMemo(() => {
    return {
      labels: chartLabels,
      datasets: [
        {
          label: 'Resolution Rate (%)',
          data: sortedIntents.map(a => Number(a.resolution_rate ?? 0)),
          backgroundColor: '#e4e4e7',
          hoverBackgroundColor: '#0d9488',
          borderRadius: 6,
          borderSkipped: false,
        },
        {
          label: 'Satisfied Rate (%)',
          data: sortedIntents.map(a => Number(a.satisfied_rate_pct ?? a.customer_satisfaction ?? 0)),
          backgroundColor: '#e2e8f0',
          hoverBackgroundColor: '#334155',
          borderRadius: 6,
          borderSkipped: false,
        },
      ],
    };
  }, [sortedIntents, chartLabels]);

  const topSummary = useMemo(() => sortedIntents[0] ?? null, [sortedIntents]);

  // ✅ Latest conversations leaderboard:
  // sort by: satisfied first, then resolved, then newest
  const latestLeaderboard = useMemo(() => {
    const score = (i: Interaction) => {
      const satisfied = i.satisfaction_score === 1 ? 2 : i.satisfaction_score === 2 ? 0 : 1; // 2 best
      const resolved = (typeof i.success === 'boolean' ? (i.success ? 2 : 0) : i.status === 'completed' ? 2 : 0);
      return satisfied * 10 + resolved;
    };

    return [...(interactions ?? [])]
      .sort((a, b) => {
        const sa = score(a);
        const sb = score(b);
        if (sb !== sa) return sb - sa;

        const da = new Date(a.created_at ?? 0).getTime();
        const db = new Date(b.created_at ?? 0).getTime();
        return db - da;
      })
      .slice(0, 15);
  }, [interactions]);

  const satLabel = (v: any) => {
    if (v === 1) return 'Satisfied';
    if (v === 2) return 'Unsatisfied';
    return '—';
  };

  return (
    <div className="px-8 py-6 bg-ink-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-display text-ink-900">Agent Performance</h1>
        <p className="text-body text-ink-500 mt-1">
          Bot performance by intent (Resolution + Satisfaction)
        </p>
      </div>

      {/* Top intent highlight */}
      {topSummary && (
        <div className="bg-white border border-ink-200 rounded-xl p-5 shadow-sm mb-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-label uppercase text-ink-500 tracking-wide">Best Intent</p>
              <div className="mt-1 text-xl font-semibold text-ink-900">
                {prettyIntent(topSummary.agent_name)}
              </div>
              <p className="text-caption text-ink-500 mt-1">
                Resolution: {(topSummary.resolution_rate ?? 0).toFixed(1)}% ·
                Satisfied: {(topSummary.satisfied_rate_pct ?? topSummary.customer_satisfaction ?? 0).toFixed(1)}% ·
                Feedback: {(topSummary.feedback_rate_pct ?? 0).toFixed(1)}%
              </p>
            </div>
            <div className="w-10 h-10 rounded-full bg-ink-900 flex items-center justify-center">
              <CheckCircle className="text-white" size={20} />
            </div>
          </div>
        </div>
      )}

      {/* ✅ Combined chart */}
      <div className="bg-white border border-ink-200 rounded-xl p-5 shadow-sm mb-8">
        <div className="flex items-center mb-4">
          <TrendingUp className="text-ink-700 mr-2" size={18} />
          <h3 className="text-title text-ink-900">Resolution + Satisfaction by Intent</h3>
        </div>

        <Chart
          type="bar"
          data={combinedChartData}
          className="h-72"
          options={{
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                max: 100,
                ticks: { callback: (v: any) => `${v}%` },
              },
            },
            plugins: {
              legend: { position: 'bottom' },
            },
          }}
        />
      </div>

      {/* Intent table (replaces cards) */}
      <div className="bg-white border border-ink-200 rounded-xl overflow-hidden shadow-sm mb-8">
        <div className="px-6 py-4 border-b border-ink-200 bg-ink-50">
          <h3 className="text-title text-ink-900">Intent Leaderboard</h3>
          <p className="text-caption text-ink-500 mt-1">Sorted by resolution rate</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-white">
              <tr className="border-b border-ink-200">
                <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Intent</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Interactions</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Resolution</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Satisfied</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Feedback</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Avg Time</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-ink-100">
              {sortedIntents.map((row) => (
                <tr key={row.agent_name} className="hover:bg-ink-50">
                  <td className="px-6 py-4 whitespace-nowrap font-medium text-ink-900">
                    {prettyIntent(row.agent_name)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-ink-600">{row.interactions_handled}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-ink-600">{(row.resolution_rate ?? 0).toFixed(1)}%</td>
                  <td className="px-6 py-4 whitespace-nowrap text-ink-600">
                    {(row.satisfied_rate_pct ?? row.customer_satisfaction ?? 0).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-ink-600">{(row.feedback_rate_pct ?? 0).toFixed(1)}%</td>
                  <td className="px-6 py-4 whitespace-nowrap text-ink-600">{formatTime(row.avg_resolution_time ?? 0)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* ✅ Latest conversations (sorted by high resolution + satisfaction) */}
      <div className="bg-white border border-ink-200 rounded-xl overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-ink-200 bg-ink-50">
          <h3 className="text-title text-ink-900">Latest Conversations (Best First)</h3>
          <p className="text-caption text-ink-500 mt-1">
            Sorted by satisfied + resolved, then newest
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-white">
              <tr className="border-b border-ink-200">
                <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Time</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Intent</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Resolved</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Satisfaction</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Time to Resolve</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-ink-100">
              {latestLeaderboard.map((i) => (
                <tr key={i.interaction_id} className="hover:bg-ink-50">
                  <td className="px-6 py-4 whitespace-nowrap text-ink-600">
                    {i.created_at ? new Date(i.created_at).toLocaleString() : '—'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap font-medium text-ink-900">
                    {prettyIntent(i.intent)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-ink-600">{i.status ?? '—'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-ink-600">
                    {typeof i.success === 'boolean' ? (i.success ? 'Yes' : 'No') : (i.status === 'completed' ? 'Yes' : '—')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-ink-600">{satLabel(i.satisfaction_score)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-ink-600">{formatTime(i.resolution_time_seconds ?? 0)}</td>
                </tr>
              ))}

              {latestLeaderboard.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-ink-500">
                    No interactions loaded.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AgentPerformanceSection;
