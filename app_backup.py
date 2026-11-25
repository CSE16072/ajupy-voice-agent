from modules.memory import create_database, save_message, get_messages, clear_messages
import streamlit as st
import os

from modules.speech_to_text import transcribe_audio
from modules.ai_brain import generate_response
from modules.text_to_speech import generate_speech


st.set_page_config(
    page_title="AJUPY AI Voice Assistant",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ AJUPY AI Voice Assistant")

st.write(
    "Hello! I am AJUPY AI. "
    "I can listen, think, remember our conversation, and respond."
)

# Initialize conversation memory
create_database()

if "messages" not in st.session_state:
    st.session_state.messages = get_messages()

# Display previous conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Microphone input
st.subheader("🎤 Talk to AJUPY AI")

audio = st.audio_input("Record your voice")

if audio:
    if st.button("Process My Voice"):

        with st.spinner("Listening to your voice..."):
            user_text = transcribe_audio(audio)

        if user_text:

            st.success("I understood your voice!")

            # Save user message
            st.session_state.messages.append({
                "role": "user",
                "content": user_text
            })
            save_message("user", user_text)

            with st.chat_message("user"):
                st.write(user_text)

            # Send previous conversation to Gemini
            chat_history = st.session_state.messages[:-1]

            with st.spinner("AJUPY AI is thinking..."):
                ai_response = generate_response(
                    user_text,
                    chat_history
                )

            # Save AI response
            st.session_state.messages.append({
                "role": "assistant",
                "content": ai_response
            })

            with st.chat_message("assistant"):
                st.write(ai_response)

                with st.spinner("Generating voice..."):
                    audio_path = generate_speech(ai_response)

                if audio_path:
                    try:
                        with open(audio_path, "rb") as audio_file:
                                  audio_bytes = audio_file.read()
                                  st.audio(
                                audio_bytes,
                               format="audio/mp3",
                                autoplay=True
)
                    finally:
                        if os.path.exists(audio_path):
                            os.remove(audio_path)

        else:
            st.error("I could not understand your voice. Please try again.")


# Text input
st.divider()
st.subheader("💬 Or type your message")

typed_message = st.chat_input("Ask AJUPY AI something...")

if typed_message:

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": typed_message
    })
    save_message("user", typed_message)

    with st.chat_message("user"):
        st.write(typed_message)

    # Get previous conversation
    chat_history = st.session_state.messages[:-1]

    with st.spinner("AJUPY AI is thinking..."):
        ai_response = generate_response(
            typed_message,
            chat_history
        )

    # Save AI response
    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_response
    })
    save_message("assistant", ai_response)

    with st.chat_message("assistant"):
        st.write(ai_response)

        audio_path = generate_speech(ai_response)

        if audio_path:
            try:
                with open(audio_path, "rb") as audio_file:
                    st.audio(
                        audio_file.read(),
                        format="audio/mp3"
                    )
            finally:
                if os.path.exists(audio_path):
                    os.remove(audio_path)


# Clear conversation button
st.divider()

if st.button("🗑️ Clear Conversation"):
    clear_messages()
    st.session_state.messages = []
    st.rerun()