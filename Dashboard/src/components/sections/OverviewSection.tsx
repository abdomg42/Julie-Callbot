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
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  const formatPercentage = (value: number): string => {
    return `${value.toFixed(1)}%`;
  };

  // Sample data for charts
  const satisfactionTrendData = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    datasets: [
      {
        label: 'Customer Satisfaction',
        data: [4.2, 4.1, 4.4, metrics.customerSatisfaction],
        borderColor: '#0d9488',
        backgroundColor: 'rgba(13, 148, 136, 0.05)',
        borderWidth: 2,
        fill: true,
        tension: 0.3,
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
        borderRadius: 4,
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
        backgroundColor: [
          '#dc2626',
          '#d97706',
          '#a1a1aa',
          '#0d9488',
        ],
        borderWidth: 0,
      },
    ],
  };

  return (
    <div className="px-8 py-6 bg-ink-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-display text-ink-900">
          Overview
        </h1>
        <p className="text-body text-ink-500 mt-1">Performance metrics for your support system</p>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <MetricCard
          title="Interactions"
          value={metrics.totalInteractions.toLocaleString()}
          subtitle="Last 24 hours"
          trend="up"
          trendValue="+12%"
        />
        
        <MetricCard
          title="Success Rate"
          value={formatPercentage(metrics.successRate)}
          subtitle="Resolution success"
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
          title="Avg Response"
          value={formatTime(metrics.avgResponseTime)}
          subtitle="System response"
          trend="down"
          trendValue="-150ms"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
        <div className="lg:col-span-2 bg-white border border-ink-200 rounded-lg p-5">
          <h3 className="text-title text-ink-900 mb-4">Satisfaction Trend</h3>
          <Chart
            type="line"
            data={satisfactionTrendData}
            className="h-56"
            options={{
              scales: {
                y: {
                  beginAtZero: true,
                  max: 5,
                },
              },
            }}
          />
        </div>

        <div className="bg-white border border-ink-200 rounded-lg p-5">
          <h3 className="text-title text-ink-900 mb-4">Issues by Urgency</h3>
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
      <div className="bg-white rounded-xl p-6 shadow-xl border border-gray-100 mb-8">
        <div className="flex items-center mb-4">
          <Clock className="text-indigo-500 mr-3" size={24} />
          <h3 className="text-xl font-bold text-gray-900">Weekly Response Time</h3>
        </div>
        <Chart
          type="bar"
          data={responseTimeData}
          className="h-48"
          options={{
            scales: {
              y: {
                beginAtZero: true,
              },
            },
          }}
        />
      </div>

      {/* System Health - simplified */}
      <div className="bg-white border border-ink-200 rounded-lg p-5">
        <h3 className="text-title text-ink-900 mb-5">System Health</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border border-ink-200 rounded-md">
            <div className="flex items-center mb-2">
              <CheckCircle className="text-positive mr-2" size={18} />
              <span className="text-sm font-medium text-ink-900">Bot Performance</span>
            </div>
            <p className="text-caption text-positive">Optimal</p>
          </div>
          
          <div className="p-4 border border-ink-200 rounded-md">
            <div className="flex items-center mb-2">
              <Clock className="text-accent mr-2" size={18} />
              <span className="text-sm font-medium text-ink-900">Response Time</span>
            </div>
            <p className="text-caption text-accent">Good</p>
          </div>
          
          <div className="p-4 border border-ink-200 rounded-md">
            <div className="flex items-center mb-2">
              <AlertTriangle className="text-caution mr-2" size={18} />
              <span className="text-sm font-medium text-ink-900">Queue Load</span>
            </div>
            <p className="text-caption text-caution">Moderate</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OverviewSection;