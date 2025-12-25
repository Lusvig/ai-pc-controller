"""
Simple Voice Handler - Works without webrtcvad

Provides voice input/output functionality using only
packages that install without C compilation.
"""

import threading
import queue
import time
from typing import Optional, Callable, Dict, Any
from loguru import logger

# Speech Recognition
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.warning("SpeechRecognition not available")

# Text to Speech
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not available")


class VoiceHandler:
    """
    Handles voice input (speech-to-text) and output (text-to-speech).
    
    This version works without webrtcvad or other packages that
    require C compilation.
    """
    
    def __init__(
        self,
        language: str = "en-US",
        voice_rate: int = 175,
        voice_volume: float = 1.0
    ):
        """
        Initialize the voice handler.
        
        Args:
            language: Language code for speech recognition
            voice_rate: Speed of text-to-speech (words per minute)
            voice_volume: Volume for text-to-speech (0.0 to 1.0)
        """
        self.language = language
        self.voice_rate = voice_rate
        self.voice_volume = voice_volume
        
        # Speech recognition
        self.recognizer: Optional[sr.Recognizer] = None
        self.microphone: Optional[sr.Microphone] = None
        self._sr_available = SPEECH_RECOGNITION_AVAILABLE
        
        # Text to speech
        self.tts_engine: Optional[pyttsx3.Engine] = None
        self._tts_available = PYTTSX3_AVAILABLE
        
        # State
        self._is_listening = False
        self._stop_listening = None
        self._listen_thread: Optional[threading.Thread] = None
        self._tts_queue: queue.Queue = queue.Queue()
        self._tts_thread: Optional[threading.Thread] = None
        self._tts_running = False
        
        # Initialize components
        self._init_speech_recognition()
        self._init_tts()
        
        logger.info(f"VoiceHandler initialized - SR: {self._sr_available}, TTS: {self._tts_available}")
    
    def _init_speech_recognition(self) -> None:
        """Initialize speech recognition."""
        if not SPEECH_RECOGNITION_AVAILABLE:
            return
            
        try:
            self.recognizer = sr.Recognizer()
            
            # Adjust for ambient noise settings
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            self.recognizer.phrase_threshold = 0.3
            
            # Test microphone availability
            try:
                self.microphone = sr.Microphone()
                with self.microphone as source:
                    # Quick calibration
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                logger.info("Microphone initialized successfully")
            except OSError as e:
                logger.warning(f"Microphone not available: {e}")
                self.microphone = None
                self._sr_available = False
                
        except Exception as e:
            logger.error(f"Failed to initialize speech recognition: {e}")
            self._sr_available = False
    
    def _init_tts(self) -> None:
        """Initialize text-to-speech."""
        if not PYTTSX3_AVAILABLE:
            return
        
        try:
            self.tts_engine = pyttsx3.init()
            
            # Configure voice
            self.tts_engine.setProperty('rate', self.voice_rate)
            self.tts_engine.setProperty('volume', self.voice_volume)
            
            # Try to get available voices
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Prefer English voice
                for voice in voices:
                    if 'english' in voice.name.lower() or 'en' in voice.id.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            # Start TTS worker thread
            self._tts_running = True
            self._tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
            self._tts_thread.start()
            
            logger.info("Text-to-speech initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            self._tts_available = False
    
    def _tts_worker(self) -> None:
        """Worker thread for text-to-speech."""
        while self._tts_running:
            try:
                # Get text to speak with timeout
                text = self._tts_queue.get(timeout=0.5)
                
                if text is None:  # Shutdown signal
                    break
                    
                if self.tts_engine:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                    
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"TTS error: {e}")
    
    @property
    def is_available(self) -> bool:
        """Check if voice functionality is available."""
        return self._sr_available or self._tts_available
    
    @property
    def speech_recognition_available(self) -> bool:
        """Check if speech recognition is available."""
        return self._sr_available and self.microphone is not None
    
    @property
    def tts_available(self) -> bool:
        """Check if text-to-speech is available."""
        return self._tts_available and self.tts_engine is not None
    
    def speak(self, text: str, block: bool = False) -> None:
        """
        Speak text using text-to-speech.
        
        Args:
            text: Text to speak
            block: If True, wait for speech to complete
        """
        if not self._tts_available or not text:
            logger.debug(f"TTS not available, would say: {text}")
            return
        
        logger.debug(f"Speaking: {text}")
        
        if block:
            # Speak directly
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS error: {e}")
        else:
            # Queue for background speaking
            self._tts_queue.put(text)
    
    def listen(
        self,
        timeout: float = 5.0,
        phrase_timeout: float = 3.0
    ) -> Optional[str]:
        """
        Listen for speech and return recognized text.
        
        Args:
            timeout: Maximum time to wait for speech to start
            phrase_timeout: Maximum time for a phrase
            
        Returns:
            Recognized text or None if failed
        """
        if not self._sr_available or self.microphone is None:
            logger.warning("Speech recognition not available")
            return None
        
        logger.debug("Listening for speech...")
        
        try:
            with self.microphone as source:
                # Listen for audio
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_timeout
                )
            
            # Recognize speech
            text = self.recognizer.recognize_google(
                audio,
                language=self.language
            )
            
            logger.info(f"Recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            logger.debug("No speech detected (timeout)")
            return None
        except sr.UnknownValueError:
            logger.debug("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            return None
    
    def listen_continuous(
        self,
        callback: Callable[[str], None],
        stop_event: threading.Event = None
    ) -> None:
        """
        Continuously listen for speech in background.
        
        Args:
            callback: Function to call with recognized text
            stop_event: Event to signal stopping
        """
        if not self._sr_available or self.microphone is None:
            logger.warning("Cannot start continuous listening - not available")
            return
        
        if self._is_listening:
            logger.warning("Already listening")
            return
        
        self._is_listening = True
        stop_event = stop_event or threading.Event()
        
        def listen_thread():
            logger.info("Continuous listening started")
            
            while not stop_event.is_set() and self._is_listening:
                try:
                    text = self.listen(timeout=2.0, phrase_timeout=5.0)
                    if text:
                        callback(text)
                except Exception as e:
                    logger.error(f"Continuous listen error: {e}")
                    time.sleep(0.5)
            
            logger.info("Continuous listening stopped")
            self._is_listening = False
        
        self._listen_thread = threading.Thread(target=listen_thread, daemon=True)
        self._listen_thread.start()
    
    def stop_listening(self) -> None:
        """Stop continuous listening."""
        self._is_listening = False
        if self._listen_thread and self._listen_thread.is_alive():
            self._listen_thread.join(timeout=2.0)
    
    def calibrate(self, duration: float = 2.0) -> bool:
        """
        Calibrate for ambient noise.
        
        Args:
            duration: Duration to sample ambient noise
            
        Returns:
            True if calibration succeeded
        """
        if not self._sr_available or self.microphone is None:
            return False
        
        try:
            logger.info(f"Calibrating for {duration} seconds...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            logger.info(f"Calibration complete. Energy threshold: {self.recognizer.energy_threshold}")
            return True
        except Exception as e:
            logger.error(f"Calibration failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get voice handler status."""
        return {
            "speech_recognition": {
                "available": self._sr_available,
                "microphone": self.microphone is not None,
                "listening": self._is_listening,
                "energy_threshold": self.recognizer.energy_threshold if self.recognizer else None
            },
            "text_to_speech": {
                "available": self._tts_available,
                "rate": self.voice_rate,
                "volume": self.voice_volume
            }
        }
    
    def shutdown(self) -> None:
        """Clean up resources."""
        logger.info("Shutting down voice handler")
        
        # Stop listening
        self.stop_listening()
        
        # Stop TTS thread
        self._tts_running = False
        self._tts_queue.put(None)  # Signal to stop
        
        if self._tts_thread and self._tts_thread.is_alive():
            self._tts_thread.join(timeout=2.0)
        
        # Clean up TTS engine
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except Exception:
                pass
        
        logger.info("Voice handler shutdown complete")


# Convenience function
def create_voice_handler(**kwargs) -> VoiceHandler:
    """Create and return a voice handler instance."""
    return VoiceHandler(**kwargs)