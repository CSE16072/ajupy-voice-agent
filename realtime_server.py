
import asyncio
import traceback
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from google import genai
from google.genai import types

from config import GEMINI_API_KEY



# --------------------------------------------------
# APPLICATION SETUP
# --------------------------------------------------

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
HTML_FILE = BASE_DIR / "static" / "index.html"

MODEL = "gemini-3.8-live"

client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(api_version="v1beta")
)


# --------------------------------------------------
# WEB PAGE ROUTES
# --------------------------------------------------

@app.get("/")
async def home():
    return {
        "message": "AJUPY Real-Time Voice Server is running!"
    }


@app.get("/ui")
async def user_interface():
    return FileResponse(HTML_FILE)


# --------------------------------------------------
# WEBSOCKET ROUTE
# --------------------------------------------------

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    print("\nBrowser connected to AJUPY")

    try:

        live_config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],

            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Kore"
                    )
                )
            ),

            system_instruction=(
                "You are AJUPY, a friendly and intelligent AI voice assistant. "
                "Speak naturally and conversationally. "
                "Listen carefully and answer the user's questions. "
                "Remember information shared earlier in this conversation. "
                "If the user tells you their name, remember it during this session. "
                "Keep your answers clear, friendly, and concise."
            ),

            input_audio_transcription=types.AudioTranscriptionConfig(),

            realtime_input_config=types.RealtimeInputConfig(
                automatic_activity_detection=(
                    types.AutomaticActivityDetection(
                        disabled=False,
                        start_of_speech_sensitivity=(
                            types.StartSensitivity.START_SENSITIVITY_HIGH
                        ),
                        end_of_speech_sensitivity=(
                            types.EndSensitivity.END_SENSITIVITY_HIGH
                        ),
                        prefix_padding_ms=20,
                        silence_duration_ms=500
                    )
                ),

                activity_handling=(
                    types.ActivityHandling.START_OF_ACTIVITY_INTERRUPTS
                )
            )
        )

        # Keep ONE Gemini session open for the entire conversation.
        async with client.aio.live.connect(
            model=MODEL,
            config=live_config
        ) as session:

            print("Connected to Gemini Live successfully")
            print("Automatic voice detection is enabled")

            # ------------------------------------------
            # BROWSER MICROPHONE -> GEMINI
            # ------------------------------------------

            async def receive_from_browser():

                chunk_count = 0

                print("Browser audio receiver started")

                while True:

                    audio_data = await websocket.receive_bytes()

                    if not audio_data:
                        continue

                    chunk_count += 1

                    if chunk_count % 100 == 0:
                        print(
                            "Microphone audio received:",
                            chunk_count,
                            "chunks"
                        )

                    await session.send_realtime_input(
                        audio=types.Blob(
                            data=audio_data,
                            mime_type="audio/pcm;rate=16000"
                        )
                    )

            # ------------------------------------------
            # GEMINI -> BROWSER AUDIO
            # ------------------------------------------

            async def receive_from_gemini():

                print("Gemini audio receiver started")

                audio_chunk_count = 0
                turn_count = 0

                # IMPORTANT:
                # The SDK receive() iterator ends after one turn.
                # Re-enter it to receive the next turn using
                # the SAME Gemini session.

                while True:

                    print("Waiting for Gemini response...")

                    async for message in session.receive():

                        if not message.server_content:
                            continue

                        server_content = message.server_content

                        # Recognized user speech
                        if server_content.input_transcription:

                            recognized_text = (
                                server_content.input_transcription.text
                            )

                            if recognized_text:
                                print("USER SAID:", recognized_text)

                        # Gemini audio response
                        model_turn = server_content.model_turn

                        if model_turn:

                            for part in model_turn.parts:

                                if (
                                    part.inline_data
                                    and part.inline_data.data
                                ):

                                    audio_output = part.inline_data.data

                                    if len(audio_output) <= 2:
                                        continue

                                    audio_chunk_count += 1

                                    await websocket.send_bytes(
                                        audio_output
                                    )

                                    if audio_chunk_count % 20 == 0:
                                        print(
                                            "Gemini audio chunks sent:",
                                            audio_chunk_count
                                        )

                        # End of one Gemini response
                        if server_content.turn_complete:

                            turn_count += 1

                            print(
                                "Gemini response completed.",
                                "Turn:",
                                turn_count
                            )

                            await websocket.send_json({
                                "type": "turn_complete"
                            })

                    # The iterator ended after this turn.
                    # Do not close the session. Listen again.

                    print(
                        "Gemini finished one receive cycle. "
                        "Listening for the next turn..."
                    )

                    await asyncio.sleep(0)

            # ------------------------------------------
            # RUN BOTH TASKS
            # ------------------------------------------

            print("Starting continuous conversation...")

            browser_task = asyncio.create_task(
                receive_from_browser(),
                name="browser_to_gemini"
            )

            gemini_task = asyncio.create_task(
                receive_from_gemini(),
                name="gemini_to_browser"
            )

            tasks = [browser_task, gemini_task]

            try:

                done, pending = await asyncio.wait(
                    tasks,
                    return_when=asyncio.FIRST_COMPLETED
                )

                print("One conversation task ended.")

                for task in done:

                    print("Finished task:", task.get_name())

                    try:
                        task.result()

                        print(
                            "Task completed normally:",
                            task.get_name()
                        )

                    except Exception as error:

                        print(
                            "TASK ERROR:",
                            task.get_name(),
                            repr(error)
                        )

                        traceback.print_exc()

                # Cancel the other task only when the
                # browser disconnects or an error occurs.

                for task in pending:
                    task.cancel()

                await asyncio.gather(
                    *pending,
                    return_exceptions=True
                )

            except Exception as error:

                print("TASK MANAGEMENT ERROR:", repr(error))
                traceback.print_exc()

                raise

    except WebSocketDisconnect:

        print("Browser disconnected from AJUPY")

    except Exception as error:

        print("\nAJUPY SERVER ERROR:", repr(error))
        traceback.print_exc()

    finally:

        print("AJUPY WebSocket session ended\n")
