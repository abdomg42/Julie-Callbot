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

  const initials = (label: string) => {
    const t = (label || '').trim();
    if (!t) return '—';
    const parts = t.split(/\s+/).slice(0, 2);
    return parts.map(p => p[0]?.toUpperCase()).join('');
  };

  const badge = (tone: 'green' | 'red' | 'gray' | 'blue' | 'amber') => {
    switch (tone) {
      case 'green':
        return 'bg-positive/10 text-positive border-positive/15';
      case 'red':
        return 'bg-negative/10 text-negative border-negative/15';
      case 'blue':
        return 'bg-sky-500/10 text-sky-700 border-sky-500/15';
      case 'amber':
        return 'bg-caution/12 text-caution border-caution/20';
      default:
        return 'bg-ink-100/70 text-ink-600 border-ink-200/70';
    }
  };

  const resolvedBadge = (i: Interaction) => {
    const resolved =
      typeof i.success === 'boolean'
        ? i.success
        : i.status === 'completed'
        ? true
        : null;

    if (resolved === true) return { label: 'Resolved', cls: badge('green') };
    if (resolved === false) return { label: 'Not resolved', cls: badge('red') };
    return { label: '—', cls: badge('gray') };
  };

  const satisfactionBadge = (v: any) => {
    if (v === 1) return { label: 'Satisfied', cls: badge('green') };
    if (v === 2) return { label: 'Unsatisfied', cls: badge('amber') };
    return { label: '—', cls: badge('gray') };
  };

  // empty state to avoid Chart crashing
  if (!agentData || agentData.length === 0) {
    return (
      <div className="min-h-screen bg-ink-50">
        <div className="px-8 py-6">
          <div className="mb-8">
            <h1 className="text-display text-ink-900">Agent Performance</h1>
            <p className="text-body text-ink-500 mt-1">
              No intent metrics yet (need interactions with intent).
            </p>
          </div>

          <div className="bg-white border border-ink-200/70 rounded-2xl px-6 py-6 shadow-[0_10px_30px_rgba(15,23,42,0.06)]">
            <p className="text-ink-700 font-medium">Nothing to show yet.</p>
          </div>
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
          backgroundColor: '#2DD4BF', 
          hoverBackgroundColor: '#0d9488',
          borderRadius: 10,
          borderSkipped: false,
        },
        {
          label: 'Satisfied Rate (%)',
          data: sortedIntents.map(a => Number(a.satisfied_rate_pct ?? a.customer_satisfaction ?? 0)),
          backgroundColor: 'rgba(51, 65, 85, 0.16)',
          hoverBackgroundColor: '#334155',
          borderRadius: 10,
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

  const card =
    'bg-white border border-ink-200/70 rounded-2xl shadow-[0_10px_30px_rgba(15,23,42,0.06)]';

  return (
    <div className="min-h-screen bg-ink-50">
      <div className="px-8 py-6">
        <div className="mb-8">
          <h1 className="text-display text-ink-900">Agent Performance</h1>
          <p className="text-body text-ink-500 mt-1">
            Bot performance by intent (Resolution + Satisfaction)
          </p>
        </div>

        {/* Top intent highlight */}
        {topSummary && (
          <div className={`${card} px-6 py-5 mb-6`}>
            <div className="flex items-start justify-between gap-6">
              <div>
                <p className="text-label text-ink-500 tracking-wide">Best Intent</p>
                <div className="mt-1 text-xl font-semibold text-ink-900">
                  {prettyIntent(topSummary.agent_name)}
                </div>
                <p className="text-caption text-ink-500 mt-1">
                  Resolution: {(topSummary.resolution_rate ?? 0).toFixed(1)}% ·{' '}
                  Satisfied: {(topSummary.satisfied_rate_pct ?? topSummary.customer_satisfaction ?? 0).toFixed(1)}% ·{' '}
                  Feedback: {(topSummary.feedback_rate_pct ?? 0).toFixed(1)}%
                </p>
              </div>

              <div className="h-11 w-11 rounded-2xl bg-positive/10 flex items-center justify-center">
                <CheckCircle className="text-positive" size={20} />
              </div>
            </div>
          </div>
        )}

        {/* ✅ Combined chart */}
        <div className={`${card} px-6 py-5 mb-8`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-2xl bg-ink-100/70 flex items-center justify-center">
                <TrendingUp className="text-ink-700" size={18} />
              </div>
              <div>
                <h3 className="text-title text-ink-900">Resolution + Satisfaction by Intent</h3>
                <p className="text-caption text-ink-500 mt-0.5">Top intents sorted by resolution</p>
              </div>
            </div>
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

        {/* Intent table */}
        <div className={`${card} overflow-hidden mb-8`}>
          <div className="px-6 py-4 border-b border-ink-200/70 bg-ink-50">
            <h3 className="text-title text-ink-900">Intent Leaderboard</h3>
            <p className="text-caption text-ink-500 mt-1">Sorted by resolution rate</p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-ink-50">
                <tr className="border-b border-ink-200/70">
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
                  <tr key={row.agent_name} className="hover:bg-ink-50/70">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-3">
                        <div className="h-9 w-9 rounded-full bg-sky-500/10 text-sky-700 flex items-center justify-center text-xs font-bold">
                          {initials(prettyIntent(row.agent_name))}
                        </div>
                        <div className="font-semibold text-ink-900">
                          {prettyIntent(row.agent_name)}
                        </div>
                      </div>
                    </td>

                    <td className="px-6 py-4 whitespace-nowrap text-ink-600">
                      {row.interactions_handled}
                    </td>

                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${badge('blue')}`}>
                        {(row.resolution_rate ?? 0).toFixed(1)}%
                      </span>
                    </td>

                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${badge('green')}`}>
                        {(row.satisfied_rate_pct ?? row.customer_satisfaction ?? 0).toFixed(1)}%
                      </span>
                    </td>

                    <td className="px-6 py-4 whitespace-nowrap text-ink-600">
                      {(row.feedback_rate_pct ?? 0).toFixed(1)}%
                    </td>

                    <td className="px-6 py-4 whitespace-nowrap text-ink-600">
                      {formatTime(row.avg_resolution_time ?? 0)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/*  Latest conversations (sorted by high resolution + satisfaction) */}
        <div className={`${card} overflow-hidden`}>
          <div className="px-6 py-4 border-b border-ink-200/70 bg-ink-50">
            <h3 className="text-title text-ink-900">Latest Conversations (Best First)</h3>
            <p className="text-caption text-ink-500 mt-1">
              Sorted by satisfied + resolved, then newest
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-ink-50">
                <tr className="border-b border-ink-200/70">
                  <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Time</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Intent</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Resolved</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Satisfaction</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider">Time to Resolve</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-ink-100">
                {latestLeaderboard.map((i) => {
                  const r = resolvedBadge(i);
                  const s = satisfactionBadge(i.satisfaction_score);

                  return (
                    <tr key={i.interaction_id} className="hover:bg-ink-50/70">
                      <td className="px-6 py-4 whitespace-nowrap text-ink-600">
                        {i.created_at ? new Date(i.created_at).toLocaleString() : '—'}
                      </td>

                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-3">
                          <div className="h-9 w-9 rounded-full bg-violet-500/10 text-violet-700 flex items-center justify-center text-xs font-bold">
                            {initials(prettyIntent(i.intent))}
                          </div>
                          <div className="font-semibold text-ink-900">{prettyIntent(i.intent)}</div>
                        </div>
                      </td>

                      <td className="px-6 py-4 whitespace-nowrap text-ink-600">
                        {i.status ?? '—'}
                      </td>

                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${r.cls}`}>
                          {r.label}
                        </span>
                      </td>

                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${s.cls}`}>
                          {s.label}
                        </span>
                      </td>

                      <td className="px-6 py-4 whitespace-nowrap text-ink-600">
                        {formatTime(i.resolution_time_seconds ?? 0)}
                      </td>
                    </tr>
                  );
                })}

                {latestLeaderboard.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-6 py-10 text-ink-500">
                      No interactions loaded.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="h-6" />
      </div>
    </div>
  );
};

export default AgentPerformanceSection;
