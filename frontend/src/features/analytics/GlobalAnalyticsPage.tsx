import React, { useEffect, useState, useMemo } from 'react';
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
import Navbar from '../../components/Navbar';
import { analyticsService } from '../../services/analyticsService';
import { projectService } from '../../services/projectService';
import type { GlobalAnalyticsResponse, Project } from '../../types';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

const METRIC_CONFIG = {
  ndvi: { label: 'NDVI Trends', color: '#10b981', unit: '' },
  carbon_sequestration_tons: { label: 'Carbon Sequestration Trends', color: '#f59e0b', unit: 'tons' },
  biodiversity_index: { label: 'Biodiversity Trends', color: '#8b5cf6', unit: '' },
  canopy_cover_pct: { label: 'Canopy Cover Trends', color: '#06b6d4', unit: '%' },
} as const;

type MetricKey = keyof typeof METRIC_CONFIG;

// A distinct color palette for multiple comparison lines
const CHART_COLORS = [
  '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#14b8a6', '#f97316'
];

const GlobalAnalyticsPage: React.FC = () => {
  const [data, setData] = useState<GlobalAnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filter states
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjects, setSelectedProjects] = useState<string[]>([]);
  const [projectTypes, setProjectTypes] = useState<string[]>([]);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [compareBy, setCompareBy] = useState<'site' | 'project'>('project');
  
  const [activeMetric, setActiveMetric] = useState<MetricKey>('ndvi');

  // Fetch projects for filter dropdown
  useEffect(() => {
    projectService.list().then(res => setProjects(res.projects)).catch(console.error);
  }, []);

  const fetchGlobalAnalytics = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await analyticsService.getGlobalAnalytics({
        projectIds: selectedProjects.length > 0 ? selectedProjects : undefined,
        projectTypes: projectTypes.length > 0 ? projectTypes : undefined,
        startDate: startDate || undefined,
        endDate: endDate || undefined,
        compareBy,
      });
      setData(res);
    } catch (e: any) {
      console.error("Global Analytics Error:", e);
      let errMsg = 'Failed to load global analytics';
      if (e.response?.data?.detail) {
        errMsg = typeof e.response.data.detail === 'string' ? e.response.data.detail : JSON.stringify(e.response.data.detail);
      } else if (e.message) {
        errMsg = e.message;
      }
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGlobalAnalytics();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedProjects, projectTypes, startDate, endDate, compareBy]);

  const handleProjectToggle = (id: string) => {
    setSelectedProjects(prev => prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]);
  };

  const handleTypeToggle = (type: string) => {
    setProjectTypes(prev => prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]);
  };

  const chartData = useMemo(() => {
    if (!data || data.comparison_series.length === 0) return null;

    // Collect all unique dates across all series to form the X-axis labels
    const allDates = new Set<string>();
    data.comparison_series.forEach(series => {
      series.data.forEach(dp => {
        allDates.add(dp.recorded_date);
      });
    });
    const labels = Array.from(allDates).sort().map(d => 
      new Date(d).toLocaleDateString('en-US', { month: 'short', year: '2-digit' })
    );

    const datasets = data.comparison_series.map((series, idx) => {
      const color = CHART_COLORS[idx % CHART_COLORS.length];
      
      // Map data points by date for this series
      const dataMap = new Map();
      series.data.forEach(dp => {
        dataMap.set(dp.recorded_date, dp[activeMetric]);
      });

      // Construct array matching the unified labels array
      const mappedData = Array.from(allDates).sort().map(d => dataMap.get(d) ?? null);

      return {
        label: series.entity_name,
        data: mappedData,
        borderColor: color,
        backgroundColor: `${color}20`,
        fill: false,
        tension: 0.3,
        pointRadius: 3,
        pointHoverRadius: 6,
      };
    });

    return { labels, datasets };
  }, [data, activeMetric]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top' as const, labels: { color: '#94a3b8' } },
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
        ticks: { color: '#94a3b8', maxTicksLimit: 10 },
      },
      y: {
        grid: { color: 'rgba(255,255,255,0.06)' },
        ticks: { color: '#94a3b8' },
      },
    },
  };

  const AVAILABLE_TYPES = ['Carbon Sequestration', 'Biodiversity Conservation', 'Reforestation'];

  return (
    <div className="page-wrapper">
      <Navbar />
      <main className="dashboard-content">
        <header className="page-header">
          <div>
            <h1>Global Analytics</h1>
            <p className="text-muted">Cross-project environmental overview and comparison.</p>
          </div>
        </header>

        <div className="analytics-layout" style={{ display: 'grid', gridTemplateColumns: '250px 1fr', gap: '2rem', alignItems: 'start' }}>
          {/* Filters Sidebar */}
          <aside className="filters-panel" style={{ backgroundColor: '#1e293b', padding: '1.5rem', borderRadius: '8px' }}>
            <h3 style={{ marginTop: 0, marginBottom: '1rem', fontSize: '1.1rem' }}>Filters</h3>
            
            <div style={{ marginBottom: '1.5rem' }}>
              <label className="form-label">Compare By</label>
              <select className="form-input" value={compareBy} onChange={e => setCompareBy(e.target.value as any)}>
                <option value="project">Project</option>
                <option value="site">Site</option>
              </select>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label className="form-label">Date Range</label>
              <input type="date" className="form-input" style={{ marginBottom: '0.5rem' }} value={startDate} onChange={e => setStartDate(e.target.value)} />
              <input type="date" className="form-input" value={endDate} onChange={e => setEndDate(e.target.value)} />
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label className="form-label">Project Types</label>
              {AVAILABLE_TYPES.map(type => (
                <label key={type} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', fontSize: '0.9rem', color: '#cbd5e1' }}>
                  <input type="checkbox" checked={projectTypes.includes(type)} onChange={() => handleTypeToggle(type)} />
                  {type}
                </label>
              ))}
            </div>

            <div>
              <label className="form-label">Projects</label>
              {projects.map(p => (
                <label key={p.id} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', fontSize: '0.9rem', color: '#cbd5e1' }}>
                  <input type="checkbox" checked={selectedProjects.includes(p.id)} onChange={() => handleProjectToggle(p.id)} />
                  {p.name}
                </label>
              ))}
            </div>
          </aside>

          {/* Main Content */}
          <div className="analytics-main">
            {loading && !data ? (
              <div className="analytics-loading" style={{ padding: '3rem', textAlign: 'center' }}>
                <div className="spinner" />
                <p>Loading analytics...</p>
              </div>
            ) : error ? (
              <div className="alert alert-error">{error}</div>
            ) : data ? (
              <>
                {/* KPI Cards */}
                <div className="summary-row" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
                  <div className="summary-card" style={{ backgroundColor: '#1e293b' }}>
                    <span className="summary-label">Total Area Monitored</span>
                    <span className="summary-value" style={{ color: '#0ea5e9' }}>{data.kpis.total_monitored_area_ha} ha</span>
                  </div>
                  <div className="summary-card" style={{ backgroundColor: '#1e293b' }}>
                    <span className="summary-label">Total Carbon</span>
                    <span className="summary-value" style={{ color: METRIC_CONFIG.carbon_sequestration_tons.color }}>{data.kpis.total_carbon_sequestered} t</span>
                  </div>
                  <div className="summary-card" style={{ backgroundColor: '#1e293b' }}>
                    <span className="summary-label">Avg NDVI</span>
                    <span className="summary-value" style={{ color: METRIC_CONFIG.ndvi.color }}>{data.kpis.average_ndvi}</span>
                  </div>
                  <div className="summary-card" style={{ backgroundColor: '#1e293b' }}>
                    <span className="summary-label">Avg Biodiversity</span>
                    <span className="summary-value" style={{ color: METRIC_CONFIG.biodiversity_index.color }}>{data.kpis.average_biodiversity}</span>
                  </div>
                  <div className="summary-card" style={{ backgroundColor: '#1e293b' }}>
                    <span className="summary-label">Avg Canopy Cover</span>
                    <span className="summary-value" style={{ color: METRIC_CONFIG.canopy_cover_pct.color }}>{data.kpis.average_canopy_cover}%</span>
                  </div>
                </div>

                {/* Metric Selector for Charts */}
                <div className="metric-tabs" style={{ marginBottom: '1.5rem' }}>
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

                {/* Comparison Chart */}
                <div className="chart-container" style={{ backgroundColor: '#1e293b', padding: '1.5rem', borderRadius: '8px', minHeight: '400px' }}>
                  {chartData ? (
                    <Line data={chartData} options={chartOptions} />
                  ) : (
                    <p className="text-muted text-center" style={{ marginTop: '4rem' }}>No data available for the selected filters.</p>
                  )}
                </div>
              </>
            ) : null}
          </div>
        </div>
      </main>
    </div>
  );
};

export default GlobalAnalyticsPage;
