"""
🔊 SIMPLE TTS SERVICE - Google Text-to-Speech (gTTS)
====================================================

Service de synthèse vocale utilisant gTTS (Google Text-to-Speech).
Simple, rapide et fiable pour la voix française.

✅ AVANTAGES:
- Léger et rapide
- Qualité voix française excellente
- Gratuit et stable
- Pas de téléchargement de modèles
- Fonctionne avec internet

📥 INPUT:
{
  "text": "Bonjour, comment puis-je vous aider ?",
  "emotion": "neutral"
}

📤 OUTPUT:
{
  "audio_base64": "SUQzBAAAAAAAI1...",
  "duration_ms": 2500,
  "cached": false
}
"""

import os
import hashlib
import base64
import time
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False


class SimpleTTSService:
    """
    🎙️ Simple Text-to-Speech Service using gTTS
    
    Features:
    - French voice synthesis with gTTS
    - Intelligent caching for performance
    - Base64 audio output
    - Lightweight and fast
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize simple TTS Service
        
        Args:
            cache_dir: Directory for caching audio files
        """
        # Setup cache directory
        self.cache_dir = Path(cache_dir or "tool_router/cache/tts_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🔊 Initializing Simple TTS Service...")
        print(f"📁 Cache directory: {self.cache_dir.absolute()}")
        
        self.fallback_mode = not GTTS_AVAILABLE
        
        if not GTTS_AVAILABLE:
            print("⚠️  gTTS not available. Using fallback mode.")
        else:
            print("✅ gTTS available - ready for French voice synthesis!")
        
        # Service statistics
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "audio_generations": 0,
            "avg_generation_time": 0.0
        }
        
    def _get_cache_key(self, text: str, emotion: str = "neutral") -> str:
        """Generate cache key for text and emotion (OPTIMIZED)"""
        # Normalize text for better caching
        normalized = text.lower().strip().replace("?", "").replace("!", "").replace(".", "")
        content = f"{normalized}_fr"  # Removed emotion for more cache hits
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[str]:
        """Load audio from cache as base64"""
        cache_file = self.cache_dir / f"{cache_key}.mp3"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    audio_data = f.read()
                return base64.b64encode(audio_data).decode('utf-8')
            except Exception as e:
                print(f"⚠️  Cache read error: {e}")
                return None
        return None
    
    def _save_to_cache(self, cache_key: str, audio_data: bytes) -> None:
        """Save audio data to cache"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.mp3"
            with open(cache_file, 'wb') as f:
                f.write(audio_data)
        except Exception as e:
            print(f"⚠️  Cache save error: {e}")
    
    def generate_speech(
        self, 
        text: str, 
        emotion: str = "neutral", 
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Generate speech audio from text
        
        Args:
            text: Text to convert to speech
            emotion: Emotion context (for future use)
            use_cache: Whether to use cached audio
            
        Returns:
            Dictionary with audio_base64, duration_ms, cached status
        """
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        if self.fallback_mode or not text.strip():
            return {
                "audio_base64": None,
                "duration_ms": 0,
                "cached": False,
                "error": "TTS not available or empty text"
            }
        
        # Generate cache key
        cache_key = self._get_cache_key(text, emotion)
        
        # Try to load from cache first
        if use_cache:
            cached_audio = self._load_from_cache(cache_key)
            if cached_audio:
                self.stats["cache_hits"] += 1
                duration_ms = int(len(text) * 60)  # Estimate: ~60ms per character
                
                return {
                    "audio_base64": cached_audio,
                    "duration_ms": duration_ms,
                    "cached": True,
                    "generation_time": time.time() - start_time
                }
        
        # Generate new audio with gTTS
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate speech with gTTS (French)
            tts = gTTS(text=text, lang='fr', slow=False)
            tts.save(temp_path)
            
            # Read the generated audio
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            # Clean up temp file
            os.unlink(temp_path)
            
            # Cache the audio
            if use_cache:
                self._save_to_cache(cache_key, audio_data)
            
            # Convert to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Estimate duration (rough calculation)
            duration_ms = int(len(text) * 60)  # ~60ms per character for French
            
            # Update statistics
            generation_time = time.time() - start_time
            self.stats["audio_generations"] += 1
            self.stats["avg_generation_time"] = (
                (self.stats["avg_generation_time"] * (self.stats["audio_generations"] - 1) + generation_time) /
                self.stats["audio_generations"]
            )
            
            return {
                "audio_base64": audio_base64,
                "duration_ms": duration_ms,
                "cached": False,
                "generation_time": generation_time
            }
            
        except Exception as e:
            print(f"⚠️  TTS generation error: {e}")
            return {
                "audio_base64": None,
                "duration_ms": 0,
                "cached": False,
                "error": str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        cache_hit_rate = (
            (self.stats["cache_hits"] / self.stats["total_requests"] * 100)
            if self.stats["total_requests"] > 0 else 0
        )
        
        return {
            **self.stats,
            "cache_hit_rate": f"{cache_hit_rate:.1f}%",
            "cache_dir": str(self.cache_dir),
            "fallback_mode": self.fallback_mode
        }
    
    def clear_cache(self) -> int:
        """Clear all cached audio files"""
        deleted = 0
        for file_path in self.cache_dir.glob("*.mp3"):
            try:
                file_path.unlink()
                deleted += 1
            except Exception as e:
                print(f"⚠️  Error deleting {file_path}: {e}")
        
        print(f"🗑️  Cleared {deleted} cached audio files")
        return deleted


# Test function
if __name__ == "__main__":
    # Test the Simple TTS Service
    tts = SimpleTTSService()
    
    test_text = "Bonjour, je suis l'assistant CNP Assurances. Comment puis-je vous aider aujourd'hui ?"
    
    print(f"\n🧪 Testing TTS with: '{test_text}'")
    result = tts.generate_speech(test_text)
    
    if result["audio_base64"]:
        print(f"✅ Audio generated successfully!")
        print(f"   Duration: {result['duration_ms']}ms")
        print(f"   Cached: {result['cached']}")
        print(f"   Generation time: {result.get('generation_time', 0):.2f}s")
        
        # Test caching
        print(f"\n🧪 Testing cache...")
        cached_result = tts.generate_speech(test_text)
        print(f"✅ Cache hit: {cached_result['cached']}")
    else:
        print(f"❌ Audio generation failed: {result.get('error', 'Unknown error')}")
    
    # Show statistics
    stats = tts.get_stats()
    print(f"\n📊 TTS Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")