# 해당 코드는 streamlit cloud에서 self.get_pyaudio() 와 같은 오류가 발생한다 대안은?


# Claude 3.5 Sonnet
# PyAudio가 Streamlit Cloud에서 문제가 되는 것을 해결하기 위해, 
# 웹 브라우저의 기본 녹음 기능을 사용하는 방식으로 수정하겠습니다. 
# 아래 코드는 JavaScript의 MediaRecorder API를 활용하여 구현한 버전입니다.

# Streamlit Web Speech App
import streamlit as st
import random
from gtts import gTTS
import os
import tempfile
import base64
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from io import BytesIO
import wave

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

# 음성 인식 처리 함수
def process_audio(audio_bytes):
    if audio_bytes is None:
        return None
        
    # WAV 파일 생성
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:
        with wave.open(temp_wav.name, 'wb') as wav_file:
            wav_file.setnchannels(1)  # mono
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(48000)  # sample rate
            wav_file.writeframes(audio_bytes)
        
        # 음성 인식
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(temp_wav.name) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language='en-US')
                return text.lower()
        except Exception as e:
            st.error(f"Error processing audio: {str(e)}")
            return None
        finally:
            os.unlink(temp_wav.name)

# 녹음 섹션
st.markdown("### Record your pronunciation")
audio_bytes = audio_recorder()

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    transcript = process_audio(audio_bytes)
    
    if transcript:
        st.session_state.transcript = transcript
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
    3. Click the microphone button to start recording
    4. Speak the word clearly
    5. Click the microphone button again to stop recording
    6. See if your pronunciation matches the word
    7. Click '🔄 New Word' to practice with a different word
    
    **Note**: Make sure your browser has permission to use the microphone.
    """)


# 그리고 requirements.txt 파일도 다음과 같이 수정해야 합니다:

# requirements.txt
# streamlit
# gTTS
# SpeechRecognition
# audio-recorder-streamlit


# 주요 변경사항:

# PyAudio 대신 audio-recorder-streamlit 라이브러리를 사용합니다.
# 브라우저의 네이티브 오디오 녹음 기능을 활용합니다.
# 녹음된 오디오를 WAV 형식으로 변환하여 처리합니다.
# 사용 방법:

# 위 코드를 app.py로 저장합니다.
# requirements.txt 파일을 생성하고 필요한 패키지를 추가합니다.
# GitHub에 코드를 푸시합니다.
# Streamlit Cloud에서 배포합니다.
# 이 버전의 장점:

# Streamlit Cloud에서 안정적으로 작동합니다.
# PyAudio 종속성 문제가 해결되었습니다.
# 브라우저 네이티브 녹음 기능을 사용하여 더 나은 호환성을 제공합니다.
# 사용자 인터페이스가 더 직관적입니다.
# 주의사항:

# 브라우저의 마이크 접근 권한을 허용해야 합니다.
# 처음 녹음 시 권한 요청이 표시될 수 있습니다.
# 인터넷 연결이 필요합니다.
# 녹음 품질은 사용자의 마이크 품질에 따라 달라질 수 있습니다.
# 이제 이 앱은 Streamlit Cloud에서 문제없이 실행될 것입니다. 
# 사용자는 마이크 버튼을 클릭하여 녹음을 시작하고, 다시 클릭하여 녹음을 중지할 수 있습니다. 
# 녹음된 음성은 자동으로 텍스트로 변환되어 정확도를 확인할 수 있습니다.