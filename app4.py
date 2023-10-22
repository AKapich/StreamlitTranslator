import streamlit as st
from streamlit_audio_recorder.st_audiorec import st_audiorec
# import whisper
import numpy as np

# model = whisper.load_model("base")

# def transcribe(audio):
    
#     #time.sleep(3)
#     # load audio and pad/trim it to fit 30 seconds
#     audio = whisper.load_audio(audio)
#     audio = whisper.pad_or_trim(audio)

#     # make log-Mel spectrogram and move to the same device as the model
#     mel = whisper.log_mel_spectrogram(audio).to(model.device)

#     # detect the spoken language
#     _, probs = model.detect_language(mel)
#     print(f"Detected language: {max(probs, key=probs.get)}")

#     # decode the audio
#     options = whisper.DecodingOptions(fp16 = False)
#     result = whisper.decode(model, mel, options)
#     return result.text

# import torch
# from transformers import pipeline

# # start model
# device = "cuda:0" if torch.cuda.is_available() else "cpu"

# translation_pipe = pipeline(
#         "automatic-speech-recognition", model="openai/whisper-base", device=device
#     )

# def translate(audio, lang = "en"):
#     outputs = translation_pipe(audio, max_new_tokens=256, generate_kwargs={"task": "transcribe", "language": lang})
#     return outputs["text"]
    
def translate(audio, lang = "en"):
    return "test"
    
# Customizing the Streamlit page layout
st.set_page_config(
    page_title="tłumacz",
    page_icon="🎤",
    layout="wide",
)


AVAILABLE_MODEL_SIZES = ["tiny", "base", "small", "medium", "large"]
AVAILABLE_LANGUAGES = {}

# Center the app title and adjust padding
st.markdown(
    """
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    .stTitle {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def audiorec_demo_app():

    st.title('Audio Recorder App')
    st.subheader('Record and Playback Audio')

    # Add a little info on how to use the app
    st.markdown(
        "🎤 To record audio, simply click the 'Start Recording' button. "
        "Once you're done, click 'Stop Recording' and 'Save Recording' to play it back. "
        "You can also reset the recording if needed."
    )
    
    model_size = st.selectbox("Wybierz rozmiar modelu: ", AVAILABLE_MODEL_SIZES)
    
    input_language = st.selectbox("Wybierz język wejściowy", ["PL", "EN"])
    output_language = st.selectbox("Wybierz język wyjściowy", ["PL", "EN"])

    wav_audio_data = st_audiorec()

    filename = "temp.wav"

    if wav_audio_data is not None:
        # Display the recorded audio
        st.subheader('Transcribed text:')

        with open(filename, "wb") as f:
            f.write(wav_audio_data)
        with open(filename, "rb") as f:
            audio = f.read()
        cols=st.columns(2)
        with cols[0]:
            with st.spinner("Transcribing text..."):
                output_text = translate(audio, lang="pl")
                st.markdown(f"**Orginalny tekst [{input_language}]:** {output_text}")
        with cols[1]:
            with st.spinner("Translating text..."):
                translated_text = translate(audio, lang="en")
                st.markdown(f"**Tłumaczenie [{output_language}]:** {translated_text}")

if __name__ == '__main__':
    audiorec_demo_app()
