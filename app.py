import streamlit as st
from audio_recorder_streamlit import audio_recorder
import random
from gtts import gTTS
import os
import tempfile
import speech_recognition as sr
from io import BytesIO
import base64
import wave
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 페이지 설정
st.set_page_config(page_title="English Pronunciation Practice", layout="centered")

# CSS 스타일
st.markdown("""
    <style>
    .main { padding: 2rem; }
    .word-display {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 2rem;
        margin: 1rem 0;
        background-color: #f0f2f6;
        border-radius: 10px;
    }
    .status-area {
        margin: 1rem 0;
        padding: 1rem;
        border-radius: 5px;
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

if 'error_count' not in st.session_state:
    st.session_state.error_count = 0

# TTS 함수
@st.cache_data
def get_tts_audio(text):
    """텍스트를 음성으로 변환하고 base64 인코딩된 문자열 반환"""
    try:
        tts = gTTS(text=text, lang='en')
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_base64 = base64.b64encode(audio_buffer.getvalue()).decode()
        return f'data:audio/mp3;base64,{audio_base64}'
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        return None

def process_audio(audio_bytes):
    """오디오 바이트를 처리하여 텍스트로 변환"""
    try:
        # 임시 WAV 파일 생성
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:
            temp_wav_path = temp_wav.name
            # WAV 파일로 저장
            with wave.open(temp_wav_path, 'wb') as wav_file:
                wav_file.setnchannels(1)  # 모노
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(44100)  # 샘플레이트
                wav_file.writeframes(audio_bytes)

            # 음성 인식
            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_wav_path) as source:
                audio = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio, language='en-US')
                    return text.lower()
                except sr.UnknownValueError:
                    logger.warning("Speech not recognized")
                    return None
                except sr.RequestError as e:
                    logger.error(f"Could not request results: {str(e)}")
                    return None
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        return None
    finally:
        # 임시 파일 삭제
        try:
            os.unlink(temp_wav_path)
        except Exception as e:
            logger.error(f"Error removing temporary file: {str(e)}")

# 메인 앱 UI
st.title("English Pronunciation Practice")
st.markdown("---")

# 현재 단어 표시
st.markdown(f'<div class="word-display">{st.session_state.current_word}</div>', unsafe_allow_html=True)

# 발음 듣기 버튼
if st.button("🔊 Listen to Pronunciation"):
    audio_base64 = get_tts_audio(st.session_state.current_word)
    if audio_base64:
        st.markdown(f'<audio autoplay controls><source src="{audio_base64}"></audio>', unsafe_allow_html=True)
    else:
        st.error("Could not generate pronunciation audio. Please try again.")

# 새로운 단어 선택
if st.button("🔄 New Word"):
    st.session_state.current_word = random.choice(st.session_state.words)
    st.session_state.error_count = 0
    st.experimental_rerun()

# 녹음 섹션
st.markdown("### Record your pronunciation")
st.markdown("Click the microphone button and speak the word clearly.")

# 오디오 녹음기 설정
audio_bytes = audio_recorder(
    pause_threshold=2.0,
    sample_rate=44100,
    channels=1
)

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    
    with st.spinner("Processing your speech..."):
        transcript = process_audio(audio_bytes)
        
        if transcript:
            st.markdown("### Your pronunciation:")
            st.write(transcript)
            
            if transcript.strip() == st.session_state.current_word:
                st.success("✨ Correct! Well done!")
                st.balloons()
            else:
                st.error(f"Not quite right. Try again! You said: '{transcript}'")
                st.session_state.error_count += 1
        else:
            st.warning("Could not recognize speech. Please try again.")
            st.session_state.error_count += 1

# 도움말 표시
with st.expander("ℹ️ Tips for better recognition"):
    st.markdown("""
    1. **Speak clearly**: Pronounce each word distinctly
    2. **Proper distance**: Keep your microphone about 6-12 inches from your mouth
    3. **Quiet environment**: Minimize background noise
    4. **Check volume**: Make sure your microphone volume is at an appropriate level
    5. **Timing**: 
       - Wait a moment after clicking the record button
       - Speak when you see the recording indicator
       - The recording will automatically stop after you finish speaking
    
    If you're having problems:
    - Make sure your browser has permission to use the microphone
    - Try using a different microphone
    - Refresh the page if the recorder isn't working
    - Speak at a normal pace and volume
    """)

# 문제 해결 팁 (에러가 많을 경우)
if st.session_state.error_count >= 3:
    st.error("Having trouble with speech recognition? Try these tips:")
    st.markdown("""
    1. Speak more slowly and clearly
    2. Reduce background noise
    3. Move closer to your microphone
    4. Check your microphone settings
    5. Try refreshing the page
    """)