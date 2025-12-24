"""Speech-to-text handler."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.utils.exceptions import SpeechRecognitionError


@dataclass
class RecognitionResult:
    text: str
    confidence: Optional[float] = None


class SpeechRecognitionHandler:
    def __init__(self, language: str = "en-US", timeout: int = 5, phrase_timeout: int = 3):
        self.language = language
        self.timeout = timeout
        self.phrase_timeout = phrase_timeout

    def listen_once(self) -> RecognitionResult:
        """Listen using the SpeechRecognition library."""

        try:
            import speech_recognition as sr

            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                audio = recognizer.listen(source, timeout=self.timeout, phrase_time_limit=self.phrase_timeout)
            text = recognizer.recognize_google(audio, language=self.language)
            return RecognitionResult(text=text)
        except Exception as e:
            raise SpeechRecognitionError(str(e)) from e
