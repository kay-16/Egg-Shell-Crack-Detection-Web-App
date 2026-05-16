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
            
        /* Custom audio file UPLOAD button */
        [data-testid="stFileUploaderDropzone"] button {
            background-color: #3772a5 !important;
            color: white !important;
            border: 1px solid #000000 !important; 
            padding: 8px 20px !important;
            margin: 0 auto !important;
            display: block !important;
            font-size: 0 !important; 
        }
            
        /* Custom button label */
        [data-testid="stFileUploaderDropzone"] button::after {
            content: "Upload audio file" !important;
            display: block !important;
            font-size: 16px !important; 
            line-height: normal !important;
            color: white !important;
        }
        
        # /*State 1: Initial Upload */
        # .upload-view [data-testid="stFileUploaderDropzone"] button::after {
        #     content: "Upload audio file" !important;
        #     font-size: 16px !important;
        #     display: block !important;
        # }

        # /*State 2: New File Button */
        # .new-upload-view [data-testid="stFileUploaderDropzone"] button::after {
        #     content: "New audio file" !important;
        #     font-size: 14px !important;
        #     display: block !important;
        # }

        /*Small UI cleanup for the dropzone */
        [data-testid="stFileUploaderDropzone"] {
            border: none !important;
            background-color: transparent !important;
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
    
    done_button = tw_wrap(st.button)(
        "Done",
        key="done_action",
        use_container_width=True,
        classes="w-fit mx-auto block bg-[#3772a5] text-white border-black px-6"
    )

    if done_button:
        # To clear the result from state and refresh to start over
        if "classification_result" in st.session_state:
            del st.session_state.classification_result
        st.rerun()
        

 # if st.button("Done", use_container_width=True):


# --- Setup & UI

# Call to integrate Tailwind
tw.initialize_tailwind()

if "classification_result" not in st.session_state:
    # # Main Container (black border)
    # main_container = tw_wrap(st.container)(
    #     classes="border-1 border-black p-10 flex flex-col items-center justify-center space-y-4"
    # )

    # # Upload audio container
    # audio_container = tw_wrap(st.container)(
    #     key="audio-container",
    #     classes="border-1 border-black p-10 flex flex-col items-center justify-center space-y-4"
    # )

    
    with st.container(border=True, width=1000, height=430):
        st.write("CNN-based EggCrack Detection")
        col_left, col_right = st.columns([3,2])

        # LEFT SIDE OF THE CONTAINER (upload area)
        with col_left:
             with st.container(border=True, width=500, height=260):
                # Placeholders
                image_spot = st.empty()
                text_spot = st.empty()

                # Call the uploader (define 'audio_file')
                audio_file = tw_wrap(st.file_uploader)(
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
                ["Best Model 1", "Best Model 2", "Best Model 3", "Best Model 4", "Best Model 5"],
                index=None
            )

            # DETECT BUTTON
            detect_button = tw_wrap(st.button)(
                "Detect Cracks", 
                key="detect_action",
                classes="w-fit mx-auto block bg-[#7bc040] text-white rounded-full border-1 border-black px-6"
                )
            
            # Check if button was clicked
            if detect_button: 
                # if no file upload
                if not audio_file:
                    st.warning("Choose an audio file to detect", icon="⚠️")

                # if no model selected
                elif model_selected_btn is None:
                    st.warning("Choose a model before proceeding", icon="⚠️")

                # if file upload and model are selected, proceed with detection
                else: 
                    with st.spinner("Analysing audio for cracks...", show_time=True):
                        time.sleep(2)
                        prediction_result="CRACKED" # PUT ACTUAL MODEL OUTPUT HERE (cracked/uncracked)
                    st.success("Detection Done!")
                    st.session_state.classification_result = prediction_result
                    show_result(prediction_result)
                    # st.session_state.classification_result = result
                    # st.info("Analysing audio for cracks...") # Call CNN model here for later

            
                
            

# /* Custom button label */
#         [data-testid="stFileUploaderDropzone"] button::after {
#             content: "Upload Audio File" !important;
#             display: block !important;
#             font-size: 16px !important; 
#             line-height: normal !important;
#             color: white !important;
#         }
