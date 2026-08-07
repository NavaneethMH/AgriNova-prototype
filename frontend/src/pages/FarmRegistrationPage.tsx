import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { FarmMap } from '../components/FarmMap';
import { farmService } from '../services/api';
import { GeoJSONPolygon, CropType, SoilType } from '../types';

export const FarmRegistrationPage: React.FC = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [cropType, setCropType] = useState<CropType>('corn');
  const [soilType, setSoilType] = useState<SoilType>('clay_loam');
  const [plantingDate, setPlantingDate] = useState('');
  const [boundary, setBoundary] = useState<GeoJSONPolygon | null>(null);
  const [areaHa, setAreaHa] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleBoundaryChange = (newBoundary: GeoJSONPolygon, calculatedArea: number) => {
    setBoundary(newBoundary);
    setAreaHa(calculatedArea);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!boundary) {
      // Default sample polygon if user didn't draw one
      const defaultPoly: GeoJSONPolygon = {
        type: 'Polygon',
        coordinates: [
          [
            [-119.4200, 36.7800],
            [-119.4150, 36.7850],
            [-119.4080, 36.7820],
            [-119.4120, 36.7750],
            [-119.4200, 36.7800],
          ],
        ],
      };
      setBoundary(defaultPoly);
    }

    if (!name.trim()) {
      setError('Please enter a farm name.');
      return;
    }

    setLoading(true);
    try {
      await farmService.createFarm({
        name,
        description,
        crop_type: cropType,
        soil_type: soilType,
        planting_date: plantingDate || undefined,
        boundary: boundary || {
          type: 'Polygon',
          coordinates: [
            [
              [-119.4200, 36.7800],
              [-119.4150, 36.7850],
              [-119.4080, 36.7820],
              [-119.4120, 36.7750],
              [-119.4200, 36.7800],
            ],
          ],
        },
      });
      navigate('/farms');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save farm boundary.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-4">
        <Link to="/farms" className="text-on-surface-variant hover:bg-surface-variant/50 p-2 rounded-full transition-colors flex items-center justify-center">
          <span className="material-symbols-outlined">arrow_back</span>
        </Link>
        <h2 className="text-headline-lg font-headline-lg text-on-surface">Register Your Farm</h2>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-error-container text-on-error-container text-sm flex items-center gap-2">
          <span className="material-symbols-outlined text-sm">error</span>
          <span>{error}</span>
        </div>
      )}

      {/* Bento Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Step 1: Map Module (Left side) */}
        <div className="lg:col-span-7 flex flex-col gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-on-primary text-label-sm font-label-sm font-bold">
              1
            </div>
            <h3 className="text-headline-md font-headline-md text-on-surface">Define Boundaries</h3>
          </div>

          <div className="h-[450px] lg:h-[520px] w-full">
            <FarmMap onBoundaryChange={handleBoundaryChange} />
          </div>
        </div>

        {/* Step 2: Form Module (Right side) */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-surface-variant border border-outline-variant flex items-center justify-center text-on-surface-variant text-label-sm font-label-sm font-bold">
              2
            </div>
            <h3 className="text-headline-md font-headline-md text-on-surface">Farm Details</h3>
          </div>

          <form onSubmit={handleSave} className="glass-panel p-6 rounded-xl flex flex-col gap-4 h-full">
            <div className="flex flex-col gap-1.5">
              <label className="text-label-md font-label-md text-on-surface-variant">Farm Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. North Field Beta"
                required
                className="input-field"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-label-md font-label-md text-on-surface-variant">Crop Type</label>
                <select
                  value={cropType}
                  onChange={(e) => setCropType(e.target.value as CropType)}
                  className="select-field"
                >
                  <option value="corn">Corn (Maize)</option>
                  <option value="wheat">Wheat</option>
                  <option value="soybeans">Soybeans</option>
                  <option value="rice">Rice</option>
                  <option value="cotton">Cotton</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-label-md font-label-md text-on-surface-variant">Soil Type</label>
                <select
                  value={soilType}
                  onChange={(e) => setSoilType(e.target.value as SoilType)}
                  className="select-field"
                >
                  <option value="clay_loam">Clay Loam</option>
                  <option value="sandy_loam">Sandy Loam</option>
                  <option value="silt">Silt</option>
                  <option value="loam">Loam</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-label-md font-label-md text-on-surface-variant">Planting Date</label>
              <input
                type="date"
                value={plantingDate}
                onChange={(e) => setPlantingDate(e.target.value)}
                className="input-field"
              />
            </div>

            {/* Auto-calculated Area Box */}
            <div className="mt-2 p-4 rounded-lg bg-surface-container border border-outline-variant/50 flex items-center justify-between">
              <div className="flex flex-col">
                <span className="text-label-sm font-label-sm text-on-surface-variant">Calculated Area</span>
                <span className="text-headline-md font-headline-md text-on-surface font-semibold">
                  {areaHa != null ? `${areaHa} ha` : '-- ha'}
                </span>
              </div>
              <div className="w-10 h-10 rounded-full bg-surface flex items-center justify-center text-primary/70">
                <span className="material-symbols-outlined">calculate</span>
              </div>
            </div>

            <div className="mt-auto pt-4 flex flex-col gap-3">
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-primary hover:bg-primary/90 text-on-primary h-12 rounded-xl flex items-center justify-center gap-2 text-label-md font-label-md transition-colors shadow-md shadow-primary/20 font-semibold"
              >
                <span className="material-symbols-outlined text-[20px]">save</span>
                {loading ? 'Saving Farm...' : 'Save Farm Boundary'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
