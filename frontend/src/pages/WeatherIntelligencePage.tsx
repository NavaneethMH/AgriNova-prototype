import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { farmService, weatherService } from '../services/api';

export const WeatherIntelligencePage: React.FC = () => {
  const { data: farmsData } = useQuery({
    queryKey: ['farms'],
    queryFn: () => farmService.getFarms(1, 50),
  });

  const firstFarm = farmsData?.items[0];

  const { data: weather } = useQuery({
    queryKey: ['weather', firstFarm?.id],
    queryFn: () => weatherService.getWeather(firstFarm!.id),
    enabled: !!firstFarm,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-headline-lg font-headline-lg text-on-surface">Weather Intelligence</h2>
        <p className="text-body-md text-on-surface-variant">Real-time microclimate observations and forecast data</p>
      </div>

      {/* Current Conditions Header Card */}
      <div className="bg-gradient-to-r from-primary-container to-tertiary-container text-white rounded-2xl p-8 shadow-lg relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div>
            <span className="inline-block px-3 py-1 bg-white/20 backdrop-blur-md rounded-full text-xs font-semibold uppercase mb-2">
              {weather?.weather_main || 'Partly Cloudy'} • Live Feed
            </span>
            <h3 className="text-4xl font-bold mb-1">{firstFarm?.name || 'Central Sector Field'}</h3>
            <p className="text-white/80 text-sm">Updated {weather?.observed_at ? new Date(weather.observed_at).toLocaleTimeString() : 'Just now'}</p>
          </div>

          <div className="flex items-center gap-6">
            <span className="text-6xl font-extrabold">{weather?.temperature != null ? `${weather.temperature}°C` : '24°C'}</span>
            <div className="space-y-1 text-sm text-white/90">
              <div>Feels like: <strong>{weather?.feels_like != null ? `${weather.feels_like}°C` : '22°C'}</strong></div>
              <div>Humidity: <strong>{weather?.humidity != null ? `${weather.humidity}%` : '68%'}</strong></div>
              <div>Wind: <strong>{weather?.wind_speed != null ? `${weather.wind_speed} m/s` : '3.2 m/s'}</strong></div>
            </div>
          </div>
        </div>
      </div>

      {/* Weather Grid Details */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-surface-container-lowest p-5 rounded-xl border border-outline-variant/20 shadow-sm">
          <div className="flex items-center gap-2 text-on-surface-variant mb-2">
            <span className="material-symbols-outlined text-tertiary">water_drop</span>
            <span className="text-xs font-semibold">24h Rainfall</span>
          </div>
          <div className="text-2xl font-bold text-on-surface">{weather?.rainfall_24h ?? 0} mm</div>
        </div>

        <div className="bg-surface-container-lowest p-5 rounded-xl border border-outline-variant/20 shadow-sm">
          <div className="flex items-center gap-2 text-on-surface-variant mb-2">
            <span className="material-symbols-outlined text-[#F59E0B]">compress</span>
            <span className="text-xs font-semibold">Atmospheric Pressure</span>
          </div>
          <div className="text-2xl font-bold text-on-surface">{weather?.pressure ?? 1014} hPa</div>
        </div>

        <div className="bg-surface-container-lowest p-5 rounded-xl border border-outline-variant/20 shadow-sm">
          <div className="flex items-center gap-2 text-on-surface-variant mb-2">
            <span className="material-symbols-outlined text-primary">cloud</span>
            <span className="text-xs font-semibold">Cloud Cover</span>
          </div>
          <div className="text-2xl font-bold text-on-surface">{weather?.cloud_cover ?? 45}%</div>
        </div>

        <div className="bg-surface-container-lowest p-5 rounded-xl border border-outline-variant/20 shadow-sm">
          <div className="flex items-center gap-2 text-on-surface-variant mb-2">
            <span className="material-symbols-outlined text-error">wb_sunny</span>
            <span className="text-xs font-semibold">UV Index</span>
          </div>
          <div className="text-2xl font-bold text-on-surface">{weather?.uv_index ?? 5.2} (Mod)</div>
        </div>
      </div>
    </div>
  );
};
