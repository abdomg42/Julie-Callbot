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
  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
        },
      },
      title: {
        display: false,
      },
    },
    ...options,
  };

  const ChartComponent = {
    bar: Bar,
    pie: Pie,
    line: Line,
    doughnut: Doughnut,
  }[type];

  return (
    <div className={`${className}`}>
      <ChartComponent data={data} options={defaultOptions} />
    </div>
  );
};

export default Chart;