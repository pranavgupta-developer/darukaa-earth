/**
 * Analytics dashboard component.
 *
 * Displays time-series charts and summary metrics for a selected site.
 * Uses Chart.js for interactive data visualization.
 */

import React, { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { analyticsService } from '../../services/analyticsService';
import type { SiteAnalyticsResponse } from '../../types';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

interface AnalyticsDashboardProps {
  siteId: string;
}

const METRIC_CONFIG = {
  ndvi: { label: 'NDVI', color: '#10b981', unit: '' },
  carbon_sequestration_tons: { label: 'Carbon Seq.', color: '#f59e0b', unit: 'tons' },
  biodiversity_index: { label: 'Biodiversity', color: '#8b5cf6', unit: '' },
  canopy_cover_pct: { label: 'Canopy Cover', color: '#06b6d4', unit: '%' },
} as const;

type MetricKey = keyof typeof METRIC_CONFIG;

const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ siteId }) => {
  const [analytics, setAnalytics] = useState<SiteAnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeMetric, setActiveMetric] = useState<MetricKey>('ndvi');

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await analyticsService.getSiteAnalytics(siteId);
        setAnalytics(data);
      } catch {
        setError('Failed to load analytics');
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, [siteId]);

  if (loading) {
    return (
      <div className="analytics-loading">
        <div className="spinner spinner-sm" />
        <p>Loading analytics...</p>
      </div>
    );
  }

  if (error) {
    return <div className="alert alert-error alert-sm">{error}</div>;
  }

  if (!analytics || analytics.total_records === 0) {
    return (
      <div className="analytics-empty">
        <p className="text-muted">No analytics data available for this site.</p>
      </div>
    );
  }

  const metricConfig = METRIC_CONFIG[activeMetric];
  const labels = analytics.data.map((d) =>
    new Date(d.recorded_date).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
  );

  const chartData = {
    labels,
    datasets: [
      {
        label: metricConfig.label,
        data: analytics.data.map((d) => d[activeMetric]),
        borderColor: metricConfig.color,
        backgroundColor: `${metricConfig.color}20`,
        fill: true,
        tension: 0.3,
        pointRadius: 2,
        pointHoverRadius: 5,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#1e293b',
        titleColor: '#f8fafc',
        bodyColor: '#cbd5e1',
        padding: 12,
        cornerRadius: 8,
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(255,255,255,0.06)' },
        ticks: { color: '#94a3b8', maxTicksLimit: 8 },
      },
      y: {
        grid: { color: 'rgba(255,255,255,0.06)' },
        ticks: { color: '#94a3b8' },
      },
    },
  };

  const summary = analytics.summary[activeMetric];

  return (
    <div className="analytics-dashboard">
      <h3 className="analytics-title">📊 {analytics.site_name} — Analytics</h3>

      {/* Metric tabs */}
      <div className="metric-tabs">
        {(Object.keys(METRIC_CONFIG) as MetricKey[]).map((key) => (
          <button
            key={key}
            onClick={() => setActiveMetric(key)}
            className={`metric-tab ${activeMetric === key ? 'active' : ''}`}
            style={activeMetric === key ? { borderColor: METRIC_CONFIG[key].color } : {}}
          >
            {METRIC_CONFIG[key].label}
          </button>
        ))}
      </div>

      {/* Summary cards */}
      {summary && (
        <div className="summary-row">
          <div className="summary-card">
            <span className="summary-label">Latest</span>
            <span className="summary-value">
              {summary.latest_value?.toFixed(2) ?? 'N/A'} {metricConfig.unit}
            </span>
          </div>
          <div className="summary-card">
            <span className="summary-label">Average</span>
            <span className="summary-value">
              {summary.average?.toFixed(2) ?? 'N/A'} {metricConfig.unit}
            </span>
          </div>
          <div className="summary-card">
            <span className="summary-label">Trend</span>
            <span
              className={`summary-value ${
                summary.trend_pct != null && summary.trend_pct >= 0 ? 'trend-up' : 'trend-down'
              }`}
            >
              {summary.trend_pct != null ? `${summary.trend_pct > 0 ? '+' : ''}${summary.trend_pct}%` : 'N/A'}
            </span>
          </div>
        </div>
      )}

      {/* Chart */}
      <div className="chart-container">
        <Line data={chartData} options={chartOptions} />
      </div>

      <p className="analytics-meta">
        {analytics.total_records} records · {analytics.start_date} to {analytics.end_date}
      </p>
    </div>
  );
};

export default AnalyticsDashboard;
