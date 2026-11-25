
import streamlit as st
from modules.speech_to_text import transcribe_audio

st.set_page_config(page_title="AJUPY AI Speech Test")

st.title("AJUPY AI - Speech Recognition Test")

st.write("Speak into your microphone to test speech recognition.")

audio = st.audio_input("Record your voice")

if audio:
    st.audio(audio)

    if st.button("Convert Speech to Text"):
        with st.spinner("Recognizing your speech..."):
            result = transcribe_audio(audio)

        if result:
            st.success("Speech converted successfully!")
            st.write("You said:", result)
        else:
            st.error("Could not recognize your speech.")
