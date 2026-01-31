// Types for the dashboard data
export interface Interaction {
  interaction_id: string;
  created_at: string;
  updated_at?: string;
  customer_id?: string;
  customer_phone?: string;
  session_id: string;
  channel: 'chat' | 'phone' | 'email' | 'sms';
  intent: string;
  urgency: 'low' | 'medium' | 'high' | 'critical';
  emotion: 'positive' | 'neutral' | 'negative' | 'frustrated' | 'satisfied';
  confidence: number;
  customer_message: string;
  bot_response: string;
  conversation_history: ConversationMessage[] | null;
  action_taken: string;
  action_type?: string;
  success: boolean;
  execution_time_ms?: number;
  is_handoff: boolean;
  handoff_reason?: string;
  handoff_queue?: string;
  handoff_department?: string;
  assigned_agent?: string;
  ticket_status?: 'pending' | 'assigned' | 'queued' | 'resolved' | 'closed';
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  priority?: 'normal' | 'high';
  resolved_at?: string;
  resolution_time_seconds?: number;
  customer_satisfaction?: number; // 1-5 scale
  satisfaction_score?: 1 | 2 | null;
  feedback_comment?: string;
  metadata?: Record<string, any>;
}

export interface ConversationMessage {
  speaker: 'customer' | 'bot' | 'agent';
  message_text: string;
  timestamp: string;
  detected_emotion?: string;
  confidence?: number;
  message_id?: string;
  turn_number?: number;
  metadata?: Record<string, any>;
  detected_intent?: string;
}

export interface DashboardMetrics {
  totalInteractions: number;
  successRate: number;
  handoffRate: number;
  avgResponseTime: number;
  customerSatisfaction: number;
  activeIssues: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
}


export type AgentPerformance = {
  agent_name: string; // now this is intent string
  interactions_handled: number;
  resolution_rate: number;
  avg_resolution_time: number;
  customer_satisfaction: number;
  satisfied_rate_pct?: number;
  feedback_rate_pct?: number;
  top_handoff_reasons: { reason: string; count: number }[];
};
