import React, { useState } from 'react';
import type { Interaction, ConversationMessage } from '../../types/dashboard';
import { MessageSquare, User, Bot, Search } from 'lucide-react';

interface ConversationQualitySectionProps {
  interactions: Interaction[];
}

const ConversationQualitySection: React.FC<ConversationQualitySectionProps> = ({ interactions }) => {
  const [selectedConversation, setSelectedConversation] = useState<Interaction | null>(null);
  const [filterByQuality, setFilterByQuality] = useState<'all' | 'good' | 'poor'>('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Calculate conversation quality score
  const calculateQualityScore = (interaction: Interaction): number => {
    let score = (interaction.customer_satisfaction || 0) * 20; // 20-100 base on satisfaction
    if (interaction.success) score += 10;
    if (interaction.execution_time_ms && interaction.execution_time_ms < 2000) score += 10;
    if (interaction.is_handoff) score -= 10;
    
    // Emotion progression bonus
    const history = interaction.conversation_history;
    if (Array.isArray(history) && history.length > 2) {
      const firstEmotion = history[0]?.detected_emotion;
      const lastEmotion = history[history.length - 1]?.detected_emotion;
      if (firstEmotion === 'frustrated' && (lastEmotion === 'satisfied' || lastEmotion === 'positive')) {
        score += 15; // Successful de-escalation
      }
    }
    
    return Math.min(Math.max(score, 0), 100);
  };

  const getQualityLevel = (score: number): { label: string; color: string; bgColor: string } => {
    if (score >= 75) return { label: 'Excellent', color: 'text-positive', bgColor: 'bg-accent-light' };
    if (score >= 50) return { label: 'Good', color: 'text-ink-600', bgColor: 'bg-ink-100' };
    return { label: 'Needs Improvement', color: 'text-negative', bgColor: 'bg-red-50' };
  };

  const getEmotionColor = (emotion: string): string => {
    switch (emotion) {
      case 'positive': return 'text-positive';
      case 'satisfied': return 'text-positive';
      case 'neutral': return 'text-ink-500';
      case 'frustrated': return 'text-negative';
      case 'stressed': return 'text-negative';
      case 'negative': return 'text-negative';
      default: return 'text-ink-500';
    }
  };

  const filteredInteractions = interactions.filter(interaction => {
    const qualityScore = calculateQualityScore(interaction);
    const matchesFilter = filterByQuality === 'all' || 
      (filterByQuality === 'good' && qualityScore >= 75) ||
      (filterByQuality === 'poor' && qualityScore < 50);
    
    const matchesSearch = searchTerm === '' || 
      (interaction.customer_message && interaction.customer_message.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (interaction.assigned_agent && interaction.assigned_agent.toLowerCase().includes(searchTerm.toLowerCase()));
    
    return matchesFilter && matchesSearch;
  });

  const goodConversations = interactions.filter(i => calculateQualityScore(i) >= 75);
  const poorConversations = interactions.filter(i => calculateQualityScore(i) < 50);

  return (
    <div className="px-8 py-6 bg-ink-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-display text-ink-900">
          Conversations
        </h1>
        <p className="text-body text-ink-500 mt-1">Analyze conversations to improve agent performance</p>
      </div>

      {/* Quality Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white border border-ink-200 rounded-lg p-5">
          <span className="text-label uppercase text-ink-500 tracking-wide">Total Conversations</span>
          <div className="text-2xl font-semibold text-ink-900 mt-2">{interactions.length}</div>
        </div>

        <div className="bg-white border border-ink-200 rounded-lg p-5">
          <span className="text-label uppercase text-ink-500 tracking-wide">High Quality</span>
          <div className="text-2xl font-semibold text-positive mt-2">{goodConversations.length}</div>
          <p className="text-caption text-ink-500 mt-1">{((goodConversations.length / interactions.length) * 100).toFixed(1)}% of total</p>
        </div>

        <div className="bg-white border border-ink-200 rounded-lg p-5">
          <span className="text-label uppercase text-ink-500 tracking-wide">Needs Improvement</span>
          <div className="text-2xl font-semibold text-negative mt-2">{poorConversations.length}</div>
          <p className="text-caption text-ink-500 mt-1">{((poorConversations.length / interactions.length) * 100).toFixed(1)}% of total</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Conversation List */}
        <div className="lg:col-span-1">
          <div className="bg-white border border-ink-200 rounded-lg">
            <div className="p-4 border-b border-ink-100">
              <h3 className="text-title text-ink-900 mb-4">Conversations</h3>
              
              {/* Search and Filter */}
              <div className="space-y-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-ink-400" size={16} />
                  <input
                    type="text"
                    placeholder="Search conversations..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-3 py-2 border border-ink-200 rounded-md text-sm text-ink-900 placeholder-ink-400 focus:border-accent"
                  />
                </div>
                
                <select
                  value={filterByQuality}
                  onChange={(e) => setFilterByQuality(e.target.value as 'all' | 'good' | 'poor')}
                  className="w-full px-3 py-2 border border-ink-200 rounded-md text-sm text-ink-700 focus:border-accent"
                >
                  <option value="all">All Conversations</option>
                  <option value="good">High Quality</option>
                  <option value="poor">Needs Improvement</option>
                </select>
              </div>
            </div>

            <div className="max-h-[500px] overflow-y-auto">
              {filteredInteractions.map((interaction) => {
                const qualityScore = calculateQualityScore(interaction);
                const quality = getQualityLevel(qualityScore);
                
                return (
                  <button
                    key={interaction.interaction_id}
                    onClick={() => setSelectedConversation(interaction)}
                    className={`w-full p-4 text-left border-b border-ink-100 transition-subtle ${
                      selectedConversation?.interaction_id === interaction.interaction_id 
                        ? 'bg-accent-light border-l-2 border-l-accent' 
                        : 'hover:bg-ink-50'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-sm font-medium text-ink-900">
                        {interaction.interaction_id}
                      </span>
                      <span className={`text-label ${quality.color}`}>
                        {quality.label}
                      </span>
                    </div>
                    <p className="text-caption text-ink-500 mb-1">
                      {interaction.assigned_agent || 'Bot Only'} · {interaction.channel}
                    </p>
                    <p className="text-caption text-ink-400 truncate">
                      {interaction.customer_message ? interaction.customer_message.substring(0, 80) + '...' : 'No message'}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Conversation Viewer */}
        <div className="lg:col-span-2">
          {selectedConversation ? (
            <div className="bg-white border border-ink-200 rounded-lg">
              <div className="p-5 border-b border-ink-100">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="text-title text-ink-900">
                      {selectedConversation.interaction_id}
                    </h3>
                    <div className="flex items-center gap-4 mt-2 text-caption text-ink-500">
                      <span>{selectedConversation.assigned_agent || 'Bot Only'}</span>
                      <span>·</span>
                      <span>{selectedConversation.channel}</span>
                      <span>·</span>
                      <span>{selectedConversation.resolution_time_seconds ? `${selectedConversation.resolution_time_seconds}s` : 'N/A'}</span>
                      {selectedConversation.is_handoff && (
                        <span className="text-caution">Escalated</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex items-center">
                      <span className="text-sm font-medium text-ink-900">{selectedConversation.customer_satisfaction}</span>
                      <span className="text-caption text-ink-400 ml-1">/5</span>
                    </div>
                    {(() => {
                      const quality = getQualityLevel(calculateQualityScore(selectedConversation));
                      return (
                        <span className={`text-label ${quality.color}`}>
                          {quality.label}
                        </span>
                      );
                    })()}
                  </div>
                </div>
              </div>

              {/* Conversation Thread - The Emotional Anchor */}
              <div className="p-5">
                <div className="space-y-5 max-h-[420px] overflow-y-auto">
                  {Array.isArray(selectedConversation.conversation_history) && selectedConversation.conversation_history.map((message: ConversationMessage, index: number) => {
                    const isCustomer = message.speaker === 'customer';
                    const isBot = message.speaker === 'bot' || message.speaker === 'agent';
                    
                    return (
                      <div key={index} className={`flex gap-3 ${isCustomer ? 'flex-row-reverse' : ''}`}>
                        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                          isCustomer 
                            ? 'bg-ink-800' 
                            : isBot 
                            ? 'bg-accent'
                            : 'bg-positive'
                        }`}>
                          {isCustomer ? (
                            <User size={14} className="text-white" />
                          ) : isBot ? (
                            <Bot size={14} className="text-white" />
                          ) : (
                            <User size={14} className="text-white" />
                          )}
                        </div>
                        <div className={`flex-1 max-w-[75%] ${isCustomer ? 'text-right' : ''}`}>
                          <div className={`flex items-center gap-2 mb-1 ${isCustomer ? 'justify-end' : ''}`}>
                            <span className="text-caption font-medium text-ink-700">
                              {message.speaker === 'customer' ? 'Customer' : message.speaker === 'bot' ? 'Bot' : 'Agent'}
                            </span>
                            {message.detected_emotion && (
                              <span className={`text-caption ${getEmotionColor(message.detected_emotion)}`}>
                                {message.detected_emotion}
                              </span>
                            )}
                          </div>
                          <div className={`inline-block px-4 py-3 rounded-lg ${
                            isCustomer 
                              ? 'bg-ink-100 text-ink-900' 
                              : 'bg-ink-50 text-ink-800 border border-ink-200'
                          }`}>
                            <p className="text-body leading-relaxed">{message.message_text || 'No message'}</p>
                          </div>
                          <p className="text-caption text-ink-400 mt-1">
                            {(() => {
                              try {
                                return message.timestamp ? new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'N/A';
                              } catch {
                                return 'Invalid time';
                              }
                            })()}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Conversation Analysis */}
                <div className="mt-6 pt-5 border-t border-ink-100">
                  <h4 className="text-sm font-medium text-ink-700 mb-4">Analysis</h4>
                  <div className="grid grid-cols-2 gap-x-8 gap-y-3">
                    <div className="flex justify-between">
                      <span className="text-caption text-ink-500">Outcome</span>
                      <span className={`text-caption font-medium ${selectedConversation.success ? 'text-positive' : 'text-negative'}`}>
                        {selectedConversation.success ? 'Successful' : 'Unsuccessful'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-caption text-ink-500">Response Time</span>
                      <span className="text-caption font-medium text-ink-700">{selectedConversation.execution_time_ms}ms</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-caption text-ink-500">Intent</span>
                      <span className="text-caption font-medium text-ink-700">{selectedConversation.intent.replace('_', ' ')}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-caption text-ink-500">Urgency</span>
                      <span className="text-caption font-medium text-ink-700">{selectedConversation.urgency}</span>
                    </div>
                  </div>
                  {selectedConversation.feedback_comment && (
                    <div className="mt-4 p-3 bg-ink-50 rounded-md">
                      <span className="text-caption text-ink-500">Feedback:</span>
                      <p className="text-caption text-ink-700 mt-1">{selectedConversation.feedback_comment}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white border border-ink-200 rounded-lg p-12 text-center">
              <MessageSquare className="mx-auto text-ink-300 mb-4" size={40} />
              <h3 className="text-title text-ink-700 mb-2">Select a Conversation</h3>
              <p className="text-body text-ink-500">Choose a conversation from the list to view details</p>
            </div>
          )}
        </div>
      </div>

      {/* Learning Insights - Subtle, editorial */}
      <div className="mt-8 border-t border-ink-200 pt-8">
        <h3 className="text-title text-ink-900 mb-5">Learning Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <div className="flex items-center mb-3">
              <div className="w-1 h-4 bg-positive rounded mr-3"></div>
              <h4 className="text-sm font-medium text-ink-800">Success Patterns</h4>
            </div>
            <ul className="text-caption text-ink-600 space-y-2">
              <li>Quick acknowledgment of customer concerns</li>
              <li>Offering compensation for inconvenience</li>
              <li>Clear explanation of next steps</li>
              <li>Emotional de-escalation techniques</li>
            </ul>
          </div>
          
          <div>
            <div className="flex items-center mb-3">
              <div className="w-1 h-4 bg-negative rounded mr-3"></div>
              <h4 className="text-sm font-medium text-ink-800">Common Issues</h4>
            </div>
            <ul className="text-caption text-ink-600 space-y-2">
              <li>Delayed response to customer frustration</li>
              <li>Complex authentication processes</li>
              <li>Lack of proactive communication</li>
              <li>Insufficient escalation criteria</li>
            </ul>
          </div>
          
          <div>
            <div className="flex items-center mb-3">
              <div className="w-1 h-4 bg-accent rounded mr-3"></div>
              <h4 className="text-sm font-medium text-ink-800">Best Practices</h4>
            </div>
            <ul className="text-caption text-ink-600 space-y-2">
              <li>Empathy in first response</li>
              <li>Solution-focused language</li>
              <li>Follow-up confirmation</li>
              <li>Clear escalation handoffs</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConversationQualitySection;