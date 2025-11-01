import asyncio
import edge_tts
import uuid
import os
import re
from langdetect import detect

class EdgeSpeech:
    def __init__(self, output_dir="tts_output", default_voice="en-US-AriaNeural"):
        self.output_dir = output_dir
        self.default_voice = default_voice
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def detect_language(self, text):
        try:
            lang = detect(text)
            if lang.startswith("hi"):
                return "hi-IN"
            else:
                return "en-US"
        except:
            return "en-US"

    def clean_text(self, text: str) -> str:
        if not text:
            return ""

        text = re.sub(r"[*_`~#>\[\]]", "", text)

        text = re.sub(r"http\S+", "", text)

        text = re.sub(r"(?i)(here's your story:|sure!|once upon a time[:,]*)", "", text)

        text = re.sub(r"\n+", ". ", text)

        text = re.sub(r"\s{2,}", " ", text)

        return text.strip()

    async def _speak_async(self, text, voice, filename):
        #for generating speech.
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(filename)

    def synthesize(self, text, voice=None):
        detected_lang = self.detect_language(text)
        if "hi" in detected_lang:
            voice = "hi-IN-SwaraNeural"
        else:
            voice = voice or self.default_voice
        cleaned_text = self.clean_text(text)

        if not cleaned_text:
            raise ValueError("Cannot synthesize empty or invalid text.")

        filename = f"{uuid.uuid4().hex[:8]}.mp3"
        filepath = os.path.join(self.output_dir, filename)
        voice = voice or self.default_voice

        # Run async TTS loop
        try:
            asyncio.run(self._speak_async(cleaned_text, voice, filepath))
        except Exception as e:
            raise RuntimeError(f"TTS synthesis failed: {e}")

            return filepath
