export type UserRole = 'farmer' | 'admin' | 'analyst';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  avatar_url?: string;
  phone?: string;
  organization?: string;
  timezone: string;
  created_at: string;
  last_login_at?: string;
}

export type CropType = 'corn' | 'wheat' | 'soybeans' | 'rice' | 'cotton' | 'sugarcane' | 'barley' | 'sorghum' | 'other';
export type SoilType = 'clay_loam' | 'sandy_loam' | 'silt' | 'loam' | 'sandy_clay' | 'silty_clay' | 'other';

export interface GeoJSONPolygon {
  type: 'Polygon';
  coordinates: number[][][];
}

export interface Farm {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  crop_type: CropType;
  soil_type: SoilType;
  planting_date?: string;
  harvest_date?: string;
  boundary: GeoJSONPolygon;
  area_hectares?: number;
  latitude?: number;
  longitude?: number;
  country?: string;
  region?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface WeatherData {
  id: string;
  farm_id: string;
  temperature?: number;
  feels_like?: number;
  humidity?: number;
  pressure?: number;
  wind_speed?: number;
  wind_direction?: number;
  uv_index?: number;
  rainfall_1h: number;
  rainfall_24h: number;
  cloud_cover?: number;
  weather_main?: string;
  weather_desc?: string;
  weather_icon?: string;
  source: string;
  is_forecast: boolean;
  observed_at: string;
  fetched_at: string;
}

export interface SatelliteData {
  id: string;
  farm_id: string;
  ndvi?: number;
  ndvi_min?: number;
  ndvi_max?: number;
  ndwi?: number;
  ndwi_min?: number;
  ndwi_max?: number;
  ndvi_heatmap?: { grid: number[][]; size: number };
  ndwi_heatmap?: { grid: number[][]; size: number };
  satellite: string;
  scene_id?: string;
  cloud_coverage?: number;
  is_simulated: boolean;
  scene_date: string;
  fetched_at: string;
}

export type StressLevel = 'healthy' | 'moderate' | 'critical';

export interface Prediction {
  id: string;
  farm_id: string;
  stress_level: StressLevel;
  stress_score: number;
  confidence: number;
  recommendation: string;
  detailed_analysis?: Record<string, any>;
  healthy_pct?: number;
  moderate_pct?: number;
  critical_pct?: number;
  model_version: string;
  ndvi?: number;
  ndwi?: number;
  temperature?: number;
  humidity?: number;
  rainfall?: number;
  predicted_at: string;
}

export interface RecommendationResponse {
  farm_id: string;
  farm_name: string;
  stress_level: StressLevel;
  stress_score: number;
  confidence: number;
  primary_recommendation: string;
  secondary_recommendations: string[];
  urgency: 'immediate' | 'within_48h' | 'monitor' | 'none';
  estimated_water_need?: number;
  next_prediction_due: string;
  predicted_at: string;
}

export interface DashboardKPI {
  label: string;
  value: string;
  unit?: string;
  trend?: string;
  trend_direction?: 'up' | 'down' | 'stable';
}

export interface DashboardData {
  user_name: string;
  total_farms: number;
  total_area_hectares: number;
  kpis: DashboardKPI[];
  latest_prediction?: Prediction;
  latest_weather?: WeatherData;
  latest_satellite?: SatelliteData;
  recent_notifications: Notification[];
  farms_summary: {
    id: string;
    name: string;
    crop_type: CropType;
    area_hectares: number;
    latitude?: number;
    longitude?: number;
  }[];
}

export interface Notification {
  id: string;
  user_id: string;
  farm_id?: string;
  title: string;
  message: string;
  type: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  action_label?: string;
  action_url?: string;
  data: Record<string, any>;
  is_read: boolean;
  read_at?: string;
  is_dismissed: boolean;
  created_at: string;
}

export interface AnalyticsDataPoint {
  date: string;
  ndvi?: number;
  ndwi?: number;
  stress_score?: number;
  temperature?: number;
  humidity?: number;
  rainfall?: number;
}

export interface AnalyticsResponse {
  farm_id: string;
  farm_name: string;
  period: 'weekly' | 'monthly' | 'all';
  data_points: AnalyticsDataPoint[];
  summary: Record<string, any>;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}
