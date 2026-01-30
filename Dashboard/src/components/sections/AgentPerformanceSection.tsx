import React, { useMemo } from 'react';
import type { AgentPerformance } from '../../types/dashboard';
import Chart from '../Chart';
import { User, CheckCircle, TrendingUp, ThumbsUp, MessageSquare } from 'lucide-react';

interface AgentPerformanceSectionProps {
  agentData: AgentPerformance[];
}

const AgentPerformanceSection: React.FC<AgentPerformanceSectionProps> = ({ agentData }) => {
  const formatTime = (seconds: number): string => {
    if (!Number.isFinite(seconds) || seconds <= 0) return '—';
    if (seconds < 60) return `${Math.round(seconds)}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
  };

  const getPerformanceColor = (rate: number): string => {
    if (rate >= 90) return 'text-emerald-700';
    if (rate >= 75) return 'text-amber-700';
    return 'text-rose-700';
  };

  const getBadge = (rate: number): { label: string; classes: string } => {
    if (rate >= 90) return { label: 'Excellent', classes: 'bg-emerald-50 text-emerald-700 border border-emerald-100' };
    if (rate >= 75) return { label: 'Good', classes: 'bg-amber-50 text-amber-800 border border-amber-100' };
    return { label: 'Needs Attention', classes: 'bg-rose-50 text-rose-700 border border-rose-100' };
  };

  const chartLabels = useMemo(
    () => agentData.map(a => a.agent_name.split(' ')[0]),
    [agentData]
  );

  const resolutionRateData = useMemo(
    () => ({
      labels: chartLabels,
      datasets: [
        {
          label: 'Resolution Rate (%)',
          data: agentData.map(a => a.resolution_rate ?? 0),
          backgroundColor: '#e4e4e7',
          hoverBackgroundColor: '#0d9488',
          borderRadius: 6,
          borderSkipped: false,
        },
      ],
    }),
    [agentData, chartLabels]
  );

  // satisfaction_score based metric
  const satisfactionByAgentData = useMemo(
    () => ({
      labels: chartLabels,
      datasets: [
        {
          label: 'Satisfied (%)',
          data: agentData.map(a => a.satisfied_rate_pct ?? 0),
          backgroundColor: '#e2e8f0',
          hoverBackgroundColor: '#334155',
          borderRadius: 6,
          borderSkipped: false,
        },
      ],
    }),
    [agentData, chartLabels]
  );

  const topSummary = useMemo(() => {
    if (!agentData.length) return null;
    const best = [...agentData].sort((a, b) => (b.resolution_rate ?? 0) - (a.resolution_rate ?? 0))[0];
    return best ?? null;
  }, [agentData]);

  return (
    <div className="px-8 py-6 bg-ink-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-display text-ink-900">Agent Performance</h1>
        <p className="text-body text-ink-500 mt-1">
          Resolution rate + satisfaction_score feedback (Yes/No)
        </p>
      </div>

      {/* Quick highlight */}
      {topSummary && (
        <div className="bg-white border border-ink-200 rounded-xl p-5 shadow-sm mb-8">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-label uppercase text-ink-500 tracking-wide">Top Performer</p>
              <div className="mt-1 text-xl font-semibold text-ink-900">{topSummary.agent_name}</div>
              <p className="text-caption text-ink-500 mt-1">
                Resolution: {topSummary.resolution_rate.toFixed(1)}% · Satisfied: {(topSummary.satisfied_rate_pct ?? 0).toFixed(1)}%
              </p>
            </div>
            <div className="w-10 h-10 rounded-full bg-ink-900 flex items-center justify-center">
              <CheckCircle className="text-white" size={20} />
            </div>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-8">
        <div className="bg-white border border-ink-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center mb-4">
            <TrendingUp className="text-ink-700 mr-2" size={18} />
            <h3 className="text-title text-ink-900">Resolution Rate</h3>
          </div>
          <Chart
            type="bar"
            data={resolutionRateData}
            className="h-64"
            options={{
              scales: {
                y: { beginAtZero: true, max: 100 },
              },
              plugins: {
                legend: { position: 'bottom' },
              },
            }}
          />
        </div>

        <div className="bg-white border border-ink-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center mb-4">
            <ThumbsUp className="text-ink-700 mr-2" size={18} />
            <h3 className="text-title text-ink-900">Satisfied Rate (satisfaction_score)</h3>
          </div>
          <Chart
            type="bar"
            data={satisfactionByAgentData}
            className="h-64"
            options={{
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
      </div>

      {/* Agent cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 mb-8">
        {agentData.map(agent => {
          const badge = getBadge(agent.resolution_rate ?? 0);

          return (
            <div key={agent.agent_name} className="bg-white border border-ink-200 rounded-xl p-5 shadow-sm">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-ink-900 flex items-center justify-center mr-3">
                    <User className="text-white" size={18} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-ink-900">{agent.agent_name}</h3>
                    <span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium ${badge.classes}`}>
                      {badge.label}
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-ink-50 rounded-lg border border-ink-100">
                  <span className="text-sm text-ink-600">Interactions</span>
                  <span className="font-semibold text-ink-900">{agent.interactions_handled}</span>
                </div>

                <div className="flex justify-between items-center p-3 bg-ink-50 rounded-lg border border-ink-100">
                  <span className="text-sm text-ink-600">Resolution Rate</span>
                  <span className={`font-semibold ${getPerformanceColor(agent.resolution_rate ?? 0)}`}>
                    {(agent.resolution_rate ?? 0).toFixed(1)}%
                  </span>
                </div>

                <div className="flex justify-between items-center p-3 bg-ink-50 rounded-lg border border-ink-100">
                  <span className="text-sm text-ink-600">Avg Resolution Time</span>
                  <span className="font-semibold text-ink-900">{formatTime(agent.avg_resolution_time ?? 0)}</span>
                </div>

                <div className="flex justify-between items-center p-3 bg-ink-50 rounded-lg border border-ink-100">
                  <span className="text-sm text-ink-600">Satisfied</span>
                  <span className="font-semibold text-ink-900">
                    {(agent.satisfied_rate_pct ?? 0).toFixed(1)}%
                  </span>
                </div>

                <div className="flex justify-between items-center p-3 bg-ink-50 rounded-lg border border-ink-100">
                  <span className="text-sm text-ink-600">Feedback Coverage</span>
                  <span className="font-semibold text-ink-900">
                    {(agent.feedback_rate_pct ?? 0).toFixed(1)}%
                  </span>
                </div>

                {agent.top_handoff_reasons?.length > 0 && (
                  <div className="pt-3 border-t border-ink-200">
                    <div className="flex items-center mb-2">
                      <MessageSquare className="text-ink-600 mr-2" size={14} />
                      <p className="text-sm font-medium text-ink-700">Top Escalation Reasons</p>
                    </div>
                    <div className="space-y-1.5">
                      {agent.top_handoff_reasons.slice(0, 3).map((r, idx) => (
                        <div key={idx} className="flex justify-between items-center p-2 bg-white rounded border border-ink-200 text-xs">
                          <span className="text-ink-700 capitalize">{r.reason.replaceAll('_', ' ')}</span>
                          <span className="bg-ink-100 text-ink-700 px-2 py-0.5 rounded-full font-medium">
                            {r.count}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Leaderboard */}
      <div className="bg-white border border-ink-200 rounded-xl overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-ink-200 bg-ink-50">
          <h3 className="text-title text-ink-900">Leaderboard</h3>
          <p className="text-caption text-ink-500 mt-1">Sorted by resolution rate</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-white">
              <tr className="border-b border-ink-200">
                <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Agent</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Interactions</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Resolution</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Avg Time</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Satisfied</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Feedback</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-ink-100">
              {[...agentData]
                .sort((a, b) => (b.resolution_rate ?? 0) - (a.resolution_rate ?? 0))
                .map((agent) => (
                  <tr key={agent.agent_name} className="hover:bg-ink-50">
                    <td className="px-6 py-4 whitespace-nowrap font-medium text-ink-900">{agent.agent_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-ink-600">{agent.interactions_handled}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`font-medium ${getPerformanceColor(agent.resolution_rate ?? 0)}`}>
                        {(agent.resolution_rate ?? 0).toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-ink-600">{formatTime(agent.avg_resolution_time ?? 0)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-ink-600">{(agent.satisfied_rate_pct ?? 0).toFixed(1)}%</td>
                    <td className="px-6 py-4 whitespace-nowrap text-ink-600">{(agent.feedback_rate_pct ?? 0).toFixed(1)}%</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Coaching (keep it but make it subtle) */}
      <div className="mt-8 bg-white border border-ink-200 rounded-xl p-6 shadow-sm">
        <div className="flex items-center mb-4">
          <CheckCircle className="text-ink-700 mr-2" size={18} />
          <h3 className="text-title text-ink-900">Coaching Opportunities</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-ink-50 rounded-lg border border-ink-100">
            <h4 className="text-sm font-medium text-ink-900 mb-2">Focus Areas</h4>
            <ul className="text-sm text-ink-600 space-y-1.5">
              <li>Complex issue resolution techniques</li>
              <li>Authentication flow improvements</li>
              <li>De-escalation in first 2 turns</li>
            </ul>
          </div>

          <div className="p-4 bg-ink-50 rounded-lg border border-ink-100">
            <h4 className="text-sm font-medium text-ink-900 mb-2">Best Practices</h4>
            <ul className="text-sm text-ink-600 space-y-1.5">
              <li>Quick acknowledgment of concerns</li>
              <li>Clear next steps + time estimates</li>
              <li>Confirm resolution before closing</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentPerformanceSection;
