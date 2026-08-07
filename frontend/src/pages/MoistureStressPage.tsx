import React from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { farmService, satelliteService, predictionService } from '../services/api';
import { StressMap } from '../components/StressMap';

export const MoistureStressPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const farmId = searchParams.get('farm_id');

  const { data: farmsData } = useQuery({
    queryKey: ['farms'],
    queryFn: () => farmService.getFarms(1, 50),
  });

  const selectedFarm = farmsData?.items.find((f) => f.id === farmId) || farmsData?.items[0];

  const { data: satellite } = useQuery({
    queryKey: ['satellite', selectedFarm?.id],
    queryFn: () => satelliteService.getSatellite(selectedFarm!.id),
    enabled: !!selectedFarm,
  });

  const { data: prediction } = useQuery({
    queryKey: ['prediction', selectedFarm?.id],
    queryFn: () => predictionService.predict({ farm_id: selectedFarm!.id }),
    enabled: !!selectedFarm,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-headline-lg font-headline-lg text-on-surface">Moisture Stress Analysis</h2>
        <p className="text-body-md text-on-surface-variant">
          Satellite-based vegetation (NDVI) and water deficit (NDWI) indices
        </p>
      </div>

      {/* Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8">
          <StressMap farm={selectedFarm} satelliteData={satellite} />
        </div>

        <div className="lg:col-span-4 space-y-6">
          {/* Stress Breakdown Card */}
          <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/20 p-6 shadow-sm">
            <h3 className="text-headline-md font-headline-md text-on-surface mb-4">Moisture Zone Breakdown</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-semibold text-primary">Healthy Zone (High NDVI)</span>
                  <span>{prediction?.healthy_pct ?? 82}%</span>
                </div>
                <div className="w-full bg-surface-variant h-2.5 rounded-full overflow-hidden">
                  <div className="bg-primary h-full rounded-full" style={{ width: `${prediction?.healthy_pct ?? 82}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-semibold text-[#F59E0B]">Moderate Stress</span>
                  <span>{prediction?.moderate_pct ?? 12}%</span>
                </div>
                <div className="w-full bg-surface-variant h-2.5 rounded-full overflow-hidden">
                  <div className="bg-[#F59E0B] h-full rounded-full" style={{ width: `${prediction?.moderate_pct ?? 12}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-semibold text-error">Critical Stress</span>
                  <span>{prediction?.critical_pct ?? 6}%</span>
                </div>
                <div className="w-full bg-surface-variant h-2.5 rounded-full overflow-hidden">
                  <div className="bg-error h-full rounded-full" style={{ width: `${prediction?.critical_pct ?? 6}%` }} />
                </div>
              </div>
            </div>
          </div>

          {/* Satellite Specs Card */}
          <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/20 p-6 shadow-sm space-y-3">
            <h3 className="text-headline-md font-headline-md text-on-surface mb-2">Sentinel-2 Scene Info</h3>
            <div className="flex justify-between text-sm border-b border-outline-variant/20 pb-2">
              <span className="text-on-surface-variant">Satellite Constellation</span>
              <span className="font-semibold text-on-surface">{satellite?.satellite || 'Sentinel-2'}</span>
            </div>
            <div className="flex justify-between text-sm border-b border-outline-variant/20 pb-2">
              <span className="text-on-surface-variant">Mean NDVI</span>
              <span className="font-semibold text-primary">{satellite?.ndvi ?? 0.68}</span>
            </div>
            <div className="flex justify-between text-sm border-b border-outline-variant/20 pb-2">
              <span className="text-on-surface-variant">Mean NDWI</span>
              <span className="font-semibold text-tertiary">{satellite?.ndwi ?? -0.05}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-on-surface-variant">Spatial Resolution</span>
              <span className="font-semibold text-on-surface">10m / pixel</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
