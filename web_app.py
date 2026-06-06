import streamlit as st
import pandas as pd
import st_tailwind as tw
from st_tailwind import tw_wrap
from pathlib import Path
import time

from src.inference_logic import preprocess_audio, get_prediction
from src.preprocessing import prepare_audio
from src.visualize_lms import visualize_npy_spectrogram
from src.hardware_control import trigger_hardware

MODEL_PATHS = {
    "efficientnet_b0_audio_spec" : "models/efficientnet_b0_audio_spec_best_model.pth",
    "mobilenet_v3_audio" : "models/mobilenet_v3_audio_best_model.pth",
    "regnet_y_800mf_audio_spec" : "models/regnet_y_800mf_audio_spec_best_model.pth",
    "regnet_y_800mf_spec" : "models/regnet_y_800mf_spec_best_model.pth",
    "shufflenet_v2_audio_spec" : "models/shufflenet_v2_audio_spec_best_model.pth",
    "shufflenet_v2_spec" : "models/shufflenet_v2_spec_best_model.pth"
}

# Removes some audio upload elements (UI-related)
st.markdown("""
    <style>
        /* 1. Hide the default 'Drag and drop file here' text and layout metadata */
        [data-testid="stFileUploaderDropzone"] > div > span,
        [data-testid="stFileUploaderDropzone"] div div,
        [data-testid="stFileUploaderFileName"] {
            display: none !important;
        }
        
        /* 2. Configure the dropzone container layout */
        [data-testid="stFileUploaderDropzone"] {
            display: flex !important;
            justify-content: center !important;
            flex-direction: column !important;
            align-items: center !important;
            border: none !important;
            background-color: transparent !important;
            padding: 0 !important;
        }

        /* 3. Style the upload button perfectly (handles both empty and uploaded states) */
        [data-testid="stFileUploaderDropzone"] button {
            background-color: #3772a5 !important;
            color: white !important;
            border: 1px solid #000000 !important; 
            padding: 8px 20px !important;
            margin: 0 auto !important;
            display: block !important;
            font-size: 0 !important; /* Hides default 'Browse files' text */
            border-radius: 4px !important;
        }
            
        /* 4. Force our custom text onto the button face universally */
        [data-testid="stFileUploaderDropzone"] button::after {
            content: "Upload audio file" !important;
            display: block !important;
            font-size: 16px !important; 
            line-height: normal !important;
            color: white !important;
        }

        /* 5. Hide the interior default text inside the button container */
        [data-testid="stFileUploaderDropzone"] button * {
            display: none !important;
        }

        /* 6. Custom styling for the green Detect Cracks button */
        div.stButton button {
        background-color: #7bc040 !important;
        color: white !important;
        border-radius: 9999px !important; /* Rounded-full pill shape */
        border: 1px solid black !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
        width: fit-content !important;
        margin: 0 auto !important;
        display: block !important;
        }     
            
        /* 7. Force all native bordered containers to render a solid black outline */
        div[data-testid="stContainer"] {
            border: 1px solid #000000 !important;
        }
    </style>
""", unsafe_allow_html=True)


# --- Classification Result
# In your streamlit file:
# --- Classification Result
@st.dialog("Results")
def show_result(res, log_mel, recorded_file=None):
    
    # FIX: If we have an automated hardware file, extract its name. Otherwise use the uploader.
    if recorded_file is not None:
        # Path(recorded_file).name converts "folder/audio.wav" -> "audio.wav"
        display_name = Path(recorded_file).name 
        save_reference = recorded_file
    else:
        display_name = audio_file.name if audio_file is not None else "Live Recording"
        save_reference = display_name

    st.write(f"Audio Source: {display_name}")

    # Color based on results
    color = "#FF4B4B" if res == "CRACKED" else "#2ECC71"

    st.markdown(
        f"""
        <div style="text-align: center;">
            <h3>Egg Classification:</h3>
            <h1 style="color: {color}; margin-bottom: 10;">{res}</h1>  
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.write('### Acoustic Signature Analysis')
    
    # Pass the correct file reference so matplotlib saves the image with the correct name
    fig = visualize_npy_spectrogram(log_mel, save_reference)
    st.pyplot(fig)

    done_button = st.button(
        "Done",
        key="done_action",
        use_container_width=True
    )

    if done_button:
        if "classification_result" in st.session_state:
            del st.session_state.classification_result
        st.rerun()


# --- Setup & UI

# Call to integrate Tailwind
tw.initialize_tailwind()

if "classification_result" not in st.session_state:
   
     with st.container(border=True, width=680, height=430):
        st.write("CNN-based EggCrack Detection")
        col_left, col_right = st.columns([3,2])

        # LEFT SIDE OF THE CONTAINER (upload area)
        with col_left:
            with st.container(border=True, width=500, height=260):
                # Placeholders
                image_spot = st.empty()
                text_spot = st.empty()

                # Call the uploader (define 'audio_file')
                audio_file = st.file_uploader(
                    "uploader",
                    type=["mp3","wav","ogg"],
                    label_visibility="collapsed"
                )

                # Upload file (Uploader)
                if audio_file is None:
                    with image_spot.container():
                        sub1, sub2, sub3 = st.columns([2, 2, 1])
                        # Mic Image
                        sub2.image("assets/mic_plus.svg", width=60)
                else:
                    with image_spot.container():
                        sub1, sub2, sub3 = st.columns([2, 4, 1])
                        # Show audio player if a file is uploaded
                        sub2.image("assets/waveform.svg", width=180)
                        text_spot.markdown(f"<p style='text-align:center; color:#3772a5;'>{audio_file.name}</p>", unsafe_allow_html=True)

                # Show audio player if a file is uploaded (Upload done)
                if audio_file is not None:
                    st.audio(audio_file)
                    

        # RIGHT SIDE OF THE CONTAINER (radio buttons, detect button)
        with col_right:
            
            # RADIO BUTTONS
            st.write("**Please select a model:**")
            model_selected_btn = st.radio(
                "Model Selection",
                ["efficientnet_b0_audio_spec", 
                "mobilenet_v3_audio", 
                "regnet_y_800mf_audio_spec", 
                "regnet_y_800mf_spec", 
                "shufflenet_v2_audio_spec", 
                "shufflenet_v2_spec"],
                index=None
            )

            hardware_btn = st.button(
                "Tap",
                key="auto_hardware_action"
            )

            # DETECT BUTTON
            # detect_button = st.button(
            #     "Detect Cracks", 
            #     key="detect_action"
            # )
            if hardware_btn:
                # Check if button was clicked
                if model_selected_btn is None: 
                    st.warning("Choose a model before proceeding", icon="⚠️")
                    # if no model selected
                   

                    # if file upload and model are selected, proceed with detection
                else: 
                    with st.spinner("Analysing Tapping... Recording Acoustic Response...", show_time=True):
                        # Get the file path from the mapping dictionary
                        # selected_path = MODEL_PATHS[model_selected_btn]
                        # selected_model = selected_path.split("/")
                        # selected_model = selected_model[1].split('_') 
                        try:
                            # 1. Trigger rig: live_wav_file will hold the path string (e.g., 'captured_audio.wav')
                            live_wav_file, log_mel_matrix = trigger_hardware()

                            # 2. Get the correct model paths and keys
                            selected_path = MODEL_PATHS[model_selected_btn] 
                            
                            model_key = ""
                            if "regnet" in model_selected_btn.lower(): model_key = "regnet_y"
                            elif "efficientnet" in model_selected_btn.lower(): model_key = "efficientnet_b0"
                            elif "mobilenet" in model_selected_btn.lower(): model_key = "mobilenet_v3"
                            elif "shufflenet" in model_selected_btn.lower(): model_key = "shufflenet_v2"

                            # 3. Preprocess the newly recorded hardware audio file
                            processed_data, log_mel = preprocess_audio(live_wav_file)

                            # 4. Run inference
                            prediction_result = get_prediction(selected_path, processed_data, model_key)

                            time.sleep(3)
                            st.success("Analysis Complete!")
                            st.session_state.classification_result = prediction_result

                            # 5. FIX: Pass the actual recorded file path straight to the dialog window
                            show_result(prediction_result, log_mel, recorded_file=live_wav_file)

                        except Exception as e:
                            st.error(f"Error loading model: {e}")
                                                    
            
# if no file upload
    # if not audio_file:
    #     st.warning("Choose an audio file to detect", icon="⚠️")
