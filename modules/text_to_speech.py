
from gtts import gTTS
import tempfile


def generate_speech(text, language="en"):
    try:
        tts = gTTS(text=text, lang=language)

        with tempfile.NamedTemporaryFile(
            suffix=".mp3", delete=False
        ) as audio_file:
            audio_path = audio_file.name

        tts.save(audio_path)

        return audio_path

    except Exception as error:
        print("Text-to-speech error:", error)
        return None
