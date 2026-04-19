import streamlit as st
import pandas as pd

st.write("[Best model name]-based EggCrack Detection")


with st.container(border=True, width="stretch", height=400):
    audio_file = st.file_uploader("Upload audio file", type=["mp3","wav","ogg"])

    if audio_file is not None:
        st.audio(audio_file, format=f'audio/{audio_file.type.split("/")[-1]}')

# df = pd.read_csv("data.csv")
# st.line_chart(df)