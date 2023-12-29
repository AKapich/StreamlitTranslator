import streamlit as st
from audio_recorder.streamlit_audio_recorder.st_audiorec import st_audiorec
from transformers import pipeline
import torch
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO
import streamlit as st

@st.cache_resource()
def load_model():
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    return pipeline("automatic-speech-recognition", model="openai/whisper-large", device=device)

pipe = load_model()

@st.cache_data
def transcribe(audio, lang='pl'):
    outputs = pipe(audio, max_new_tokens=256, generate_kwargs={"task": "transcribe", "language": f"{lang}"})
    return outputs["text"]


def text2speech(text, language):
    tts = gTTS(text, lang=language)
    audio_stream = BytesIO()
    tts.write_to_fp(audio_stream)
    audio_stream.seek(0)
    play(AudioSegment.from_mp3(audio_stream))


st.markdown('''<style>.css-1egvi7u {margin-top: -3rem;}</style>''',
            unsafe_allow_html=True)
st.markdown('''<style>.stAudio {height: 45px;}</style>''',
            unsafe_allow_html=True)
st.markdown('''<style>.css-v37k9u a {color: #ff4c4b;}</style>''',
            unsafe_allow_html=True)
st.markdown('''<style>.css-nlntq9 a {color: #ff4c4b;}</style>''',
            unsafe_allow_html=True) 

langdict = language_abbreviations = {
"Afrikaans": "af",
"Arabski": "ar",
"Armeński": "hy",
"Azerski": "az",
"Białoruski": "be",
"Bośniacki": "bs",
"Bułgarski": "bg",
"Kataloński": "ca",
"Chiński": "zh",
"Chorwacki": "hr",
"Czeski": "cs",
"Duński": "da",
"Holenderski": "nl",
"Angielski": "en",
"Estoński": "et",
"Fiński": "fi",
"Francuski": "fr",
"Galicyjski": "gl",
"Niemiecki": "de",
"Grecki": "el",
"Hebrajski": "he",
"Hindi": "hi",
"Węgierski": "hu",
"Islandzki": "is",
"Indonezyjski": "id",
"Włoski": "it",
"Japoński": "ja",
"Kazachski": "kk",
"Koreański": "ko",
"Łotewski": "lv",
"Litewski": "lt",
"Macedoński": "mk",
"Malajski": "ms",
"Marathi": "mr",
"Maori": "mi",
"Nepalski": "ne",
"Norweski": "no",
"Perski": "fa",
"Polski": "pl",
"Portugalski": "pt",
"Rumuński": "ro",
"Rosyjski": "ru",
"Serbski": "sr",
"Słowacki": "sk",
"Słoweński": "sl",
"Hiszpański": "es",
"Suahili": "sw",
"Szwedzki": "sv",
"Tagalog": "tl",
"Tamilski": "ta",
"Tajski": "th",
"Turecki": "tr",
"Ukraiński": "uk",
"Urdu": "ur",
"Wietnamski": "vi",
"Walijski": "cy",
}


def main():
    st.title('Tłumacz')
    option = st.selectbox("Wybierz formę wgrania danych: ", ['Mikrofon', 'Gotowy plik audio [.wav]'], 0)
    st.markdown("---")
    
    st.markdown('''<style>body {padding: 10px;} .stAudio {height: 45px;} .css-1egvi7u {margin-top: -3rem;} .css-v37k9u a {color: #ff4c4b;}</style>''',
                 unsafe_allow_html=True)


    with st.sidebar:
        st.title("Ustawienia językowe")
        og_lang = st.selectbox("Wybierz język wejściowy: ", langdict.keys(), 38)
        output_lang = st.selectbox("Wybierz język wyjściowy:", langdict.keys(), 13)
        st.markdown("---")
        st.write("Tłumacz stworzony przez:")
        st.write("[Tymoteusz Kwieciński](https://github.com/Fersoil)")
        st.write("[Michał Matejczuk](https://github.com/matejczukm)")
        st.write("[Aleks Kapich](https://github.com/AKapich)")
        

    if option =='Mikrofon':
        wav_audio_data = st_audiorec()
        col_info, col_space = st.columns([0.57, 0.43])
        with col_info:
            st.write('\n')
    else:
        wav_audio_data = st.file_uploader("Wybierz plik audio", type=["wav"])
        if wav_audio_data is not None:
            wav_audio_data = wav_audio_data.read()


    st.markdown("---")
    if wav_audio_data is not None:
        st.write('**Oryginalny tekst:**')
        with st.spinner("Transkrybowanie tekstu..."):
            st.write(transcribe(wav_audio_data, lang=langdict[og_lang]), unsafe_allow_html=True)
        st.write(f'**Tłumaczenie na {output_lang.lower()}:**')
        with st.spinner("Tłumaczenie tekstu..."):
            translation = transcribe(wav_audio_data, lang=langdict[output_lang])
            st.write(translation, unsafe_allow_html=True)
            text2speech(translation, langdict[output_lang])
    


if __name__ == '__main__':
    main()