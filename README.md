# AI Music Producer

An autonomous AI music production system that generates commercially competitive instrumentals for sale online.

## Overview

This platform uses a **MIDI-first hybrid pipeline** to generate beats:
1. **AI Composition** — Generates MIDI melodies, chords, basslines, drums
2. **Sound Selection** — Assigns premium sounds based on genre
3. **VST Rendering** — Renders through FluidSynth/VST instruments
4. **Mixing** — Applies genre-specific EQ, compression, effects
5. **Mastering** — Optimizes loudness for commercial release
6. **Export** — Outputs WAV, MP3, stems, MIDI
7. **Quality Control** — Spectral analysis and AI scoring
8. **Shopify** — Automatic product upload and sales

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git
- Make (optional, for convenience commands)

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd ai-music-producer

# Copy environment file
cp .env.example .env

# Build and start all services
make build
make up

# Or with Docker Compose directly
docker-compose up -d
```

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost:8000 | FastAPI backend |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Dashboard | http://localhost:3000 | Next.js admin panel |
| Flower | http://localhost:5555 | Celery monitor |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache/Queue |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend (Next.js 14)                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Beat Browser │  │ Waveform     │  │ Analytics    │      │
│  │ Player       │  │ Visualizer   │  │ Dashboard    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│  API Gateway (FastAPI)                                      │
│  Auth • Rate Limit • Routing • WebSockets                   │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │ MIDI    │          │ Sound   │          │ Mix/    │
   │ Worker  │          │ Worker  │          │ Master  │
   └────┬────┘          └────┬────┘          └────┬────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Redis + Celery   │
                    │  Queue System     │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  PostgreSQL       │
                    │  Data Store       │
                    └───────────────────┘
```

## Services

| Service | Port | Responsibility |
|---------|------|---------------|
| API Gateway | 8000 | REST API, WebSockets, auth |
| MIDI Worker | — | MIDI generation, composition |
| Sound Worker | — | Sound assignment, VST rendering |
| Mix Worker | — | Mixing, effects chains |
| Master Worker | — | Mastering, loudness |
| Export Worker | — | File export, previews |
| QC Worker | — | Quality analysis |
| Shopify Worker | — | Store integration |
| Admin Dashboard | 3000 | Web UI |

## Generating Beats

### Via API

```bash
# Generate a single beat
curl -X POST http://localhost:8000/api/v1/beats/generate \
  -H "Content-Type: application/json" \
  -d '{
    "genre_id": "<genre-uuid>",
    "bpm": 140,
    "key_signature": "C minor",
    "mood": "dark",
    "duration_seconds": 180
  }'

# Batch generation
curl -X POST http://localhost:8000/api/v1/beats/batch-generate \
  -H "Content-Type: application/json" \
  -d '{
    "genre_ids": ["<uuid1>", "<uuid2>"],
    "count_per_genre": 10
  }'
```

### Via Dashboard

1. Open http://localhost:3000
2. Navigate to "Generate"
3. Select genre, BPM, key
4. Click "Generate Beat"
5. Monitor progress in real-time

## Configuration

Edit `.env` file:

```env
# Database
DB_PASSWORD=your_secure_password
DATABASE_URL=postgresql://aimusic:password@localhost:5432/aimusic

# Shopify (optional)
SHOPIFY_API_KEY=your_key
SHOPIFY_API_SECRET=your_secret
SHOPIFY_STORE_URL=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_token

# External APIs (optional)
SPOTIFY_CLIENT_ID=your_id
YOUTUBE_API_KEY=your_key
```

## Cost Analysis

| Component | Cost per Beat |
|-----------|--------------|
| MIDI Generation | £0.001 |
| Sound Assignment | £0.001 |
| VST Rendering | £0.005 |
| Mixing | £0.002 |
| Mastering | £0.001 |
| Export | £0.001 |
| QC | £0.002 |
| **Total** | **£0.013** |

Target: **Under £0.10 per beat** ✅

## Development

```bash
# Run API locally
make dev-api

# Run dashboard locally
make dev-dashboard

# View logs
make logs

# Run tests
make test

# Database console
make psql

# Redis console
make redis-cli
```

## Project Structure

```
ai-music-producer/
├── docker-compose.yml
├── Makefile
├── .env.example
├── services/
│   ├── api-gateway/          # FastAPI main API
│   ├── composition-engine/   # MIDI generation
│   ├── sound-engine/         # Sound selection & VST
│   ├── mixing-engine/        # Mixing chains
│   ├── mastering-engine/     # Loudness optimization
│   ├── quality-scoring/      # QC analysis
│   ├── export-pipeline/      # File export
│   ├── shopify-integration/  # E-commerce
│   ├── trend-research/       # Trend detection
│   └── adaptive-learning/    # ML feedback loop
├── frontend/
│   └── admin-dashboard/      # Next.js UI
├── shared/
│   ├── models/               # Pydantic models
│   └── utils/                # Shared utilities
├── migrations/               # Database migrations
├── models/                   # AI model weights
├── output/                   # Generated files
└── tests/                    # Test suites
```

## License

Proprietary — All rights reserved.

## Support

For issues and feature requests, please open a GitHub issue.
