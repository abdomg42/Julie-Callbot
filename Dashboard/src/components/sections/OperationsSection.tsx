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
    stats.avgTime = stats.totalTime / stats.count;
  });

  // System confidence levels
  const avgConfidence = interactions.reduce((sum, i) => sum + i.confidence, 0) / interactions.length;
  const confidenceTrend = [
    { period: 'Last Hour', confidence: 0.92 },
    { period: 'Last 4 Hours', confidence: 0.89 },
    { period: 'Last Day', confidence: avgConfidence },
    { period: 'Last Week', confidence: 0.87 },
  ];

  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
  };

  const getUrgencyColor = (urgency: string): string => {
    switch (urgency) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getResponseTimeColor = (range: string): string => {
    switch (range) {
      case 'Fast (<1s)': return 'bg-green-500';
      case 'Good (1-2s)': return 'bg-blue-500';
      case 'Slow (2-5s)': return 'bg-yellow-500';
      case 'Very Slow (>5s)': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="p-8 bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      <div className="mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-2">
          Operational Performance
        </h1>
        <p className="text-gray-600">System efficiency, resource allocation, and performance metrics</p>
      </div>

      {/* Key Performance Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg p-6 card-shadow">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">Avg Response Time</h3>
            <Clock className="text-blue-500" size={20} />
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-1">
            {(interactions.reduce((sum, i) => sum + ms(i.execution_time_ms), 0) / interactions.length / 1000).toFixed(2)}s
          </div>
          <p className="text-xs text-green-600">-12% from last week</p>
        </div>

        <div className="bg-white rounded-lg p-6 card-shadow">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">System Confidence</h3>
            <TrendingUp className="text-green-500" size={20} />
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-1">
            {(avgConfidence * 100).toFixed(1)}%
          </div>
          <p className="text-xs text-green-600">+3% from last week</p>
        </div>

        <div className="bg-white rounded-lg p-6 card-shadow">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">Total Handoffs</h3>
            <AlertTriangle className="text-orange-500" size={20} />
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-1">
            {interactions.filter(i => i.is_handoff).length}
          </div>
          <p className="text-xs text-red-600">+2 from yesterday</p>
        </div>

        <div className="bg-white rounded-lg p-6 card-shadow">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">Peak Load</h3>
            <BarChart3 className="text-purple-500" size={20} />
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-1">
            {Math.max(...hourlyVolume.map(h => h.count))}
          </div>
          <p className="text-xs text-gray-600">interactions/hour</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Response Time Distribution */}
        <div className="bg-white rounded-lg p-6 card-shadow">
          <div className="flex items-center mb-4">
            <Activity className="text-blue-500 mr-2" size={20} />
            <h3 className="text-lg font-semibold text-gray-900">Response Time Distribution</h3>
          </div>
          <div className="space-y-3">
            {Object.entries(responseTimeRanges).map(([range, count]) => {
              const percentage = (count / interactions.length) * 100;
              return (
                <div key={range} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-3 ${getResponseTimeColor(range)}`}></div>
                    <span className="text-sm font-medium text-gray-700">{range}</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-24 bg-gray-200 rounded-full h-2 mr-3">
                      <div 
                        className={`h-2 rounded-full ${getResponseTimeColor(range)}`}
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-600 w-8 text-right">{count}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Handoff Reasons */}
        <div className="bg-white rounded-lg p-6 card-shadow">
          <div className="flex items-center mb-4">
            <AlertTriangle className="text-orange-500 mr-2" size={20} />
            <h3 className="text-lg font-semibold text-gray-900">Handoff Reasons</h3>
          </div>
          <div className="space-y-3">
            {Object.entries(handoffReasons)
              .sort(([, a], [, b]) => b - a)
              .map(([reason, count]) => {
                const percentage = (count / Object.values(handoffReasons).reduce((a, b) => a + b, 0)) * 100;
                return (
                  <div key={reason} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {reason.replace('_', ' ')}
                    </span>
                    <div className="flex items-center">
                      <div className="w-20 bg-gray-200 rounded-full h-2 mr-3">
                        <div 
                          className="h-2 bg-orange-500 rounded-full"
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-600 w-8 text-right">{count}</span>
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      </div>

      {/* Resolution Time by Urgency */}
      <div className="bg-white rounded-lg p-6 card-shadow mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Resolution Time by Urgency</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(urgencyStats)
            .sort(([a], [b]) => {
              const order = { 'critical': 0, 'high': 1, 'medium': 2, 'low': 3 };
              return order[a as keyof typeof order] - order[b as keyof typeof order];
            })
            .map(([urgency, stats]) => (
              <div key={urgency} className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className={`px-2 py-1 rounded text-xs font-medium capitalize ${getUrgencyColor(urgency)}`}>
                    {urgency}
                  </span>
                  <span className="text-sm text-gray-600">{stats.count} tickets</span>
                </div>
                <div className="text-lg font-bold text-gray-900 mb-1">
                  {formatTime(stats.avgTime)}
                </div>
                <p className="text-xs text-gray-600">Average resolution time</p>
              </div>
            ))}
        </div>
      </div>

      {/* System Confidence Trend */}
      <div className="bg-white rounded-lg p-6 card-shadow">
        <div className="flex items-center mb-4">
          <TrendingUp className="text-green-500 mr-2" size={20} />
          <h3 className="text-lg font-semibold text-gray-900">System Confidence Trend</h3>
        </div>
        <div className="space-y-4">
          {confidenceTrend.map((period) => {
            const confidencePercentage = period.confidence * 100;
            const confidenceColor = confidencePercentage >= 90 ? 'text-green-600' : 
                                   confidencePercentage >= 80 ? 'text-yellow-600' : 'text-red-600';
            return (
              <div key={period.period} className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{period.period}</span>
                <div className="flex items-center">
                  <div className="w-32 bg-gray-200 rounded-full h-3 mr-3">
                    <div 
                      className={`h-3 rounded-full ${
                        confidencePercentage >= 90 ? 'bg-green-500' :
                        confidencePercentage >= 80 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${confidencePercentage}%` }}
                    ></div>
                  </div>
                  <span className={`text-sm font-medium w-12 text-right ${confidenceColor}`}>
                    {confidencePercentage.toFixed(1)}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default OperationsSection;