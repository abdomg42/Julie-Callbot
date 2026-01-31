import React from 'react';
import {
  BarChart3,
  Users,
  MessageSquare,
  Heart,
  TrendingUp,
} from 'lucide-react';

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
    <aside
      className={[
        // Mobile collapsed / Desktop expanded
        'h-full flex flex-col',
        'w-[72px] md:w-[260px]',
        'bg-[#243248] py-6',
        'shadow-[inset_-1px_0_0_rgba(255,255,255,0.06)]',
      ].join(' ')}
    >
      {/* Brand */}
      <div className="px-4 md:px-5 mb-8">
        <div className="flex items-center gap-3">
          {/* <div className="w-11 h-11 rounded-2xl bg-white/10 flex items-center justify-center">
            <span className="text-white font-semibold text-lg leading-none">
            <img src="" alt="" />

            </span>
          </div> */}

          {/* hide on mobile */}
          <div className="hidden md:block">
            <div className="text-white font-semibold leading-tight">AI Dreamer</div>
            <div className="text-white/60 text-xs mt-0.5">Callbot Dashboard</div>
          </div>
        </div>
      </div>

      {/* Main nav */}
      <nav className="flex-1 px-3 md:px-4">
        <div className="flex flex-col gap-1.5">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() => onTabChange(item.id)}
                title={item.label}
                aria-label={item.label}
                className={[
                  'relative w-full h-11 rounded-2xl',
                  'flex items-center',
                  'px-3 md:px-3.5',
                  'transition-all',
                  isActive ? 'bg-white/10' : 'hover:bg-white/8',
                ].join(' ')}
              >
                {/* active left bar (desktop only looks best, but keep it always) */}
                <span
                  className={[
                    'absolute left-0 top-1/2 -translate-y-1/2',
                    'h-6 w-1 rounded-full',
                    isActive ? 'bg-[#6D5EF3]' : 'bg-transparent',
                  ].join(' ')}
                />

                {/* Icon */}
                <div
                  className={[
                    'w-10 h-10 rounded-2xl flex items-center justify-center',
                    isActive ? 'bg-[#6D5EF3] shadow-[0_10px_25px_rgba(109,94,243,0.35)]' : 'bg-transparent',
                  ].join(' ')}
                >
                  <Icon size={20} className={isActive ? 'text-white' : 'text-white/70'} />
                </div>

                {/* Label (hidden on mobile) */}
                <div className="hidden md:flex flex-col items-start ml-3 min-w-0">
                  <span className={['text-sm font-semibold truncate', isActive ? 'text-white' : 'text-white/80'].join(' ')}>
                    {item.label}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </nav>

      {/* Divider */}
      <div className="px-4 md:px-5 my-4">
        <div className="h-px bg-white/10" />
      </div>
    </aside>
  );
};

export default Sidebar;
