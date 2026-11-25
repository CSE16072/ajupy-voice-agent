
import asyncio
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

# Connect using Gemini Live API (v1beta)
client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(
        api_version="v1beta"
    )
)

MODEL = "gemini-3.8-live"


async def test_live():

    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Kore"
                )
            )
        )
    )

    print("Connecting to Gemini Live...")

    async with client.aio.live.connect(
        model=MODEL,
        config=config
    ) as session:

        print("Connected successfully!")

        await session.send_client_content(
            turns=types.Content(
                role="user",
                parts=[
                    types.Part(
                        text="Hello AJUPY! Introduce yourself in one short sentence."
                    )
                ]
            ),
            turn_complete=True
        )

        print("Waiting for audio response...")

        audio_received = False

        async for message in session.receive():

            if message.server_content:
                model_turn = message.server_content.model_turn

                if model_turn:
                    for part in model_turn.parts:

                        if part.inline_data and part.inline_data.data:
                            audio_received = True

                            print(
                                "Audio received:",
                                len(part.inline_data.data),
                                "bytes"
                            )

                if message.server_content.turn_complete:
                    break

        if audio_received:
            print("\nSUCCESS! Gemini Live generated audio.")
        else:
            print("\nConnected, but no audio chunks were received.")


if __name__ == "__main__":
    asyncio.run(test_live())
