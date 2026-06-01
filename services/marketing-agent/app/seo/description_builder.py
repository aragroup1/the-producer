"""YouTube description builder with SEO optimization.

Generates descriptions with:
- Timestamps for beat sections
- SEO-optimized first 2 lines
- Call-to-action blocks
- Link placeholders
- Hashtag blocks
"""

import random
from typing import Dict, List, Optional, Any
from datetime import datetime
import structlog

logger = structlog.get_logger()


class DescriptionBuilder:
    """Build optimized YouTube descriptions for beats."""
    
    # CTA templates
    CTAS = [
        "🔥 Subscribe for more beats every week!",
        "🎹 New beats uploaded daily — hit the bell!",
        "💰 Purchase this beat: [LINK]",
        "📧 Contact for exclusive rights: [EMAIL]",
        "⬇️ Free download: [LINK]",
        "🎵 Follow me on Instagram: [INSTAGRAM]",
        "🔔 Turn on notifications for new drops!",
    ]
    
    # License pricing blocks
    LICENSE_BLOCKS = [
        """💰 Licensing:
• Basic Lease (MP3) — £20
• Premium Lease (WAV + Stems) — £50
• Exclusive Rights — £200
• Unlimited License — £100""",
        
        """📜 Available Licenses:
• MP3 Lease — £20
• WAV Lease — £35
• Trackout/Stems — £50
• Exclusive — £200""",
    ]
    
    # Section timestamps for different structures
    SECTION_TIMESTAMPS = {
        "short": [
            (0, "Intro"),
            (8, "Verse"),
            (24, "Hook"),
            (40, "Outro"),
        ],
        "standard": [
            (0, "Intro"),
            (8, "Verse 1"),
            (24, "Hook"),
            (40, "Verse 2"),
            (56, "Hook"),
            (72, "Bridge"),
            (88, "Hook"),
            (104, "Outro"),
        ],
        "extended": [
            (0, "Intro"),
            (8, "Verse 1"),
            (24, "Hook"),
            (40, "Verse 2"),
            (56, "Hook"),
            (72, "Bridge"),
            (88, "Hook"),
            (104, "Verse 3"),
            (120, "Hook"),
            (136, "Outro"),
        ]
    }
    
    def __init__(self):
        self.used_descriptions = set()
    
    def build_description(self, beat_info: Dict[str, Any],
                          title: str = None,
                          timestamps: bool = True,
                          include_cta: bool = True,
                          include_license: bool = True) -> str:
        """Build a complete optimized description.
        
        Args:
            beat_info: Beat metadata
            title: Video title (for first line)
            timestamps: Include section timestamps
            include_cta: Include call-to-action
            include_license: Include pricing
        
        Returns:
            Full description string
        """
        parts = []
        
        # SEO-optimized first 2 lines (visible in search)
        parts.append(self._build_first_lines(beat_info, title))
        
        # Blank line
        parts.append("")
        
        # Timestamps
        if timestamps:
            ts_block = self._build_timestamps(beat_info)
            if ts_block:
                parts.append(ts_block)
                parts.append("")
        
        # License info
        if include_license:
            parts.append(random.choice(self.LICENSE_BLOCKS))
            parts.append("")
        
        # CTA
        if include_cta:
            parts.append(random.choice(self.CTAS))
            parts.append("")
        
        # Tags / hashtags
        parts.append(self._build_hashtags(beat_info))
        
        description = "\n".join(parts)
        
        logger.info("description_built", 
                   beat_id=beat_info.get('beat_id', 'unknown'),
                   length=len(description))
        
        return description
    
    def _build_first_lines(self, beat_info: Dict[str, Any], 
                           title: str = None) -> str:
        """Build SEO-optimized first 2 lines."""
        genre = beat_info.get('genre', 'Beat')
        bpm = beat_info.get('bpm', 140)
        key = beat_info.get('key', 'C')
        scale = beat_info.get('scale', 'minor')
        mood = beat_info.get('mood', 'dark')
        
        genre_display = genre.replace('_', ' ').title()
        
        if title:
            first_line = f"🎹 {title}"
        else:
            first_line = f"🎹 {mood.title()} {genre_display} Type Beat | {bpm} BPM | {key} {scale.title()}"
        
        second_line = f"Free {genre_display.lower()} type beat instrumental. Available for lease and exclusive rights."
        
        return f"{first_line}\n{second_line}"
    
    def _build_timestamps(self, beat_info: Dict[str, Any]) -> str:
        """Build timestamp section."""
        structure = beat_info.get('structure', 'standard')
        bpm = beat_info.get('bpm', 140)
        
        # Calculate actual times based on BPM
        # 1 bar = 4 beats = 240/bpm seconds
        seconds_per_bar = 240 / bpm if bpm > 0 else 1.7
        
        timestamps = self.SECTION_TIMESTAMPS.get(structure, self.SECTION_TIMESTAMPS["standard"])
        
        lines = ["⏱️ Timestamps:"]
        
        for bar, section_name in timestamps:
            seconds = int(bar * seconds_per_bar)
            minutes = seconds // 60
            secs = seconds % 60
            lines.append(f"{minutes}:{secs:02d} — {section_name}")
        
        return "\n".join(lines)
    
    def _build_hashtags(self, beat_info: Dict[str, Any]) -> str:
        """Build hashtag block."""
        genre = beat_info.get('genre', 'typebeat')
        
        hashtags = [
            f"#{genre}beat",
            "#typebeat",
            "#instrumental",
            "#beatsforsale",
            "#producer",
            "#beatmaker",
            "#flstudio",
            "#ableton",
            f"#{genre}",
            "#freebeat",
            "#hiphop",
            "#rapbeat",
        ]
        
        return " ".join(hashtags)
    
    def build_shorts_description(self, beat_info: Dict[str, Any]) -> str:
        """Build description optimized for Shorts."""
        genre = beat_info.get('genre', 'beat')
        bpm = beat_info.get('bpm', 140)
        
        lines = [
            f"🔥 {genre.replace('_', ' ').title()} Type Beat | {bpm} BPM",
            "",
            "💰 Full beat: [LINK]",
            "",
            "#shorts #typebeat #beats #producer"
        ]
        
        return "\n".join(lines)
    
    def generate_tags(self, beat_info: Dict[str, Any],
                      trending_keywords: List[str] = None) -> List[str]:
        """Generate YouTube tags.
        
        Returns list of tags (max 500 chars total).
        """
        genre = beat_info.get('genre', 'typebeat')
        bpm = beat_info.get('bpm', 140)
        key = beat_info.get('key', 'C')
        scale = beat_info.get('scale', 'minor')
        mood = beat_info.get('mood', 'dark')
        
        base_tags = [
            f"{genre} type beat",
            f"{genre} beat",
            f"{genre} instrumental",
            "type beat",
            "free type beat",
            "instrumental",
            "beats",
            "hip hop beat",
            "rap beat",
            f"{mood} beat",
            f"{mood} instrumental",
            f"{bpm} bpm",
            f"{key} {scale}",
            "producer",
            "beatmaker",
            "fl studio",
            "ableton",
            "logic pro",
        ]
        
        # Add trending keywords
        if trending_keywords:
            base_tags.extend(trending_keywords[:5])
        
        # Add artist-style tags
        artist_tags = self._get_artist_tags(genre)
        base_tags.extend(artist_tags)
        
        # Remove duplicates and limit
        unique_tags = list(dict.fromkeys(base_tags))
        
        # Ensure total length under 500 chars
        total_len = 0
        final_tags = []
        for tag in unique_tags:
            if total_len + len(tag) + 2 <= 500:  # +2 for comma and space
                final_tags.append(tag)
                total_len += len(tag) + 2
            else:
                break
        
        return final_tags
    
    def _get_artist_tags(self, genre: str) -> List[str]:
        """Get artist-style tags for a genre."""
        artist_map = {
            "trap": ["travis scott type beat", "future type beat", "lil baby type beat"],
            "drill": ["central cee type beat", "pop smoke type beat", "headie one type beat"],
            "boom_bap": ["joey badass type beat", "griselda type beat"],
            "rnb": ["bryson tiller type beat", "drake type beat", "partynextdoor type beat"],
            "afrobeats": ["burna boy type beat", "wizkid type beat", "davido type beat"],
            "lofi": ["lofi hip hop", "chill beats", "study beats"],
        }
        
        return artist_map.get(genre, [])
    
    def score_description(self, description: str) -> Dict[str, float]:
        """Score a description for optimization."""
        scores = {}
        
        # Length score (optimal: 500-1500 chars)
        length = len(description)
        if 500 <= length <= 1500:
            scores['length'] = 1.0
        elif length < 500:
            scores['length'] = 0.6
        elif length <= 2000:
            scores['length'] = 0.8
        else:
            scores['length'] = 0.4
        
        # Timestamp score
        scores['has_timestamps'] = 1.0 if '⏱️' in description or 'Timestamp' in description else 0.0
        
        # CTA score
        scores['has_cta'] = 1.0 if any(cta.split()[0] in description for cta in self.CTAS) else 0.0
        
        # Link score
        scores['has_links'] = 1.0 if '[LINK]' in description or 'http' in description else 0.0
        
        # Hashtag score
        scores['has_hashtags'] = 1.0 if '#' in description else 0.0
        
        # First line hook score
        lines = description.split('\n')
        if lines:
            first_line = lines[0]
            scores['hook_length'] = 1.0 if 30 <= len(first_line) <= 120 else 0.5
        
        scores['overall'] = sum(scores.values()) / len(scores)
        
        return {k: round(v, 3) for k, v in scores.items()}
