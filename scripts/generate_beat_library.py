#!/usr/bin/env python3
"""
Batch Beat Library Generator

Generates an initial catalog of beats across multiple genres.
Usage:
    python scripts/generate_beat_library.py --count 50
    python scripts/generate_beat_library.py --genres trap,drill,afrobeats --count 30
    python scripts/generate_beat_library.py --auto-approve

Requires the API to be running locally.
"""

import argparse
import asyncio
import random
import httpx
from typing import List

API_BASE = "http://localhost:8000/api/v1"

# Genre configurations with target counts
GENRE_TARGETS = {
    'trap': {'count': 20, 'bpm_range': (130, 160), 'moods': ['dark', 'melodic', 'aggressive']},
    'drill': {'count': 15, 'bpm_range': (140, 160), 'moods': ['dark', 'melodic', 'uk']},
    'afrobeats': {'count': 15, 'bpm_range': (100, 120), 'moods': ['upbeat', 'vibey', 'romantic']},
    'lofi': {'count': 10, 'bpm_range': (70, 85), 'moods': ['chill', 'sad', 'dreamy']},
    'rnb': {'count': 10, 'bpm_range': (65, 80), 'moods': ['smooth', 'trap_soul', 'alternative']},
    'boom_bap': {'count': 10, 'bpm_range': (85, 95), 'moods': ['classic', 'jazz', 'soulful']},
    'hyperpop': {'count': 5, 'bpm_range': (140, 160), 'moods': ['glitch', 'emotional', 'bouncy']},
    'ambient': {'count': 5, 'bpm_range': (60, 80), 'moods': ['ethereal', 'cinematic']},
}

KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


async def get_genres(client: httpx.AsyncClient) -> List[dict]:
    """Fetch available genres from API."""
    try:
        resp = await client.get(f"{API_BASE}/genres")
        if resp.status_code == 200:
            data = resp.json()
            return data.get('items', [])
    except Exception as e:
        print(f"Warning: Could not fetch genres: {e}")
    return []


async def generate_beat(
    client: httpx.AsyncClient,
    genre_id: str,
    genre_name: str,
    bpm: int,
    key: str,
    mood: str,
    auto_approve: bool = False
) -> dict:
    """Generate a single beat via API."""
    
    payload = {
        'genre_id': genre_id,
        'bpm': bpm,
        'key_signature': key,
        'mood': mood,
        'duration_seconds': 180,
        'title': f"{genre_name.title()} {mood.title()} — {bpm} BPM",
        'tags': [genre_name, mood, str(bpm) + 'bpm', 'ai-generated'],
        'priority': 5,
    }
    
    try:
        resp = await client.post(f"{API_BASE}/beats/generate", json=payload)
        if resp.status_code == 202:
            data = resp.json()
            beat_id = data.get('beat_id')
            print(f"  ✓ Queued: {payload['title']} (ID: {beat_id[:8]}...)")
            
            if auto_approve and beat_id:
                # Note: Approval should happen after generation completes
                # This is a placeholder - in production, use a callback
                pass
            
            return data
        else:
            print(f"  ✗ Failed: {payload['title']} — {resp.status_code}: {resp.text[:100]}")
            return {}
    except Exception as e:
        print(f"  ✗ Error: {payload['title']} — {e}")
        return {}


async def generate_library(args):
    """Generate the full beat library."""
    
    print("=" * 60)
    print("THE PRODUCER — Batch Beat Library Generator")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get genres
        genres = await get_genres(client)
        
        if not genres:
            print("\nERROR: Could not connect to API or no genres found.")
            print("Make sure the API is running: python -m services.api-gateway.app.main")
            return
        
        # Map genre names to IDs
        genre_map = {g['name'].lower(): g['id'] for g in genres}
        
        # Filter to requested genres
        target_genres = args.genres.split(',') if args.genres else list(GENRE_TARGETS.keys())
        
        total_target = 0
        for genre_name in target_genres:
            if genre_name in GENRE_TARGETS:
                total_target += GENRE_TARGETS[genre_name]['count']
        
        if args.count:
            total_target = args.count
        
        print(f"\nTarget: {total_target} beats across {len(target_genres)} genres")
        print(f"API: {API_BASE}")
        print(f"Auto-approve: {args.auto_approve}")
        print("-" * 60)
        
        generated = 0
        failed = 0
        
        for genre_name in target_genres:
            if genre_name not in genre_map:
                print(f"\n⚠ Genre '{genre_name}' not found in API, skipping")
                continue
            
            if genre_name not in GENRE_TARGETS:
                print(f"\n⚠ No config for '{genre_name}', using defaults")
                config = {'count': 5, 'bpm_range': (120, 140), 'moods': ['dark']}
            else:
                config = GENRE_TARGETS[genre_name]
            
            genre_id = genre_map[genre_name]
            target_count = config['count']
            
            if args.count:
                # Distribute count evenly
                target_count = max(1, args.count // len(target_genres))
            
            print(f"\n📀 {genre_name.upper()} (target: {target_count})")
            
            for i in range(target_count):
                bpm = random.randint(config['bpm_range'][0], config['bpm_range'][1])
                key = random.choice(KEYS)
                mood = random.choice(config['moods'])
                
                result = await generate_beat(
                    client, genre_id, genre_name, bpm, key, mood,
                    auto_approve=args.auto_approve
                )
                
                if result:
                    generated += 1
                else:
                    failed += 1
                
                # Small delay to not overwhelm the API
                await asyncio.sleep(0.5)
        
        print("\n" + "=" * 60)
        print(f"GENERATION COMPLETE")
        print(f"  Generated: {generated}")
        print(f"  Failed: {failed}")
        print(f"  Total: {generated + failed}")
        print("=" * 60)
        print("\nBeats are being processed in the background.")
        print("Check the dashboard to see progress.")
        print(f"\nNext steps:")
        print(f"  1. Monitor generation: http://localhost:3000")
        print(f"  2. Approve beats that pass QC")
        print(f"  3. Sync approved beats to Shopify")


def main():
    parser = argparse.ArgumentParser(description='Generate a batch of beats')
    parser.add_argument('--count', type=int, help='Total beats to generate')
    parser.add_argument('--genres', type=str, help='Comma-separated genre list (default: all)')
    parser.add_argument('--auto-approve', action='store_true', help='Auto-approve beats after generation')
    parser.add_argument('--api-url', type=str, default=API_BASE, help='API base URL')
    
    args = parser.parse_args()
    
    asyncio.run(generate_library(args))


if __name__ == '__main__':
    main()
