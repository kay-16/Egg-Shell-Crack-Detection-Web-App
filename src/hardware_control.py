import pyaudio
import wave
import serial
import time
import os

from . import logger
from . import visualize_lms
from . import filtering
from . import filename_utils   

# Auto-detect operating system to set correct port
if os.name == 'nt':
    TARGET_PORT = 'COM3' 
else:
    TARGET_PORT = '/dev/cu.usbmodemFX2348N1'

# REMOVED global arduino = serial.Serial(...) definition from here!

def send_signal(ser, signal):
    """Pass the active serial instance to write data safely"""
    ser.write(bytes(signal, 'utf-8'))
    time.sleep(0.05) # Small delay for stability

def trigger_hardware():
    # PyAudio audio streaming parameter definitions
    CHUNK = 512
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 1.5

    # FILENAMES + METADATA FOR CSV
    WAVE_OUTPUT_FILENAME = "egg100-5-cracked-1-p4-sv0.wav" 

    CLEANED_WAV_FILENAME = filename_utils.get_cleaned_filename(WAVE_OUTPUT_FILENAME)
    CLEANED_NPY_FILENAME = filename_utils.get_npy_filename(CLEANED_WAV_FILENAME)
    METADATA = filename_utils.extract_metadata(WAVE_OUTPUT_FILENAME)

    p = pyaudio.PyAudio()
    stream = None
    wf = None
    arduino = None

    try:
        # 1. Open the serial connection dynamic-on-demand
        print(f"Opening connection to Arduino on {TARGET_PORT}...")
        arduino = serial.Serial(port=TARGET_PORT, baudrate=115200, timeout=.1)
        time.sleep(2) # Wait briefly for the connection to fully establish

        # 2. Alert Arduino to prepare
        send_signal(arduino, 'f')
        time.sleep(4)

        # Open audio stream
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK,)  # Use connected microphone

        print("* Recording started...")
        print(f"  Duration: {RECORD_SECONDS} seconds")
        frames = []

        # 3. FIX: Actually send the 's' signal to drop the physical tapper!
        print("Sending signal 's' to Arduino...")
        send_signal(arduino, 's')

        # Record audio response
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            except IOError as e:
                print(f"Warning: Buffer overflow - continuing...")
                continue

        print("* Recording complete")
        
        # Save the recorded audio file
        if frames:
            wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            # Log metadata to csv file
            logger.log_egg_data(METADATA, WAVE_OUTPUT_FILENAME)
                
            # Filtering logic
            clean_file = CLEANED_WAV_FILENAME
            filtering.run_filtering(WAVE_OUTPUT_FILENAME, clean_file)

            # Visualize log-mel matrix
            npy_file = CLEANED_NPY_FILENAME
            log_mel, sr = visualize_lms.convert_audio_to_logmel_npy(clean_file, npy_file)
            
            # NOTE: If visualize_lms uses plt.show(), it might throw warnings in Streamlit backend. 
            # But it saves clean_file data correctly for processing.
            visualize_lms.visualize_npy_spectrogram(log_mel, filename=WAVE_OUTPUT_FILENAME, sr=sr)

            return clean_file, log_mel
        else:
            raise Exception("No audio data recorded")

    finally:
        # Cleanup audio stream safely
        if stream is not None:
            try:
                if stream.is_active():
                    stream.stop_stream()
                stream.close()
            except:
                pass
        
        if p is not None:
            try:
                p.terminate()
            except:
                pass

        # 4. CRITICAL: Close the Serial port resource cleanly so it can be re-opened on next tap
        if arduino is not None and arduino.is_open:
            try:
                arduino.close()
                print("Serial connection closed cleanly.")
            except:
                pass