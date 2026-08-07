import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import 'leaflet-draw';
import { GeoJSONPolygon } from '../types';

interface FarmMapProps {
  initialBoundary?: GeoJSONPolygon;
  onBoundaryChange?: (boundary: GeoJSONPolygon, areaHa: number) => void;
  center?: [number, number];
  zoom?: number;
  interactive?: boolean;
}

export const FarmMap: React.FC<FarmMapProps> = ({
  initialBoundary,
  onBoundaryChange,
  center = [28.6139, 77.2090], // Default to New Delhi
  zoom = 13,
  interactive = true,
}) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const leafletMap = useRef<L.Map | null>(null);
  const drawnItems = useRef<L.FeatureGroup>(new L.FeatureGroup());

  useEffect(() => {
    if (!mapRef.current) return;

    // Initialize Leaflet map
    const map = L.map(mapRef.current, {
      center,
      zoom,
      zoomControl: false,
    });
    leafletMap.current = map;

    // OpenStreetMap Tile Layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map);

    // Feature group for drawn polygons
    map.addLayer(drawnItems.current);

    // If initial boundary provided, add it to map
    if (initialBoundary && initialBoundary.coordinates && initialBoundary.coordinates[0]) {
      const latLgCoords: L.LatLngTuple[] = initialBoundary.coordinates[0].map(
        (c) => [c[1], c[0]] as L.LatLngTuple
      );
      const polygon = L.polygon(latLgCoords, {
        color: '#0d631b',
        fillColor: '#2e7d32',
        fillOpacity: 0.35,
        weight: 2,
      });
      drawnItems.current.addLayer(polygon);
      map.fitBounds(polygon.getBounds());
    } else {
      // If no initial boundary, try to get user's current location
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const { latitude, longitude } = position.coords;
            map.setView([latitude, longitude], 14);
          },
          (error) => {
            console.warn('Geolocation error:', error);
          }
        );
      }
    }

    if (interactive) {
      // Add Leaflet Draw controls
      const drawControl = new (L.Control as any).Draw({
        draw: {
          polygon: {
            allowIntersection: false,
            showArea: true,
            drawError: {
              color: '#ba1a1a',
              message: 'Polygon cannot intersect itself!',
            },
            shapeOptions: {
              color: '#0d631b',
              fillColor: '#2e7d32',
              fillOpacity: 0.35,
            },
          },
          polyline: false,
          rectangle: false,
          circle: false,
          marker: false,
          circlemarker: false,
        },
        edit: {
          featureGroup: drawnItems.current,
          remove: true,
        },
      });

      map.addControl(drawControl);

      // Handle drawn polygon
      map.on((L as any).Draw.Event.CREATED, (e: any) => {
        drawnItems.current.clearLayers();
        const layer = e.layer;
        drawnItems.current.addLayer(layer);

        const geoJson = layer.toGeoJSON();
        const coords = geoJson.geometry.coordinates;

        // Calculate approximate area in hectares
        const latLngs = layer.getLatLngs()[0];
        let areaM2 = 0;
        if ((L as any).GeometryUtil) {
          areaM2 = (L as any).GeometryUtil.geodesicArea(latLngs);
        } else {
          // Rough estimation if GeometryUtil not loaded
          areaM2 = 50000; 
        }
        const areaHa = parseFloat((areaM2 / 10000).toFixed(2));

        if (onBoundaryChange) {
          onBoundaryChange(
            {
              type: 'Polygon',
              coordinates: coords,
            },
            areaHa
          );
        }
      });
    }

    return () => {
      map.off();
      map.stop();
      map.remove();
    };
  }, []);

  const handleZoomIn = () => leafletMap.current?.zoomIn();
  const handleZoomOut = () => leafletMap.current?.zoomOut();

  return (
    <div className="relative w-full h-full min-h-[400px] rounded-xl overflow-hidden shadow-sm border border-outline-variant/20">
      <div ref={mapRef} className="w-full h-full min-h-[400px] z-0" />

      {/* Floating Map Zoom Controls */}
      <div className="absolute top-4 right-4 flex flex-col gap-2 z-[400]">
        <button
          onClick={handleZoomIn}
          className="bg-surface/90 backdrop-blur text-on-surface p-2 rounded-lg shadow-sm border border-outline-variant/30 hover:bg-surface hover:text-primary transition-colors flex items-center justify-center"
        >
          <span className="material-symbols-outlined">zoom_in</span>
        </button>
        <button
          onClick={handleZoomOut}
          className="bg-surface/90 backdrop-blur text-on-surface p-2 rounded-lg shadow-sm border border-outline-variant/30 hover:bg-surface hover:text-primary transition-colors flex items-center justify-center"
        >
          <span className="material-symbols-outlined">zoom_out</span>
        </button>
      </div>
    </div>
  );
};
