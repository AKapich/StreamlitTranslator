import streamlit as st
from audio_recorder.streamlit_audio_recorder.st_audiorec import st_audiorec
from transformers import pipeline
import torch
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO
import streamlit as st
import datetime as dt
import  streamlit_toggle as tog

import streamlit_authenticator as stauth
import sqlite3
from pathlib import Path
import os

global FILE_PATH 
FILE_PATH = Path("/volume")  / "translator.db"

class DatabaseConnection:
	def __init__(self, database):
		self.connection = None
		self.database = database

	def __enter__(self):
		self.connection = sqlite3.connect(self.database)
		return self.connection 

	def __exit__(self, exc_type, exc_val, exc_tb):
		if exc_type or exc_val or exc_tb:
			pass
		else:
			self.connection.commit()
		
		self.connection.close()


##### FUNKCJE LOGOWANIA/REJESTRACJI #####
def log_in(credentials):
    global LOGGED_IN, USERNAME 
    authenticator = stauth.Authenticate(credentials, 'translator_cookie', 'translator_signature_key', cookie_expiry_days=7)
    name, auth_status, username = authenticator.login("Login", "main")
    username = username.capitalize()

    if auth_status:
        st.success(f"Zalogowany jako {username}")
        st.sidebar.write(f"Zalogowany jako **{username}**")
        authenticator.logout("Wyloguj", "sidebar")
        USERNAME, LOGGED_IN = username, True
    else:
        if username!='':
            st.error(f"Nieprawidłowe hasło dla użytkownika {username}")
        USERNAME, LOGGED_IN = username, False


def register(usernames):
    with st.form("Rejestracja"):
        st.write("<p style='font-size: 28px;'>Rejestracja</p>", unsafe_allow_html=True)
        username = st.text_input("Nazwa użytkownika")
        password = st.text_input("Hasło", type="password")
        password2 = st.text_input("Powtórz hasło", type="password")
        register = st.form_submit_button("Zarejestruj się")  # Change the button text here
    if register:
        if password != password2:
            st.error("Podane hasła różnią się od siebie")
            st.stop()
        elif username in usernames:
            st.error("Nazwa użytkownika jest już zajęta")
            st.stop()
        else:
            with DatabaseConnection(FILE_PATH) as conn:
                cursor = conn.cursor()
                hashed_password = stauth.Hasher(passwords=[password]).generate()[0]
                cursor.execute(f"INSERT INTO Users (username, hashed_password) VALUES (?, ?)", (username, hashed_password,))
            st.success(f"Rejestracja jako {username} udana. Teraz proszę się zalogować.")

    
def enter(action):
    with DatabaseConnection(FILE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users")
        user_data = cursor.fetchall()
        usernames = [row[0] for row in user_data]
        passwords = [row[1] for row in user_data]

    credentials = {"usernames":{}}
    for un, name, pw in zip(usernames, usernames, passwords):
        user_dict = {"name":name,"password":pw}
        credentials["usernames"].update({un:user_dict})
   
    if action == "Register":
        register(usernames)
    elif action == "Login":
        log_in(credentials)


##### ZAPISYWANIE HISTORII #####
def display_row(h):
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.write(f"{h[0]}")
    with col2:
        st.write(f"{h[4]} → {h[5]}")
    st.success(f"{h[2]} ➡️ {h[3]}")
    st.write("---")


def view_history(username):
    st.header("Historia tłumaczeń")
    st.markdown("---")
    with DatabaseConnection(FILE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM History WHERE username='{username}' ORDER BY ROWID DESC")
        history = cursor.fetchall()
    if len(history)==0:
        st.warning("Brak historii tłumaczeń")
        st.stop()
    for h in history[:3]:
        display_row(h)
    if len(history)>3:
        toggle = tog.st_toggle_switch("Pokaż więcej", active_color="#173928", track_color='#265f42', key="toggle_switch")
        if toggle:
            for h in history[3:]:
                display_row(h)

def save_history(username, transcription, translation, og_lang, output_lang, date):
    with DatabaseConnection(FILE_PATH) as conn:
        cursor = conn.cursor()
        # weryfikacja, czy pojawiło się nowe tłumaczenie
        cursor.execute(f"SELECT transcription, translation FROM History WHERE username='{username}' ORDER BY ROWID DESC LIMIT 1")
        last_row = cursor.fetchone()
        if last_row==None or last_row[0]+last_row[1]!=transcription+translation:
            cursor.execute(f"INSERT INTO History (date, username, transcription, translation, og_lang, output_lang) VALUES (?, ?, ?, ?, ?, ?)",
                        (date, username, transcription, translation, og_lang, output_lang,))


##### FUNKCJE TŁUMACZENIA #####
@st.cache_resource(show_spinner=False)
def load_model():
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    return pipeline("automatic-speech-recognition", model="openai/whisper-tiny", device=device)
pipe = load_model()


@st.cache_data(show_spinner=False)
def transcribe(audio, lang='pl'):
    outputs = pipe(audio, max_new_tokens=256, generate_kwargs={"task": "transcribe", "language": f"{lang}"})
    return outputs["text"]


@st.cache_data(show_spinner=False)
def text2speech(text, language):
    tts = gTTS(text, lang=language)
    audio_stream = BytesIO()
    tts.write_to_fp(audio_stream)
    audio_stream.seek(0)
    return AudioSegment.from_mp3(audio_stream)


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
        st.write('---')
        st.title("Ustawienia językowe")
        og_lang = st.selectbox("Wybierz język wejściowy: ", langdict.keys(), 38)
        output_lang = st.selectbox("Wybierz język wyjściowy:", langdict.keys(), 13)
        st.markdown("---")
        st.write("Tłumacz stworzony przez:")
        st.write("[Aleks Kapich](https://github.com/AKapich)")
        st.write("[Tymoteusz Kwieciński](https://github.com/Fersoil)")
        st.write("[Michał Matejczuk](https://github.com/matejczukm)")
        

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
            transcription = transcribe(wav_audio_data, lang=langdict[og_lang])
            st.write(transcription, unsafe_allow_html=True)
        try:
            st.write(f'**Tłumaczenie na {output_lang.lower()}:**')
            with st.spinner("Tłumaczenie tekstu..."):
                translation = transcribe(wav_audio_data, lang=langdict[output_lang])
                st.write(translation, unsafe_allow_html=True)
                save_history(USERNAME, transcription, translation, og_lang, output_lang, dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                sound = text2speech(translation, langdict[output_lang])

                tmp_filepath = "/tmp/output.wav"
                sound.export(tmp_filepath, format="wav")
                
                if st.button('🔊'):
                    st.audio(tmp_filepath)
        except AssertionError:
            st.error('Nie udało się przetłumaczyć tekstu. Spróbuj ponownie.')



if __name__ == '__main__':
    global LOGGED_IN
    global USERNAME
    LOGGED_IN = False
    USERNAME = None
    tab1, tab2, tab3, tab4 = st.tabs(["🔑 Login", "✍🏻 Rejestracja", "🔊 Tłumacz", "📄 Historia"])

    with tab1:
        enter(action="Login")
    with tab2:
        enter(action="Register")
    with tab3:
        if LOGGED_IN:
            main()
        else:
            st.warning("Proszę zalogować się, aby użyć tłumacza")
    with tab4:
        if LOGGED_IN:
            view_history(USERNAME)
        else:
            st.warning("Proszę zalogować się, aby mieć dostęp do historii")
