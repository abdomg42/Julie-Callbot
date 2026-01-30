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

  const getQualityLevel = (score: number): { label: string; cls: string } => {
    if (score >= 75) return { label: 'Excellent', cls: badge('green') };
    if (score >= 50) return { label: 'Good', cls: badge('blue') };
    return { label: 'Needs Improvement', cls: badge('amber') };
  };

  const getEmotionColor = (emotion: string): string => {
    switch (emotion) {
      case 'positive':
      case 'satisfied':
        return 'text-positive';
      case 'neutral':
        return 'text-ink-500';
      case 'frustrated':
      case 'stressed':
      case 'negative':
        return 'text-negative';
      default:
        return 'text-ink-500';
    }
  };

  const filteredInteractions = interactions.filter(interaction => {
    const qualityScore = calculateQualityScore(interaction);
    const matchesFilter =
      filterByQuality === 'all' ||
      (filterByQuality === 'good' && qualityScore >= 75) ||
      (filterByQuality === 'poor' && qualityScore < 50);

    const matchesSearch =
      searchTerm === '' ||
      (interaction.customer_message &&
        interaction.customer_message.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (interaction.assigned_agent && interaction.assigned_agent.toLowerCase().includes(searchTerm.toLowerCase()));

    return matchesFilter && matchesSearch;
  });

  const goodConversations = interactions.filter(i => calculateQualityScore(i) >= 75);
  const poorConversations = interactions.filter(i => calculateQualityScore(i) < 50);

  const card =
    'bg-white border border-ink-200/70 rounded-2xl shadow-[0_10px_30px_rgba(15,23,42,0.06)]';

  return (
    <div className="min-h-screen bg-ink-50">
      <div className="px-8 py-6">
        <div className="mb-8">
          <h1 className="text-display text-ink-900">Conversations</h1>
          <p className="text-body text-ink-500 mt-1">
            Analyze conversations to improve agent performance
          </p>
        </div>

        {/* Quality Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className={`${card} px-6 py-5`}>
            <span className="text-label text-ink-500 tracking-wide">Total Conversations</span>
            <div className="text-3xl font-semibold text-ink-900 mt-3">{interactions.length}</div>
          </div>

          <div className={`${card} px-6 py-5`}>
            <span className="text-label text-ink-500 tracking-wide">High Quality</span>
            <div className="text-3xl font-semibold text-positive mt-3">{goodConversations.length}</div>
            <p className="text-caption text-ink-500 mt-2">
              {interactions.length ? ((goodConversations.length / interactions.length) * 100).toFixed(1) : '0.0'}% of total
            </p>
          </div>

          <div className={`${card} px-6 py-5`}>
            <span className="text-label text-ink-500 tracking-wide">Needs Improvement</span>
            <div className="text-3xl font-semibold text-negative mt-3">{poorConversations.length}</div>
            <p className="text-caption text-ink-500 mt-2">
              {interactions.length ? ((poorConversations.length / interactions.length) * 100).toFixed(1) : '0.0'}% of total
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Conversation List */}
          <div className="lg:col-span-1">
            <div className={`${card} overflow-hidden`}>
              <div className="px-6 py-5 border-b border-ink-200/70 bg-ink-50">
                <h3 className="text-title text-ink-900">Conversations</h3>
                <p className="text-caption text-ink-500 mt-1">
                  Search and filter by quality
                </p>

                {/* Search and Filter */}
                <div className="mt-4 space-y-3">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-400" size={16} />
                    <input
                      type="text"
                      placeholder="Search conversations..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className={[
                        'w-full pl-10 pr-3 py-2.5',
                        'border border-ink-200/70 rounded-xl',
                        'text-sm text-ink-900 placeholder-ink-400',
                        'bg-white',
                        'focus:outline-none focus:ring-2 focus:ring-accent/20 focus:border-accent/60',
                      ].join(' ')}
                    />
                  </div>

                  <select
                    value={filterByQuality}
                    onChange={(e) => setFilterByQuality(e.target.value as 'all' | 'good' | 'poor')}
                    className={[
                      'w-full px-3 py-2.5',
                      'border border-ink-200/70 rounded-xl',
                      'text-sm text-ink-700 bg-white',
                      'focus:outline-none focus:ring-2 focus:ring-accent/20 focus:border-accent/60',
                    ].join(' ')}
                  >
                    <option value="all">All Conversations</option>
                    <option value="good">High Quality</option>
                    <option value="poor">Needs Improvement</option>
                  </select>
                </div>
              </div>

              <div className="max-h-[540px] overflow-y-auto">
                {filteredInteractions.map((interaction) => {
                  const qualityScore = calculateQualityScore(interaction);
                  const quality = getQualityLevel(qualityScore);

                  const isSelected = selectedConversation?.interaction_id === interaction.interaction_id;

                  return (
                    <button
                      key={interaction.interaction_id}
                      onClick={() => setSelectedConversation(interaction)}
                      className={[
                        'w-full text-left px-6 py-4',
                        'border-b border-ink-100',
                        'transition-subtle',
                        isSelected ? 'bg-accent/5' : 'hover:bg-ink-50/70',
                      ].join(' ')}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <div className="flex items-center gap-2">
                            {isSelected && <span className="h-2 w-2 rounded-full bg-accent" />}
                            <span className="text-sm font-semibold text-ink-900 truncate">
                              {interaction.interaction_id}
                            </span>
                          </div>
                          <p className="text-caption text-ink-500 mt-1">
                            {interaction.assigned_agent || 'Bot Only'} · {interaction.channel}
                          </p>
                        </div>

                        <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${quality.cls}`}>
                          {quality.label}
                        </span>
                      </div>

                      <p className="text-caption text-ink-400 mt-2 truncate">
                        {interaction.customer_message
                          ? interaction.customer_message.substring(0, 80) + (interaction.customer_message.length > 80 ? '...' : '')
                          : 'No message'}
                      </p>
                    </button>
                  );
                })}

                {filteredInteractions.length === 0 && (
                  <div className="px-6 py-10 text-ink-500">
                    No conversations match your filters.
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Conversation Viewer */}
          <div className="lg:col-span-2">
            {selectedConversation ? (
              <div className={`${card} overflow-hidden`}>
                <div className="px-6 py-5 border-b border-ink-200/70 bg-ink-50">
                  <div className="flex justify-between items-start gap-6">
                    <div>
                      <h3 className="text-title text-ink-900">{selectedConversation.interaction_id}</h3>

                      <div className="flex flex-wrap items-center gap-2 mt-3 text-caption text-ink-500">
                        <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${badge('gray')}`}>
                          {selectedConversation.assigned_agent || 'Bot Only'}
                        </span>
                        <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${badge('blue')}`}>
                          {selectedConversation.channel}
                        </span>
                        <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${badge('gray')}`}>
                          {selectedConversation.resolution_time_seconds ? `${selectedConversation.resolution_time_seconds}s` : 'N/A'}
                        </span>

                        {selectedConversation.is_handoff && (
                          <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${badge('amber')}`}>
                            Escalated
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${badge('gray')}`}>
                        <span className="text-ink-900 font-semibold">{selectedConversation.customer_satisfaction}</span>
                        <span className="text-ink-400 ml-1">/5</span>
                      </div>

                      {(() => {
                        const quality = getQualityLevel(calculateQualityScore(selectedConversation));
                        return (
                          <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${quality.cls}`}>
                            {quality.label}
                          </span>
                        );
                      })()}
                    </div>
                  </div>
                </div>

                {/* Conversation Thread */}
                <div className="px-6 py-5">
                  <div className="space-y-5 max-h-[440px] overflow-y-auto pr-1">
                    {Array.isArray(selectedConversation.conversation_history) &&
                      selectedConversation.conversation_history.map((message: ConversationMessage, index: number) => {
                        const isCustomer = message.speaker === 'customer';
                        const isBot = message.speaker === 'bot' || message.speaker === 'agent';

                        return (
                          <div key={index} className={`flex gap-3 ${isCustomer ? 'flex-row-reverse' : ''}`}>
                            {/* Avatar */}
                            <div
                              className={[
                                'flex-shrink-0 h-9 w-9 rounded-2xl flex items-center justify-center',
                                isCustomer
                                  ? 'bg-ink-900'
                                  : isBot
                                  ? 'bg-accent'
                                  : 'bg-positive',
                              ].join(' ')}
                            >
                              {isCustomer ? (
                                <User size={14} className="text-white" />
                              ) : isBot ? (
                                <Bot size={14} className="text-white" />
                              ) : (
                                <User size={14} className="text-white" />
                              )}
                            </div>

                            <div className={`flex-1 max-w-[78%] ${isCustomer ? 'text-right' : ''}`}>
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

                              <div
                                className={[
                                  'inline-block px-4 py-3 rounded-2xl',
                                  isCustomer
                                    ? 'bg-ink-100 text-ink-900'
                                    : 'bg-white text-ink-800 border border-ink-200/70 shadow-[0_8px_24px_rgba(15,23,42,0.05)]',
                                ].join(' ')}
                              >
                                <p className="text-body leading-relaxed">
                                  {message.message_text || 'No message'}
                                </p>
                              </div>

                              <p className="text-caption text-ink-400 mt-1">
                                {(() => {
                                  try {
                                    return message.timestamp
                                      ? new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                                      : 'N/A';
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
                  <div className="mt-6 pt-5 border-t border-ink-200/70">
                    <h4 className="text-sm font-semibold text-ink-800 mb-4">Analysis</h4>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div className="flex items-center justify-between rounded-xl border border-ink-200/70 bg-white px-4 py-3">
                        <span className="text-caption text-ink-500">Outcome</span>
                        <span className={`text-caption font-semibold ${selectedConversation.success ? 'text-positive' : 'text-negative'}`}>
                          {selectedConversation.success ? 'Successful' : 'Unsuccessful'}
                        </span>
                      </div>

                      <div className="flex items-center justify-between rounded-xl border border-ink-200/70 bg-white px-4 py-3">
                        <span className="text-caption text-ink-500">Response Time</span>
                        <span className="text-caption font-semibold text-ink-700">
                          {selectedConversation.execution_time_ms ?? '—'}ms
                        </span>
                      </div>

                      <div className="flex items-center justify-between rounded-xl border border-ink-200/70 bg-white px-4 py-3">
                        <span className="text-caption text-ink-500">Intent</span>
                        <span className="text-caption font-semibold text-ink-700">
                          {(selectedConversation.intent || '—').replace('_', ' ')}
                        </span>
                      </div>

                      <div className="flex items-center justify-between rounded-xl border border-ink-200/70 bg-white px-4 py-3">
                        <span className="text-caption text-ink-500">Urgency</span>
                        <span className="text-caption font-semibold text-ink-700">
                          {selectedConversation.urgency ?? '—'}
                        </span>
                      </div>
                    </div>

                    {selectedConversation.feedback_comment && (
                      <div className="mt-4 rounded-2xl border border-ink-200/70 bg-ink-50 px-4 py-3">
                        <span className="text-caption text-ink-500">Feedback</span>
                        <p className="text-caption text-ink-700 mt-1">
                          {selectedConversation.feedback_comment}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className={`${card} px-10 py-14 text-center`}>
                <MessageSquare className="mx-auto text-ink-300 mb-4" size={40} />
                <h3 className="text-title text-ink-700 mb-2">Select a Conversation</h3>
                <p className="text-body text-ink-500">
                  Choose a conversation from the list to view details
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="h-6" />
      </div>
    </div>
  );
};

export default ConversationQualitySection;
