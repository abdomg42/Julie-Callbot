import React, { useEffect, useMemo, useState } from 'react';
import type { Interaction } from '../../types/dashboard';
import apiClient from '../../api/client';
import Chart from '../Chart';
import { Heart, TrendingUp, MessageCircle, Mail, Phone, MessageSquare } from 'lucide-react';

interface CustomerExperienceSectionProps {
  interactions: Interaction[];
}

/**
 * satisfaction_score:
 * 1 = satisfied (Oui)
 * 2 = unsatisfied (Non)
 * null/undefined = no feedback
 */
type SatisfactionStatsRow = {
  date: string;
  total_interactions: number;
  feedbacks_collected: number;
  satisfied_count: number;
  unsatisfied_count: number;
  satisfaction_rate_pct: number; // 0..100
  feedback_collection_rate_pct: number; // 0..100
};

type SatisfactionByIntentRow = {
  intent: string;
  total_with_feedback: number;
  satisfied: number;
  unsatisfied: number;
  satisfaction_rate_pct: number; // 0..100
  status?: string;
};

const safeNum = (v: unknown, fallback = 0) => (typeof v === 'number' && Number.isFinite(v) ? v : fallback);
const safeStr = (v: unknown, fallback = '') => (typeof v === 'string' ? v : fallback);

const CustomerExperienceSection: React.FC<CustomerExperienceSectionProps> = ({ interactions }) => {
  const [trendRows, setTrendRows] = useState<SatisfactionStatsRow[]>([]);
  const [byIntentRows, setByIntentRows] = useState<SatisfactionByIntentRow[]>([]);
  const [loading, setLoading] = useState(true);

  // Emotion distribution (from interactions)
  const emotionCounts = useMemo(() => {
    return interactions.reduce((acc, interaction) => {
      const key = interaction.emotion ?? 'neutral';
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
  }, [interactions]);

  const totalInteractions = interactions.length;

  // Fallback stats from interactions (no API)
  const fallbackSatisfaction = useMemo(() => {
    const withFeedback = interactions.filter(i => i.satisfaction_score === 1 || i.satisfaction_score === 2);
    const satisfied = withFeedback.filter(i => i.satisfaction_score === 1).length;
    const unsatisfied = withFeedback.filter(i => i.satisfaction_score === 2).length;
    const total = withFeedback.length;

    return {
      total,
      satisfied,
      unsatisfied,
      satisfactionRate: total ? (satisfied / total) * 100 : 0,
      feedbackRate: interactions.length ? (total / interactions.length) * 100 : 0,
    };
  }, [interactions]);

  // Load trend + by-intent from API (optional). If fails, falls back silently.
  useEffect(() => {
    let mounted = true;

    const load = async () => {
      setLoading(true);
      try {
        // These must exist in api client or will be undefined (safe)
        const trendRes = (apiClient as any).getSatisfactionStats
          ? await (apiClient as any).getSatisfactionStats(30)
          : null;

        const intentRes = (apiClient as any).getSatisfactionByIntent
          ? await (apiClient as any).getSatisfactionByIntent()
          : null;

        const tItems = (trendRes as any)?.items ?? (trendRes as any)?.data?.items ?? trendRes ?? [];
        const iItems = (intentRes as any)?.items ?? (intentRes as any)?.data?.items ?? intentRes ?? [];

        const trendSafe: SatisfactionStatsRow[] = Array.isArray(tItems)
          ? tItems.map((r: any) => ({
              date: safeStr(r?.date),
              total_interactions: safeNum(r?.total_interactions),
              feedbacks_collected: safeNum(r?.feedbacks_collected),
              satisfied_count: safeNum(r?.satisfied_count),
              unsatisfied_count: safeNum(r?.unsatisfied_count),
              satisfaction_rate_pct: safeNum(r?.satisfaction_rate_pct),
              feedback_collection_rate_pct: safeNum(r?.feedback_collection_rate_pct),
            }))
          : [];

        const intentSafe: SatisfactionByIntentRow[] = Array.isArray(iItems)
          ? iItems.map((r: any) => ({
              intent: safeStr(r?.intent),
              total_with_feedback: safeNum(r?.total_with_feedback),
              satisfied: safeNum(r?.satisfied),
              unsatisfied: safeNum(r?.unsatisfied),
              satisfaction_rate_pct: safeNum(r?.satisfaction_rate_pct),
              status: typeof r?.status === 'string' ? r.status : undefined,
            }))
          : [];

        if (mounted) {
          setTrendRows(trendSafe);
          setByIntentRows(intentSafe);
        }
      } catch {
        if (mounted) {
          setTrendRows([]);
          setByIntentRows([]);
        }
      } finally {
        if (mounted) setLoading(false);
      }
    };

    load();
    return () => {
      mounted = false;
    };
  }, []);

  const getEmotionColor = (emotion: string): string => {
    switch (emotion) {
      case 'positive':
      case 'satisfied':
        return 'bg-emerald-500';
      case 'neutral':
        return 'bg-slate-400';
      case 'frustrated':
        return 'bg-amber-500';
      case 'negative':
        return 'bg-rose-500';
      default:
        return 'bg-slate-400';
    }
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'chat':
        return MessageSquare;
      case 'phone':
        return Phone;
      case 'email':
        return Mail;
      case 'sms':
        return MessageCircle;
      default:
        return MessageSquare;
    }
  };

  // Trend: API first, fallback if empty
  const trend = useMemo(() => {
    if (trendRows.length) {
      // show last 14 (and reverse to chronological)
      const sliced = [...trendRows].slice(0, 14).reverse();
      return sliced.map(r => {
        let label = r.date;
        try {
          label = new Date(r.date).toLocaleDateString(undefined, { month: 'short', day: '2-digit' });
        } catch {
          // keep raw date
        }
        return {
          label,
          satisfaction: safeNum(r.satisfaction_rate_pct),
          feedbackRate: safeNum(r.feedback_collection_rate_pct),
        };
      });
    }

    // fallback: use real computed values (not random/mock)
    return [
      { label: 'W1', satisfaction: fallbackSatisfaction.satisfactionRate, feedbackRate: fallbackSatisfaction.feedbackRate },
      { label: 'W2', satisfaction: fallbackSatisfaction.satisfactionRate, feedbackRate: fallbackSatisfaction.feedbackRate },
      { label: 'W3', satisfaction: fallbackSatisfaction.satisfactionRate, feedbackRate: fallbackSatisfaction.feedbackRate },
      { label: 'W4', satisfaction: fallbackSatisfaction.satisfactionRate, feedbackRate: fallbackSatisfaction.feedbackRate },
    ];
  }, [trendRows, fallbackSatisfaction]);

  const satisfactionTrendData = useMemo(() => {
    return {
      labels: trend.map(t => t.label),
      datasets: [
        {
          label: 'Satisfaction Rate (%)',
          data: trend.map(t => t.satisfaction),
          borderColor: '#0d9488',
          backgroundColor: 'rgba(13, 148, 136, 0.10)',
          borderWidth: 2,
          fill: true,
          tension: 0.35,
          pointRadius: 3,
          pointBackgroundColor: '#0d9488',
        },
        {
          label: 'Feedback Collected (%)',
          data: trend.map(t => t.feedbackRate),
          borderColor: '#334155',
          backgroundColor: 'rgba(51, 65, 85, 0.06)',
          borderWidth: 2,
          fill: false,
          tension: 0.35,
          pointRadius: 2,
          pointBackgroundColor: '#334155',
        },
      ],
    };
  }, [trend]);

  // Channel feedback performance from interactions
  const channelFeedback = useMemo(() => {
    const acc: Record<string, { total: number; feedback: number; satisfied: number; unsatisfied: number }> = {};
    for (const i of interactions) {
      const ch = i.channel;
      acc[ch] ??= { total: 0, feedback: 0, satisfied: 0, unsatisfied: 0 };
      acc[ch].total++;

      const score = i.satisfaction_score;
      if (score === 1 || score === 2) {
        acc[ch].feedback++;
        if (score === 1) acc[ch].satisfied++;
        if (score === 2) acc[ch].unsatisfied++;
      }
    }
    return acc;
  }, [interactions]);

  // Intent table: API first, fallback compute
  const intentTable = useMemo(() => {
    if (byIntentRows.length) return byIntentRows;

    const acc: Record<string, { intent: string; total_with_feedback: number; satisfied: number; unsatisfied: number }> = {};
    for (const i of interactions) {
      const score = i.satisfaction_score;
      if (score !== 1 && score !== 2) continue;

      const key = i.intent ?? 'unknown';
      acc[key] ??= { intent: key, total_with_feedback: 0, satisfied: 0, unsatisfied: 0 };
      acc[key].total_with_feedback++;
      if (score === 1) acc[key].satisfied++;
      if (score === 2) acc[key].unsatisfied++;
    }

    return Object.values(acc)
      .map(r => {
        const rate = r.total_with_feedback ? (r.satisfied / r.total_with_feedback) * 100 : 0;
        return {
          ...r,
          satisfaction_rate_pct: rate,
          status: rate >= 80 ? '✅ Excellent' : rate >= 60 ? '⚠️ Acceptable' : '❌ Needs work',
        };
      })
      .sort((a, b) => a.satisfaction_rate_pct - b.satisfaction_rate_pct);
  }, [byIntentRows, interactions]);

  const overallSatisfactionRate = trendRows.length
    ? safeNum(trendRows[trendRows.length - 1]?.satisfaction_rate_pct, 0)
    : fallbackSatisfaction.satisfactionRate;

  const overallFeedbackRate = trendRows.length
    ? safeNum(trendRows[trendRows.length - 1]?.feedback_collection_rate_pct, 0)
    : fallbackSatisfaction.feedbackRate;

  return (
    <div className="px-8 py-6 bg-ink-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-display text-ink-900">Customer Experience</h1>
        <p className="text-body text-ink-500 mt-1">Satisfaction, sentiment, and feedback quality signals</p>
      </div>

      {/* Top KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white border border-ink-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-label uppercase text-ink-500 tracking-wide">Satisfaction Rate</span>
            <TrendingUp className="text-ink-600" size={18} />
          </div>
          <div className="mt-2 text-2xl font-semibold text-ink-900">{overallSatisfactionRate.toFixed(1)}%</div>
          <p className="text-caption text-ink-500 mt-1">Based on satisfaction_score (1/2)</p>
        </div>

        <div className="bg-white border border-ink-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-label uppercase text-ink-500 tracking-wide">Feedback Collected</span>
            <Heart className="text-ink-600" size={18} />
          </div>
          <div className="mt-2 text-2xl font-semibold text-ink-900">{overallFeedbackRate.toFixed(1)}%</div>
          <p className="text-caption text-ink-500 mt-1">Percent of interactions with feedback</p>
        </div>

        <div className="bg-white border border-ink-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-label uppercase text-ink-500 tracking-wide">Total Interactions</span>
            <MessageSquare className="text-ink-600" size={18} />
          </div>
          <div className="mt-2 text-2xl font-semibold text-ink-900">{totalInteractions.toLocaleString()}</div>
          <p className="text-caption text-ink-500 mt-1">From current loaded dataset</p>
        </div>
      </div>

      {/* Emotion + Trend */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
        <div className="lg:col-span-1 bg-white border border-ink-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center mb-4">
            <Heart className="text-ink-700 mr-2" size={18} />
            <h3 className="text-title text-ink-900">Emotion Distribution</h3>
          </div>

          <div className="space-y-3">
            {Object.entries(emotionCounts).map(([emotion, count]) => {
              const percentage = totalInteractions ? (count / totalInteractions) * 100 : 0;
              return (
                <div key={emotion} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-2.5 h-2.5 rounded-full mr-3 ${getEmotionColor(emotion)}`} />
                    <span className="text-sm font-medium text-ink-700 capitalize">{emotion}</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-28 bg-ink-100 rounded-full h-2 mr-3">
                      <div className={`h-2 rounded-full ${getEmotionColor(emotion)}`} style={{ width: `${percentage}%` }} />
                    </div>
                    <span className="text-sm text-ink-500 w-10 text-right">{count}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="lg:col-span-2 bg-white border border-ink-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-title text-ink-900">Satisfaction Trend</h3>
            <span className="text-caption text-ink-500">{loading ? 'Loading…' : 'Last days'}</span>
          </div>

          <Chart
            type="line"
            data={satisfactionTrendData as any}
            className="h-64"
            options={
              {
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
              } as any
            }
          />
        </div>
      </div>

      {/* Channel Performance */}
      <div className="bg-white border border-ink-200 rounded-xl p-5 shadow-sm mb-8">
        <h3 className="text-title text-ink-900 mb-4">Channel Feedback Performance</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(channelFeedback).map(([channel, stats]) => {
            const Icon = getChannelIcon(channel);
            const satRate = stats.feedback ? (stats.satisfied / stats.feedback) * 100 : 0;

            return (
              <div key={channel} className="p-4 border border-ink-200 rounded-lg">
                <div className="flex items-center mb-2">
                  <Icon className="text-ink-700 mr-2" size={16} />
                  <span className="font-medium text-ink-900 capitalize">{channel}</span>
                </div>

                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-ink-500">Interactions</span>
                    <span className="font-medium text-ink-900">{stats.total}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-ink-500">Feedbacks</span>
                    <span className="font-medium text-ink-900">{stats.feedback}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-ink-500">Satisfaction</span>
                    <span className="font-medium text-ink-900">{satRate.toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Satisfaction by Intent */}
      <div className="bg-white border border-ink-200 rounded-xl p-5 shadow-sm mb-8">
        <h3 className="text-title text-ink-900 mb-4">Satisfaction by Intent</h3>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-ink-200">
                <th className="text-left py-3 px-4 font-medium text-ink-700">Intent</th>
                <th className="text-left py-3 px-4 font-medium text-ink-700">Feedback Volume</th>
                <th className="text-left py-3 px-4 font-medium text-ink-700">Satisfied</th>
                <th className="text-left py-3 px-4 font-medium text-ink-700">Unsatisfied</th>
                <th className="text-left py-3 px-4 font-medium text-ink-700">Satisfaction</th>
                <th className="text-left py-3 px-4 font-medium text-ink-700">Status</th>
              </tr>
            </thead>

            <tbody>
              {intentTable.map(row => {
                const rate = safeNum((row as any).satisfaction_rate_pct, 0);
                const color = rate >= 80 ? 'text-emerald-700' : rate >= 60 ? 'text-amber-700' : 'text-rose-700';

                return (
                  <tr key={row.intent} className="border-b border-ink-100 hover:bg-ink-50">
                    <td className="py-3 px-4">
                      <span className="font-medium text-ink-900 capitalize">{row.intent.replace(/_/g, ' ')}</span>
                    </td>
                    <td className="py-3 px-4 text-ink-600">{(row as any).total_with_feedback}</td>
                    <td className="py-3 px-4 text-ink-600">{(row as any).satisfied}</td>
                    <td className="py-3 px-4 text-ink-600">{(row as any).unsatisfied}</td>
                    <td className="py-3 px-4">
                      <span className={`font-medium ${color}`}>{rate.toFixed(1)}%</span>
                    </td>
                    <td className="py-3 px-4 text-ink-600">{(row as any).status ?? '—'}</td>
                  </tr>
                );
              })}

              {!intentTable.length && (
                <tr>
                  <td className="py-6 px-4 text-ink-500" colSpan={6}>
                    No satisfaction feedback yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Feedback Highlights */}
      <div className="bg-white border border-ink-200 rounded-xl p-5 shadow-sm">
        <h3 className="text-title text-ink-900 mb-4">Feedback Highlights</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-emerald-700 mb-3">Satisfied</h4>
            <div className="space-y-2">
              {interactions
                .filter(i => i.satisfaction_score === 1 && i.feedback_comment)
                .slice(0, 3)
                .map((interaction, idx) => (
                  <div key={idx} className="p-3 bg-emerald-50 rounded border border-emerald-100">
                    <p className="text-sm text-ink-800">"{interaction.feedback_comment}"</p>
                    <p className="text-xs text-emerald-700 mt-1">Feedback: Satisfied (1)</p>
                  </div>
                ))}

              {!interactions.some(i => i.satisfaction_score === 1 && i.feedback_comment) && (
                <p className="text-sm text-ink-500">No satisfied feedback comments yet.</p>
              )}
            </div>
          </div>

          <div>
            <h4 className="font-medium text-rose-700 mb-3">Unsatisfied</h4>
            <div className="space-y-2">
              {interactions
                .filter(i => i.satisfaction_score === 2 && i.feedback_comment)
                .slice(0, 3)
                .map((interaction, idx) => (
                  <div key={idx} className="p-3 bg-rose-50 rounded border border-rose-100">
                    <p className="text-sm text-ink-800">"{interaction.feedback_comment}"</p>
                    <p className="text-xs text-rose-700 mt-1">Feedback: Unsatisfied (2)</p>
                  </div>
                ))}

              {!interactions.some(i => i.satisfaction_score === 2 && i.feedback_comment) && (
                <p className="text-sm text-ink-500">No unsatisfied feedback comments yet.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomerExperienceSection;
