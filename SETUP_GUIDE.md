# Step-by-Step Setup Guide: AI Beat Generator

## Goal
Get your AI Music Producer generating commercial-quality beats that you can sell.

---

## Phase 1: Get Real Samples (This Week)

### What You Need to Buy

| Priority | Item | Where to Buy | Est. Cost | Why |
|----------|------|-------------|-----------|-----|
| **1** | **Cymatics Diablo Drum Kit** | cymatics.fm | £50-80 | Industry-standard trap drums |
| **1** | **Cymatics Titan Drum Kit** | cymatics.fm | £50-80 | Alternative trap/drill drums |
| **2** | **Cymatics 808 Collection** | cymatics.fm | £30-50 | Tuned 808s in every key |
| **2** | **Xfer Serum** | xferrecords.com | £150 | Professional wavetable synth |
| **3** | **Splice Subscription** | splice.com | £8/month | Unlimited one-shots & loops |
| **3** | **Cymatics Odyssey** | cymatics.fm | £50-80 | Melodic loops & one-shots |

**Total: ~£400-600 to start** (you don't need everything at once)

### Free Alternatives (If You Want to Test First)

| Item | Where | Notes |
|------|-------|-------|
| Cymatics Free Packs | cymatics.fm/free-download | 5-10 free packs, good quality |
| Spitfire LABS | labs.spitfireaudio.com | Free orchestral/ambient instruments |
| Vital Synth | vital.audio | Free wavetable synth (Serum alternative) |
| 99Sounds Drum Kits | 99sounds.org | Free drum samples |

### How to Organize Your Samples

Once downloaded, organize them into this exact structure (the code expects this):

```
samples/
├── drums/
│   ├── kicks/
│   │   ├── trap/           ← Put your trap kicks here
│   │   ├── drill/          ← Put your drill kicks here
│   │   ├── afrobeats/      ← Put your afrobeats kicks here
│   │   └── lofi/           ← Put your lofi kicks here
│   ├── snares/
│   │   ├── trap/
│   │   └── ...
│   ├── hihats/
│   │   ├── trap/
│   │   └── ...
│   ├── 808s/
│   │   ├── trap/           ← Name files like: 808_C.wav, 808_F#.wav
│   │   └── ...
│   ├── claps/
│   │   └── ...
│   └── percs/
│       └── ...
├── melodic/
│   ├── synth_leads/
│   │   ├── trap/           ← Name files like: lead_C.wav, lead_A#3.wav
│   │   └── ...
│   ├── synth_pads/
│   │   └── ...
│   ├── pianos/
│   │   └── ...
│   ├── bass/
│   │   └── ...
│   ├── plucks/
│   │   └── ...
│   └── guitars/
│       └── ...
└── fx/
    ├── risers/
    ├── impacts/
    ├── transitions/
    └── ambience/
```

**Naming Convention for Root Notes:**
- `808_C.wav` → C3 (MIDI note 48)
- `808_C1.wav` → C1 (MIDI note 36)
- `lead_A#3.wav` → A#3 (MIDI note 58)
- `kick_01.wav` → No root note (drums don't need one)

---

## Phase 2: Test Your Setup (Same Day)

### Step 1: Verify Samples Are Detected

```bash
cd "c:\Users\AraLT\OneDrive\Documents\Business\The Producer"
source .venv/Scripts/activate
python -c "
import importlib.util
spec = importlib.util.spec_from_file_location('sample_engine', 'services/sound-engine/app/sample_engine.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

engine = mod.SampleEngine()

# Check what loaded
for key, sm in engine.sample_maps.items():
    print(f'{key[0]}/{key[1]}: {len(sm.samples)} samples')
"
```

You should see all your categories with sample counts.

### Step 2: Generate Your First Real Beat

```bash
python scripts/demo_generate_beat.py --genre trap --bpm 140 --output ./output
```

This creates:
- `./output/stems/` — Individual instrument tracks
- `./output/demo_*.wav` — Full mixed beat

### Step 3: Listen and Evaluate

Open the WAV file in any audio player. Ask yourself:
- Do the drums sound punchy?
- Is the 808 deep and tuned?
- Do the melodies sound professional?
- Is the overall mix balanced?

**If something sounds off, it's the samples** — not the code.

---

## Phase 3: Generate Beats in Bulk (Week 1-2)

### Generate 50 Beats

```bash
# Create a batch generation script
python -c "
import os
import sys
sys.path.insert(0, '.')
import importlib.util

spec = importlib.util.spec_from_file_location('sample_engine', 'services/sound-engine/app/sample_engine.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

from scripts.demo_generate_beat import generate_beat

genres = ['trap', 'drill', 'afrobeats', 'lofi']
bpms = {'trap': [130, 140, 150], 'drill': [140, 150], 'afrobeats': [100, 110, 120], 'lofi': [80, 90]}
keys = ['C', 'D', 'E', 'F', 'G', 'A']

output_dir = './batch_output'
os.makedirs(output_dir, exist_ok=True)

for genre in genres:
    for bpm in bpms[genre]:
        for key in keys[:2]:  # Just 2 keys per combo for testing
            try:
                beat_id = generate_beat(genre, bpm, key, output_dir)
                print(f'Generated: {beat_id}')
            except Exception as e:
                print(f'Failed {genre}/{bpm}/{key}: {e}')
"
```

### Expected Output
- 24 beats (4 genres × 3 BPMs × 2 keys)
- Each beat: ~30 seconds, 4 stems + mix
- Total time: ~10-15 minutes

---

## Phase 4: Quality Control (Week 2)

### Run QC on Generated Beats

```bash
python -c "
import os
import sys
sys.path.insert(0, '.')
import importlib.util

# Load quality scorer
spec = importlib.util.spec_from_file_location('qc_tasks', 'services/quality-scoring/app/tasks.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

scorer = mod.QualityScorer()

output_dir = './batch_output'
for file in os.listdir(output_dir):
    if file.endswith('_mix.wav'):
        path = os.path.join(output_dir, file)
        results = scorer.full_quality_check(path)
        print(f'{file}: Score={results[\"overall_score\"]:.1f}/10, Passed={results[\"passed\"]}')
"
```

### What to Look For

| Score | Action |
|-------|--------|
| 8-10 | Excellent — keep and tag for premium |
| 6-7 | Good — acceptable for sale |
| 4-5 | Fair — needs remix or regeneration |
| 0-3 | Poor — discard and adjust parameters |

---

## Phase 5: Prepare for Sale (Week 3-4)

### What You Need to Sell Beats

1. **Audio Files**
   - Full beat (WAV + MP3 320kbps)
   - Tagged preview (with voiceover watermark)
   - Stems ZIP (for lease/premium licenses)

2. **Metadata**
   - Genre, BPM, Key
   - Mood tags (dark, melodic, aggressive, etc.)
   - Track length
   - License type (basic, premium, exclusive)

3. **Platform**
   - BeatStars, Airbit, or your own Shopify store

### Generate Export-Ready Files

The export pipeline already handles this:

```python
from services.export-pipeline.app.tasks import ExportPipeline

pipeline = ExportPipeline(output_base='./for_sale')

# Export all formats
result = pipeline.export_beat(
    beat_id='my_beat_001',
    audio_path='./batch_output/my_beat_mix.wav',
    midi_path='./batch_output/my_beat.mid',
    formats=['wav', 'mp3', 'preview', 'midi']
)

print(result)
# {
#   'wav': './for_sale/beats/my_beat_001.wav',
#   'mp3': './for_sale/beats/my_beat_001.mp3',
#   'preview': './for_sale/previews/my_beat_001_preview.mp3',
#   'midi': './for_sale/midi/my_beat_001.mid'
# }
```

---

## Quick Reference: Daily Workflow

### Generate 10 Beats

```bash
# 1. Activate environment
cd "c:\Users\AraLT\OneDrive\Documents\Business\The Producer"
source .venv/Scripts/activate

# 2. Generate beats
for genre in trap drill; do
  for bpm in 130 140 150; do
    python scripts/demo_generate_beat.py --genre $genre --bpm $bpm --output ./daily_output
  done
done

# 3. Check quality
python -m pytest tests/unit/test_sample_engine.py -v

# 4. Listen to outputs
ls ./daily_output/*.wav
```

### Cost Per Beat

| Component | Cost |
|-----------|------|
| Samples (amortized) | ~£0.01 |
| Compute (your PC) | £0.00 |
| Storage | ~£0.001 |
| **Total** | **~£0.011 per beat** |

**Target selling price: £20-50 per beat** = 1800-4500x margin

---

## Troubleshooting

### "No samples found for kick"
→ Check `samples/drums/kicks/trap/` exists and has WAV files

### "Beat sounds robotic"
→ Increase humanization: `--humanize 10` in render call

### "Drums too quiet"
→ Check sample levels. Real samples should peak around -6 to -3 dB.

### "Mix is clipping"
→ The engine auto-limits to 0.95, but you may need to lower stem gains in `mix_stems()`

### "808s not tuned"
→ Name your 808 files with root notes: `808_C.wav`, `808_F#.wav`

---

## Next Steps After You're Generating

1. **Build a catalog** — Generate 100+ beats, tag them well
2. **Set up BeatStars/Airbit** — Upload previews, set prices
3. **Create a brand** — Name, logo, consistent style
4. **Market on social** — Instagram/TikTok with beat previews
5. **Build the web store** — Next.js frontend + Shopify integration
6. **Train AI models** — Collect your best MIDI, train MusicTransformer

---

## Support

If something breaks:
1. Run tests: `python -m pytest tests/unit/ -v`
2. Check logs — structlog outputs detailed info
3. Verify samples are in the right directories
4. Check the demo script works: `python scripts/demo_generate_beat.py`

**The system is ready. The quality is in your samples. Go get good sounds.**
