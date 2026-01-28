import React from 'react';
import type { AgentPerformance } from '../../types/dashboard';
import Chart from '../Chart';
import { User, CheckCircle, Star, TrendingUp } from 'lucide-react';

interface AgentPerformanceSectionProps {
  agentData: AgentPerformance[];
}

const AgentPerformanceSection: React.FC<AgentPerformanceSectionProps> = ({ agentData }) => {
  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
  };

  const getPerformanceColor = (rate: number): string => {
    if (rate >= 90) return 'text-emerald-600';
    if (rate >= 75) return 'text-amber-600';
    return 'text-red-600';
  };

  const getPerformanceBadge = (rate: number): { label: string; color: string } => {
    if (rate >= 90) return { label: 'Excellent', color: 'bg-gradient-to-r from-emerald-400 to-emerald-600 text-white' };
    if (rate >= 75) return { label: 'Good', color: 'bg-gradient-to-r from-amber-400 to-amber-600 text-white' };
    return { label: 'Needs Improvement', color: 'bg-gradient-to-r from-red-400 to-red-600 text-white' };
  };

  // Chart data
  const performanceComparisonData = {
    labels: agentData.map(agent => agent.agent_name.split(' ')[0]),
    datasets: [
      {
        label: 'Resolution Rate (%)',
        data: agentData.map(agent => agent.resolution_rate),
        backgroundColor: [
          '#ec4899',
          '#8b5cf6', 
          '#6366f1',
          '#14b8a6',
          '#f97316',
        ],
        borderRadius: 8,
        borderSkipped: false,
      },
    ],
  };

  const satisfactionData = {
    labels: agentData.map(agent => agent.agent_name.split(' ')[0]),
    datasets: [
      {
        label: 'Customer Satisfaction',
        data: agentData.map(agent => agent.customer_satisfaction),
        borderColor: '#8b5cf6',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: agentData.map((_, index) => 
          ['#ec4899', '#8b5cf6', '#6366f1', '#14b8a6', '#f97316'][index % 5]
        ),
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 8,
      },
    ],
  };

  return (
    <div className="p-8 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
          Agent Performance
        </h1>
        <p className="text-gray-600">Individual agent metrics and performance insights</p>
      </div>

      {/* Performance Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div className="bg-white rounded-xl p-6 shadow-xl border border-gray-100">
          <div className="flex items-center mb-4">
            <TrendingUp className="text-purple-500 mr-3" size={24} />
            <h3 className="text-xl font-bold text-gray-900">Resolution Rate Comparison</h3>
          </div>
          <Chart
            type="bar"
            data={performanceComparisonData}
            className="h-64"
            options={{
              scales: {
                y: {
                  beginAtZero: true,
                  max: 100,
                },
              },
            }}
          />
        </div>

        <div className="bg-white rounded-xl p-6 shadow-xl border border-gray-100">
          <div className="flex items-center mb-4">
            <Star className="text-yellow-500 mr-3" size={24} />
            <h3 className="text-xl font-bold text-gray-900">Satisfaction Trend</h3>
          </div>
          <Chart
            type="line"
            data={satisfactionData}
            className="h-64"
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
      </div>

      {/* Performance Summary Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
        {agentData.map((agent) => {
          const badge = getPerformanceBadge(agent.resolution_rate);
          const colors = ['from-pink-400 to-purple-600', 'from-blue-400 to-indigo-600', 'from-emerald-400 to-teal-600'];
          const colorIndex = Math.abs(agent.agent_name.charCodeAt(0)) % colors.length;
          
          return (
            <div key={agent.agent_name} className="bg-white rounded-xl p-6 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <div className={`bg-gradient-to-br ${colors[colorIndex]} rounded-full p-3 mr-3 shadow-lg`}>
                    <User className="text-white" size={20} />
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900">{agent.agent_name}</h3>
                    <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${badge.color} shadow-sm`}>
                      {badge.label}
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Interactions</span>
                  <span className="font-bold text-blue-600 text-lg">{agent.interactions_handled}</span>
                </div>

                <div className="flex justify-between items-center p-3 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Resolution Rate</span>
                  <span className={`font-bold text-lg ${getPerformanceColor(agent.resolution_rate)}`}>
                    {agent.resolution_rate.toFixed(1)}%
                  </span>
                </div>

                <div className="flex justify-between items-center p-3 bg-gradient-to-r from-orange-50 to-pink-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Avg Time</span>
                  <span className="font-bold text-orange-600 text-lg">
                    {formatTime(agent.avg_resolution_time)}
                  </span>
                </div>

                <div className="flex justify-between items-center p-3 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Satisfaction</span>
                  <div className="flex items-center">
                    <Star className="text-yellow-400 fill-current mr-1" size={16} />
                    <span className="font-bold text-yellow-600 text-lg">
                      {agent.customer_satisfaction.toFixed(1)}
                    </span>
                  </div>
                </div>

                {/* Top Handoff Reasons */}
                {agent.top_handoff_reasons.length > 0 && (
                  <div className="pt-3 border-t border-gray-200">
                    <p className="text-sm font-medium text-gray-700 mb-2">Top Escalation Reasons:</p>
                    <div className="space-y-1">
                      {agent.top_handoff_reasons.slice(0, 2).map((reason, idx) => (
                        <div key={idx} className="flex justify-between items-center p-2 bg-gray-50 rounded text-xs">
                          <span className="text-gray-600 capitalize">{reason.reason.replace('_', ' ')}</span>
                          <span className="bg-gray-200 text-gray-700 px-2 py-1 rounded-full font-medium">{reason.count}</span>
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

      {/* Performance Comparison Table */}
      <div className="bg-white rounded-xl shadow-xl overflow-hidden border border-gray-100">
        <div className="px-6 py-4 bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
          <h3 className="text-xl font-bold text-gray-900">Performance Leaderboard</h3>
          <p className="text-sm text-gray-600">Compare agents across key metrics</p>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gradient-to-r from-purple-100 to-blue-100">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Agent
                </th>
                <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Interactions
                </th>
                <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Resolution Rate
                </th>
                <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Avg Time
                </th>
                <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Satisfaction
                </th>
                <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Performance
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {agentData
                .sort((a, b) => b.resolution_rate - a.resolution_rate)
                .map((agent, index) => {
                  const badge = getPerformanceBadge(agent.resolution_rate);
                  const rowColors = ['bg-gradient-to-r from-pink-50 to-purple-50', 'bg-gradient-to-r from-blue-50 to-indigo-50', 'bg-white'];
                  
                  return (
                    <tr key={agent.agent_name} className={`hover:bg-gradient-to-r hover:from-gray-50 hover:to-blue-50 transition-colors ${index < 3 ? rowColors[index] : 'bg-white'}`}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="bg-gradient-to-br from-blue-400 to-purple-600 rounded-full p-2 mr-3">
                            <User className="text-white" size={16} />
                          </div>
                          <div>
                            <span className="font-bold text-gray-900">{agent.agent_name}</span>
                            {index === 0 && (
                              <div className="flex items-center mt-1">
                                <span className="inline-block w-3 h-3 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full mr-1" title="Top Performer"></span>
                                <span className="text-xs font-medium text-orange-600">Top Performer</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-lg font-bold text-blue-600">
                          {agent.interactions_handled}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-lg font-bold ${getPerformanceColor(agent.resolution_rate)}`}>
                          {agent.resolution_rate.toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-lg font-medium text-gray-900">
                        {formatTime(agent.avg_resolution_time)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <Star className="text-yellow-400 fill-current mr-1" size={16} />
                          <span className="text-lg font-bold text-yellow-600">{agent.customer_satisfaction.toFixed(1)}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${badge.color}`}>
                          {badge.label}
                        </span>
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Coaching Opportunities */}
      <div className="mt-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-8 text-white shadow-xl">
        <div className="flex items-center mb-6">
          <CheckCircle className="text-white mr-3" size={28} />
          <h3 className="text-2xl font-bold">Coaching Opportunities</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white/20 backdrop-blur rounded-xl p-6 border border-white/30">
            <h4 className="font-bold text-xl text-white mb-4">Focus Areas</h4>
            <ul className="text-white/90 space-y-2">
              <li className="flex items-center"><span className="w-2 h-2 bg-yellow-400 rounded-full mr-2"></span>Complex issue resolution techniques</li>
              <li className="flex items-center"><span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>Authentication process optimization</li>
              <li className="flex items-center"><span className="w-2 h-2 bg-pink-400 rounded-full mr-2"></span>Customer de-escalation strategies</li>
            </ul>
          </div>
          <div className="bg-white/20 backdrop-blur rounded-xl p-6 border border-white/30">
            <h4 className="font-bold text-xl text-white mb-4">Best Practices</h4>
            <ul className="text-white/90 space-y-2">
              <li className="flex items-center"><span className="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>Quick acknowledgment of concerns</li>
              <li className="flex items-center"><span className="w-2 h-2 bg-purple-400 rounded-full mr-2"></span>Clear explanation of next steps</li>
              <li className="flex items-center"><span className="w-2 h-2 bg-orange-400 rounded-full mr-2"></span>Follow-up for complex issues</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentPerformanceSection;