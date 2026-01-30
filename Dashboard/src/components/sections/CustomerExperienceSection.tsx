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

  const card =
    'bg-white border border-ink-200/70 rounded-2xl shadow-[0_10px_30px_rgba(15,23,42,0.06)]';

  const badge = (tone: 'green' | 'red' | 'gray' | 'amber' | 'blue') => {
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
          status: rate >= 80 ? 'Excellent' : rate >= 60 ? 'Acceptable' : 'Needs work',
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
    <div className="min-h-screen bg-ink-50">
      <div className="px-8 py-6">
        <div className="mb-8">
          <h1 className="text-display text-ink-900">Customer Experience</h1>
          <p className="text-body text-ink-500 mt-1">
            Satisfaction, sentiment, and feedback quality signals
          </p>
        </div>

        {/* Top KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className={`${card} px-6 py-5`}>
            <div className="flex items-start justify-between">
              <span className="text-label text-ink-500 tracking-wide">Satisfaction Rate</span>
              <div className="h-10 w-10 rounded-2xl bg-emerald-500/10 flex items-center justify-center">
                <TrendingUp className="text-emerald-700" size={18} />
              </div>
            </div>
            <div className="mt-3 text-3xl font-semibold text-ink-900">{overallSatisfactionRate.toFixed(1)}%</div>
            <p className="text-caption text-ink-500 mt-2">Based on satisfaction_score (1/2)</p>
          </div>

          <div className={`${card} px-6 py-5`}>
            <div className="flex items-start justify-between">
              <span className="text-label text-ink-500 tracking-wide">Feedback Collected</span>
              <div className="h-10 w-10 rounded-2xl bg-rose-500/10 flex items-center justify-center">
                <Heart className="text-rose-700" size={18} />
              </div>
            </div>
            <div className="mt-3 text-3xl font-semibold text-ink-900">{overallFeedbackRate.toFixed(1)}%</div>
            <p className="text-caption text-ink-500 mt-2">Percent of interactions with feedback</p>
          </div>

          <div className={`${card} px-6 py-5`}>
            <div className="flex items-start justify-between">
              <span className="text-label text-ink-500 tracking-wide">Total Interactions</span>
              <div className="h-10 w-10 rounded-2xl bg-sky-500/10 flex items-center justify-center">
                <MessageSquare className="text-sky-700" size={18} />
              </div>
            </div>
            <div className="mt-3 text-3xl font-semibold text-ink-900">{totalInteractions.toLocaleString()}</div>
            <p className="text-caption text-ink-500 mt-2">From current loaded dataset</p>
          </div>
        </div>

        {/* Emotion + Trend */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
          <div className={`lg:col-span-1 ${card} px-6 py-5`}>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-2xl bg-rose-500/10 flex items-center justify-center">
                  <Heart className="text-rose-700" size={18} />
                </div>
                <div>
                  <h3 className="text-title text-ink-900">Emotion Distribution</h3>
                  <p className="text-caption text-ink-500 mt-0.5">From detected emotions</p>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              {Object.entries(emotionCounts).map(([emotion, count]) => {
                const percentage = totalInteractions ? (count / totalInteractions) * 100 : 0;
                return (
                  <div key={emotion} className="flex items-center justify-between gap-3">
                    <div className="flex items-center min-w-0">
                      <div className={`w-2.5 h-2.5 rounded-full mr-3 ${getEmotionColor(emotion)}`} />
                      <span className="text-sm font-semibold text-ink-700 capitalize truncate">{emotion}</span>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="w-28 bg-ink-100 rounded-full h-2 overflow-hidden">
                        <div
                          className={`h-2 rounded-full ${getEmotionColor(emotion)}`}
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

          <div className={`lg:col-span-2 ${card} px-6 py-5`}>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-title text-ink-900">Satisfaction Trend</h3>
                <p className="text-caption text-ink-500 mt-1">
                  {loading ? 'Loading…' : 'Recent period'}
                </p>
              </div>
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
        <div className={`${card} px-6 py-5 mb-8`}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-title text-ink-900">Channel Feedback Performance</h3>
              <p className="text-caption text-ink-500 mt-1">Feedback rate and satisfaction by channel</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(channelFeedback).map(([channel, stats]) => {
              const Icon = getChannelIcon(channel);
              const satRate = stats.feedback ? (stats.satisfied / stats.feedback) * 100 : 0;
              const fbRate = stats.total ? (stats.feedback / stats.total) * 100 : 0;

              return (
                <div key={channel} className="rounded-2xl border border-ink-200/70 bg-white px-5 py-4 hover:shadow-[0_12px_30px_rgba(15,23,42,0.08)] transition-subtle">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="h-10 w-10 rounded-2xl bg-ink-100/70 flex items-center justify-center">
                      <Icon className="text-ink-700" size={18} />
                    </div>
                    <div>
                      <div className="font-semibold text-ink-900 capitalize">{channel}</div>
                      <div className="text-caption text-ink-500">{stats.total} interactions</div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-ink-500">Feedback rate</span>
                      <span className="font-semibold text-ink-900">{fbRate.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-ink-500">Satisfaction</span>
                      <span className="font-semibold text-ink-900">{satRate.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-ink-500">Feedbacks</span>
                      <span className="font-semibold text-ink-900">{stats.feedback}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Satisfaction by Intent */}
        <div className={`${card} overflow-hidden mb-8`}>
          <div className="px-6 py-5 border-b border-ink-200/70 bg-ink-50">
            <h3 className="text-title text-ink-900">Satisfaction by Intent</h3>
            <p className="text-caption text-ink-500 mt-1">Where customers feel happiest (and where to improve)</p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-ink-50">
                <tr className="border-b border-ink-200/70">
                  <th className="text-left py-3 px-6 text-xs font-semibold text-ink-600 uppercase tracking-wider">Intent</th>
                  <th className="text-left py-3 px-6 text-xs font-semibold text-ink-600 uppercase tracking-wider">Feedback Volume</th>
                  <th className="text-left py-3 px-6 text-xs font-semibold text-ink-600 uppercase tracking-wider">Satisfied</th>
                  <th className="text-left py-3 px-6 text-xs font-semibold text-ink-600 uppercase tracking-wider">Unsatisfied</th>
                  <th className="text-left py-3 px-6 text-xs font-semibold text-ink-600 uppercase tracking-wider">Satisfaction</th>
                  <th className="text-left py-3 px-6 text-xs font-semibold text-ink-600 uppercase tracking-wider">Status</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-ink-100">
                {intentTable.map(row => {
                  const rate = safeNum((row as any).satisfaction_rate_pct, 0);
                  const tone = rate >= 80 ? 'green' : rate >= 60 ? 'amber' : 'red';
                  const statusTone = rate >= 80 ? 'green' : rate >= 60 ? 'blue' : 'amber';

                  return (
                    <tr key={row.intent} className="hover:bg-ink-50/70">
                      <td className="py-4 px-6">
                        <span className="font-semibold text-ink-900 capitalize">{row.intent.replace(/_/g, ' ')}</span>
                      </td>
                      <td className="py-4 px-6 text-ink-600">{(row as any).total_with_feedback}</td>
                      <td className="py-4 px-6 text-ink-600">{(row as any).satisfied}</td>
                      <td className="py-4 px-6 text-ink-600">{(row as any).unsatisfied}</td>
                      <td className="py-4 px-6">
                        <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${badge(tone as any)}`}>
                          {rate.toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-4 px-6">
                        <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${badge(statusTone as any)}`}>
                          {(row as any).status ?? '—'}
                        </span>
                      </td>
                    </tr>
                  );
                })}

                {!intentTable.length && (
                  <tr>
                    <td className="py-10 px-6 text-ink-500" colSpan={6}>
                      No satisfaction feedback yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Feedback Highlights */}
        <div className={`${card} px-6 py-5`}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-title text-ink-900">Feedback Highlights</h3>
            <span className="text-caption text-ink-500">Latest comments</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-emerald-700 mb-3">Satisfied</h4>
              <div className="space-y-3">
                {interactions
                  .filter(i => i.satisfaction_score === 1 && i.feedback_comment)
                  .slice(0, 3)
                  .map((interaction, idx) => (
                    <div key={idx} className="rounded-2xl border border-emerald-200/60 bg-emerald-50/60 px-4 py-3">
                      <p className="text-sm text-ink-800 leading-relaxed">
                        “{interaction.feedback_comment}”
                      </p>
                      <div className="mt-2">
                        <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${badge('green')}`}>
                          Satisfied (1)
                        </span>
                      </div>
                    </div>
                  ))}

                {!interactions.some(i => i.satisfaction_score === 1 && i.feedback_comment) && (
                  <p className="text-sm text-ink-500">No satisfied feedback comments yet.</p>
                )}
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-rose-700 mb-3">Unsatisfied</h4>
              <div className="space-y-3">
                {interactions
                  .filter(i => i.satisfaction_score === 2 && i.feedback_comment)
                  .slice(0, 3)
                  .map((interaction, idx) => (
                    <div key={idx} className="rounded-2xl border border-rose-200/60 bg-rose-50/60 px-4 py-3">
                      <p className="text-sm text-ink-800 leading-relaxed">
                        “{interaction.feedback_comment}”
                      </p>
                      <div className="mt-2">
                        <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${badge('red')}`}>
                          Unsatisfied (2)
                        </span>
                      </div>
                    </div>
                  ))}

                {!interactions.some(i => i.satisfaction_score === 2 && i.feedback_comment) && (
                  <p className="text-sm text-ink-500">No unsatisfied feedback comments yet.</p>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="h-6" />
      </div>
    </div>
  );
};

export default CustomerExperienceSection;
