import streamlit as st
import random
from gtts import gTTS
import os
import tempfile
import speech_recognition as sr
import logging
import time
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import queue
import threading
import av
import numpy as np
import pydub
import io

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

if 'audio_buffer' not in st.session_state:
    st.session_state.audio_buffer = []

# 음성 처리를 위한 클래스
class AudioProcessor:
    def __init__(self):
        self.audio_buffer = []
        self.recording = False
        self.audio_queue = queue.Queue()

    def process_audio(self, frame):
        if self.recording:
            sound = frame.to_ndarray()
            self.audio_buffer.extend(sound.flatten().tolist())

    def start_recording(self):
        self.recording = True
        self.audio_buffer = []

    def stop_recording(self):
        self.recording = False
        return np.array(self.audio_buffer, dtype=np.int16)

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

# 음성 인식 함수
def process_audio_data(audio_data, sample_rate=16000):
    """음성 데이터를 텍스트로 변환"""
    try:
        # WAV 파일로 변환
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:
            # WAV 파일 생성
            with wave.open(temp_wav.name, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data.tobytes())

            # 음성 인식
            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_wav.name) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio, language='en-US')
                return text.lower()
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        return None
    finally:
        if os.path.exists(temp_wav.name):
            os.unlink(temp_wav.name)

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
st.markdown("Click 'START' to begin recording and 'STOP' when finished.")

audio_processor = AudioProcessor()

def video_frame_callback(frame):
    """비디오 프레임 콜백 (오디오만 사용하므로 빈 프레임 반환)"""
    return frame

def audio_frame_callback(frame):
    """오디오 프레임 콜백"""
    audio_processor.process_audio(frame)
    return frame

# WebRTC 스트리머 설정
ctx = webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SENDONLY,
    audio_receiver_size=1024,
    video_receiver_size=0,
    rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    },
    video_frame_callback=video_frame_callback,
    audio_frame_callback=audio_frame_callback,
    media_stream_constraints={
        "video": False,
        "audio": True,
    },
)

# 녹음 제어
if ctx.state.playing:
    if st.button("Start Recording"):
        audio_processor.start_recording()
        st.session_state.recording = True
        st.info("Recording... Speak now!")

    if st.button("Stop Recording"):
        if hasattr(st.session_state, 'recording') and st.session_state.recording:
            audio_data = audio_processor.stop_recording()
            st.session_state.recording = False
            
            if len(audio_data) > 0:
                # 음성 처리
                transcript = process_audio_data(audio_data)
                
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
                    st.warning("Could not recognize speech. Please try again.")
            else:
                st.warning("No audio recorded. Please try again.")

# 도움말
with st.expander("ℹ️ Tips for better recognition"):
    st.markdown("""
    1. **Speak clearly**: Pronounce each word distinctly
    2. **Proper distance**: Keep your microphone about 6-12 inches from your mouth
    3. **Quiet environment**: Minimize background noise
    4. **Check volume**: Make sure your microphone volume is at an appropriate level
    5. **Browser settings**: 
       - Allow microphone access when prompted
       - Use a modern browser (Chrome recommended)
       - Ensure stable internet connection
    
    If you're having problems:
    - Refresh the page
    - Check microphone permissions
    - Try using a different microphone
    - Clear browser cache
    """)