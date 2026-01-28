// Types for the dashboard data
export interface Interaction {
  interaction_id: string;
  created_at: string;
  session_id: string;
  channel: 'chat' | 'phone' | 'email' | 'sms';
  intent: string;
  urgency: 'low' | 'medium' | 'high' | 'critical';
  emotion: 'positive' | 'neutral' | 'negative' | 'frustrated' | 'satisfied';
  confidence: number;
  customer_message: string;
  bot_response: string;
  conversation_history: ConversationMessage[];
  action_taken: string;
  success: boolean;
  execution_time_ms: number;
  is_handoff: boolean;
  handoff_reason?: string;
  assigned_agent?: string;
  ticket_status: 'open' | 'in_progress' | 'resolved' | 'closed';
  resolved_at?: string;
  resolution_time_seconds?: number;
  customer_satisfaction: number; // 1-5 scale
  feedback_comment?: string;
  metadata: Record<string, any>;
}

export interface ConversationMessage {
  timestamp: string;
  sender: 'customer' | 'bot' | 'agent';
  message: string;
  emotion?: string;
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

export interface AgentPerformance {
  agent_name: string;
  interactions_handled: number;
  resolution_rate: number;
  avg_resolution_time: number;
  customer_satisfaction: number;
  top_handoff_reasons: { reason: string; count: number }[];
}