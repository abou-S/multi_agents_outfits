import streamlit as st
from streamlit_mic_recorder import mic_recorder

st.title("🎙️ Test micro")

audio = mic_recorder(
    start_prompt="🎤 Enregistrer",
    stop_prompt="⏹️ Stop",
    just_once=False,
    use_container_width=True
)

if audio:
    st.audio(audio['bytes'], format='audio/wav')
    st.success("Audio reçu !")
