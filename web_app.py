import streamlit as st
import pandas as pd
import st_tailwind as tw
from st_tailwind import tw_wrap

# Removes some audio upload elements
st.markdown("""
    <style>
        /* Hides the 'Drag and drop' text */
        [data-testid="stFileUploaderDropzone"] div div {
            display: none !important;
        }
        
        /* Hides the 'Limit 200MB' text */
        [data-testid="stFileUploaderFileName"] {
            display: none !important;
        }
            
        /* Removes the Gray Background and Border */
        [data-testid="stFileUploaderDropzone"] {
            background-color: transparent !important;
            border: none !important;
            padding: 0 !important;

        /* Ensures the 'Browse files' button stays visible and centered */
        [data-testid="stFileUploaderDropzone"] button {
            display: block !important;
            margin: auto !important;
        }
    </style>
""", unsafe_allow_html=True)


# Call to integrate Tailwind
tw.initialize_tailwind()

st.write("[Best model name]-based EggCrack Detection")

# Upload Logic
audio_container = tw_wrap(st.container)(
    key="main-container",
    classes="border-1 border-black flex justify-center"
)
with st.container(border=True, width=600, height=300):
    st.image("assets/mic_plus.svg", width=45)

    audio_file = st.file_uploader(
        "Upload audio file", 
        type=["mp3","wav","ogg"], 
        width=300, 
        max_upload_size=200,
        label_visibility="collapsed")

    # Show audio player if a file is uploaded
    if audio_file is not None:
        st.audio(audio_file, format=f'audio/{audio_file.type.split("/")[-1]}')


# Detect Button
detect_button = tw_wrap(st.button)(
    "Detect Cracks", 
    key="detect_action",
    classes="w-fit bg-green-600 text-white rounded-full border-1 border-black px-6 flex justify-center place-content-center"
    )

if detect_button:
    st.info("Analysing audio for cracks...") # Call CNN model here for later


# df = pd.read_csv("data.csv")
# st.line_chart(df)