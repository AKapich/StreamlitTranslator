import streamlit as st
import pyaudio
import wave
import os
import numpy as np
from io import BytesIO
from pydub import AudioSegment
import sounddevice as sd

# Function to record audio
def record_audio(filename, duration):
    audio_data = []

    with st.spinner("Recording..."):
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        frames_per_buffer=1024)

        for _ in range(int(44100 / 1024 * duration)):
            data = stream.read(1024)
            audio_data.append(data)

        stream.stop_stream()
        stream.close()

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(audio_data))

# Function to play audio
def play_audio(audio_bytes):
    st.audio(audio_bytes, format="audio/wav")

st.title("Audio Collection App")

p = pyaudio.PyAudio()

# Record audio
if st.button("Record Audio"):
    st.write("Recording...")
    audio_buffer = BytesIO()
    record_audio(audio_buffer, duration=5)
    st.success("Audio recorded!")
    
    audio_buffer.seek(0)
    audio_bytes = audio_buffer.read()
    
    # Save audio to a file
    filename = "recorded_audio.wav"
    with open(filename, "wb") as f:
        f.write(audio_bytes)
    
    # Play the recorded audio
    st.audio(audio_bytes, format="audio/wav")
    
    # Download the recorded audio
    st.markdown(f"**[Download Recorded Audio](data:audio/wav;base64,{audio_bytes.decode('utf-8', 'ignore')})**")

# Play uploaded audio
uploaded_audio = st.file_uploader("Upload an audio file", type=["wav"])
if uploaded_audio is not None:
    st.write("Playing uploaded audio...")
    audio_bytes = uploaded_audio.read()
    play_audio(audio_bytes)

# Clean up
st.write("Cleaning up...")
p.terminate()
