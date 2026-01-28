import React from 'react';
import { BarChart3, Users, MessageSquare, Heart, TrendingUp } from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  const menuItems = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'agents', label: 'Agent Performance', icon: Users },
    { id: 'conversations', label: 'Conversations', icon: MessageSquare },
    { id: 'experience', label: 'Customer Experience', icon: Heart },
    { id: 'operations', label: 'Operations', icon: TrendingUp },
  ];

  return (
    <div className="w-56 bg-ink-900 h-full flex flex-col">
      <div className="px-5 py-6">
        <h1 className="text-lg font-semibold text-white tracking-tight">
          CallBot
        </h1>
        <p className="text-xs text-ink-400 mt-0.5">Analytics</p>
      </div>
      
      <nav className="flex-1 px-3 mt-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`w-full flex items-center px-3 py-2.5 text-left rounded-md transition-subtle mb-1 ${
                isActive 
                  ? 'bg-ink-800 text-white' 
                  : 'text-ink-400 hover:text-ink-200 hover:bg-ink-800/50'
              }`}
            >
              <Icon 
                size={18} 
                className={`mr-3 ${
                  isActive ? 'text-accent' : 'text-ink-500'
                }`} 
              />
              <span className="text-sm font-medium">{item.label}</span>
            </button>
          );
        })}
      </nav>
      
      <div className="px-4 py-4 border-t border-ink-800">
        <div className="flex items-center">
          <div className="w-1.5 h-1.5 bg-positive rounded-full mr-2"></div>
          <span className="text-xs text-ink-400">Systems operational</span>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;