import streamlit as st
from st_audiorec import st_audiorec

from transformers import pipeline
import torch

device = "cuda:0" if torch.cuda.is_available() else "cpu"
pipe = pipeline(
    "automatic-speech-recognition", model="openai/whisper-base", device=device
)

def transcribe(audio, lang='pl'):
    outputs = pipe(audio, max_new_tokens=256, generate_kwargs={"task": "transcribe", "language": f"{lang}"})
    return outputs["text"]

def translate(audio, lang='en'):
    outputs = pipe(audio, max_new_tokens=256, generate_kwargs={"task": "translate", "language": f"{lang}"})
    return outputs["text"]


st.set_page_config(page_title="streamlit_audio_recorder")
# Design move app further up and remove top padding
st.markdown('''<style>.css-1egvi7u {margin-top: -3rem;}</style>''',
            unsafe_allow_html=True)
# Design change st.Audio to fixed height of 45 pixels
st.markdown('''<style>.stAudio {height: 45px;}</style>''',
            unsafe_allow_html=True)
# # Design change hyperlink href link color
st.markdown('''<style>.css-v37k9u a {color: #ff4c4b;}</style>''',
            unsafe_allow_html=True)  # darkmode
st.markdown('''<style>.css-nlntq9 a {color: #ff4c4b;}</style>''',
            unsafe_allow_html=True)  # lightmode

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
    st.write('\n')
    
    st.markdown('''<style>body {padding: 10px;} .stAudio {height: 45px;} .css-1egvi7u {margin-top: -3rem;} .css-v37k9u a {color: #ff4c4b;}</style>''',
                 unsafe_allow_html=True)


    with st.sidebar:
        st.title("Ustawienia językowe")
        og_lang = st.selectbox("Wybierz język wejściowy: ", langdict.keys(), 38)
        output_lang = st.selectbox("Wybierz język wyjściowy:", langdict.keys(), 13)

    wav_audio_data = st_audiorec()

    col_info, col_space = st.columns([0.57, 0.43])
    with col_info:
        st.write('\n')
    

    if wav_audio_data is not None:
        st.write('**Original Text:**')
        st.write(transcribe(wav_audio_data, lang=langdict[og_lang]), unsafe_allow_html=True)
        st.write('**Translation:**')
        st.write(translate(wav_audio_data, lang=langdict[output_lang]), unsafe_allow_html=True)



if __name__ == '__main__':
    main()