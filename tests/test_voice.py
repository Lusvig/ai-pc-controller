from src.voice.wake_word_detector import WakeWordConfig, WakeWordDetector


def test_wake_word_detector_smoke():
    d = WakeWordDetector(WakeWordConfig(enabled=False))
    d.start()
    d.stop()
