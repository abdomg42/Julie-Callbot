import React from 'react';
import type { Interaction } from '../../types/dashboard';
import { Clock, AlertTriangle, Activity, BarChart3, TrendingUp } from 'lucide-react';

interface OperationsSectionProps {
  interactions: Interaction[];
}
const ms = (v?: number | null) => (typeof v === "number" ? v : 0);

const OperationsSection: React.FC<OperationsSectionProps> = ({ interactions }) => {
  // Response time distribution
  const responseTimeRanges = {
    'Fast (<1s)': interactions.filter(i => ms(i.execution_time_ms) < 1000).length,
    'Good (1-2s)': interactions.filter(i => ms(i.execution_time_ms) >= 1000 && ms(i.execution_time_ms) < 2000).length,
    'Slow (2-5s)': interactions.filter(i => ms(i.execution_time_ms) >= 2000 && ms(i.execution_time_ms) < 5000).length,
    'Very Slow (>5s)': interactions.filter(i => ms(i.execution_time_ms) >= 5000).length,
  };

  // Handoff reasons analysis
  const handoffReasons = interactions
    .filter(i => i.is_handoff && i.handoff_reason)
    .reduce((acc, interaction) => {
      const reason = interaction.handoff_reason!;
      acc[reason] = (acc[reason] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

  // Peak hours analysis (mock data based on timestamps)
  const hourlyVolume = Array.from({ length: 24 }, (_, hour) => {
    const count = Math.floor(Math.random() * 20) + 5; // Mock data
    return { hour, count };
  });

  // Resolution time by urgency
  const urgencyStats = interactions.reduce((acc, interaction) => {
    if (!acc[interaction.urgency]) {
      acc[interaction.urgency] = { count: 0, totalTime: 0, avgTime: 0 };
    }
    acc[interaction.urgency].count++;
    if (interaction.resolution_time_seconds) {
      acc[interaction.urgency].totalTime += interaction.resolution_time_seconds;
    }
    return acc;
  }, {} as Record<string, { count: number; totalTime: number; avgTime: number }>);

  Object.keys(urgencyStats).forEach(urgency => {
    const stats = urgencyStats[urgency];
    stats.avgTime = stats.count ? stats.totalTime / stats.count : 0;
  });

  // System confidence levels
  const avgConfidence = interactions.reduce((sum, i) => sum + i.confidence, 0) / (interactions.length || 1);
  const confidenceTrend = [
    { period: 'Last Hour', confidence: 0.92 },
    { period: 'Last 4 Hours', confidence: 0.89 },
    { period: 'Last Day', confidence: avgConfidence },
    { period: 'Last Week', confidence: 0.87 },
  ];

  const formatTime = (seconds: number): string => {
    if (!Number.isFinite(seconds) || seconds <= 0) return '—';
    if (seconds < 60) return `${Math.round(seconds)}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
  };

  const badge = (tone: 'green' | 'red' | 'amber' | 'gray' | 'blue') => {
    switch (tone) {
      case 'green':
        return 'bg-positive/10 text-positive border-positive/15';
      case 'red':
        return 'bg-negative/10 text-negative border-negative/15';
      case 'amber':
        return 'bg-caution/12 text-caution border-caution/20';
      case 'blue':
        return 'bg-sky-500/10 text-sky-700 border-sky-500/15';
      default:
        return 'bg-ink-100/70 text-ink-600 border-ink-200/70';
    }
  };

  const getUrgencyTone = (urgency: string) => {
    switch (urgency) {
      case 'critical':
        return badge('red');
      case 'high':
        return badge('amber');
      case 'medium':
        return badge('blue');
      case 'low':
        return badge('green');
      default:
        return badge('gray');
    }
  };

  const getResponseTimeTone = (range: string): string => {
    switch (range) {
      case 'Fast (<1s)':
        return 'bg-positive';
      case 'Good (1-2s)':
        return 'bg-sky-600';
      case 'Slow (2-5s)':
        return 'bg-caution';
      case 'Very Slow (>5s)':
        return 'bg-negative';
      default:
        return 'bg-ink-400';
    }
  };

  const card =
    'bg-white border border-ink-200/70 rounded-2xl shadow-[0_10px_30px_rgba(15,23,42,0.06)]';

  const avgRespSec =
    interactions.length
      ? interactions.reduce((sum, i) => sum + ms(i.execution_time_ms), 0) / interactions.length / 1000
      : 0;

  const totalHandoffs = interactions.filter(i => i.is_handoff).length;
  const peakLoad = Math.max(...hourlyVolume.map(h => h.count));

  return (
    <div className="min-h-screen bg-ink-50">
      <div className="px-8 py-6">
        <div className="mb-8">
          <h1 className="text-display text-ink-900">Operational Performance</h1>
          <p className="text-body text-ink-500 mt-1">
            System efficiency, resource allocation, and performance metrics
          </p>
        </div>

        {/* Key Performance Indicators */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className={`${card} px-6 py-5`}>
            <div className="flex items-start justify-between">
              <span className="text-label text-ink-500 tracking-wide">Avg Response Time</span>
              <div className="h-10 w-10 rounded-2xl bg-sky-500/10 flex items-center justify-center">
                <Clock className="text-sky-700" size={18} />
              </div>
            </div>
            <div className="mt-3 text-3xl font-semibold text-ink-900">
              {avgRespSec.toFixed(2)}s
            </div>
            <p className="text-caption text-ink-500 mt-2">Based on execution_time_ms</p>
          </div>

          <div className={`${card} px-6 py-5`}>
            <div className="flex items-start justify-between">
              <span className="text-label text-ink-500 tracking-wide">System Confidence</span>
              <div className="h-10 w-10 rounded-2xl bg-positive/10 flex items-center justify-center">
                <TrendingUp className="text-positive" size={18} />
              </div>
            </div>
            <div className="mt-3 text-3xl font-semibold text-ink-900">
              {(avgConfidence * 100).toFixed(1)}%
            </div>
            <p className="text-caption text-ink-500 mt-2">Average confidence score</p>
          </div>

          <div className={`${card} px-6 py-5`}>
            <div className="flex items-start justify-between">
              <span className="text-label text-ink-500 tracking-wide">Total Handoffs</span>
              <div className="h-10 w-10 rounded-2xl bg-caution/12 flex items-center justify-center">
                <AlertTriangle className="text-caution" size={18} />
              </div>
            </div>
            <div className="mt-3 text-3xl font-semibold text-ink-900">
              {totalHandoffs}
            </div>
            <p className="text-caption text-ink-500 mt-2">Interactions escalated</p>
          </div>

          <div className={`${card} px-6 py-5`}>
            <div className="flex items-start justify-between">
              <span className="text-label text-ink-500 tracking-wide">Peak Load</span>
              <div className="h-10 w-10 rounded-2xl bg-violet-500/10 flex items-center justify-center">
                <BarChart3 className="text-violet-700" size={18} />
              </div>
            </div>
            <div className="mt-3 text-3xl font-semibold text-ink-900">
              {peakLoad}
            </div>
            <p className="text-caption text-ink-500 mt-2">interactions/hour (mock)</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-8">
          {/* Response Time Distribution */}
          <div className={`${card} px-6 py-5`}>
            <div className="flex items-center gap-3 mb-4">
              <div className="h-10 w-10 rounded-2xl bg-sky-500/10 flex items-center justify-center">
                <Activity className="text-sky-700" size={18} />
              </div>
              <div>
                <h3 className="text-title text-ink-900">Response Time Distribution</h3>
                <p className="text-caption text-ink-500 mt-0.5">Share of interactions by latency</p>
              </div>
            </div>

            <div className="space-y-3">
              {Object.entries(responseTimeRanges).map(([range, count]) => {
                const percentage = interactions.length ? (count / interactions.length) * 100 : 0;
                return (
                  <div key={range} className="flex items-center justify-between gap-4">
                    <div className="flex items-center min-w-0">
                      <div className={`w-2.5 h-2.5 rounded-full mr-3 ${getResponseTimeTone(range)}`} />
                      <span className="text-sm font-semibold text-ink-700 truncate">{range}</span>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="w-28 bg-ink-100 rounded-full h-2 overflow-hidden">
                        <div
                          className={`h-2 rounded-full ${getResponseTimeTone(range)}`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                      <span className="text-sm text-ink-500 w-10 text-right">{count}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Handoff Reasons */}
          <div className={`${card} px-6 py-5`}>
            <div className="flex items-center gap-3 mb-4">
              <div className="h-10 w-10 rounded-2xl bg-caution/12 flex items-center justify-center">
                <AlertTriangle className="text-caution" size={18} />
              </div>
              <div>
                <h3 className="text-title text-ink-900">Handoff Reasons</h3>
                <p className="text-caption text-ink-500 mt-0.5">Top reasons for escalation</p>
              </div>
            </div>

            <div className="space-y-3">
              {Object.entries(handoffReasons)
                .sort(([, a], [, b]) => b - a)
                .map(([reason, count]) => {
                  const total = Object.values(handoffReasons).reduce((a, b) => a + b, 0) || 1;
                  const percentage = (count / total) * 100;

                  return (
                    <div key={reason} className="flex items-center justify-between gap-4">
                      <span className="text-sm font-semibold text-ink-700 capitalize min-w-0 truncate">
                        {reason.replace('_', ' ')}
                      </span>

                      <div className="flex items-center gap-3">
                        <div className="w-28 bg-ink-100 rounded-full h-2 overflow-hidden">
                          <div
                            className="h-2 bg-caution rounded-full"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                        <span className="text-sm text-ink-500 w-10 text-right">{count}</span>
                      </div>
                    </div>
                  );
                })}

              {Object.keys(handoffReasons).length === 0 && (
                <div className="text-sm text-ink-500">No handoff reasons available.</div>
              )}
            </div>
          </div>
        </div>

        {/* Resolution Time by Urgency */}
        <div className={`${card} px-6 py-5 mb-8`}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-title text-ink-900">Resolution Time by Urgency</h3>
              <p className="text-caption text-ink-500 mt-1">Average resolution time per urgency bucket</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(urgencyStats)
              .sort(([a], [b]) => {
                const order = { critical: 0, high: 1, medium: 2, low: 3 };
                return (order as any)[a] - (order as any)[b];
              })
              .map(([urgency, stats]) => (
                <div
                  key={urgency}
                  className="rounded-2xl border border-ink-200/70 bg-white px-5 py-4 hover:shadow-[0_12px_30px_rgba(15,23,42,0.08)] transition-subtle"
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold capitalize ${getUrgencyTone(urgency)}`}>
                      {urgency}
                    </span>
                    <span className="text-sm text-ink-500">{stats.count} tickets</span>
                  </div>

                  <div className="text-xl font-semibold text-ink-900">
                    {formatTime(stats.avgTime)}
                  </div>
                  <p className="text-caption text-ink-500 mt-1">Average resolution time</p>
                </div>
              ))}
          </div>
        </div>

        {/* System Confidence Trend */}
        <div className={`${card} px-6 py-5`}>
          <div className="flex items-center gap-3 mb-4">
            <div className="h-10 w-10 rounded-2xl bg-positive/10 flex items-center justify-center">
              <TrendingUp className="text-positive" size={18} />
            </div>
            <div>
              <h3 className="text-title text-ink-900">System Confidence Trend</h3>
              <p className="text-caption text-ink-500 mt-0.5">Confidence across recent periods</p>
            </div>
          </div>

          <div className="space-y-4">
            {confidenceTrend.map((period) => {
              const confidencePercentage = period.confidence * 100;

              const tone =
                confidencePercentage >= 90 ? 'green' : confidencePercentage >= 80 ? 'amber' : 'red';

              return (
                <div key={period.period} className="flex items-center justify-between gap-4">
                  <span className="text-sm font-medium text-ink-600">{period.period}</span>

                  <div className="flex items-center gap-3">
                    <div className="w-40 bg-ink-100 rounded-full h-2 overflow-hidden">
                      <div
                        className={`h-2 rounded-full ${
                          tone === 'green' ? 'bg-positive' : tone === 'amber' ? 'bg-caution' : 'bg-negative'
                        }`}
                        style={{ width: `${confidencePercentage}%` }}
                      />
                    </div>

                    <span className={`text-sm font-semibold w-14 text-right ${
                      tone === 'green' ? 'text-positive' : tone === 'amber' ? 'text-caution' : 'text-negative'
                    }`}>
                      {confidencePercentage.toFixed(1)}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="h-6" />
      </div>
    </div>
  );
};

export default OperationsSection;
