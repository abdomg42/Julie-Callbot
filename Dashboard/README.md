# CallBot Dashboard

A comprehensive React-based dashboard for monitoring customer support and call-bot performance analytics.

## Features

### Dashboard Sections

1. **Overview** - High-level system health and performance metrics
   - Total interactions, success rates, handoff rates
   - Average response times and customer satisfaction
   - Active issues by urgency level
   - System health indicators

2. **Agent Performance** - Individual agent analytics and coaching insights
   - Performance comparison across agents  
   - Resolution rates and response times
   - Customer satisfaction by agent
   - Top handoff reasons and coaching opportunities

3. **Conversation Quality & Learning** - The core learning component
   - Interactive conversation browser with quality scoring
   - Good vs poor conversation identification
   - Emotion journey analysis showing customer sentiment progression
   - Learning insights with success patterns and common issues
   - Best practice examples from high-performing conversations

4. **Customer Experience** - Customer-centric analytics
   - Emotion distribution and satisfaction trends
   - Channel performance comparison (chat, phone, email, SMS)
   - Intent vs satisfaction analysis
   - Customer feedback highlights

5. **Operational Performance** - System efficiency metrics
   - Response time distribution and trends
   - Handoff reasons analysis
   - Peak hours and load analysis
   - System confidence levels

## Technology Stack

- **Frontend**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Build Tool**: Vite
- **Charts**: Chart.js (ready to integrate)

## Data Structure

The dashboard uses a comprehensive data model including:
- `Interaction` records with conversation history
- Customer satisfaction and feedback
- Agent performance metrics
- System confidence and execution times
- Emotion tracking throughout conversations

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Development

The dashboard runs at `http://localhost:5173` in development mode.

## Key Learning Features

### Conversation Analysis
- **Quality Scoring**: Automated scoring based on satisfaction, success, response time, and emotion progression
- **Emotion Tracking**: Visualizes customer emotion changes throughout conversations
- **Success Patterns**: Identifies communication techniques that lead to positive outcomes
- **De-escalation Examples**: Shows how successful agents handle frustrated customers

### Agent Coaching
- **Best Practice Library**: High-quality conversation examples for training
- **Common Issues**: Identifies recurring problems and improvement areas  
- **Performance Insights**: Individual agent strengths and development opportunities
- **Collaborative Learning**: Anonymous sharing of effective techniques

## Dashboard Philosophy

This dashboard is designed with a **learning-first approach**:
- Focuses on improvement rather than punishment
- Provides actionable insights for agent development
- Emphasizes transparency and continuous learning
- Supports both individual and team growth

## Customization

The dashboard is built with modularity in mind:
- Easy to add new metrics and visualizations
- Configurable data sources
- Extensible section architecture
- Responsive design for all devices
