
from faster_whisper import WhisperModel
import tempfile
import os

# Load the speech recognition model
model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)


def transcribe_audio(audio_file):
    try:
        # Save uploaded audio temporarily
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as temp_audio:

            temp_audio.write(audio_file.getvalue())
            audio_path = temp_audio.name

        # Convert speech into text
        segments, info = model.transcribe(
            audio_path,
            beam_size=5
        )

        text = " ".join(
            segment.text for segment in segments
        ).strip()

        return text

    except Exception as error:
        print("Speech recognition error:", error)
        return ""

    finally:
        if "audio_path" in locals() and os.path.exists(audio_path):
            os.remove(audio_path)
