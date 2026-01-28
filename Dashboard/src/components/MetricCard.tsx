import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: string;
  className?: string;
  valueColor?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  trendValue,
  className = '',
  valueColor = 'text-ink-900'
}) => {
  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;
  const trendColor = trend === 'up' ? 'text-positive' : trend === 'down' ? 'text-negative' : 'text-ink-400';

  return (
    <div className={`bg-white border border-ink-200 rounded-lg p-5 transition-subtle hover:border-ink-300 ${className}`}>
      <div className="flex items-start justify-between mb-3">
        <span className="text-label uppercase text-ink-500 tracking-wide">{title}</span>
        {trend && trendValue && (
          <div className={`flex items-center ${trendColor}`}>
            <TrendIcon size={14} className="mr-1" />
            <span className="text-xs font-medium">{trendValue}</span>
          </div>
        )}
      </div>
      <div className={`text-2xl font-semibold ${valueColor} tracking-tight`}>{value}</div>
      {subtitle && <p className="text-caption text-ink-500 mt-1">{subtitle}</p>}
    </div>
  );
};

export default MetricCard;