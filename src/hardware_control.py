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
    TARGET_PORT = 'COM3' # change to actual port later
else:
    TARGET_PORT = '/dev/cu.usbmodemFX2348N1'

arduino = serial.Serial(port=TARGET_PORT, baudrate=115200, timeout=.1) # /dev/cu.usbmodemFX2348N1

# mac port: /dev/cu.usbmodemFX2348N1

def send_signal(signal):
    # Send the signal to the Arduino, encoded as bytes
    arduino.write(bytes(signal, 'utf-8'))
    time.sleep(0.05) # Small delay for stability

# Wait briefly for the serial connection to establish
time.sleep(2) 

def trigger_hardware():
    # PyAudio audio streaming parameter definitions
    CHUNK = 512
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS =1.5



    # FILENAMES + METADATA FOR CSV
    WAVE_OUTPUT_FILENAME = "egg100-5-cracked-1-p4-sv0.wav" # only edit this !!!! egg(ikapila)-(fold 1-5)-(uncracked|cracked)-(target 0/1)-p(1-4))-sv(0-2)

    # Target: 0 - uncracked | 1 - cracked
    # sv(serverity): 0 - uncracked | 1- cracked | 2 - microcrack
    # fold: default 1 to 5, then back to 1


    CLEANED_WAV_FILENAME = filename_utils.get_cleaned_filename(WAVE_OUTPUT_FILENAME)
    CLEANED_NPY_FILENAME = filename_utils.get_npy_filename(CLEANED_WAV_FILENAME)
    METADATA = filename_utils.extract_metadata(WAVE_OUTPUT_FILENAME)

    p = pyaudio.PyAudio()
    stream = None
    wf = None

    try:
        # Open audio stream
        send_signal('f')
        time.sleep(4)
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=2)  # Use connected microphone

        print("* Recording started...")
        print(f"  Duration: {RECORD_SECONDS} seconds")
        frames = []

        # Send the signal to execute the function
        print("Sending signal 's' to Arduino...")

        # Record audio
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            except IOError as e:
                print(f"Warning: Buffer overflow - continuing...")
                continue

    
        # print("Signal sent.") # Wait to ensure the signal is processed
        # arduino.close()
        print("* Recording complete")
        
        # Save the recorded audio file
        if frames:
            wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

            if wf is not None:
                try:
                    wf.close()
                except:
                    pass
            
            # log metadat to csv file
            logger.log_egg_data(METADATA, WAVE_OUTPUT_FILENAME)
                
            # Calculate file info
            # duration = len(frames) * CHUNK / RATE
            # import os
            # file_size = os.path.getsize(WAVE_OUTPUT_FILENAME) / 1024  # KB

            # filtering.py logic
            clean_file = CLEANED_WAV_FILENAME
            # time.sleep(5)
            filtering.run_filtering(WAVE_OUTPUT_FILENAME, clean_file)


            # visualize_lms.py logic
            npy_file = CLEANED_NPY_FILENAME
            log_mel, sr = visualize_lms.convert_audio_to_logmel_npy(clean_file, npy_file)
            visualize_lms.visualize_npy_spectrogram(log_mel, filename=WAVE_OUTPUT_FILENAME, sr=sr)

            return clean_file, log_mel
        else:
            raise Exception("No audio data recorded")

        #     print(f"Saved to {WAVE_OUTPUT_FILENAME}")
        #     print(f"Duration: {duration:.1f} seconds")
        #     print(f"Size: {file_size:.1f} KB")
        # else:
        #     print("✗ No audio data recorded")



    # except IOError as e:
    #     print(f"✗ Recording failed: {e}")
    #     print("Check that your microphone is connected and not in use.")
    # except KeyboardInterrupt:
    #     print("\n✗ Recording interrupted by user")
    # except Exception as e:
    #     print(f"✗ Unexpected error: {e}")
        
    finally:
        # Cleanup stream
        if stream is not None:
            try:
                if stream.is_active():
                    stream.stop_stream()
                stream.close()
            except:
                pass
        
        # Cleanup PyAudio
        if p is not None:
            try:
                p.terminate()
            except:
                pass
        