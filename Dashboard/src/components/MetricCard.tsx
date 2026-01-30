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
  const TrendIcon =
    trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;

  const trendTone =
    trend === 'up'
      ? {
          text: 'text-positive',
          bg: 'bg-positive/10',
          border: 'border-positive/15'
        }
      : trend === 'down'
      ? {
          text: 'text-negative',
          bg: 'bg-negative/10',
          border: 'border-negative/15'
        }
      : {
          text: 'text-ink-500',
          bg: 'bg-ink-100/70',
          border: 'border-ink-200/70'
        };

  return (
    <div
      className={[
        // Figma-like surface
        'bg-white',
        'border border-ink-200/70',
        'rounded-2xl',
        'px-6 py-5',
        'shadow-[0_10px_30px_rgba(15,23,42,0.06)]',
        'transition-subtle',
        'hover:border-ink-300/70 hover:shadow-[0_14px_40px_rgba(15,23,42,0.10)]',
        className
      ].join(' ')}
    >
      <div className="flex items-start justify-between gap-3">
        <span className="text-label text-ink-500 tracking-wide">
          {title}
        </span>

        {trend && trendValue && (
          <div
            className={[
              'inline-flex items-center',
              'rounded-full',
              'px-2.5 py-1',
              'border',
              trendTone.bg,
              trendTone.border,
              trendTone.text
            ].join(' ')}
          >
            <TrendIcon size={14} className="mr-1" />
            <span className="text-xs font-semibold">{trendValue}</span>
          </div>
        )}
      </div>

      <div className={['mt-3 text-3xl font-semibold tracking-tight', valueColor].join(' ')}>
        {value}
      </div>

      {subtitle && <p className="text-caption text-ink-500 mt-2">{subtitle}</p>}
    </div>
  );
};

export default MetricCard;
