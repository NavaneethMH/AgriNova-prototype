import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { farmService } from '../services/api';
import { Link } from 'react-router-dom';

export const FarmManagementPage: React.FC = () => {
  const queryClient = useQueryClient();

  const { data: farmsData, isLoading } = useQuery({
    queryKey: ['farms'],
    queryFn: () => farmService.getFarms(1, 50),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => farmService.deleteFarm(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['farms'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  const farms = farmsData?.items || [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-headline-lg font-headline-lg text-on-surface">My Farms</h2>
          <p className="text-body-md text-on-surface-variant">Manage your registered agricultural boundaries and sectors</p>
        </div>
        <Link
          to="/farms/register"
          className="inline-flex items-center gap-2 px-5 py-3 bg-primary text-on-primary rounded-xl font-label-md shadow-sm hover:bg-primary-container transition-colors"
        >
          <span className="material-symbols-outlined text-[20px]">add</span>
          Register New Farm
        </Link>
      </div>

      {isLoading ? (
        <div className="flex justify-center p-12">
          <span className="material-symbols-outlined text-3xl text-primary animate-spin">sync</span>
        </div>
      ) : farms.length === 0 ? (
        <div className="bg-surface-container-lowest rounded-xl p-12 text-center border border-outline-variant/20 shadow-sm space-y-4">
          <div className="w-16 h-16 bg-primary-container/20 text-primary rounded-full flex items-center justify-center mx-auto">
            <span className="material-symbols-outlined text-3xl">agriculture</span>
          </div>
          <h3 className="text-headline-md font-headline-md text-on-surface">No Farms Registered Yet</h3>
          <p className="text-body-md text-on-surface-variant max-w-md mx-auto">
            Draw your first farm polygon boundary on the interactive map to start satellite tracking and AI moisture analytics.
          </p>
          <Link
            to="/farms/register"
            className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-on-primary rounded-xl font-label-md shadow-md"
          >
            Draw Farm Polygon
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {farms.map((farm) => (
            <div
              key={farm.id}
              className="bg-surface-container-lowest rounded-xl border border-outline-variant/20 shadow-sm p-6 flex flex-col justify-between hover:shadow-md transition-shadow"
            >
              <div>
                <div className="flex justify-between items-start mb-3">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary-container/15 text-primary text-xs font-semibold capitalize">
                    <span className="material-symbols-outlined text-[14px]">eco</span>
                    {farm.crop_type.replace('_', ' ')}
                  </span>
                  <button
                    onClick={() => {
                      if (confirm(`Are you sure you want to delete ${farm.name}?`)) {
                        deleteMutation.mutate(farm.id);
                      }
                    }}
                    className="text-outline hover:text-error transition-colors p-1"
                    title="Delete Farm"
                  >
                    <span className="material-symbols-outlined text-[18px]">delete</span>
                  </button>
                </div>

                <h3 className="text-headline-md font-headline-md text-on-surface mb-2">{farm.name}</h3>
                {farm.description && (
                  <p className="text-body-md text-on-surface-variant line-clamp-2 mb-4">{farm.description}</p>
                )}

                <div className="grid grid-cols-2 gap-3 text-sm pt-2 border-t border-outline-variant/20">
                  <div>
                    <span className="text-on-surface-variant text-xs block">Area</span>
                    <span className="font-semibold text-on-surface">
                      {farm.area_hectares != null ? `${farm.area_hectares} ha` : 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-on-surface-variant text-xs block">Soil Type</span>
                    <span className="font-semibold text-on-surface capitalize">
                      {farm.soil_type.replace('_', ' ')}
                    </span>
                  </div>
                </div>
              </div>

              <div className="pt-6 flex gap-2">
                <Link
                  to={`/stress-analysis?farm_id=${farm.id}`}
                  className="flex-1 py-2 text-center bg-surface-container hover:bg-surface-variant text-on-surface rounded-lg text-label-sm font-semibold transition-colors"
                >
                  View Stress
                </Link>
                <Link
                  to={`/recommendations?farm_id=${farm.id}`}
                  className="flex-1 py-2 text-center bg-primary text-on-primary rounded-lg text-label-sm font-semibold hover:bg-primary-container transition-colors"
                >
                  AI Recommendations
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
