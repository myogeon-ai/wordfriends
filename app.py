# 크롬을 이용해서 영어 단어를 제시하고 영어로 음성을 녹음하고 
# 녹음된 내용을 기록해서 출력하려고 하는데 적당한 코드를 작성해줘


# streamlit cloud에서 사용하고 싶어
# Claude 3.5 Sonnet
# Streamlit을 사용하여 비슷한 기능을 구현한 코드를 만들어드리겠습니다. Streamlit Cloud에서 실행할 수 있는 버전입니다.

import streamlit as st
import random
import speech_recognition as sr
from gtts import gTTS
import os
import time
import tempfile

# 페이지 설정
st.set_page_config(page_title="English Pronunciation Practice", layout="centered")

# CSS 스타일 적용
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
    }
    .word-display {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 2rem;
        margin: 1rem 0;
        background-color: #f0f2f6;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 세션 상태 초기화
if 'words' not in st.session_state:
    st.session_state.words = [
        'apple', 'banana', 'chocolate', 'diamond', 'elephant',
        'flower', 'guitar', 'hamburger', 'island', 'jungle',
        'kitchen', 'lemon', 'monkey', 'notebook', 'orange'
    ]

if 'current_word' not in st.session_state:
    st.session_state.current_word = random.choice(st.session_state.words)

if 'transcript' not in st.session_state:
    st.session_state.transcript = ""

# 제목
st.title("English Pronunciation Practice")
st.markdown("---")

# 현재 단어 표시
st.markdown(f'<div class="word-display">{st.session_state.current_word}</div>', unsafe_allow_html=True)

# TTS 함수
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        tts.save(fp.name)
        return fp.name

# 발음 듣기 버튼
if st.button("🔊 Listen to Pronunciation"):
    audio_file = text_to_speech(st.session_state.current_word)
    st.audio(audio_file)
    os.unlink(audio_file)  # 임시 파일 삭제

# 새로운 단어 선택
if st.button("🔄 New Word"):
    st.session_state.current_word = random.choice(st.session_state.words)
    st.session_state.transcript = ""
    st.experimental_rerun()

# 음성 인식 함수
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎤 Listening... Speak now!")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            st.write("Processing...")
            text = r.recognize_google(audio, language='en-US')
            return text.lower()
        except sr.WaitTimeoutError:
            st.error("No speech detected. Please try again.")
            return None
        except sr.UnknownValueError:
            st.error("Could not understand the audio. Please try again.")
            return None
        except sr.RequestError:
            st.error("Could not request results. Check your internet connection.")
            return None

# 녹음 버튼
if st.button("🎤 Start Recording"):
    transcript = speech_to_text()
    if transcript:
        st.session_state.transcript = transcript
        
# 결과 표시
if st.session_state.transcript:
    st.markdown("### Your pronunciation:")
    st.write(st.session_state.transcript)
    
    if st.session_state.transcript.strip() == st.session_state.current_word:
        st.success("✨ Correct! Well done!")
    else:
        st.error("Try again!")

# 도움말 표시
with st.expander("ℹ️ How to use"):
    st.markdown("""
    1. Look at the displayed word
    2. Click '🔊 Listen to Pronunciation' to hear the correct pronunciation
    3. Click '🎤 Start Recording' and speak the word
    4. See if your pronunciation matches the word
    5. Click '🔄 New Word' to practice with a different word
    
    **Note**: Make sure your microphone is connected and working properly.
    """)

# 필요한 requirements.txt 내용 표시
st.sidebar.markdown("### Required packages:")
st.sidebar.code("""
streamlit
SpeechRecognition
gTTS
PyAudio
""")
# 이 코드를 사용하기 위해서는 다음과 같은 설정이 필요합니다:


# 먼저 requirements.txt 파일을 생성하고 다음 내용을 추가합니다:
# requirements.txt
# streamlit  
# SpeechRecognition  
# gTTS  
# PyAudio  
# 위의 Python 코드를 app.py로 저장합니다.



# Streamlit Cloud에 배포하는 방법:

# GitHub에 코드를 푸시합니다
# https://streamlit.io/cloud 에 접속합니다
# GitHub 저장소와 연결하여 앱을 배포합니다
# 이 앱의 주요 기능:

# 영어 단어를 화면에 표시
# TTS를 통해 정확한 발음을 들을 수 있음
# 마이크를 통해 사용자의 발음을 녹음
# 음성을 텍스트로 변환하여 정확도 확인
# 새로운 단어로 변경 가능
# 사용상 주의사항:

# 마이크 접근 권한을 허용해야 합니다
# 인터넷 연결이 필요합니다
# 음성 인식은 영어(en-US)로 설정되어 있습니다
# 조용한 환경에서 사용하는 것이 좋습니다
# 추가 기능:

# 단어 목록은 필요에 따라 수정 가능합니다
# TTS를 통해 정확한 발음을 들을 수 있습니다
# 직관적인 UI로 사용이 쉽습니다
# 결과를 즉시 확인할 수 있습니다
# 이 앱을 Streamlit Cloud에 배포하면 웹 브라우저를 통해 어디서든 접근하여 영어 발음 연습을 할 수 있습니다.

