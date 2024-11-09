import streamlit as st
import random
from gtts import gTTS
import os
import tempfile
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
import numpy as np
import wave
import io
import logging
import time
from pydub import AudioSegment

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

if 'transcript' not in st.session_state:
    st.session_state.transcript = ""

if 'error_count' not in st.session_state:
    st.session_state.error_count = 0

# 오디오 처리 함수
def convert_audio_for_processing(audio_bytes):
    """오디오 데이터를 speech recognition에 적합한 형식으로 변환"""
    try:
        # 오디오 세그먼트로 변환
        audio_segment = AudioSegment.from_file(
            io.BytesIO(audio_bytes),
            format="wav"
        )
        
        # 품질 개선
        audio_segment = audio_segment.set_channels(1)  # 모노로 변환
        audio_segment = audio_segment.set_frame_rate(16000)  # 샘플링 레이트 조정
        
        # 노이즈 감소를 위한 정규화
        audio_segment = audio_segment.normalize()
        
        # WAV 형식으로 변환
        buffer = io.BytesIO()
        audio_segment.export(buffer, format="wav")
        
        return buffer.getvalue()
    except Exception as e:
        logger.error(f"Audio conversion error: {str(e)}")
        return None

def process_audio(audio_bytes, max_retries=3):
    """음성을 텍스트로 변환하는 함수"""
    if audio_bytes is None:
        return None
    
    # 오디오 데이터 변환
    processed_audio = convert_audio_for_processing(audio_bytes)
    if processed_audio is None:
        return None
    
    # 임시 WAV 파일 생성
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:
        temp_wav.write(processed_audio)
        temp_wav_path = temp_wav.name
    
    recognizer = sr.Recognizer()
    
    # 노이즈 처리 설정
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 300
    recognizer.pause_threshold = 0.8
    
    for attempt in range(max_retries):
        try:
            with sr.AudioFile(temp_wav_path) as source:
                # 노이즈 조정
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # 오디오 데이터 읽기
                audio_data = recognizer.record(source)
                
                # 음성 인식 시도
                text = recognizer.recognize_google(
                    audio_data,
                    language='en-US',
                    show_all=False
                )
                return text.lower()
                
        except sr.RequestError as e:
            logger.error(f"API request error (attempt {attempt + 1}): {str(e)}")
            time.sleep(1)  # API 요청 간 대기
            
        except sr.UnknownValueError:
            logger.error(f"Speech not recognized (attempt {attempt + 1})")
            if attempt == max_retries - 1:
                st.warning("Could not recognize speech. Please speak more clearly and try again.")
            
        except Exception as e:
            logger.error(f"Unexpected error (attempt {attempt + 1}): {str(e)}")
            if attempt == max_retries - 1:
                st.error("An error occurred during processing. Please try again.")
            
        finally:
            if attempt == max_retries - 1:
                try:
                    os.unlink(temp_wav_path)
                except Exception as e:
                    logger.error(f"Error removing temporary file: {str(e)}")
    
    return None

# TTS 함수
@st.cache_data
def get_tts_audio(text):
    """텍스트를 음성으로 변환"""
    try:
        tts = gTTS(text=text, lang='en')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            return fp.name
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        return None

# 메인 앱 UI
st.title("English Pronunciation Practice")
st.markdown("---")

# 현재 단어 표시
st.markdown(f'<div class="word-display">{st.session_state.current_word}</div>', unsafe_allow_html=True)

# 발음 듣기 버튼
if st.button("🔊 Listen to Pronunciation"):
    audio_file = get_tts_audio(st.session_state.current_word)
    if audio_file:
        st.audio(audio_file)
        os.unlink(audio_file)
    else:
        st.error("Could not generate pronunciation audio. Please try again.")

# 새로운 단어 선택
if st.button("🔄 New Word"):
    st.session_state.current_word = random.choice(st.session_state.words)
    st.session_state.transcript = ""
    st.experimental_rerun()

# 녹음 섹션
st.markdown("### Record your pronunciation")
st.markdown("Click the microphone button and speak the word clearly.")

audio_bytes = audio_recorder(
    pause_threshold=2.0,
    sample_rate=16000,
    channels=1
)

if audio_bytes:
    with st.spinner("Processing your speech..."):
        # 녹음된 오디오 재생
        st.audio(audio_bytes, format="audio/wav")
        
        # 음성 처리
        transcript = process_audio(audio_bytes)
        
        if transcript:
            st.session_state.transcript = transcript
            st.markdown("### Your pronunciation:")
            st.write(st.session_state.transcript)
            
            if st.session_state.transcript.strip() == st.session_state.current_word:
                st.success("✨ Correct! Well done!")
                st.balloons()
            else:
                st.error(f"Not quite right. Try again! You said: '{st.session_state.transcript}'")
        else:
            st.session_state.error_count += 1
            if st.session_state.error_count >= 3:
                st.error("Having trouble with speech recognition. Please try these tips:")
                st.markdown("""
                    - Speak clearly and at a normal pace
                    - Reduce background noise
                    - Position your microphone closer
                    - Check your microphone settings
                    """)
            else:
                st.warning("Please try speaking again, more clearly.")

# 도움말
with st.expander("ℹ️ Tips for better recognition"):
    st.markdown("""
    1. **Speak clearly**: Pronounce each word distinctly
    2. **Proper distance**: Keep your microphone about 6-12 inches from your mouth
    3. **Quiet environment**: Minimize background noise
    4. **Check volume**: Make sure your microphone volume is at an appropriate level
    5. **Practice timing**: Wait for the recording to start before speaking
    
    If you're having consistent problems:
    - Try refreshing the page
    - Check your browser's microphone permissions
    - Try using a different microphone
    - Ensure you have a stable internet connection
    """)

# 디버그 정보 (개발 중에만 표시)
if st.session_state.get('debug_mode', False):
    with st.expander("🔧 Debug Information"):
        st.write("Error count:", st.session_state.error_count)
        st.write("Current word:", st.session_state.current_word)
        st.write("Last transcript:", st.session_state.transcript)