import type { Interaction, DashboardMetrics, AgentPerformance, ConversationMessage } from '../types/dashboard';

// Mock conversation histories
const conversationHistory1: ConversationMessage[] = [
  {
    timestamp: '2024-01-27T10:30:00Z',
    sender: 'customer',
    message: 'Hi, I need help with my order. It seems to be delayed.',
    emotion: 'neutral'
  },
  {
    timestamp: '2024-01-27T10:30:15Z',
    sender: 'bot',
    message: 'I understand you\'re concerned about your order delay. Let me check that for you right away. Could you please provide your order number?',
  },
  {
    timestamp: '2024-01-27T10:30:45Z',
    sender: 'customer',
    message: 'It\'s ORDER-12345. This is really frustrating, I needed this by today.',
    emotion: 'frustrated'
  },
  {
    timestamp: '2024-01-27T10:31:00Z',
    sender: 'agent',
    message: 'I completely understand your frustration, and I sincerely apologize for this inconvenience. I\'ve located your order ORDER-12345, and I can see it was indeed delayed due to a warehouse issue. Let me see what expedited shipping options we can offer you at no extra cost.',
  },
  {
    timestamp: '2024-01-27T10:32:00Z',
    sender: 'customer',
    message: 'Okay, thank you for looking into this so quickly.',
    emotion: 'neutral'
  },
  {
    timestamp: '2024-01-27T10:33:00Z',
    sender: 'agent',
    message: 'I\'ve arranged for overnight shipping at no charge, and your order will arrive tomorrow by 2 PM. I\'ve also applied a 20% discount to your account for the inconvenience. You\'ll receive a tracking number within the hour. Is there anything else I can help you with today?',
  },
  {
    timestamp: '2024-01-27T10:33:30Z',
    sender: 'customer',
    message: 'That\'s perfect! Thank you so much for the quick resolution and the discount. Great service!',
    emotion: 'satisfied'
  }
];

const conversationHistory2: ConversationMessage[] = [
  {
    timestamp: '2024-01-27T14:20:00Z',
    sender: 'customer',
    message: 'My account is locked and I can\'t access it',
    emotion: 'frustrated'
  },
  {
    timestamp: '2024-01-27T14:20:30Z',
    sender: 'bot',
    message: 'I can help unlock your account. Please verify your email.',
  },
  {
    timestamp: '2024-01-27T14:21:00Z',
    sender: 'customer',
    message: 'john.doe@email.com but this isn\'t working',
    emotion: 'frustrated'
  },
  {
    timestamp: '2024-01-27T14:21:30Z',
    sender: 'bot',
    message: 'Let me transfer you to a specialist.',
  },
];

// Mock interactions data
export const mockInteractions: Interaction[] = [
  {
    interaction_id: 'INT-001',
    created_at: '2024-01-27T10:30:00Z',
    session_id: 'SES-001',
    channel: 'chat',
    intent: 'order_inquiry',
    urgency: 'medium',
    emotion: 'frustrated',
    confidence: 0.95,
    customer_message: 'Hi, I need help with my order. It seems to be delayed.',
    bot_response: 'I understand you\'re concerned about your order delay. Let me check that for you right away.',
    conversation_history: conversationHistory1,
    action_taken: 'escalated_to_agent',
    success: true,
    execution_time_ms: 2500,
    is_handoff: true,
    handoff_reason: 'complex_issue',
    assigned_agent: 'Sarah Johnson',
    ticket_status: 'resolved',
    resolved_at: '2024-01-27T10:35:00Z',
    resolution_time_seconds: 300,
    customer_satisfaction: 5,
    feedback_comment: 'Great service! Quick resolution and compensation.',
    metadata: { priority: 'high', department: 'orders' }
  },
  {
    interaction_id: 'INT-002',
    created_at: '2024-01-27T11:15:00Z',
    session_id: 'SES-002',
    channel: 'phone',
    intent: 'billing_question',
    urgency: 'low',
    emotion: 'neutral',
    confidence: 0.88,
    customer_message: 'I have a question about my last bill',
    bot_response: 'I can help you with billing questions. What would you like to know?',
    conversation_history: [
      {
        timestamp: '2024-01-27T11:15:00Z',
        sender: 'customer',
        message: 'I have a question about my last bill',
        emotion: 'neutral'
      },
      {
        timestamp: '2024-01-27T11:15:15Z',
        sender: 'bot',
        message: 'I can help you with billing questions. What would you like to know?'
      },
      {
        timestamp: '2024-01-27T11:15:30Z',
        sender: 'customer',
        message: 'Why was I charged extra this month?',
        emotion: 'neutral'
      },
      {
        timestamp: '2024-01-27T11:15:45Z',
        sender: 'bot',
        message: 'I see an additional service charge for premium support. This was added per your request last month.'
      }
    ],
    action_taken: 'provided_information',
    success: true,
    execution_time_ms: 1200,
    is_handoff: false,
    assigned_agent: undefined,
    ticket_status: 'resolved',
    resolved_at: '2024-01-27T11:18:00Z',
    resolution_time_seconds: 180,
    customer_satisfaction: 4,
    metadata: { priority: 'low', department: 'billing' }
  },
  {
    interaction_id: 'INT-003',
    created_at: '2024-01-27T14:20:00Z',
    session_id: 'SES-003',
    channel: 'chat',
    intent: 'account_access',
    urgency: 'high',
    emotion: 'frustrated',
    confidence: 0.75,
    customer_message: 'My account is locked and I can\'t access it',
    bot_response: 'I can help unlock your account. Please verify your email.',
    conversation_history: conversationHistory2,
    action_taken: 'escalated_to_agent',
    success: false,
    execution_time_ms: 3500,
    is_handoff: true,
    handoff_reason: 'authentication_required',
    assigned_agent: 'Mike Chen',
    ticket_status: 'in_progress',
    customer_satisfaction: 2,
    feedback_comment: 'Process was too complicated and took too long',
    metadata: { priority: 'high', department: 'technical' }
  },
  {
    interaction_id: 'INT-004',
    created_at: '2024-01-27T15:45:00Z',
    session_id: 'SES-004',
    channel: 'email',
    intent: 'product_information',
    urgency: 'low',
    emotion: 'positive',
    confidence: 0.92,
    customer_message: 'Can you tell me about your premium features?',
    bot_response: 'I\'d be happy to explain our premium features. Here\'s what\'s included...',
    conversation_history: [
      {
        timestamp: '2024-01-27T15:45:00Z',
        sender: 'customer',
        message: 'Can you tell me about your premium features?',
        emotion: 'positive'
      },
      {
        timestamp: '2024-01-27T15:45:15Z',
        sender: 'bot',
        message: 'I\'d be happy to explain our premium features. Here\'s what\'s included: Advanced analytics, priority support, custom integrations, and unlimited storage.'
      }
    ],
    action_taken: 'provided_information',
    success: true,
    execution_time_ms: 800,
    is_handoff: false,
    ticket_status: 'resolved',
    resolved_at: '2024-01-27T15:47:00Z',
    resolution_time_seconds: 120,
    customer_satisfaction: 5,
    metadata: { priority: 'low', department: 'sales' }
  }
];

// Generate dashboard metrics from mock data
export function calculateDashboardMetrics(interactions: Interaction[]): DashboardMetrics {
  const total = interactions.length;
  const successful = interactions.filter(i => i.success).length;
  const handoffs = interactions.filter(i => i.is_handoff).length;
  const avgResponseTime = interactions.reduce((sum, i) => sum + i.execution_time_ms, 0) / total;
  const avgSatisfaction = interactions.reduce((sum, i) => sum + i.customer_satisfaction, 0) / total;
  
  const activeIssues = interactions.filter(i => i.ticket_status !== 'resolved' && i.ticket_status !== 'closed');
  
  return {
    totalInteractions: total,
    successRate: (successful / total) * 100,
    handoffRate: (handoffs / total) * 100,
    avgResponseTime: avgResponseTime,
    customerSatisfaction: avgSatisfaction,
    activeIssues: {
      low: activeIssues.filter(i => i.urgency === 'low').length,
      medium: activeIssues.filter(i => i.urgency === 'medium').length,
      high: activeIssues.filter(i => i.urgency === 'high').length,
      critical: activeIssues.filter(i => i.urgency === 'critical').length,
    }
  };
}

// Generate agent performance data
export function calculateAgentPerformance(interactions: Interaction[]): AgentPerformance[] {
  const agentMap = new Map<string, Interaction[]>();
  
  interactions.forEach(interaction => {
    if (interaction.assigned_agent) {
      if (!agentMap.has(interaction.assigned_agent)) {
        agentMap.set(interaction.assigned_agent, []);
      }
      agentMap.get(interaction.assigned_agent)!.push(interaction);
    }
  });
  
  return Array.from(agentMap.entries()).map(([agent_name, agentInteractions]) => {
    const total = agentInteractions.length;
    const resolved = agentInteractions.filter(i => i.success).length;
    const avgResolutionTime = agentInteractions
      .filter(i => i.resolution_time_seconds)
      .reduce((sum, i) => sum + (i.resolution_time_seconds || 0), 0) / total;
    const avgSatisfaction = agentInteractions.reduce((sum, i) => sum + i.customer_satisfaction, 0) / total;
    
    const handoffReasons = agentInteractions
      .filter(i => i.is_handoff && i.handoff_reason)
      .reduce((acc, i) => {
        const reason = i.handoff_reason!;
        acc[reason] = (acc[reason] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);
    
    return {
      agent_name,
      interactions_handled: total,
      resolution_rate: (resolved / total) * 100,
      avg_resolution_time: avgResolutionTime,
      customer_satisfaction: avgSatisfaction,
      top_handoff_reasons: Object.entries(handoffReasons)
        .map(([reason, count]) => ({ reason, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 3)
    };
  });
}