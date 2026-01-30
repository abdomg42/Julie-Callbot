import React from 'react';
import type { DashboardMetrics } from '../../types/dashboard';
import MetricCard from '../MetricCard';
import Chart from '../Chart';
import { AlertTriangle, CheckCircle, Clock } from 'lucide-react';

interface OverviewSectionProps {
  metrics: DashboardMetrics;
}

const OverviewSection: React.FC<OverviewSectionProps> = ({ metrics }) => {
  const formatTime = (ms: number): string => {
    if (!Number.isFinite(ms)) return '—';
    if (ms < 1000) return `${Math.round(ms)}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  const formatPercentage = (value: number): string => {
    if (!Number.isFinite(value)) return '—';
    return `${value.toFixed(1)}%`;
  };

  // Charts
  const satisfactionTrendData = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    datasets: [
      {
        label: 'Satisfaction Rate (%)',
        data: [78, 81, 84, metrics.customerSatisfaction],
        borderColor: '#0d9488',
        backgroundColor: 'rgba(13, 148, 136, 0.10)',
        borderWidth: 2,
        fill: true,
        tension: 0.35,
        pointRadius: 3,
        pointBackgroundColor: '#0d9488',
      },
    ],
  };

  const responseTimeData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Response Time (ms)',
        data: [1200, 1100, 1400, 1300, metrics.avgResponseTime, 1000, 1150],
        backgroundColor: '#e4e4e7',
        hoverBackgroundColor: '#0d9488',
        borderRadius: 10,
        borderSkipped: false,
      },
    ],
  };

  const urgencyDistributionData = {
    labels: ['Critical', 'High', 'Medium', 'Low'],
    datasets: [
      {
        data: [
          metrics.activeIssues.critical,
          metrics.activeIssues.high,
          metrics.activeIssues.medium,
          metrics.activeIssues.low,
        ],
        backgroundColor: ['#dc2626', '#d97706', '#a1a1aa', '#0d9488'],
        borderWidth: 0,
      },
    ],
  };

  // Shared Figma-like card classes
  const card =
    'bg-white border border-ink-200/70 rounded-2xl shadow-[0_10px_30px_rgba(15,23,42,0.06)]';
  const cardPad = 'px-6 py-5';

  return (
    <div className="min-h-screen bg-ink-50">
      <div className="px-8 py-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-display text-ink-900">Overview</h1>
          <p className="text-body text-ink-500 mt-1">
            Performance metrics for your support system
          </p>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <MetricCard
            title="Interactions"
            value={metrics.totalInteractions.toLocaleString()}
            subtitle="Last 30 days"
            trend="up"
            trendValue="+12%"
          />

          <MetricCard
            title="Success Rate"
            value={formatPercentage(metrics.successRate)}
            subtitle="Resolved successfully"
            trend={metrics.successRate >= 80 ? 'up' : 'down'}
            trendValue={metrics.successRate >= 80 ? '+2.1%' : '-1.5%'}
          />

          <MetricCard
            title="Handoff Rate"
            value={formatPercentage(metrics.handoffRate)}
            subtitle="Escalated to agents"
            trend={metrics.handoffRate <= 30 ? 'up' : 'down'}
            trendValue={metrics.handoffRate <= 30 ? '-3.2%' : '+4.1%'}
          />

          <MetricCard
            title="Satisfaction"
            value={formatPercentage(metrics.customerSatisfaction)}
            subtitle="From customer feedback"
            trend={metrics.customerSatisfaction >= 80 ? 'up' : 'down'}
            trendValue={metrics.customerSatisfaction >= 80 ? '+1.8%' : '-2.1%'}
          />
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
          <div className={`lg:col-span-2 ${card} ${cardPad}`}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-title text-ink-900">Satisfaction Trend</h3>
              <span className="text-xs font-medium text-ink-500">
                Last 4 weeks
              </span>
            </div>

            <Chart
              type="line"
              data={satisfactionTrendData}
              className="h-56"
              options={{
                scales: {
                  y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                      callback: (val: any) => `${val}%`,
                    },
                  },
                },
                plugins: {
                  legend: {
                    display: true,
                    labels: {
                      boxWidth: 10,
                      boxHeight: 10,
                    },
                  },
                },
              }}
            />
          </div>

          <div className={`${card} ${cardPad}`}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-title text-ink-900">Issues by Urgency</h3>
              <span className="text-xs font-medium text-ink-500">Today</span>
            </div>

            <Chart
              type="doughnut"
              data={urgencyDistributionData}
              className="h-56"
              options={{
                plugins: {
                  legend: {
                    position: 'bottom',
                  },
                },
              }}
            />
          </div>
        </div>

        {/* Response Time Chart */}
        <div className={`${card} px-6 py-6 mb-8`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-2xl bg-ink-100/70 flex items-center justify-center">
                <Clock className="text-ink-700" size={18} />
              </div>
              <div>
                <h3 className="text-title text-ink-900">Weekly Response Time</h3>
                <p className="text-caption text-ink-500 mt-0.5">
                  Avg: {formatTime(metrics.avgResponseTime)}
                </p>
              </div>
            </div>

            <span className="text-xs font-medium text-ink-500">Last 7 days</span>
          </div>

          <Chart
            type="bar"
            data={responseTimeData}
            className="h-60 w-full"
            options={{
              scales: {
                x: {
                  // ✅ makes bars occupy more horizontal space per category
                  categoryPercentage: 0.8,
                  barPercentage: 0.95,
                  grid: { display: false },
                },
                y: {
                  beginAtZero: true,
                },
              },
              plugins: {
                legend: { display: false },
              },
            }}
          />

        </div>
        {/* bottom spacing */}
        <div className="h-6" />
      </div>
    </div>
  );
};

export default OverviewSection;
