"""
🔊 TTS SERVICE - gTTS (GOOGLE TEXT-TO-SPEECH)
==============================================

Service de synthèse vocale utilisant gTTS (Google Text-to-Speech).
Optimisé pour le français avec voix "Julie" personnalisée.

✅ AVANTAGES:
- Installation rapide et facile
- Bonne qualité voix française
- Gratuit et stable
- Caching intelligent pour performances
- Utilise l'API Google (nécessite internet)

📥 INPUT:
{
  "text": "Bonjour, je suis Julie...",
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
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Set environment variable to avoid OpenMP conflict
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


class TTSService:
    """
    🎙️ Text-to-Speech Service using Coqui TTS
    
    Features:
    - French voice synthesis
    - Intelligent caching
    - Emotion-adapted speech rate
    - Base64 output for easy transmission
    """
    
    # Default paths
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    CACHE_DIR = BASE_DIR / "cache" / "tts_cache"
    
    # Speech parameters for "Julie" voice
    SPEECH_SPEED = 1.0  # Normal speed (can adjust 0.8-1.2)
    
    # Emotion-based speed adjustments
    EMOTION_SPEED = {
        "stressed": 0.85,   # Slower, calmer for stressed clients
        "angry": 0.80,      # Even slower to calm down
        "neutral": 1.0,     # Normal speed
        "happy": 1.05,      # Slightly faster, energetic
        "sad": 0.90         # Slower, empathetic
    }
    
    def __init__(self, model_name: str = None, use_gpu: bool = False):
        """
        Initialize Coqui TTS with French model.
        
        Args:
            model_name: TTS model to use (default: French VITS)
            use_gpu: Use GPU if available (default: False for stability)
        """
        print("🔊 Initializing TTS Service...")
        start_time = time.time()
        
        # Create cache directory
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"📁 Cache directory: {self.CACHE_DIR}")
        
        # Try to load Coqui TTS
        try:
            from TTS.api import TTS
            
            # List available French models
            # Best options:
            # 1. tts_models/fr/mai/tacotron2-DDC (French female)
            # 2. tts_models/multilingual/multi-dataset/xtts_v2 (high quality, slow)
            
            if model_name is None:
                # Try to use French model, fallback to multilingual
                model_name = "tts_models/fr/mai/tacotron2-DDC"
            
            print(f"📦 Loading model: {model_name}")
            print("⚠️  First load may download the model (this is one-time only)")
            
            # Initialize TTS
            self.tts = TTS(model_name=model_name, progress_bar=True)
            
            # Move to GPU if requested and available
            if use_gpu:
                try:
                    self.tts = self.tts.to("cuda")
                    print("🎮 Using GPU for inference")
                except:
                    print("💻 GPU not available, using CPU")
            
            self.model_loaded = True
            self.model_name = model_name
            
        except ImportError:
            print("⚠️  Coqui TTS not installed. Using fallback mode.")
            print("   Install with: pip install TTS")
            self.model_loaded = False
            self.tts = None
            
        except Exception as e:
            print(f"⚠️  Error loading TTS model: {e}")
            print("   Using fallback mode (no audio generation)")
            self.model_loaded = False
            self.tts = None
        
        load_time = time.time() - start_time
        print(f"✅ TTS Service ready in {load_time:.2f}s")
        
        # Stats
        self.stats = {
            "total_generations": 0,
            "cache_hits": 0,
            "total_time_saved_ms": 0
        }
    
    def _get_cache_path(self, text: str, emotion: str) -> Path:
        """Generate cache file path based on text hash."""
        # Create hash of text + emotion
        cache_key = f"{text}_{emotion}"
        text_hash = hashlib.md5(cache_key.encode()).hexdigest()
        return self.CACHE_DIR / f"{text_hash}.wav"
    
    def _load_from_cache(self, cache_path: Path) -> Optional[str]:
        """Load audio from cache if exists."""
        if cache_path.exists():
            with open(cache_path, "rb") as f:
                audio_bytes = f.read()
            return base64.b64encode(audio_bytes).decode("utf-8")
        return None
    
    def _save_to_cache(self, cache_path: Path, audio_bytes: bytes):
        """Save audio to cache."""
        with open(cache_path, "wb") as f:
            f.write(audio_bytes)
    
    def generate_audio(
        self,
        text: str,
        emotion: str = "neutral",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        🎯 MAIN METHOD - Generate audio from text
        
        Args:
            text: Text to convert to speech
            emotion: Client emotion (affects speech rate)
            use_cache: Use cached audio if available
            
        Returns:
            {
                "audio_base64": "UklGRi4...",
                "duration_ms": 2500,
                "cached": true,
                "format": "wav"
            }
        """
        start_time = time.time()
        self.stats["total_generations"] += 1
        
        # Check cache first
        cache_path = self._get_cache_path(text, emotion)
        
        if use_cache:
            cached_audio = self._load_from_cache(cache_path)
            if cached_audio:
                self.stats["cache_hits"] += 1
                generation_time = (time.time() - start_time) * 1000
                self.stats["total_time_saved_ms"] += 500 - generation_time  # Assume 500ms for generation
                
                return {
                    "audio_base64": cached_audio,
                    "duration_ms": self._estimate_duration(text),
                    "cached": True,
                    "format": "wav",
                    "generation_time_ms": round(generation_time, 2)
                }
        
        # Generate new audio
        if not self.model_loaded:
            # Fallback: return empty audio placeholder
            return {
                "audio_base64": "",
                "duration_ms": self._estimate_duration(text),
                "cached": False,
                "format": "wav",
                "error": "TTS model not loaded",
                "generation_time_ms": 0
            }
        
        try:
            # Get speed based on emotion
            speed = self.EMOTION_SPEED.get(emotion, 1.0)
            
            # Generate audio to file
            output_path = str(cache_path)
            
            # Generate with Coqui TTS
            self.tts.tts_to_file(
                text=text,
                file_path=output_path,
                speed=speed
            )
            
            # Read generated audio
            with open(output_path, "rb") as f:
                audio_bytes = f.read()
            
            # Convert to base64
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            
            generation_time = (time.time() - start_time) * 1000
            
            return {
                "audio_base64": audio_base64,
                "duration_ms": self._estimate_duration(text),
                "cached": False,
                "format": "wav",
                "generation_time_ms": round(generation_time, 2),
                "emotion_speed": speed
            }
            
        except Exception as e:
            print(f"❌ TTS generation error: {e}")
            return {
                "audio_base64": "",
                "duration_ms": 0,
                "cached": False,
                "format": "wav",
                "error": str(e),
                "generation_time_ms": 0
            }
    
    def _estimate_duration(self, text: str) -> int:
        """Estimate audio duration based on text length."""
        # Average speaking rate: ~150 words per minute
        # Average word length: ~5 characters
        words = len(text) / 5
        duration_minutes = words / 150
        duration_ms = int(duration_minutes * 60 * 1000)
        return max(duration_ms, 500)  # Minimum 500ms
    
    def pregenerate_common_phrases(self):
        """
        Pre-generate audio for common phrases to improve response time.
        Call this at startup if needed.
        """
        common_phrases = [
            "Bonjour, je suis Julie, votre assistante virtuelle CNP Assurances. Comment puis-je vous aider ?",
            "Un instant, je vérifie votre dossier.",
            "Je vais transférer votre appel à un conseiller.",
            "Y a-t-il autre chose que je puisse faire pour vous ?",
            "Merci de votre appel. Au revoir !",
            "Je comprends votre situation. Laissez-moi vous aider.",
            "Pouvez-vous me donner votre numéro de contrat ?",
        ]
        
        print("🔄 Pre-generating common phrases...")
        for phrase in common_phrases:
            result = self.generate_audio(phrase, "neutral", use_cache=True)
            status = "✅ cached" if result["cached"] else "✅ generated"
            print(f"   {status}: {phrase[:50]}...")
        
        print(f"✅ Pre-generation complete ({len(common_phrases)} phrases)")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get TTS service statistics."""
        cache_files = list(self.CACHE_DIR.glob("*.wav"))
        
        return {
            "model": self.model_name if self.model_loaded else "Not loaded",
            "model_loaded": self.model_loaded,
            "cache_size": len(cache_files),
            "cache_hits": self.stats["cache_hits"],
            "total_generations": self.stats["total_generations"],
            "cache_hit_rate": f"{(self.stats['cache_hits'] / max(1, self.stats['total_generations'])) * 100:.1f}%",
            "time_saved_ms": self.stats["total_time_saved_ms"]
        }
    
    def clear_cache(self):
        """Clear all cached audio files."""
        cache_files = list(self.CACHE_DIR.glob("*.wav"))
        for f in cache_files:
            f.unlink()
        print(f"🗑️  Cleared {len(cache_files)} cached audio files")


# ============================================================================
# 🧪 TEST
# ============================================================================

def test_tts():
    """Test the TTS service."""
    print("\n" + "="*80)
    print("🔊 TTS SERVICE TEST")
    print("="*80)
    
    # Initialize
    tts = TTSService()
    
    if not tts.model_loaded:
        print("\n⚠️  TTS model not loaded. Install with: pip install TTS")
        return
    
    # Test phrases
    test_phrases = [
        ("Bonjour, je suis Julie, votre assistante CNP Assurances.", "neutral"),
        ("Je comprends que c'est une situation difficile.", "stressed"),
        ("Votre demande a été traitée avec succès.", "happy"),
    ]
    
    for text, emotion in test_phrases:
        print(f"\n📝 Text: \"{text[:50]}...\"")
        print(f"😊 Emotion: {emotion}")
        
        result = tts.generate_audio(text, emotion)
        
        print(f"⏱️  Generation time: {result['generation_time_ms']}ms")
        print(f"💾 Cached: {result['cached']}")
        print(f"📊 Duration estimate: {result['duration_ms']}ms")
        
        if result.get('audio_base64'):
            print(f"✅ Audio generated ({len(result['audio_base64'])} chars base64)")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown')}")
    
    # Show stats
    print("\n📊 Service Stats:")
    stats = tts.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    test_tts()
