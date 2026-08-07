import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { farmService, analyticsService } from '../services/api';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

export const HistoricalAnalyticsPage: React.FC = () => {
  const [period, setPeriod] = useState<'weekly' | 'monthly' | 'all'>('weekly');

  const { data: farmsData } = useQuery({
    queryKey: ['farms'],
    queryFn: () => farmService.getFarms(1, 50),
  });

  const firstFarm = farmsData?.items[0];

  const { data: analytics } = useQuery({
    queryKey: ['analytics', firstFarm?.id, period],
    queryFn: () => firstFarm ? analyticsService.getAnalytics(firstFarm.id, period) : Promise.reject(new Error('No farm available')),
    enabled: !!firstFarm,
  });

  const chartData = analytics?.data_points || [
    { date: 'Mon', ndvi: 0.65, ndwi: -0.05, stress_score: 22, temperature: 24, rainfall: 0 },
    { date: 'Tue', ndvi: 0.68, ndwi: -0.04, stress_score: 18, temperature: 26, rainfall: 2 },
    { date: 'Wed', ndvi: 0.62, ndwi: -0.08, stress_score: 35, temperature: 29, rainfall: 0 },
    { date: 'Thu', ndvi: 0.58, ndwi: -0.12, stress_score: 48, temperature: 31, rainfall: 0 },
    { date: 'Fri', ndvi: 0.54, ndwi: -0.15, stress_score: 62, temperature: 33, rainfall: 0 },
    { date: 'Sat', ndvi: 0.70, ndwi: 0.05, stress_score: 15, temperature: 25, rainfall: 14 },
    { date: 'Sun', ndvi: 0.72, ndwi: 0.08, stress_score: 12, temperature: 24, rainfall: 5 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-headline-lg font-headline-lg text-on-surface">Historical Analytics</h2>
          <p className="text-body-md text-on-surface-variant">
            Time-series data for NDVI vegetation, moisture stress score, and weather trends
          </p>
        </div>

        {/* Period Selector Tabs */}
        <div className="flex bg-surface-container rounded-xl p-1 border border-outline-variant/20">
          {(['weekly', 'monthly', 'all'] as const).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-1.5 rounded-lg text-label-sm font-semibold capitalize transition-all ${
                period === p
                  ? 'bg-surface-container-lowest text-primary shadow-sm'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Chart 1: Moisture Stress Score Trend */}
      <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/20 p-6 shadow-sm space-y-4">
        <h3 className="text-headline-md font-headline-md text-on-surface">Moisture Stress Index Trend</h3>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="stressGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ba1a1a" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#ba1a1a" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e3e6" />
              <XAxis dataKey="date" stroke="#707a6c" />
              <YAxis domain={[0, 100]} stroke="#707a6c" />
              <Tooltip />
              <Area type="monotone" dataKey="stress_score" stroke="#ba1a1a" strokeWidth={3} fillOpacity={1} fill="url(#stressGrad)" name="Stress Score (0-100)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Chart 2: NDVI vs NDWI Index */}
      <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/20 p-6 shadow-sm space-y-4">
        <h3 className="text-headline-md font-headline-md text-on-surface">NDVI (Vegetation) vs NDWI (Moisture)</h3>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e3e6" />
              <XAxis dataKey="date" stroke="#707a6c" />
              <YAxis domain={[-0.5, 1]} stroke="#707a6c" />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="ndvi" stroke="#0d631b" strokeWidth={3} dot={{ r: 4 }} name="NDVI" />
              <Line type="monotone" dataKey="ndwi" stroke="#00569f" strokeWidth={3} dot={{ r: 4 }} name="NDWI" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Chart 3: Temperature vs Rainfall */}
      <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/20 p-6 shadow-sm space-y-4">
        <h3 className="text-headline-md font-headline-md text-on-surface">Temperature & Rainfall Correlation</h3>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e3e6" />
              <XAxis dataKey="date" stroke="#707a6c" />
              <YAxis yAxisId="left" stroke="#0d631b" />
              <YAxis yAxisId="right" orientation="right" stroke="#00569f" />
              <Tooltip />
              <Legend />
              <Bar yAxisId="left" dataKey="temperature" fill="#2e7d32" radius={[4, 4, 0, 0]} name="Temp (°C)" />
              <Bar yAxisId="right" dataKey="rainfall" fill="#006eca" radius={[4, 4, 0, 0]} name="Rainfall (mm)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
