import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  Filler,
} from 'chart.js';
import { Bar, Pie, Line, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  Filler
);

interface ChartProps {
  type: 'bar' | 'pie' | 'line' | 'doughnut';
  data: any;
  options?: any;
  className?: string;
}

const Chart: React.FC<ChartProps> = ({ type, data, options = {}, className = '' }) => {
  // Figma-like base styling
  const baseOptions: any = {
    responsive: true,
    maintainAspectRatio: false,
    layout: { padding: { top: 6, right: 8, bottom: 6, left: 8 } },
    plugins: {
      legend: {
        display: true,
        position: 'right',
        align: 'center',
        labels: {
          usePointStyle: true,
          pointStyle: 'circle',
          boxWidth: 8,
          boxHeight: 8,
          padding: 14,
          color: '#64748B',
          font: { size: 12, weight: '500' },
        },
      },
      title: { display: false },
      tooltip: {
        enabled: true,
        backgroundColor: 'rgba(15, 23, 42, 0.92)',
        titleColor: '#FFFFFF',
        bodyColor: '#E2E8F0',
        padding: 12,
        cornerRadius: 12,
        displayColors: true,
        boxPadding: 6,
      },
    },
    elements: {
      // ✅ bar visuals: rounded top only (rectangle-like), flat bottom
      bar: {
        borderRadius: { topLeft: 10, topRight: 10, bottomLeft: 0, bottomRight: 0 },
        borderSkipped: 'bottom',
      },
      line: {
        borderWidth: 2,
        tension: 0.35,
      },
      point: {
        radius: 2,
        hoverRadius: 4,
      },
      arc: {
        borderWidth: 0,
      },
    },
    scales:
      type === 'bar' || type === 'line'
        ? {
            x: {
              grid: {
                color: 'rgba(148, 163, 184, 0.18)',
                borderDash: [4, 4],
                drawBorder: false,
              },
              ticks: {
                color: '#64748B',
                font: { size: 12, weight: '500' },
              },
            },
            y: {
              grid: {
                color: 'rgba(148, 163, 184, 0.18)',
                borderDash: [4, 4],
                drawBorder: false,
              },
              ticks: {
                color: '#94A3B8',
                font: { size: 12, weight: '500' },
                padding: 8,
              },
            },
          }
        : undefined,
  };

  // Merge so user options override base
  const mergedOptions = {
    ...baseOptions,
    ...options,
    plugins: {
      ...baseOptions.plugins,
      ...(options?.plugins ?? {}),
      legend: {
        ...baseOptions.plugins.legend,
        ...(options?.plugins?.legend ?? {}),
      },
      tooltip: {
        ...baseOptions.plugins.tooltip,
        ...(options?.plugins?.tooltip ?? {}),
      },
    },
    scales: options?.scales ?? baseOptions.scales,
    elements: {
      ...baseOptions.elements,
      ...(options?.elements ?? {}),
    },
  };

  // Apply dataset defaults without breaking existing dataset config
  const styledData = React.useMemo(() => {
    if (!data) return data;

    const datasets = (data.datasets || []).map((ds: any) => {
      if (type === 'bar') {
        return {
          ...ds,

          // ✅ make bars feel "thicker" across the full width
          categoryPercentage: ds.categoryPercentage ?? 0.85,
          barPercentage: ds.barPercentage ?? 0.95,

          // ✅ rectangle-like shape (rounded top only)
          borderRadius:
            ds.borderRadius ??
            { topLeft: 10, topRight: 10, bottomLeft: 0, bottomRight: 0 },
          borderSkipped: ds.borderSkipped ?? 'bottom',

          // ✅ avoid pill/capsule look: keep thickness reasonable
          // If you want EVEN thicker, increase barThickness/maxBarThickness.
          barThickness: ds.barThickness ?? 50,
          maxBarThickness: ds.maxBarThickness ?? 70,
        };
      }

      if (type === 'line') {
        return {
          ...ds,
          tension: ds.tension ?? 0.35,
          borderWidth: ds.borderWidth ?? 2,
          pointRadius: ds.pointRadius ?? 2,
          pointHoverRadius: ds.pointHoverRadius ?? 4,
          fill: ds.fill ?? false,
        };
      }

      if (type === 'doughnut' || type === 'pie') {
        return {
          ...ds,
          borderWidth: ds.borderWidth ?? 0,
        };
      }

      return ds;
    });

    return { ...data, datasets };
  }, [data, type]);

  const ChartComponent = {
    bar: Bar,
    pie: Pie,
    line: Line,
    doughnut: Doughnut,
  }[type];

  return (
    <div className={`relative w-full ${className}`}>
      <ChartComponent data={styledData} options={mergedOptions} />
    </div>
  );
};

export default Chart;
