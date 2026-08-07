import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '../services/api';
import { StressMap } from '../components/StressMap';
import { Link } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const { data: dashboard, isLoading, isError } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardService.getDashboard,
    refetchInterval: 30000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-3">
          <span className="material-symbols-outlined text-4xl text-primary animate-spin">sync</span>
          <span className="text-label-md text-on-surface-variant">Loading AgriNova Dashboard...</span>
        </div>
      </div>
    );
  }

  const kpis = dashboard?.kpis || [
    { label: 'Healthy Area', value: '82%', trend: '+2.4% vs last cycle', trend_direction: 'up' },
    { label: 'Moderate Stress', value: '12%', trend: 'Stable', trend_direction: 'stable' },
    { label: 'Critical Stress', value: '6%', trend: '-1.2% vs last cycle', trend_direction: 'down' },
    { label: 'Water Saved', value: '450k L', trend: '+15% efficiency', trend_direction: 'up' },
  ];

  const latestPred = dashboard?.latest_prediction;
  const latestWeather = dashboard?.latest_weather;
  const latestSat = dashboard?.latest_satellite;

  return (
    <div className="space-y-section-gap">
      {/* Top Metrics Scrollable Cards */}
      <section>
        <div className="flex overflow-x-auto no-scrollbar gap-4 pb-2 -mx-gutter px-gutter md:mx-0 md:px-0">
          {kpis.map((kpi, idx) => (
            <div
              key={idx}
              className="flex-none w-64 bg-surface-container-lowest rounded-xl p-4 border border-outline-variant/10 shadow-sm hover:-translate-y-0.5 hover:shadow-md transition-all duration-300"
            >
              <div className="flex justify-between items-start mb-2">
                <span className="text-label-md font-label-md text-on-surface-variant">{kpi.label}</span>
                <span
                  className={`material-symbols-outlined ${
                    idx === 0
                      ? 'text-primary-container'
                      : idx === 1
                      ? 'text-[#F59E0B]'
                      : idx === 2
                      ? 'text-error'
                      : 'text-tertiary-container'
                  }`}
                  style={{ fontVariationSettings: "'FILL' 1" }}
                >
                  {idx === 0 ? 'eco' : idx === 1 ? 'warning' : idx === 2 ? 'error' : 'water_drop'}
                </span>
              </div>
              <div className="text-headline-lg font-headline-lg text-on-surface mb-1">{kpi.value}</div>
              <div
                className={`text-label-sm font-label-sm flex items-center gap-1 ${
                  kpi.trend_direction === 'up'
                    ? 'text-primary'
                    : kpi.trend_direction === 'down'
                    ? 'text-error'
                    : 'text-on-surface-variant'
                }`}
              >
                <span className="material-symbols-outlined text-[14px]">
                  {kpi.trend_direction === 'up'
                    ? 'arrow_upward'
                    : kpi.trend_direction === 'down'
                    ? 'arrow_downward'
                    : 'horizontal_rule'}
                </span>
                {kpi.trend}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Bento Grid for Map, Insights, and Weather */}
      <section className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Map Area (Spans 8 cols on desktop) */}
        <div className="md:col-span-8">
          <StressMap satelliteData={latestSat} />
        </div>

        {/* Insights and Weather (Spans 4 cols on desktop) */}
        <div className="md:col-span-4 flex flex-col gap-6">
          {/* AI Insight Card */}
          <div className="bg-gradient-to-br from-primary-container/10 to-transparent rounded-xl border border-primary/20 p-6 shadow-sm relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-2xl group-hover:bg-primary/10 transition-colors duration-500" />
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-primary-container text-on-primary-container flex items-center justify-center shadow-sm">
                <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
                  psychology
                </span>
              </div>
              <h3 className="text-label-md font-label-md font-semibold text-primary">AgriNova Insight</h3>
            </div>
            <p className="text-body-md font-body-md text-on-surface-variant leading-relaxed mb-4">
              {latestPred?.recommendation ||
                'AI predicts moderate moisture stress in the western section of your farm within the next 72 hours.'}
            </p>
            <Link
              to="/recommendations"
              className="block w-full text-center py-2.5 bg-primary text-on-primary rounded-lg text-label-md font-label-md shadow-sm hover:opacity-90 hover:shadow-md transition-all"
            >
              Review Irrigation Plan
            </Link>
          </div>

          {/* Weather Widget */}
          <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/10 shadow-sm p-6 flex flex-col justify-between flex-grow">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className="text-headline-md font-headline-md text-on-surface">Central Sector</h3>
                <p className="text-label-md font-label-md text-on-surface-variant">Current Conditions</p>
              </div>
              <span
                className="material-symbols-outlined text-tertiary-container text-4xl"
                style={{ fontVariationSettings: "'FILL' 1" }}
              >
                cloud
              </span>
            </div>
            <div className="flex justify-between items-end">
              <div className="text-display-lg font-display-lg text-on-surface">
                {latestWeather?.temperature != null ? `${latestWeather.temperature}°` : '24°'}
              </div>
              <div className="flex gap-4 text-on-surface-variant">
                <div className="flex flex-col items-center gap-1">
                  <span className="material-symbols-outlined text-[20px]">humidity_percentage</span>
                  <span className="text-label-sm font-label-sm">
                    {latestWeather?.humidity != null ? `${latestWeather.humidity}%` : '68%'}
                  </span>
                </div>
                <div className="flex flex-col items-center gap-1">
                  <span className="material-symbols-outlined text-[20px]">water_drop</span>
                  <span className="text-label-sm font-label-sm">
                    {latestWeather?.rainfall_24h != null ? `${latestWeather.rainfall_24h}mm` : '0mm'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
