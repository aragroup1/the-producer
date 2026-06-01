# AI Content Promotion System — Architecture

## System Overview

The AI Content Promotion System is a microservice within the larger AI Music Production platform. It receives generated beats and autonomously promotes them across social media and beat-selling platforms.

## Data Flow

```
┌─────────────┐     ┌─────────────────────────┐     ┌─────────────────┐
│   Beat      │────▶│  Promotion Pipeline     │────▶│   YouTube       │
│  Generated  │     │  (marketing-agent)      │     │   (Multi-chan)  │
└─────────────┘     └─────────────────────────┘     └─────────────────┘
                            │
                            ├──▶ Video (16:9 + 9:16)
                            ├──▶ Thumbnails (A/B/C variants)
                            ├──▶ SEO (titles, descriptions, tags)
                            ├──▶ Upload plans (all platforms)
                            └──▶ Schedule (optimal times)
```

## Component Architecture

### 1. Core Pipeline (`app/core/`)

**PromotionPipeline** — Orchestrates the full workflow:
1. Receive beat metadata + audio file
2. Generate SEO package (titles, descriptions, tags)
3. Generate video (full + shorts)
4. Generate thumbnails (3 variants for A/B testing)
5. Build upload plans for all platforms
6. Queue for scheduling

**ChannelManager** — Multi-channel orchestration:
- 6 default channels (Drill, Trap, Emotional, Lo-Fi, Afrobeats, R&B)
- Intelligent beat-to-channel assignment
- Upload frequency management
- Algorithm overlap avoidance

**RuleEngine** — Automation rules:
- 6 pre-built rules
- Custom rule creation via API
- IF/THEN/ELSE logic with cooldowns
- Context-aware evaluation

### 2. Video Generation (`app/video/`)

**VideoRenderer** — FFmpeg-based rendering:
- Frame-by-frame rendering with Pillow
- Audio sync via onset detection
- Genre-specific color schemes
- Text overlay with positioning

**Visualizers** — Multiple styles:
- Waveform: Classic centered line
- Spectrum: Frequency bars
- Particles: Floating particles
- Bars: Vertical bar chart
- Circular: Circular spectrum
- Glitch: Digital distortion

**ShortsGenerator** — Short-form content:
- Hook detection via energy analysis
- 15-60 second extraction
- Platform-specific durations
- All platforms at once

**TemplateRegistry** — Style management:
- 16+ templates across genres
- 16:9 and 9:16 aspect ratios
- Color schemes, fonts, motion configs

### 3. Thumbnail AI (`app/thumbnail/`)

**ThumbnailGenerator** — CTR optimization:
- Genre-specific style presets
- 3 variants per beat (A/B/C)
- Text effects (glow, neon, outline, chrome)
- Vignette, noise, gradient backgrounds

**TextOverlayRenderer** — Text effects:
- Glow, outline, shadow, gradient, neon, chrome
- Multi-line support
- Font fallback system

**ABTestManager** — Statistical testing:
- Z-test for proportions
- 95% confidence threshold
- Automatic winner selection
- Performance tracking

### 4. SEO Engine (`app/seo/`)

**TitleGenerator** — Click-optimized titles:
- 10+ title templates
- Power word insertion
- Artist name mapping
- Trending keyword integration
- Character count optimization

**DescriptionBuilder** — Full descriptions:
- SEO-optimized first 2 lines
- Section timestamps
- Licensing blocks
- CTA templates
- Hashtag generation

**KeywordResearcher** — Keyword discovery:
- YouTube autocomplete scraping
- Search volume estimation
- Competition analysis
- Opportunity scoring

**RankTracker** — Position monitoring:
- YouTube search scraping
- Position tracking over time
- Trend analysis
- Performance summary

### 5. Upload Automation (`app/upload/`)

**YouTubeUploader** — Full YouTube API:
- OAuth 2.0 with refresh tokens
- Video + thumbnail + playlist
- Multi-channel support
- Daily upload limits
- Status tracking

**TikTokUploader** — TikTok integration:
- API v2 support
- Caption generation
- Duet/stitch settings

**InstagramUploader** — Reels upload:
- Graph API integration
- Public URL requirements
- Feed sharing

**BeatStarsUploader / AirbitUploader** — Beat platforms:
- Partner API ready
- Pricing automation
- Metadata sync

### 6. Trend Detection (`app/trends/`)

**YouTubeTrendDetector** — YouTube trends:
- Trending page scraping
- Keyword extraction
- Search suggestion analysis

**TikTokTrendDetector** — TikTok trends:
- Hashtag tracking
- Viral sound detection
- Genre-specific filtering

**GoogleTrendDetector** — Google Trends:
- pytrends integration
- Interest over time
- Related queries
- Trending searches

**BeatMarketTrendDetector** — Market analysis:
- Genre momentum scoring
- Pricing trends
- Rising artists
- Market opportunities

### 7. Analytics (`app/analytics/`)

**YouTubeAnalytics** — API integration:
- Views, watch time, subscribers
- Top videos
- CTR data

**CTRTracker** — Click-through tracking:
- Per-video CTR
- Variant performance
- Industry benchmarks
- Recommendations

**RetentionAnalyzer** — Watch time analysis:
- Retention curves
- Drop-off detection
- Genre profiles
- Optimization suggestions

**ConversionTracker** — Revenue attribution:
- Full funnel tracking
- Per-video revenue
- Attribution by source
- ROI calculation

### 8. AI Learning (`app/learning/`)

**PerformanceModel** — Prediction engine:
- Nearest-neighbor matching
- Feature similarity scoring
- CTR/view prediction
- Best practices extraction

**ThumbnailOptimizer** — Thumbnail learning:
- Color performance tracking
- Text effect analysis
- Layout optimization
- CTR prediction

**TitleOptimizer** — Title learning:
- Power word analysis
- Length optimization
- Pattern recognition
- Title scoring

**GenrePredictor** — Trend prediction:
- Seasonal patterns
- Momentum calculation
- Market signal integration
- Production recommendations

### 9. Scheduling (`app/scheduler/`)

**ContentCalendar** — Post scheduling:
- Optimal time calculation
- Platform-specific frequencies
- Staggered releases
- Queue management

## Database Schema

### Extended Tables

```sql
-- Channels
CREATE TABLE channels (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    platform VARCHAR(50),
    niche VARCHAR(100),
    upload_frequency INTEGER,
    active BOOLEAN
);

-- Video content
CREATE TABLE video_contents (
    id UUID PRIMARY KEY,
    beat_id UUID REFERENCES beats(id),
    channel_id UUID REFERENCES channels(id),
    video_type VARCHAR(50),
    video_path VARCHAR(500),
    thumbnail_path VARCHAR(500),
    title VARCHAR(255),
    description TEXT,
    tags JSONB,
    status VARCHAR(50),
    platform_video_id VARCHAR(255)
);

-- Performance metrics
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY,
    video_content_id UUID REFERENCES video_contents(id),
    views INTEGER,
    ctr FLOAT,
    watch_time_seconds INTEGER,
    revenue_attributed DECIMAL(10,2)
);

-- A/B tests
CREATE TABLE ab_tests (
    id UUID PRIMARY KEY,
    beat_id UUID REFERENCES beats(id),
    test_type VARCHAR(50),
    winner VARCHAR(10),
    confidence FLOAT
);

-- Automation rules
CREATE TABLE automation_rules (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    condition JSONB,
    action JSONB,
    enabled BOOLEAN,
    trigger_count INTEGER
);
```

## API Design

### RESTful Endpoints

All endpoints follow REST conventions:
- `GET /resource` — List
- `GET /resource/{id}` — Get one
- `POST /resource` — Create
- `PUT /resource/{id}` — Update
- `DELETE /resource/{id}` — Delete

### Response Format

```json
{
  "status": "success|error|pending",
  "data": { ... },
  "message": "Human-readable message"
}
```

### Error Handling

- 400 — Bad request (validation error)
- 404 — Not found
- 500 — Internal error (with retry)
- 503 — Service unavailable (auth required)

## Celery Task Design

### Task Routing

```python
task_routes = {
    'app.tasks.process_beat_promotion': {'queue': 'marketing'},
    'app.tasks.generate_video_task': {'queue': 'marketing'},
    'app.tasks.upload_to_youtube_task': {'queue': 'marketing'},
    'app.tasks.research_youtube_trends_task': {'queue': 'marketing'},
    'app.tasks.sync_youtube_analytics_task': {'queue': 'marketing'},
}
```

### Retry Strategy

- Upload tasks: 3 retries, 5 min delay
- Pipeline tasks: 3 retries, 1 min delay
- Trend tasks: No retries (non-critical)
- Analytics: 2 retries, 10 min delay

## Security

### OAuth Token Management
- Encrypted storage
- Auto-refresh before expiry
- 90-day rotation policy

### API Keys
- Environment variables only
- Never committed to repo
- Separate per channel

### Rate Limiting
- Per-platform quotas
- Queue-based throttling
- Exponential backoff

## Scaling Strategy

### Horizontal Scaling
- **Video rendering:** Dedicated workers (CPU-intensive)
- **Upload workers:** Separate queue (API rate limits)
- **Thumbnail generation:** CPU workers, many instances
- **Trend research:** Single worker (lightweight)

### Caching
- Keyword research: 6-hour cache
- Trend data: 2-hour cache
- Templates: In-memory
- Upload status: Redis

### Storage
- Videos: Local → S3/R2
- Thumbnails: Local → S3/R2
- Analytics: PostgreSQL
- Cache: Redis

## Monitoring

### Metrics to Track
- Uploads per day per channel
- Average CTR per genre
- Revenue per video
- Pipeline success rate
- Rule trigger frequency
- API quota usage

### Alerts
- Upload failure rate > 5%
- CTR drops below 2%
- API quota at 80%
- Pipeline failure
- Trend spike detected

## Future Enhancements

### Short Term
- GPU-accelerated rendering
- Real-time dashboard
- Shopify webhook integration
- Email notifications

### Long Term
- ML-based thumbnail generation (Stable Diffusion)
- Voice-over generation
- Auto-comment replies
- Cross-platform analytics
- Predictive scheduling
- White-label licensing
