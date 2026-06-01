-- AI Music Producer — Initial Database Schema
-- Run automatically on first PostgreSQL startup

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─── Genres ────────────────────────────────────────────────────────
CREATE TABLE genres (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    parent_genre_id UUID REFERENCES genres(id) ON DELETE SET NULL,
    bpm_range_min INTEGER DEFAULT 60,
    bpm_range_max INTEGER DEFAULT 200,
    key_signatures TEXT[] DEFAULT '{}',
    typical_structure JSONB DEFAULT '{}',
    description TEXT,
    trending_score FLOAT DEFAULT 0.0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Seed genres
INSERT INTO genres (name, slug, bpm_range_min, bpm_range_max, key_signatures, typical_structure, description) VALUES
('Trap', 'trap', 130, 170, ARRAY['C minor', 'D minor', 'F minor', 'G minor'], '{"sections": ["intro", "hook", "verse", "hook", "verse", "bridge", "hook", "outro"]}', 'Modern trap beats with hard-hitting 808s'),
('Drill', 'drill', 130, 150, ARRAY['C minor', 'D minor', 'F minor'], '{"sections": ["intro", "hook", "verse", "hook", "verse", "hook", "outro"]}', 'Dark UK/NY drill with sliding 808s'),
('Lo-Fi', 'lo-fi', 70, 90, ARRAY['A minor', 'C major', 'D minor', 'E minor'], '{"sections": ["intro", "verse", "hook", "verse", "hook", "outro"]}', 'Chill lo-fi hip hop with vinyl textures'),
('Afrobeats', 'afrobeats', 90, 120, ARRAY['C major', 'F major', 'G major', 'A minor'], '{"sections": ["intro", "verse", "hook", "verse", "bridge", "hook", "outro"]}', 'West African inspired rhythmic beats'),
('Rage', 'rage', 140, 160, ARRAY['C minor', 'D minor', 'F minor'], '{"sections": ["intro", "hook", "verse", "hook", "verse", "hook", "outro"]}', 'Hyper-aggressive rage beats'),
('Cinematic Trap', 'cinematic-trap', 120, 150, ARRAY['C minor', 'D minor', 'F minor', 'A minor'], '{"sections": ["intro", "build", "drop", "verse", "hook", "verse", "hook", "outro"]}', 'Orchestral elements meets trap drums'),
('EDM', 'edm', 120, 130, ARRAY['C major', 'G major', 'A minor', 'F major'], '{"sections": ["intro", "build", "drop", "breakdown", "build", "drop", "outro"]}', 'Electronic dance music'),
('Ambient', 'ambient', 60, 80, ARRAY['C major', 'D major', 'E minor', 'A minor'], '{"sections": ["intro", "section_a", "section_b", "section_a", "outro"]}', 'Atmospheric ambient instrumentals');

-- ─── Trends ────────────────────────────────────────────────────────
CREATE TABLE trends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(50) NOT NULL,
    keyword VARCHAR(255) NOT NULL,
    genre_id UUID REFERENCES genres(id) ON DELETE SET NULL,
    volume_score FLOAT,
    growth_rate FLOAT,
    rank INTEGER,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_trends_source_keyword ON trends(source, keyword);
CREATE INDEX idx_trends_timestamp ON trends(timestamp);
CREATE INDEX idx_trends_genre ON trends(genre_id);

-- ─── Sound Libraries ───────────────────────────────────────────────
CREATE TABLE sound_libraries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    vst_type VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    genre_tags TEXT[] DEFAULT '{}',
    file_path VARCHAR(500),
    preset_data JSONB DEFAULT '{}',
    quality_score FLOAT DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_sound_libraries_category ON sound_libraries(category);
CREATE INDEX idx_sound_libraries_vst ON sound_libraries(vst_type);

-- ─── Mix Chains ────────────────────────────────────────────────────
CREATE TABLE mix_chains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    genre_id UUID REFERENCES genres(id) ON DELETE SET NULL,
    category VARCHAR(100) NOT NULL,
    chain_config JSONB NOT NULL,
    quality_score FLOAT DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ─── Beats ─────────────────────────────────────────────────────────
CREATE TABLE beats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    genre_id UUID REFERENCES genres(id) ON DELETE SET NULL,
    bpm INTEGER NOT NULL,
    key_signature VARCHAR(10),
    duration_seconds INTEGER,
    mood VARCHAR(50),
    
    -- Status workflow
    status VARCHAR(50) DEFAULT 'draft',
    -- draft → rendering → mixing → mastering → qc → approved → published
    --                    ↓           ↓          ↓
    --                 failed     failed      rejected
    
    -- Composition
    midi_data JSONB DEFAULT '{}',
    composition_params JSONB DEFAULT '{}',
    
    -- Sound assignment
    sound_assignments JSONB DEFAULT '{}',
    
    -- Mixing
    mix_chain_id UUID REFERENCES mix_chains(id) ON DELETE SET NULL,
    mix_params JSONB DEFAULT '{}',
    
    -- Mastering
    master_params JSONB DEFAULT '{}',
    loudness_lufs FLOAT,
    true_peak_db FLOAT,
    
    -- Quality
    quality_score FLOAT,
    qc_results JSONB DEFAULT '{}',
    qc_passed BOOLEAN,
    
    -- File paths
    wav_path VARCHAR(500),
    mp3_path VARCHAR(500),
    stems_path VARCHAR(500),
    midi_path VARCHAR(500),
    preview_path VARCHAR(500),
    watermarked_preview_path VARCHAR(500),
    cover_art_path VARCHAR(500),
    
    -- Metadata
    tags TEXT[] DEFAULT '{}',
    description TEXT,
    seo_title VARCHAR(255),
    seo_description TEXT,
    
    -- Shopify
    shopify_product_id VARCHAR(255),
    shopify_status VARCHAR(50),
    
    -- Analytics
    view_count INTEGER DEFAULT 0,
    play_count INTEGER DEFAULT 0,
    wishlist_count INTEGER DEFAULT 0,
    cart_add_count INTEGER DEFAULT 0,
    sales_count INTEGER DEFAULT 0,
    revenue DECIMAL(10,2) DEFAULT 0.0,
    
    -- Generation metadata
    generation_cost DECIMAL(8,4),
    generation_time_seconds INTEGER,
    ai_model_version VARCHAR(50),
    batch_id UUID,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_beats_status ON beats(status);
CREATE INDEX idx_beats_genre ON beats(genre_id);
CREATE INDEX idx_beats_bpm ON beats(bpm);
CREATE INDEX idx_beats_quality ON beats(quality_score);
CREATE INDEX idx_beats_created ON beats(created_at);
CREATE INDEX idx_beats_shopify ON beats(shopify_status);
CREATE INDEX idx_beats_batch ON beats(batch_id);
CREATE INDEX idx_beats_mood ON beats(mood);

-- ─── Beat Sections ─────────────────────────────────────────────────
CREATE TABLE beat_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    beat_id UUID REFERENCES beats(id) ON DELETE CASCADE,
    section_type VARCHAR(50) NOT NULL,
    start_bar INTEGER NOT NULL,
    end_bar INTEGER NOT NULL,
    bpm INTEGER,
    key_signature VARCHAR(10),
    midi_events JSONB DEFAULT '{}',
    automation_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_beat_sections_beat ON beat_sections(beat_id);

-- ─── Render Jobs ───────────────────────────────────────────────────
CREATE TABLE render_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    beat_id UUID REFERENCES beats(id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'queued',
    worker_id VARCHAR(100),
    priority INTEGER DEFAULT 5,
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    result_data JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_render_jobs_status ON render_jobs(status);
CREATE INDEX idx_render_jobs_beat ON render_jobs(beat_id);
CREATE INDEX idx_render_jobs_type ON render_jobs(job_type);

-- ─── Sales ─────────────────────────────────────────────────────────
CREATE TABLE sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    beat_id UUID REFERENCES beats(id) ON DELETE SET NULL,
    license_type VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    customer_email VARCHAR(255),
    customer_name VARCHAR(255),
    shopify_order_id VARCHAR(255),
    shopify_line_item_id VARCHAR(255),
    download_count INTEGER DEFAULT 0,
    downloaded_files TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_sales_beat ON sales(beat_id);
CREATE INDEX idx_sales_created ON sales(created_at);
CREATE INDEX idx_sales_license ON sales(license_type);

-- ─── QC Logs ───────────────────────────────────────────────────────
CREATE TABLE qc_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    beat_id UUID REFERENCES beats(id) ON DELETE CASCADE,
    check_type VARCHAR(100) NOT NULL,
    score FLOAT,
    passed BOOLEAN,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_qc_logs_beat ON qc_logs(beat_id);
CREATE INDEX idx_qc_logs_type ON qc_logs(check_type);

-- ─── AI Models ─────────────────────────────────────────────────────
CREATE TABLE ai_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    file_path VARCHAR(500),
    config JSONB DEFAULT '{}',
    training_data_summary JSONB DEFAULT '{}',
    metrics JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_ai_models_type ON ai_models(model_type);
CREATE INDEX idx_ai_models_active ON ai_models(is_active);

-- ─── Learning Feedback ─────────────────────────────────────────────
CREATE TABLE learning_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    beat_id UUID REFERENCES beats(id) ON DELETE CASCADE,
    feedback_type VARCHAR(50) NOT NULL,
    weight FLOAT DEFAULT 1.0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_learning_feedback_beat ON learning_feedback(beat_id);
CREATE INDEX idx_learning_feedback_type ON learning_feedback(feedback_type);

-- ─── Users (for admin dashboard) ───────────────────────────────────
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ─── Update trigger for timestamps ─────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_beats_updated_at BEFORE UPDATE ON beats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_genres_updated_at BEFORE UPDATE ON genres
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sound_libraries_updated_at BEFORE UPDATE ON sound_libraries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
