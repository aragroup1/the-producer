"""Tests for SEO engine."""

import pytest
from datetime import datetime

from app.seo.title_generator import TitleGenerator
from app.seo.description_builder import DescriptionBuilder
from app.seo.keyword_researcher import KeywordResearcher


class TestTitleGenerator:
    """Test title generation."""
    
    def test_generate_title(self):
        """Test basic title generation."""
        generator = TitleGenerator()
        
        beat_info = {
            'genre': 'trap',
            'bpm': 140,
            'key': 'C',
            'scale': 'minor',
            'mood': 'dark'
        }
        
        title = generator.generate_title(beat_info)
        
        assert len(title) > 0
        assert len(title) <= 100
        assert 'trap' in title.lower() or 'Trap' in title
    
    def test_generate_variants(self):
        """Test generating multiple variants."""
        generator = TitleGenerator()
        
        beat_info = {
            'genre': 'drill',
            'bpm': 150,
            'key': 'D',
            'scale': 'minor'
        }
        
        variants = generator.generate_variants(beat_info, count=3)
        
        assert len(variants) == 3
        assert len(set(variants)) == 3  # All unique
    
    def test_score_title(self):
        """Test title scoring."""
        generator = TitleGenerator()
        
        beat_info = {'genre': 'trap', 'bpm': 140}
        title = "Dark Trap Type Beat 2026 | Hard Instrumental"
        
        scores = generator.score_title(title, beat_info)
        
        assert 'length' in scores
        assert 'power_words' in scores
        assert 'overall' in scores
        assert scores['overall'] > 0
    
    def test_shorts_title(self):
        """Test Shorts-optimized title."""
        generator = TitleGenerator()
        
        beat_info = {'genre': 'trap', 'bpm': 140}
        title = generator.generate_title(beat_info, platform='shorts')
        
        assert any(emoji in title for emoji in ['🔥', '⚡', '💯', '🎹'])


class TestDescriptionBuilder:
    """Test description building."""
    
    def test_build_description(self):
        """Test full description generation."""
        builder = DescriptionBuilder()
        
        beat_info = {
            'genre': 'trap',
            'bpm': 140,
            'key': 'C',
            'scale': 'minor',
            'structure': 'standard'
        }
        
        desc = builder.build_description(beat_info)
        
        assert len(desc) > 100
        assert '⏱️ Timestamps:' in desc
        assert '💰' in desc or '📜' in desc
        assert '#' in desc
    
    def test_shorts_description(self):
        """Test Shorts description."""
        builder = DescriptionBuilder()
        
        beat_info = {
            'genre': 'trap',
            'bpm': 140
        }
        
        desc = builder.build_shorts_description(beat_info)
        
        assert len(desc) < 500
        assert '#shorts' in desc
    
    def test_generate_tags(self):
        """Test tag generation."""
        builder = DescriptionBuilder()
        
        beat_info = {
            'genre': 'trap',
            'bpm': 140,
            'key': 'C',
            'scale': 'minor',
            'mood': 'dark'
        }
        
        tags = builder.generate_tags(beat_info)
        
        assert len(tags) > 0
        assert 'trap type beat' in [t.lower() for t in tags]
        assert sum(len(t) for t in tags) <= 500
    
    def test_score_description(self):
        """Test description scoring."""
        builder = DescriptionBuilder()
        
        desc = builder.build_description({
            'genre': 'trap',
            'bpm': 140,
            'key': 'C',
            'scale': 'minor'
        })
        
        scores = builder.score_description(desc)
        
        assert 'length' in scores
        assert 'has_timestamps' in scores
        assert 'overall' in scores


class TestKeywordResearcher:
    """Test keyword research."""
    
    def test_get_suggestions(self):
        """Test getting search suggestions."""
        researcher = KeywordResearcher()
        
        suggestions = researcher.get_youtube_suggestions("trap type beat", max_results=5)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 5
    
    def test_research_genre(self):
        """Test researching a genre."""
        researcher = KeywordResearcher()
        
        keywords = researcher.research_genre_keywords('trap')
        
        # May return empty if API fails, but should not crash
        assert isinstance(keywords, list)
        if keywords:
            assert all(hasattr(kw, 'keyword') for kw in keywords)
    
    def test_find_opportunities(self):
        """Test finding keyword opportunities."""
        researcher = KeywordResearcher()
        
        opportunities = researcher.find_opportunities('drill', min_volume=100)
        
        assert isinstance(opportunities, list)
