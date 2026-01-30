import React from 'react';
import { BarChart3, Users, MessageSquare, Heart, TrendingUp, Settings, Menu } from 'lucide-react';

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
    <aside className="w-20 bg-slate-900 h-full flex flex-col items-center py-4">
      {/* Brand */}
      <div className="w-12 h-12 rounded-2xl bg-slate-800 flex items-center justify-center mb-6">
        <span className="text-white font-semibold text-lg">V</span>
      </div>

      {/* Main nav */}
      <nav className="flex-1 w-full flex flex-col items-center gap-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              title={item.label}
              className={[
                'w-12 h-12 rounded-2xl flex items-center justify-center transition-all',
                isActive
                  ? 'bg-violet-600 shadow-md'
                  : 'bg-transparent hover:bg-slate-800',
              ].join(' ')}
            >
              <Icon
                size={22}
                className={isActive ? 'text-white' : 'text-slate-300'}
              />
            </button>
          );
        })}
      </nav>

      {/* Bottom actions (like the Figma screens) */}
      <div className="w-full flex flex-col items-center gap-2 pb-3">
        <button
          className="w-12 h-12 rounded-2xl flex items-center justify-center hover:bg-slate-800 transition-all"
          title="Settings"
          onClick={() => onTabChange('overview')} // change if you have a settings tab later
        >
          <Settings size={22} className="text-slate-300" />
        </button>

        <button
          className="w-12 h-12 rounded-2xl flex items-center justify-center hover:bg-slate-800 transition-all"
          title="Menu"
        >
          <Menu size={22} className="text-slate-300" />
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
