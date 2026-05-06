import streamlit as st
import pandas as pd
import st_tailwind as tw
from st_tailwind import tw_wrap
import time

# Removes some audio upload elements (UI-related)
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
            
        /* Centers container of the button */
        [data-testid="stFileUploaderDropzone"] {
            display: flex !important;
            justify-content: center !important;
            flex-direction: column !important;
            align-items: center !important;
            border: none !important;
        }
            
        /* Removes the Gray Background and Border */
        [data-testid="stFileUploaderDropzone"] {
            background-color: transparent !important;
            border: none !important;
            padding: 0 !important;
        }

        /* Ensures the 'Browse files' button itself is centered */
        [data-testid="stFileUploaderDropzone"] button {
            display: block !important;
            margin: 0 auto !important;
        }
            
        /* Custom audio file upload button */
        [data-testid="stFileUploaderDropzone"] button {
            background-color: #3772a5 !important;
            color: white !important;
            border: 1px solid #000000 !important; 
            padding: 8px 20px !important;
            margin: 0 auto !important;
            display: block !important;
            font-size: 0 !important; 
            line-height: 0 !important;
        }
        
        /* Custom button label */
        [data-testid="stFileUploaderDropzone"] button::after {
            content: "Upload Audio File" !important;
            display: block !important;
            font-size: 16px !important; 
            line-height: normal !important;
            color: white !important;
        }

        /* Ensuring no other spans inside the button show up */
        [data-testid="stFileUploaderDropzone"] button * {
            display: none !important;
        }
            
    </style>
""", unsafe_allow_html=True)



# --- Classification Result
@st.dialog("Results")
def show_result(res):
    st.write(f"Audio File: {audio_file.name}")
    st.markdown(f" ### Egg Classification: {res} ", unsafe_allow_html=True)
    if st.button("Done", use_container_width=True):
        if "classification_result" in st.session_state:
            del st.session_state.classification_result
        st.rerun()


# --- Setup & UI

# Call to integrate Tailwind
tw.initialize_tailwind()
st.write("[Best model name]-based EggCrack Detection")

if "classification_result" not in st.session_state:

    # Main Container (black border)
    audio_container = tw_wrap(st.container)(
        key="main-container",
        classes="border-1 border-black rounded-xl p-10 flex flex-col items-center justify-center space-y-4"
    )
    with st.container(border=True, width=600, height=300):
        # Mic Image
        st.image("assets/mic_plus.svg", width=45)

        # Upload file (Uploader)
        audio_file = st.file_uploader(
            "Upload Audio File",
            type=["mp3","wav","ogg"], 
            width=300, 
            max_upload_size=200,
            label_visibility="collapsed")

        # 2. Show audio player if a file is uploaded (Upload done)
        if audio_file is not None:
            st.audio(audio_file, format=f'audio/{audio_file.type.split("/")[-1]}')

    # Detect Button        
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        detect_button = tw_wrap(st.button)(
            "Detect Cracks", 
            key="detect_action",
            classes="w-fit mx-auto block bg-[#7bc040] text-white rounded-full border-1 border-black px-6"
            )

    
        # --- 3. Analyzing Audio File and Detecting Cracks
        if detect_button:
            if audio_file:
                with st.spinner("Analysing audio for cracks...", show_time=True):
                    time.sleep(2)
                    prediction_result  ="CRACKED" # PUT ACTUAL MODEL OUTPUT HERE (cracked/uncracked)
                st.success("Detection Done!")
                st.session_state.classification_result = prediction_result
                show_result(prediction_result)
                # st.session_state.classification_result = result
                # st.info("Analysing audio for cracks...") # Call CNN model here for later
    
            else:
                st.warning("Choose an audio file to detect", icon="⚠️")


