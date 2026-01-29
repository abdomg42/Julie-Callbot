try:
    from ..audio.recorder import AudioRecorder
    from ..models.whisper import Whisper
    from ..models.bert_sentiment import BertSentiment
    from ..pipeline.parallel_pipeline import ParallelPipeline
except ImportError:
    from audio.recorder import AudioRecorder
    from models.whisper import Whisper
    from models.bert_sentiment import BertSentiment
    from pipeline.parallel_pipeline import ParallelPipeline


class InputsService:
    """Service réutilisable pour éviter de recharger les modèles lourds à chaque appel."""
    
    def __init__(self):
        print("🔧 Initialisation InputsService...")
        self.recorder = AudioRecorder()
        self.whisper = Whisper()
        self.bert = BertSentiment()
        self.pipeline = ParallelPipeline(self.whisper, self.bert)
        print("✅ InputsService initialisé")
    
    def process_audio_input(self):
        """Traite une entrée audio et retourne les résultats."""
        # Record until silence
        audio = self.recorder.record_until_silence()
        
        # Process in parallel
        results = self.pipeline.process(audio)
        return results


# Instance globale réutilisable
_inputs_service = None

def get_inputs_service():
    """Récupère ou crée l'instance InputsService (pattern singleton)."""
    global _inputs_service
    if _inputs_service is None:
        _inputs_service = InputsService()
    return _inputs_service

def run_inputs():
    """Interface backwards compatible - utilise le service réutilisable."""
    service = get_inputs_service()
    return service.process_audio_input()
    