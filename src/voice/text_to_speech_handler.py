"""Text-to-speech handler."""

from __future__ import annotations

from src.utils.exceptions import TextToSpeechError


class TextToSpeechHandler:
    def __init__(self, rate: int = 175, volume: float = 1.0, voice: str | None = None):
        self.rate = rate
        self.volume = volume
        self.voice = voice

    def speak(self, text: str) -> None:
        try:
            import pyttsx3

            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)
            if self.voice:
                engine.setProperty("voice", self.voice)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            raise TextToSpeechError(str(e)) from e
