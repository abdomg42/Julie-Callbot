"""
⚡ OPTIMIZED TTS SERVICE - Production Ready
============================================

Service TTS haute performance avec cache intelligent SHA256.
Utilise gTTS pour une voix française de haute qualité.

🚀 PERFORMANCES:
- Cache hits: < 10ms (phrases pré-cachées)
- Génération gTTS: ~1-2s (première occurrence)
- Stockage cache: SHA256 pour distribution uniforme

💡 STRATÉGIE D'OPTIMISATION:
1. Pré-cacher les phrases communes au démarrage
2. Cache automatique de toutes les réponses générées
3. Lecture audio non-bloquante en parallèle
"""

import os
import hashlib
import base64
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile
import io

# gTTS for quality French voice
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# pydub for audio speed control
try:
    from pydub import AudioSegment
    from pydub.playback import play
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


class OptimizedTTSService:
    """
    🎙️ High-Performance Text-to-Speech Service
    
    Features:
    - Smart SHA256 caching
    - gTTS for quality French voice
    - Thread-safe for production
    - Pre-caching of common phrases
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize optimized TTS service with smart caching."""
        self.cache_dir = Path(cache_dir or "tool_router/cache/tts_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        print("🔊 Initializing Optimized TTS Service...")
        
        # Engine availability
        self.use_gtts = GTTS_AVAILABLE
        self._lock = threading.Lock()
        
        if self.use_gtts:
            print("✅ gTTS (ONLINE) - High quality French voice enabled!")
        else:
            print("❌ No TTS engine available! Install: pip install gtts")
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "gtts_generations": 0,
            "avg_generation_time_ms": 0.0
        }
        
        print(f"📁 Cache: {self.cache_dir.absolute()}")
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key using SHA256 for better distribution."""
        normalized = text.lower().strip()
        # Remove punctuation for cache hits on similar texts
        for char in '?!.,;:':
            normalized = normalized.replace(char, '')
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:16]
    
    def _load_from_cache(self, cache_key: str) -> Optional[bytes]:
        """Load audio bytes from cache."""
        cache_file = self.cache_dir / f"{cache_key}.mp3"
        if cache_file.exists():
            try:
                return cache_file.read_bytes()
            except Exception:
                return None
        return None
    
    def _save_to_cache(self, cache_key: str, audio_data: bytes) -> None:
        """Save audio bytes to cache."""
        try:
            cache_file = self.cache_dir / f"{cache_key}.mp3"
            cache_file.write_bytes(audio_data)
        except Exception as e:
            print(f"⚠️  Cache save error: {e}")
    
    def _speed_up_audio(self, audio_data: bytes, speed_factor: float = 1.1) -> bytes:
        """Accélérer l'audio de 10% pour une parole plus rapide mais naturelle."""
        if not PYDUB_AVAILABLE:
            return audio_data
            
        try:
            # Charger l'audio depuis les bytes
            audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_data))
            
            # Accélération modérée (1.1 = 10% plus rapide - très naturel)
            sped_up = audio_segment.speedup(playback_speed=speed_factor)
            
            # Améliorer la qualité audio pour un rendu plus humain
            # Normaliser le volume pour éviter la distorsion
            sped_up = sped_up.normalize()
            
            # Ajouter un léger filtrage pour adoucir la voix
            # Réduire les hautes fréquences qui rendent la voix robotique
            sped_up = sped_up.low_pass_filter(3000)  # Filtre passe-bas à 3kHz
            
            # Exporter avec une qualité élevée
            output_buffer = io.BytesIO()
            sped_up.export(output_buffer, format="mp3", bitrate="192k")
            return output_buffer.getvalue()
            
        except Exception as e:
            print(f"⚠️  Erreur accélération audio: {e}")
            return audio_data  # Retourner l'original si erreur
    
    def _generate_gtts(self, text: str) -> Optional[bytes]:
        """Generate audio using gTTS with speed optimization."""
        if not GTTS_AVAILABLE:
            return None
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                temp_path = f.name
            
            # gTTS with French, normal speed
            tts = gTTS(text=text, lang='fr', slow=False)
            tts.save(temp_path)
            
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            os.unlink(temp_path)
            
            return audio_data
            
        except Exception as e:
            print(f"⚠️  gTTS generation error: {e}")
            return None
    
    def generate_speech(
        self, 
        text: str, 
        emotion: str = "neutral", 
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Generate speech with optimal performance.
        
        Args:
            text: Text to synthesize
            emotion: Emotional context (for future use)
            use_cache: Use cache for repeated phrases
            
        Returns:
            Dict with audio_base64, duration_ms, cached, generation_time
        """
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        if not text or not text.strip():
            return {
                "audio_base64": None,
                "duration_ms": 0,
                "cached": False,
                "error": "Empty text"
            }
        
        text = text.strip()
        cache_key = self._get_cache_key(text)
        
        # 1. Try cache first (fastest: <10ms)
        if use_cache:
            cached_audio = self._load_from_cache(cache_key)
            if cached_audio:
                self.stats["cache_hits"] += 1
                # Estimate duration: ~55ms per character for French
                duration_ms = int(len(text) * 55)
                
                return {
                    "audio_base64": base64.b64encode(cached_audio).decode('utf-8'),
                    "duration_ms": duration_ms,
                    "cached": True,
                    "generation_time": time.time() - start_time,
                    "engine": "cache"
                }
        
        # 2. Generate with gTTS
        audio_data = None
        engine_used = None
        
        if self.use_gtts:
            with self._lock:
                audio_data = self._generate_gtts(text)
            if audio_data:
                engine_used = "gtts"
                self.stats["gtts_generations"] += 1
        
        if not audio_data:
            return {
                "audio_base64": None,
                "duration_ms": 0,
                "cached": False,
                "error": "TTS generation failed"
            }
        
        # 🚀 ACCÉLÉRATION ADAPTATIVE : seulement pour les textes > 30 caractères
        # Les textes courts restent naturels, les longs sont accélérés très modérément
        if len(text) > 30:
            audio_data = self._speed_up_audio(audio_data, speed_factor=1.1)  # 10% plus rapide
            print(f"   ⚡ Audio accéléré 1.1x (texte: {len(text)} chars)")
        else:
            print(f"   🔊 Audio vitesse naturelle (texte court: {len(text)} chars)")
        
        # Cache the result for next time
        if use_cache:
            self._save_to_cache(cache_key, audio_data)
        
        generation_time = time.time() - start_time
        
        # Update average generation time
        total_gens = self.stats["gtts_generations"]
        if total_gens > 0:
            self.stats["avg_generation_time_ms"] = (
                (self.stats["avg_generation_time_ms"] * (total_gens - 1) + generation_time * 1000) 
                / total_gens
            )
        
        return {
            "audio_base64": base64.b64encode(audio_data).decode('utf-8'),
            "duration_ms": int(len(text) * 55),
            "cached": False,
            "generation_time": generation_time,
            "engine": engine_used
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        total = self.stats["total_requests"]
        cache_rate = (self.stats["cache_hits"] / total * 100) if total > 0 else 0
        
        return {
            **self.stats,
            "cache_hit_rate": f"{cache_rate:.1f}%",
            "primary_engine": "gtts",
            "cache_dir": str(self.cache_dir)
        }
    
    def preload_common_phrases(self):
        """Pre-cache common phrases for instant response."""
        common_phrases = [
            # Greetings
            "Bonjour ! Je suis Julie de CNP Assurances. Comment puis-je vous aider ?",
            "Comment puis-je vous aider aujourd'hui ?",
            # Goodbye
            "Merci pour votre appel. À bientôt !",
            "Au revoir et bonne journée !",
            "Merci pour votre appel. CNP Assurances vous remercie. Au revoir et à bientôt !",
            # Repeat requests (NEW)
            "Je n'ai pas bien compris votre demande. Pouvez-vous reformuler s'il vous plaît ?",
            "Je n'ai pas compris. Pouvez-vous répéter ?",
            "Pouvez-vous répéter votre question s'il vous plaît ?",
            "Je n'ai pas entendu. Pouvez-vous répéter votre question s'il vous plaît ?",
            # Common responses
            "Un instant, je recherche l'information.",
            "Pour déclarer un sinistre, appelez le 3477 ou utilisez votre espace client en ligne.",
            "Consultez vos contrats sur votre espace client ou appelez le 3477.",
            "Je peux vous renseigner sur vos contrats et sinistres. Quelle est votre question ?",
        ]
        
        print("📦 Pre-caching common phrases...")
        cached_count = 0
        for phrase in common_phrases:
            cache_key = self._get_cache_key(phrase)
            if not self._load_from_cache(cache_key):
                result = self.generate_speech(phrase, use_cache=True)
                if result.get("audio_base64"):
                    cached_count += 1
            else:
                cached_count += 1
        print(f"✅ {cached_count}/{len(common_phrases)} phrases in cache")


# Backward compatibility alias
SimpleTTSService = OptimizedTTSService


if __name__ == "__main__":
    # Performance test
    print("\n" + "="*60)
    print("⚡ TTS PERFORMANCE TEST")
    print("="*60)
    
    tts = OptimizedTTSService()
    
    test_phrases = [
        "Bonjour",
        "Comment puis-je vous aider ?",
        "Pour déclarer un sinistre, contactez votre partenaire.",
    ]
    
    for phrase in test_phrases:
        start = time.time()
        result = tts.generate_speech(phrase)
        elapsed = (time.time() - start) * 1000
        
        status = "✅" if elapsed < 500 else "⚠️" if elapsed < 1000 else "❌"
        print(f"\n{status} '{phrase[:30]}...'")
        print(f"   Time: {elapsed:.0f}ms | Cached: {result.get('cached')} | Engine: {result.get('engine')}")
    
    # Test cache hit
    print("\n📊 Cache test (should be < 10ms):")
    start = time.time()
    result = tts.generate_speech(test_phrases[0])
    elapsed = (time.time() - start) * 1000
    print(f"   Cache hit time: {elapsed:.1f}ms | Cached: {result.get('cached')}")
    
    print(f"\n📈 Stats: {tts.get_stats()}")
