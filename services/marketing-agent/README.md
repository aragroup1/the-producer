# AI Content Promotion System

A complete AI-operated music marketing engine for autonomous beat promotion, video generation, SEO optimization, multi-channel management, trend detection, and conversion tracking.

## 🚀 What This System Does

This is NOT a simple uploader. This is a **growth engine** that:

- **Generates videos** automatically from beats (waveform, spectrum, particle visualizers)
- **Creates thumbnails** optimized for CTR with genre-specific aesthetics
- **Generates SEO** titles, descriptions, tags, timestamps
- **Manages multiple YouTube channels** (Drill Beats, Trap Vault, Lo-Fi Station, etc.)
- **Creates Shorts/Reels/TikTok** versions automatically
- **Detects trends** across YouTube, TikTok, Google, and beat markets
- **Tracks analytics** — CTR, retention, conversions, revenue
- **Learns** what works and optimizes future content
- **Automates decisions** with IF/THEN rules

## 📊 System Stats

- **45 Python files** — 10,548 lines of engine code
- **45 unit tests** — all passing
- **15 subsystems** — Video, Thumbnail, SEO, Upload, Channels, Trends, Analytics, Learning, Rules
- **6 default channels** — Drill, Trap, Emotional Guitar, Lo-Fi, Afrobeats, R&B
- **19 genres supported** — Full genre library integration

## 🏗️ Architecture

```
marketing-agent/
├── app/
│   ├── main.py              # FastAPI service (port 8005)
│   ├── tasks.py             # Celery background tasks
│   ├── config.py            # Service configuration
│   │
│   ├── core/                # Pipeline orchestration
│   │   ├── beat_pipeline.py      # Full promotion workflow
│   │   ├── channel_manager.py    # Multi-channel management
│   │   └── rule_engine.py        # IF/THEN automation rules
│   │
│   ├── video/               # Video generation
│   │   ├── renderer.py           # FFmpeg video rendering
│   │   ├── visualizers.py        # Waveform/Spectrum/Particle
│   │   ├── shorts_generator.py   # Shorts/Reels/TikTok
│   │   └── templates.py          # Genre-specific templates
│   │
│   ├── thumbnail/           # Thumbnail AI
│   │   ├── generator.py          # Thumbnail generation
│   │   ├── text_overlay.py       # Text effects (glow/neon/outline)
│   │   ├── style_presets.py      # Genre aesthetics
│   │   └── ab_testing.py         # A/B test framework
│   │
│   ├── seo/                 # SEO engine
│   │   ├── title_generator.py    # AI-powered titles
│   │   ├── description_builder.py # Optimized descriptions
│   │   ├── keyword_researcher.py  # Trending keywords
│   │   └── rank_tracker.py       # Search position tracking
│   │
│   ├── upload/              # Upload automation
│   │   ├── youtube_uploader.py   # YouTube Data API v3
│   │   ├── tiktok_uploader.py    # TikTok API
│   │   ├── instagram_uploader.py # Instagram Graph API
│   │   └── beat_platforms.py     # BeatStars/Airbit
│   │
│   ├── trends/              # Trend detection
│   │   ├── youtube_trends.py     # YouTube trending
│   │   ├── tiktok_trends.py      # TikTok viral sounds
│   │   ├── google_trends.py      # Google Trends
│   │   └── beat_market_trends.py # Beat market analysis
│   │
│   ├── analytics/           # Analytics engine
│   │   ├── youtube_analytics.py  # YouTube Analytics API
│   │   ├── ctr_tracker.py        # CTR monitoring
│   │   ├── retention_analyzer.py # Watch time analysis
│   │   └── conversion_tracker.py # Revenue attribution
│   │
│   ├── learning/            # AI learning
│   │   ├── performance_model.py  # Performance prediction
│   │   ├── thumbnail_optimizer.py # Thumbnail learning
│   │   ├── title_optimizer.py    # Title learning
│   │   └── genre_predictor.py    # Genre trend prediction
│   │
│   └── scheduler/           # Scheduling
│       ├── content_calendar.py   # Post scheduling
│       ├── optimal_times.py      # Best posting times
│       └── queue_manager.py      # Upload queue
│
├── tests/
│   ├── unit/
│   │   ├── test_video.py
│   │   ├── test_thumbnail.py
│   │   ├── test_seo.py
│   │   └── test_core.py
│   └── test_marketing.py
│
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🎬 Video Generation

### Templates

| Template | Genre | Style | Aspect |
|----------|-------|-------|--------|
| dark_trap_16x9 | Trap | Bars | 16:9 |
| dark_trap_9x16 | Trap | Bars | 9:16 |
| uk_drill_16x9 | Drill | Spectrum | 16:9 |
| uk_drill_9x16 | Drill | Spectrum | 9:16 |
| lofi_16x9 | Lo-Fi | Particles | 16:9 |
| lofi_9x16 | Lo-Fi | Particles | 9:16 |
| rnb_16x9 | R&B | Circular | 16:9 |
| afrobeats_16x9 | Afrobeats | Waveform | 16:9 |

### Visualizer Styles

- **Waveform** — Classic centered line, syncs to audio energy
- **Spectrum** — Frequency bars with mirrored effect
- **Particles** — Floating particles for chill genres
- **Bars** — Vertical bar visualizer
- **Circular** — Circular spectrum analyzer
- **Glitch** — Digital distortion effects

## 🖼️ Thumbnail Generation

### Style Presets

| Preset | Genre | Effect | Colors |
|--------|-------|--------|--------|
| dark_trap | Trap | Neon | Black/Red |
| dark_drill | Drill | Glow | Black/Green |
| chill_lofi | Lo-Fi | Shadow | Grey/Blue |
| smooth_rnb | R&B | Gradient | Purple/Pink |
| vibrant_afrobeats | Afrobeats | Glow | Dark/Orange |
| classic_boombap | Boom Bap | Outline | Navy/Orange |

### Text Effects

- **Glow** — Soft glow behind text
- **Outline** — Bold outline for readability
- **Shadow** — Drop shadow
- **Gradient** — Vertical color gradient
- **Neon** — Neon tube effect
- **Chrome** — Metallic/chrome effect

### A/B Testing

Automatically generates 3 variants (A/B/C) per beat:
- Variant A: Big title centered
- Variant B: "FREE" badge prominent
- Variant C: Minimal with emoji

## 🔍 SEO Engine

### Title Generation

Generates optimized titles like:
- "Dark Trap Type Beat 2026 | Travis Scott x Future Style"
- "UK Drill Type Beat — 'D Minor' | Hard Dark Instrumental"
- "FREE Afrobeats Type Beat | Burna Boy x Wizkid Style"

### Description Builder

Auto-generates descriptions with:
- SEO-optimized first 2 lines
- Section timestamps (Intro/Verse/Hook/Bridge/Outro)
- Licensing info
- Call-to-action
- Hashtag block

### Keyword Research

- YouTube autocomplete scraping
- Trending keyword detection
- Search volume estimation
- Competition analysis
- Opportunity scoring

## 📺 Multi-Channel Management

### Default Channels

| Channel | Niche | Uploads/Day | Best Hours |
|---------|-------|-------------|------------|
| Drill Beats Daily | Drill | 3 | 10, 14, 19 |
| Trap Vault | Trap | 4 | 9, 13, 17, 21 |
| Emotional Guitar | Emotional | 2 | 11, 20 |
| Lo-Fi Chill Station | Lo-Fi | 2 | 8, 22 |
| Afrobeats Vibes | Afrobeats | 3 | 10, 15, 20 |
| Smooth R&B Beats | R&B | 2 | 12, 19 |

### Intelligent Assignment

Automatically assigns beats to channels based on:
- Genre match
- Upload frequency limits
- Time since last upload
- Content type compatibility

## 📈 Analytics

### CTR Tracking

- Per-video CTR monitoring
- A/B variant performance comparison
- Industry benchmark comparison
- Improvement recommendations

### Conversion Tracking

Full funnel tracking:
- Video view → Click → Add to cart → Purchase
- Revenue attribution per video
- ROI by content piece
- Best-performing genres/thumbnails/titles

## 🤖 AI Learning

### Performance Prediction

Predicts CTR and views based on:
- Genre
- Title style
- Thumbnail style
- Upload time
- Trending keywords

### Genre Predictions

Predicts trending genres 14 days ahead using:
- Seasonal patterns
- Historical momentum
- Market signals

### Best Practices

Automatically learns:
- Best color combinations per genre
- Best text effects
- Best title patterns
- Best upload times

## ⚡ Automation Rules

### Pre-built Rules

| Rule | Condition | Action |
|------|-----------|--------|
| High CTR Drill | drill + CTR > 5% | Increase drill uploads |
| Emotional Guitar Trend | emotional guitar trend spikes | Generate 10 videos |
| Low CTR Alert | CTR < 2% + impressions > 1000 | Create thumbnail A/B test |
| Viral Opportunity | views/hour > 1000 | Boost promotion + create shorts |
| Weekend Boost | Saturday/Sunday | 1.5x upload frequency |
| A/B Winner | confidence > 95% | Apply winner as default |

### Custom Rules

Create your own IF/THEN rules via API:

```python
POST /rules
{
  "name": "My Custom Rule",
  "conditions": [
    {"metric": "genre", "operator": "==", "value": "trap"},
    {"metric": "ctr", "operator": ">", "value": 0.06}
  ],
  "logical_op": "and",
  "actions": [
    {"type": "increase_uploads", "genre": "trap", "amount": 2}
  ]
}
```

## 🚀 API Endpoints

### Pipeline
- `POST /pipeline/process` — Process single beat
- `POST /pipeline/batch` — Process multiple beats

### Video
- `POST /videos/generate` — Generate full video
- `POST /videos/shorts/generate` — Generate short
- `POST /videos/shorts/all` — Generate all platform shorts

### Thumbnail
- `POST /thumbnails/generate` — Generate thumbnail
- `POST /thumbnails/variants` — Generate A/B/C variants

### SEO
- `POST /seo/titles` — Generate titles
- `POST /seo/description` — Generate description
- `POST /seo/tags` — Generate tags
- `GET /seo/keywords/research` — Research keywords
- `GET /seo/keywords/trending` — Get trending keywords

### Channels
- `GET /channels` — List channels
- `GET /channels/{id}/stats` — Channel stats
- `GET /channels/{id}/schedule` — Upload schedule
- `POST /channels/assign` — Assign beat to channel

### Trends
- `GET /trends/youtube` — YouTube trends
- `GET /trends/tiktok` — TikTok trends
- `GET /trends/market` — Beat market trends
- `GET /trends/genre/{genre}` — Genre-specific trends

### Analytics
- `POST /analytics/ctr` — Record CTR
- `GET /analytics/ctr/summary` — CTR summary
- `GET /analytics/ctr/recommendations` — Recommendations
- `GET /analytics/ctr/variants` — Variant performance

### Learning
- `GET /learning/genre-predictions` — Genre predictions
- `GET /learning/genre-recommendations` — Production recommendations
- `GET /learning/performance` — Performance insights

### Rules
- `GET /rules` — List rules
- `POST /rules` — Create rule
- `POST /rules/{id}/toggle` — Enable/disable rule
- `GET /rules/stats` — Rule stats
- `POST /rules/evaluate` — Evaluate rules

### Upload
- `POST /upload/youtube` — Upload to YouTube

## 🛠️ Setup

### Requirements

```bash
pip install -r requirements.txt
```

Key dependencies:
- FastAPI + Uvicorn
- Celery + Redis
- Pillow (image processing)
- soundfile (audio analysis)
- numpy (visualizer math)
- structlog (logging)

### YouTube API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable YouTube Data API v3
3. Create OAuth 2.0 credentials
4. Download `client_secret.json`
5. Place in `./credentials/youtube/`
6. Run auth flow once

### Running

```bash
# Start API
uvicorn app.main:app --port 8005 --reload

# Start Celery worker
celery -A app.tasks worker -Q marketing -l info

# Start Celery beat (scheduler)
celery -A app.tasks beat -l info
```

### Docker

```bash
docker build -t marketing-agent .
docker run -p 8005:8005 marketing-agent
```

## 📋 Celery Task Schedule

| Task | Frequency |
|------|-----------|
| research_youtube_trends | Every 2 hours |
| research_tiktok_trends | Every 2 hours |
| sync_youtube_analytics | Every 6 hours |
| analyze_ab_tests | Daily |
| update_learning_models | Daily |
| evaluate_automation_rules | Every hour |
| process_upload_queue | Every 15 minutes |

## 🎯 Usage Examples

### Generate Full Promotion Package

```python
import requests

response = requests.post("http://localhost:8005/pipeline/process", json={
    "beat": {
        "beat_id": "trap_140_C_minor",
        "genre": "trap",
        "bpm": 140,
        "key": "C",
        "scale": "minor",
        "file_path": "./output/trap_140_C_minor_mix.wav"
    },
    "generate_video": True,
    "generate_thumbnails": True,
    "generate_shorts": True,
    "thumbnail_variants": 3
})

result = response.json()
print(f"Video: {result['outputs']['video']}")
print(f"Thumbnails: {result['outputs']['thumbnails']}")
print(f"Shorts: {result['outputs']['shorts']}")
```

### Generate Thumbnails

```python
response = requests.post("http://localhost:8005/thumbnails/variants", json={
    "beat_info": {
        "beat_id": "drill_150_D_minor",
        "genre": "drill",
        "bpm": 150,
        "key": "D",
        "scale": "minor"
    },
    "count": 3
})
```

### Get Trend Predictions

```python
response = requests.get("http://localhost:8005/learning/genre-predictions?days_ahead=14")
predictions = response.json()["predictions"]

for pred in predictions[:5]:
    print(f"{pred['genre']}: {pred['trend_probability']:.0%} chance of trending")
```

## 📈 Scaling

### Rate Limits

| Platform | Daily Limit | Strategy |
|----------|-------------|----------|
| YouTube | 100 uploads | Queue + spread |
| TikTok | 50 uploads | 30 min apart |
| Instagram | 25 uploads | Conservative |
| BeatStars | 200 uploads | Batch |

### Hardware

**Development:**
- CPU: Any modern processor
- RAM: 16GB
- Storage: 100GB SSD

**Production (100+ uploads/day):**
- CPU: 16+ cores
- RAM: 64GB
- Storage: 1TB NVMe
- GPU: NVIDIA RTX A4000 (optional, for AI thumbnails)

**Enterprise (1000+ uploads/day):**
- Kubernetes cluster
- Dedicated GPU nodes
- CDN for video delivery
- Object storage (S3/R2)

## 🧪 Testing

```bash
cd services/marketing-agent
pytest tests/unit/ -v
```

45 tests covering:
- Video generation (templates, visualizers, renderer, shorts)
- Thumbnail generation (presets, text effects, A/B testing)
- SEO (titles, descriptions, tags, keywords)
- Core pipeline (channels, rules, upload plans)

## 🔮 Roadmap

### MVP (Done ✅)
- [x] Video generation (waveform + text)
- [x] Thumbnail generation (text overlay)
- [x] SEO metadata generation
- [x] Multi-channel management
- [x] Shorts/Reels/TikTok generation
- [x] Trend detection
- [x] Analytics tracking
- [x] A/B testing
- [x] Automation rules
- [x] AI learning system

### Growth (Next)
- [ ] YouTube OAuth auto-refresh
- [ ] TikTok direct upload API
- [ ] Instagram Reels API
- [ ] BeatStars partner API
- [ ] Shopify conversion tracking
- [ ] Email marketing integration
- [ ] Discord/Telegram notifications

### Enterprise
- [ ] GPU-accelerated rendering
- [ ] Multi-language support
- [ ] White-label capability
- [ ] Advanced ML models
- [ ] Real-time dashboard
- [ ] Team collaboration

## 📄 License

Proprietary — All rights reserved.

## 🤝 Support

For questions or issues, refer to the main project documentation.
