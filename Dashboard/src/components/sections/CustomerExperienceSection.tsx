import React from 'react';
import type { Interaction } from '../../types/dashboard';
import { Heart, TrendingUp, MessageCircle, Mail, Phone, MessageSquare } from 'lucide-react';

interface CustomerExperienceSectionProps {
  interactions: Interaction[];
}

const CustomerExperienceSection: React.FC<CustomerExperienceSectionProps> = ({ interactions }) => {
  // Calculate emotion distribution
  const emotionCounts = interactions.reduce((acc, interaction) => {
    acc[interaction.emotion] = (acc[interaction.emotion] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const totalInteractions = interactions.length;
  
  // Calculate satisfaction trends (mock weekly data)
  const satisfactionTrend = [
    { week: 'Week 1', satisfaction: 4.2 },
    { week: 'Week 2', satisfaction: 4.1 },
    { week: 'Week 3', satisfaction: 4.4 },
    { week: 'Week 4', satisfaction: 4.3 },
  ];

  // Channel performance
  const channelStats = interactions.reduce((acc, interaction) => {
    if (!acc[interaction.channel]) {
      acc[interaction.channel] = { count: 0, satisfaction: 0 };
    }
    acc[interaction.channel].count++;
    acc[interaction.channel].satisfaction += interaction.customer_satisfaction;
    return acc;
  }, {} as Record<string, { count: number; satisfaction: number }>);

  Object.keys(channelStats).forEach(channel => {
    channelStats[channel].satisfaction = channelStats[channel].satisfaction / channelStats[channel].count;
  });

  // Intent satisfaction analysis
  const intentStats = interactions.reduce((acc, interaction) => {
    if (!acc[interaction.intent]) {
      acc[interaction.intent] = { count: 0, satisfaction: 0 };
    }
    acc[interaction.intent].count++;
    acc[interaction.intent].satisfaction += interaction.customer_satisfaction;
    return acc;
  }, {} as Record<string, { count: number; satisfaction: number }>);

  Object.keys(intentStats).forEach(intent => {
    intentStats[intent].satisfaction = intentStats[intent].satisfaction / intentStats[intent].count;
  });

  const getEmotionColor = (emotion: string): string => {
    switch (emotion) {
      case 'positive': return 'bg-green-500';
      case 'satisfied': return 'bg-green-400';
      case 'neutral': return 'bg-gray-400';
      case 'frustrated': return 'bg-orange-500';
      case 'negative': return 'bg-red-500';
      default: return 'bg-gray-400';
    }
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'chat': return MessageSquare;
      case 'phone': return Phone;
      case 'email': return Mail;
      case 'sms': return MessageCircle;
      default: return MessageSquare;
    }
  };

  return (
    <div className="p-8 bg-gradient-to-br from-pink-50 via-rose-50 to-orange-50">
      <div className="mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-pink-600 to-orange-600 bg-clip-text text-transparent mb-2">
          Customer Experience
        </h1>
        <p className="text-gray-600">Customer sentiment, satisfaction trends, and experience insights</p>
      </div>

      {/* Emotion Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div className="bg-white rounded-lg p-6 card-shadow">
          <div className="flex items-center mb-4">
            <Heart className="text-red-500 mr-2" size={20} />
            <h3 className="text-lg font-semibold text-gray-900">Emotion Distribution</h3>
          </div>
          <div className="space-y-3">
            {Object.entries(emotionCounts).map(([emotion, count]) => {
              const percentage = (count / totalInteractions) * 100;
              return (
                <div key={emotion} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-3 ${getEmotionColor(emotion)}`}></div>
                    <span className="text-sm font-medium text-gray-700 capitalize">{emotion}</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-24 bg-gray-200 rounded-full h-2 mr-3">
                      <div 
                        className={`h-2 rounded-full ${getEmotionColor(emotion)}`}
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-600 w-12 text-right">{count}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 card-shadow">
          <div className="flex items-center mb-4">
            <TrendingUp className="text-blue-500 mr-2" size={20} />
            <h3 className="text-lg font-semibold text-gray-900">Satisfaction Trend</h3>
          </div>
          <div className="space-y-4">
            {satisfactionTrend.map((week) => (
              <div key={week.week} className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{week.week}</span>
                <div className="flex items-center">
                  <div className="w-16 text-right mr-2">
                    <span className="text-sm font-medium">{week.satisfaction.toFixed(1)}</span>
                  </div>
                  <div className="flex">
                    {[...Array(5)].map((_, i) => (
                      <div
                        key={i}
                        className={`w-2 h-2 rounded-full mr-1 ${
                          i < Math.floor(week.satisfaction) ? 'bg-yellow-400' : 'bg-gray-200'
                        }`}
                      ></div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Channel Performance */}
      <div className="bg-white rounded-lg p-6 card-shadow mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Channel Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(channelStats).map(([channel, stats]) => {
            const Icon = getChannelIcon(channel);
            return (
              <div key={channel} className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center mb-2">
                  <Icon className="text-blue-500 mr-2" size={16} />
                  <span className="font-medium text-gray-900 capitalize">{channel}</span>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Interactions</span>
                    <span className="font-medium">{stats.count}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Avg Satisfaction</span>
                    <span className="font-medium">{stats.satisfaction.toFixed(1)}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Intent vs Satisfaction Analysis */}
      <div className="bg-white rounded-lg p-6 card-shadow mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Satisfaction by Intent</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-medium text-gray-700">Intent</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Volume</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Avg Satisfaction</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Performance</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(intentStats)
                .sort(([, a], [, b]) => b.satisfaction - a.satisfaction)
                .map(([intent, stats]) => {
                  const performanceColor = stats.satisfaction >= 4 ? 'text-green-600' : 
                                          stats.satisfaction >= 3 ? 'text-yellow-600' : 'text-red-600';
                  return (
                    <tr key={intent} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <span className="font-medium text-gray-900 capitalize">
                          {intent.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-gray-600">{stats.count}</td>
                      <td className="py-3 px-4">
                        <span className={`font-medium ${performanceColor}`}>
                          {stats.satisfaction.toFixed(1)}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                            <div 
                              className={`h-2 rounded-full ${
                                stats.satisfaction >= 4 ? 'bg-green-500' :
                                stats.satisfaction >= 3 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${(stats.satisfaction / 5) * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Customer Feedback Summary */}
      <div className="bg-white rounded-lg p-6 card-shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Customer Feedback Highlights</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-green-700 mb-3">Positive Feedback</h4>
            <div className="space-y-2">
              {interactions
                .filter(i => i.customer_satisfaction >= 4 && i.feedback_comment)
                .slice(0, 3)
                .map((interaction, index) => (
                  <div key={index} className="p-3 bg-green-50 rounded border-l-2 border-green-300">
                    <p className="text-sm text-gray-700">"{interaction.feedback_comment}"</p>
                    <p className="text-xs text-green-600 mt-1">Rating: {interaction.customer_satisfaction}/5</p>
                  </div>
                ))}
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-red-700 mb-3">Areas for Improvement</h4>
            <div className="space-y-2">
              {interactions
                .filter(i => i.customer_satisfaction <= 2 && i.feedback_comment)
                .slice(0, 3)
                .map((interaction, index) => (
                  <div key={index} className="p-3 bg-red-50 rounded border-l-2 border-red-300">
                    <p className="text-sm text-gray-700">"{interaction.feedback_comment}"</p>
                    <p className="text-xs text-red-600 mt-1">Rating: {interaction.customer_satisfaction}/5</p>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomerExperienceSection;