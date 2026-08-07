import React, { useState, useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Farm, SatelliteData } from '../types';

interface StressMapProps {
  farm?: Farm;
  satelliteData?: SatelliteData;
}

export const StressMap: React.FC<StressMapProps> = ({ farm, satelliteData }) => {
  const [activeLayer, setActiveLayer] = useState<'ndvi' | 'moisture'>('ndvi');
  const mapRef = useRef<HTMLDivElement>(null);
  const leafletMap = useRef<L.Map | null>(null);
  const userLocation = useRef<{ latitude: number; longitude: number } | null>(null);

  const defaultCenter: [number, number] = [28.6139, 77.2090];

  // Fetch geolocation once on mount and cache it
  useEffect(() => {
    if (!farm?.latitude && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          userLocation.current = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          };
          // If the map already exists, update it immediately
          if (leafletMap.current) {
            const { latitude, longitude } = userLocation.current;
            leafletMap.current.setView([latitude, longitude], 14);
          }
        },
        (error) => console.warn('Geolocation error:', error)
      );
    }
  }, []);

  useEffect(() => {
    if (!mapRef.current) return;

    const center: [number, number] = farm?.latitude && farm?.longitude
      ? [farm.latitude, farm.longitude]
      : userLocation.current
        ? [userLocation.current.latitude, userLocation.current.longitude]
        : defaultCenter;

    const map = L.map(mapRef.current, {
      center,
      zoom: 14,
      zoomControl: false,
    });
    leafletMap.current = map;

    // Tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap',
    }).addTo(map);

    // If farm boundary exists, render polygon
    if (farm?.boundary?.coordinates?.[0]) {
      const latLngs: L.LatLngTuple[] = farm.boundary.coordinates[0].map(
        (c) => [c[1], c[0]] as L.LatLngTuple
      );
      const polygonColor = activeLayer === 'ndvi' ? '#0d631b' : '#00569f';
      const polygon = L.polygon(latLngs, {
        color: polygonColor,
        fillColor: polygonColor,
        fillOpacity: 0.3,
        weight: 3,
      }).addTo(map);
      map.fitBounds(polygon.getBounds());
    } else {
      // Sample polygon centered on user location or default
      const loc = userLocation.current || { latitude: center[0], longitude: center[1] };
      const color = activeLayer === 'ndvi' ? '#0d631b' : '#00569f';
      const sampleCoords: L.LatLngTuple[] = [
        [loc.latitude + 0.0001, loc.longitude - 0.001],
        [loc.latitude + 0.0011, loc.longitude],
        [loc.latitude - 0.0009, loc.longitude + 0.002],
        [loc.latitude - 0.0019, loc.longitude + 0.001],
      ];
      const poly = L.polygon(sampleCoords, {
        color,
        fillColor: color,
        fillOpacity: 0.35,
        weight: 3,
      }).addTo(map);
      map.fitBounds(poly.getBounds());
    }

    return () => {
      map.off();
      map.stop();
      map.remove();
    };
  }, [farm, activeLayer]);

  return (
    <div className="relative w-full h-full min-h-[400px] flex flex-col rounded-xl overflow-hidden border border-outline-variant/10 shadow-sm">
      <div className="p-4 border-b border-outline-variant/10 flex justify-between items-center z-10 bg-surface-container-lowest/90 backdrop-blur-sm">
        <h2 className="text-headline-md font-headline-md text-on-surface">Field Topography & Stress Map</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setActiveLayer(activeLayer === 'ndvi' ? 'moisture' : 'ndvi')}
            className="p-2 rounded-lg bg-surface-container hover:bg-surface-variant transition-colors text-on-surface-variant flex items-center gap-1 text-label-sm"
          >
            <span className="material-symbols-outlined text-[20px]">layers</span>
            <span className="hidden sm:inline capitalize">{activeLayer}</span>
          </button>
        </div>
      </div>

      <div ref={mapRef} className="relative flex-grow w-full h-full min-h-[350px]" />

      {/* Floating Controls Pill */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-surface/90 backdrop-blur-md rounded-full px-4 py-2 border border-outline-variant/20 shadow-lg flex gap-4 items-center z-[400]">
        <button
          onClick={() => setActiveLayer('ndvi')}
          className={`flex items-center gap-1 text-label-sm font-label-sm px-3 py-1.5 rounded-full transition-colors ${
            activeLayer === 'ndvi'
              ? 'bg-primary-container text-on-primary-container font-semibold'
              : 'text-on-surface-variant hover:bg-surface-variant'
          }`}
        >
          <span className="material-symbols-outlined text-[16px]">visibility</span> NDVI (Vegetation)
        </button>
        <div className="w-px h-4 bg-outline-variant/30" />
        <button
          onClick={() => setActiveLayer('moisture')}
          className={`flex items-center gap-1 text-label-sm font-label-sm px-3 py-1.5 rounded-full transition-colors ${
            activeLayer === 'moisture'
              ? 'bg-tertiary-container text-on-tertiary-container font-semibold'
              : 'text-on-surface-variant hover:bg-surface-variant'
          }`}
        >
          <span className="material-symbols-outlined text-[16px]">water_drop</span> NDWI (Moisture)
        </button>
      </div>

      {/* Satellite Info Pill */}
      {satelliteData && (
        <div className="absolute top-16 left-4 bg-surface/90 backdrop-blur-md rounded-lg px-3 py-1.5 border border-outline-variant/20 text-xs text-on-surface-variant z-[400] flex items-center gap-2 shadow-sm">
          <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
          <span>{satelliteData.satellite} ({satelliteData.scene_date})</span>
          <span>NDVI: <strong>{satelliteData.ndvi ?? '--'}</strong></span>
        </div>
      )}
    </div>
  );
};
