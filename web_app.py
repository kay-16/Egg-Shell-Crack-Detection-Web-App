import streamlit as st
import pandas as pd
import st_tailwind as tw
from st_tailwind import tw_wrap

# Call to integrate Tailwind
tw.initialize_tailwind()

st.write("[Best model name]-based EggCrack Detection")

# Upload Logic

audio_container = tw_wrap(st.container)(
    classes="border-1 border-black"
)
with st.container(border=True, width="stretch", height=300):
    audio_file = st.file_uploader("Upload audio file", type=["mp3","wav","ogg"])

    if audio_file is not None:
        st.audio(audio_file, format=f'audio/{audio_file.type.split("/")[-1]}')

# Detect Button
detect_button = tw_wrap(st.button)(
    "Detect Cracks", 
    key="detect_action",
    classes="w-fit bg-green-600 text-white rounded-full border-1 border-black justify-center-safe place-items-center"
    )

if detect_button:
    st.info("Analysing audio for cracks...") # Call CNN model here for later


# df = pd.read_csv("data.csv")
# st.line_chart(df)