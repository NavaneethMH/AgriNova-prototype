-- ================================================================
-- AgriNova PostgreSQL + PostGIS Schema
-- Full production schema with all tables, indices, and constraints
-- ================================================================

-- Enable PostGIS extension for geospatial data
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- for fuzzy text search

-- ================================================================
-- ENUM TYPES
-- ================================================================

CREATE TYPE user_role AS ENUM ('farmer', 'admin', 'analyst');
CREATE TYPE stress_level AS ENUM ('healthy', 'moderate', 'critical');
CREATE TYPE notification_type AS ENUM (
    'moisture_stress', 'weather_alert', 'irrigation_due',
    'satellite_update', 'ai_recommendation', 'system'
);
CREATE TYPE notification_priority AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE crop_type AS ENUM (
    'corn', 'wheat', 'soybeans', 'rice', 'cotton',
    'sugarcane', 'barley', 'sorghum', 'other'
);
CREATE TYPE soil_type AS ENUM (
    'clay_loam', 'sandy_loam', 'silt', 'loam',
    'sandy_clay', 'silty_clay', 'other'
);
CREATE TYPE audit_action AS ENUM (
    'create', 'update', 'delete', 'login', 'logout',
    'prediction_run', 'satellite_fetch', 'weather_fetch'
);

-- ================================================================
-- USERS TABLE
-- ================================================================

CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    role            user_role NOT NULL DEFAULT 'farmer',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified     BOOLEAN NOT NULL DEFAULT FALSE,
    avatar_url      TEXT,
    phone           VARCHAR(20),
    organization    VARCHAR(255),
    timezone        VARCHAR(64) DEFAULT 'UTC',
    -- Metadata
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at   TIMESTAMPTZ,
    -- Constraints
    CONSTRAINT users_email_format CHECK (email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$')
);

CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_role ON users (role);
CREATE INDEX idx_users_is_active ON users (is_active);

-- ================================================================
-- FARMS TABLE
-- ================================================================

CREATE TABLE farms (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    crop_type       crop_type NOT NULL DEFAULT 'other',
    soil_type       soil_type NOT NULL DEFAULT 'other',
    planting_date   DATE,
    harvest_date    DATE,
    -- PostGIS geometry: POLYGON in WGS84 (EPSG:4326)
    boundary        GEOMETRY(POLYGON, 4326) NOT NULL,
    -- Calculated from boundary automatically
    area_hectares   NUMERIC(12, 4),
    -- Location metadata (extracted from polygon centroid)
    latitude        NUMERIC(10, 7),
    longitude       NUMERIC(10, 7),
    country         VARCHAR(100),
    region          VARCHAR(100),
    -- Status
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    -- Metadata
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- Constraints
    CONSTRAINT farms_area_positive CHECK (area_hectares > 0 OR area_hectares IS NULL),
    CONSTRAINT farms_name_length CHECK (LENGTH(name) >= 2)
);

-- Spatial index for geometry queries
CREATE INDEX idx_farms_boundary ON farms USING GIST (boundary);
CREATE INDEX idx_farms_user_id ON farms (user_id);
CREATE INDEX idx_farms_is_active ON farms (is_active);
CREATE INDEX idx_farms_crop_type ON farms (crop_type);

-- Auto-calculate area and centroid on insert/update
CREATE OR REPLACE FUNCTION update_farm_geometry_metadata()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate area in hectares (convert from m²)
    NEW.area_hectares := ST_Area(ST_Transform(NEW.boundary, 3857)) / 10000.0;
    -- Extract centroid for lat/lon
    NEW.latitude  := ST_Y(ST_Centroid(NEW.boundary));
    NEW.longitude := ST_X(ST_Centroid(NEW.boundary));
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_farm_geometry_metadata
    BEFORE INSERT OR UPDATE ON farms
    FOR EACH ROW EXECUTE FUNCTION update_farm_geometry_metadata();

-- ================================================================
-- WEATHER DATA TABLE
-- ================================================================

CREATE TABLE weather_data (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id         UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    -- Observation values
    temperature     NUMERIC(6, 2),          -- Celsius
    feels_like      NUMERIC(6, 2),          -- Celsius
    humidity        NUMERIC(5, 2),          -- Percentage 0-100
    pressure        NUMERIC(8, 2),          -- hPa
    wind_speed      NUMERIC(7, 2),          -- m/s
    wind_direction  NUMERIC(5, 1),          -- Degrees 0-360
    rainfall_1h     NUMERIC(8, 2) DEFAULT 0, -- mm in last 1h
    rainfall_24h    NUMERIC(8, 2) DEFAULT 0, -- mm in last 24h
    cloud_cover     NUMERIC(5, 2),          -- Percentage 0-100
    visibility      NUMERIC(10, 2),         -- Meters
    uv_index        NUMERIC(4, 1),
    weather_code    INTEGER,                -- OpenWeather weather code
    weather_main    VARCHAR(100),           -- e.g. "Rain", "Clear"
    weather_desc    VARCHAR(255),           -- Detailed description
    weather_icon    VARCHAR(20),            -- OpenWeather icon code
    -- Data source
    source          VARCHAR(50) DEFAULT 'openweather',
    is_forecast     BOOLEAN DEFAULT FALSE,
    forecast_hours  INTEGER,               -- Hours ahead (for forecasts)
    -- Timing
    observed_at     TIMESTAMPTZ NOT NULL,
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- Metadata
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_weather_farm_id ON weather_data (farm_id);
CREATE INDEX idx_weather_observed_at ON weather_data (observed_at DESC);
CREATE INDEX idx_weather_farm_observed ON weather_data (farm_id, observed_at DESC);
CREATE INDEX idx_weather_is_forecast ON weather_data (is_forecast);

-- ================================================================
-- SATELLITE DATA TABLE
-- ================================================================

CREATE TABLE satellite_data (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id         UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    -- Vegetation indices
    ndvi            NUMERIC(6, 4),   -- -1.0 to 1.0
    ndvi_min        NUMERIC(6, 4),
    ndvi_max        NUMERIC(6, 4),
    ndvi_std        NUMERIC(6, 4),
    ndwi            NUMERIC(6, 4),   -- -1.0 to 1.0
    ndwi_min        NUMERIC(6, 4),
    ndwi_max        NUMERIC(6, 4),
    -- Raw band values (Sentinel-2)
    band_red        NUMERIC(8, 4),   -- B4
    band_nir        NUMERIC(8, 4),   -- B8
    band_green      NUMERIC(8, 4),   -- B3
    band_swir       NUMERIC(8, 4),   -- B11
    -- Heatmap data (JSON array of pixel values for visualization)
    ndvi_heatmap    JSONB,
    ndwi_heatmap    JSONB,
    -- Satellite metadata
    satellite       VARCHAR(50) DEFAULT 'Sentinel-2',
    scene_id        VARCHAR(255),
    cloud_coverage  NUMERIC(5, 2),    -- Percentage
    resolution      NUMERIC(6, 1),    -- Meters per pixel
    -- Source
    is_simulated    BOOLEAN DEFAULT FALSE,
    -- Timing
    scene_date      DATE NOT NULL,
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- Metadata
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_satellite_farm_id ON satellite_data (farm_id);
CREATE INDEX idx_satellite_scene_date ON satellite_data (scene_date DESC);
CREATE INDEX idx_satellite_farm_date ON satellite_data (farm_id, scene_date DESC);
CREATE INDEX idx_satellite_is_simulated ON satellite_data (is_simulated);

-- ================================================================
-- PREDICTIONS TABLE
-- ================================================================

CREATE TABLE predictions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id             UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    -- Input features
    ndvi                NUMERIC(6, 4),
    ndwi                NUMERIC(6, 4),
    temperature         NUMERIC(6, 2),
    humidity            NUMERIC(5, 2),
    rainfall            NUMERIC(8, 2),
    -- Prediction outputs
    stress_level        stress_level NOT NULL,
    stress_score        NUMERIC(5, 2) NOT NULL,  -- 0-100
    confidence          NUMERIC(5, 2) NOT NULL,  -- 0-100
    recommendation      TEXT NOT NULL,
    detailed_analysis   JSONB,  -- Additional structured analysis data
    -- Healthy/Moderate/Critical area breakdown (percentages)
    healthy_pct         NUMERIC(5, 2),
    moderate_pct        NUMERIC(5, 2),
    critical_pct        NUMERIC(5, 2),
    -- Model metadata
    model_version       VARCHAR(50) DEFAULT 'v1.0',
    model_type          VARCHAR(100) DEFAULT 'RandomForestClassifier',
    -- Timing
    predicted_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- Metadata
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_predictions_farm_id ON predictions (farm_id);
CREATE INDEX idx_predictions_user_id ON predictions (user_id);
CREATE INDEX idx_predictions_predicted_at ON predictions (predicted_at DESC);
CREATE INDEX idx_predictions_stress_level ON predictions (stress_level);
CREATE INDEX idx_predictions_farm_date ON predictions (farm_id, predicted_at DESC);

-- ================================================================
-- NOTIFICATIONS TABLE
-- ================================================================

CREATE TABLE notifications (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    farm_id         UUID REFERENCES farms(id) ON DELETE SET NULL,
    -- Content
    title           VARCHAR(255) NOT NULL,
    message         TEXT NOT NULL,
    type            notification_type NOT NULL DEFAULT 'system',
    priority        notification_priority NOT NULL DEFAULT 'medium',
    -- Action (optional deep link)
    action_label    VARCHAR(100),
    action_url      VARCHAR(500),
    -- Metadata payload
    data            JSONB DEFAULT '{}',
    -- Status
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    read_at         TIMESTAMPTZ,
    is_dismissed    BOOLEAN NOT NULL DEFAULT FALSE,
    dismissed_at    TIMESTAMPTZ,
    -- Timing
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ
);

CREATE INDEX idx_notifications_user_id ON notifications (user_id);
CREATE INDEX idx_notifications_is_read ON notifications (is_read);
CREATE INDEX idx_notifications_type ON notifications (type);
CREATE INDEX idx_notifications_created_at ON notifications (created_at DESC);
CREATE INDEX idx_notifications_user_unread ON notifications (user_id, is_read) WHERE NOT is_read;

-- ================================================================
-- AUDIT LOGS TABLE
-- ================================================================

CREATE TABLE audit_logs (
    id              BIGSERIAL PRIMARY KEY,
    user_id         UUID REFERENCES users(id) ON DELETE SET NULL,
    -- Action details
    action          audit_action NOT NULL,
    resource_type   VARCHAR(100),
    resource_id     UUID,
    -- Context
    ip_address      INET,
    user_agent      TEXT,
    request_method  VARCHAR(10),
    request_path    VARCHAR(500),
    -- Data snapshot
    old_values      JSONB,
    new_values      JSONB,
    extra_data      JSONB DEFAULT '{}',
    -- Status
    success         BOOLEAN NOT NULL DEFAULT TRUE,
    error_message   TEXT,
    -- Timing
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_user_id ON audit_logs (user_id);
CREATE INDEX idx_audit_action ON audit_logs (action);
CREATE INDEX idx_audit_resource ON audit_logs (resource_type, resource_id);
CREATE INDEX idx_audit_created_at ON audit_logs (created_at DESC);
CREATE INDEX idx_audit_ip ON audit_logs (ip_address);

-- ================================================================
-- REFRESH TOKENS TABLE
-- ================================================================

CREATE TABLE refresh_tokens (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token           VARCHAR(512) UNIQUE NOT NULL,
    expires_at      TIMESTAMPTZ NOT NULL,
    is_revoked      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at      TIMESTAMPTZ
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens (user_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens (token);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens (expires_at);

-- ================================================================
-- HELPER VIEWS
-- ================================================================

-- Farm summary view with latest prediction
CREATE OR REPLACE VIEW farm_summary AS
SELECT
    f.id,
    f.user_id,
    f.name,
    f.crop_type,
    f.soil_type,
    f.area_hectares,
    f.latitude,
    f.longitude,
    f.is_active,
    -- Latest prediction
    p.stress_level AS latest_stress_level,
    p.stress_score AS latest_stress_score,
    p.confidence   AS latest_confidence,
    p.recommendation AS latest_recommendation,
    p.predicted_at AS latest_prediction_at,
    -- Latest weather
    w.temperature  AS latest_temperature,
    w.humidity     AS latest_humidity,
    w.rainfall_24h AS latest_rainfall,
    w.observed_at  AS latest_weather_at,
    -- Latest satellite
    s.ndvi         AS latest_ndvi,
    s.ndwi         AS latest_ndwi,
    s.scene_date   AS latest_scene_date
FROM farms f
LEFT JOIN LATERAL (
    SELECT * FROM predictions WHERE farm_id = f.id ORDER BY predicted_at DESC LIMIT 1
) p ON TRUE
LEFT JOIN LATERAL (
    SELECT * FROM weather_data WHERE farm_id = f.id AND NOT is_forecast ORDER BY observed_at DESC LIMIT 1
) w ON TRUE
LEFT JOIN LATERAL (
    SELECT * FROM satellite_data WHERE farm_id = f.id ORDER BY scene_date DESC LIMIT 1
) s ON TRUE;

-- ================================================================
-- UPDATED_AT TRIGGER (reuse for all tables)
-- ================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
