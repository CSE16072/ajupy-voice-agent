
import streamlit as st
import os
from modules.text_to_speech import generate_speech

st.title("AJUPY AI - Text to Speech Test")

text = st.text_input(
    "Enter your message:",
    "Hello! Welcome to AJUPY AI."
)

if st.button("Generate Speech"):
    with st.spinner("Generating audio..."):
        audio_path = generate_speech(text)

    if audio_path:
        st.success("Speech generated successfully!")

        with open(audio_path, "rb") as audio_file:
            st.audio(audio_file.read(), format="audio/mp3")

        os.remove(audio_path)
    else:
        st.error("Speech generation failed.")
