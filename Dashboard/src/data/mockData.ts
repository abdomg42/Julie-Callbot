import type { Interaction, ConversationMessage } from '../types/dashboard';

// Mock conversation histories
const conversationHistory1: ConversationMessage[] = [
  {
    speaker: 'customer',
    message_text: 'Hi, I need help with my order. It seems to be delayed.',
    timestamp: '2024-01-27T10:30:00Z',
    detected_emotion: 'neutral',
    confidence: 0.95,
    message_id: 'MSG-001',
    turn_number: 1
  },
  {
    speaker: 'bot',
    message_text: 'I understand you\'re concerned about your order delay. Let me check that for you right away. Could you please provide your order number?',
    timestamp: '2024-01-27T10:30:15Z',
    message_id: 'MSG-002',
    turn_number: 2
  },
  {
    speaker: 'customer',
    message_text: 'It\'s ORDER-12345. This is really frustrating, I needed this by today.',
    timestamp: '2024-01-27T10:30:45Z',
    detected_emotion: 'frustrated',
    confidence: 0.88,
    message_id: 'MSG-003',
    turn_number: 3
  },
  {
    speaker: 'agent',
    message_text: 'I completely understand your frustration, and I sincerely apologize for this inconvenience. I\'ve located your order ORDER-12345, and I can see it was indeed delayed due to a warehouse issue. Let me see what expedited shipping options we can offer you at no extra cost.',
    timestamp: '2024-01-27T10:31:00Z',
    message_id: 'MSG-004',
    turn_number: 4
  },
  {
    speaker: 'customer',
    message_text: 'Okay, thank you for looking into this so quickly.',
    timestamp: '2024-01-27T10:32:00Z',
    detected_emotion: 'neutral',
    confidence: 0.92,
    message_id: 'MSG-005',
    turn_number: 5
  },
  {
    speaker: 'agent',
    message_text: 'I\'ve arranged for overnight shipping at no charge, and your order will arrive tomorrow by 2 PM. I\'ve also applied a 20% discount to your account for the inconvenience. You\'ll receive a tracking number within the hour. Is there anything else I can help you with today?',
    timestamp: '2024-01-27T10:33:00Z',
    message_id: 'MSG-006',
    turn_number: 6
  },
  {
    speaker: 'customer',
    message_text: 'That\'s perfect! Thank you so much for the quick resolution and the discount. Great service!',
    timestamp: '2024-01-27T10:33:30Z',
    detected_emotion: 'satisfied',
    confidence: 0.96,
    message_id: 'MSG-007',
    turn_number: 7
  }
];

const conversationHistory2: ConversationMessage[] = [
  {
    speaker: 'customer',
    message_text: 'My account is locked and I can\'t access it',
    timestamp: '2024-01-27T14:20:00Z',
    detected_emotion: 'frustrated',
    confidence: 0.85,
    message_id: 'MSG-008',
    turn_number: 1
  },
  {
    speaker: 'bot',
    message_text: 'I can help unlock your account. Please verify your email.',
    timestamp: '2024-01-27T14:20:30Z',
    message_id: 'MSG-009',
    turn_number: 2
  },
  {
    speaker: 'customer',
    message_text: 'john.doe@email.com but this isn\'t working',
    timestamp: '2024-01-27T14:21:00Z',
    detected_emotion: 'frustrated',
    confidence: 0.78,
    message_id: 'MSG-010',
    turn_number: 3
  },
  {
    speaker: 'bot',
    message_text: 'Let me transfer you to a specialist.',
    timestamp: '2024-01-27T14:21:30Z',
    message_id: 'MSG-011',
    turn_number: 4
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
    status: 'completed',
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
        speaker: 'customer',
        message_text: 'I have a question about my last bill',
        timestamp: '2024-01-27T11:15:00Z',
        detected_emotion: 'neutral',
        confidence: 0.88,
        message_id: 'MSG-012',
        turn_number: 1
      },
      {
        speaker: 'bot',
        message_text: 'I can help you with billing questions. What would you like to know?',
        timestamp: '2024-01-27T11:15:15Z',
        message_id: 'MSG-013',
        turn_number: 2
      },
      {
        speaker: 'customer',
        message_text: 'Why was I charged extra this month?',
        timestamp: '2024-01-27T11:15:30Z',
        detected_emotion: 'neutral',
        confidence: 0.92,
        message_id: 'MSG-014',
        turn_number: 3
      },
      {
        speaker: 'bot',
        message_text: 'I see an additional service charge for premium support. This was added per your request last month.',
        timestamp: '2024-01-27T11:15:45Z',
        message_id: 'MSG-015',
        turn_number: 4
      }
    ],
    action_taken: 'provided_information',
    success: true,
    execution_time_ms: 1200,
    is_handoff: false,
    assigned_agent: undefined,
    status: 'completed',
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
    status: 'in_progress',
    ticket_status: 'assigned',
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
    status: 'completed',
    ticket_status: 'resolved',
    resolved_at: '2024-01-27T15:47:00Z',
    resolution_time_seconds: 120,
    customer_satisfaction: 5,
    metadata: { priority: 'low', department: 'sales' }
  }
];
