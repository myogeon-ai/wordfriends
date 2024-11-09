import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import random
from gtts import gTTS
import speech_recognition as sr
import numpy as np
import logging
import av
import queue
import tempfile
import os
from io import BytesIO
import base64

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 페이지 설정
st.set_page_config(
    page_title="Pronunciation Practice",
    page_icon="🎤",
    layout="centered"
)

# 스타일 설정
st.markdown("""
    <style>
    .word-display {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        margin: 20px 0;
        background-color: #f0f2f6;
        border-radius: 10px;
    }
    .stButton button {
        width: 100%;
        margin: 10px 0;
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

if 'audio_buffer' not in st.session_state:
    st.session_state.audio_buffer = []

# TTS 함수
def get_audio_base64(text):
    """텍스트를 음성으로 변환하고 base64로 인코딩"""
    try:
        tts = gTTS(text=text, lang='en')
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_base64 = base64.b64encode(audio_buffer.getvalue()).decode()
        return f'data:audio/mp3;base64,{audio_base64}'
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        return None

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

# 메인 앱
st.title("English Pronunciation Practice")
st.markdown("---")

# 현재 단어 표시
st.markdown(f'<div class="word-display">{st.session_state.current_word}</div>', unsafe_allow_html=True)

# 발음 듣기 버튼
if st.button("🔊 Listen to Pronunciation"):
    audio_base64 = get_audio_base64(st.session_state.current_word)
    if audio_base64:
        st.markdown(f'<audio autoplay controls><source src="{audio_base64}"></audio>', unsafe_allow_html=True)
    else:
        st.error("Could not generate pronunciation audio. Please try again.")

# 새로운 단어 버튼
if st.button("🔄 New Word"):
    st.session_state.current_word = random.choice(st.session_state.words)
    st.experimental_rerun()

# 녹음 섹션
st.markdown("### Record your pronunciation")

audio_processor = AudioProcessor()

def video_frame_callback(frame):
    """비디오 프레임 콜백 (사용하지 않음)"""
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

# 녹음 컨트롤
if ctx.state.playing:
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start Recording"):
            audio_processor.start_recording()
            st.session_state.recording = True
            st.info("Recording... Speak now!")

    with col2:
        if st.button("Stop Recording"):
            if hasattr(st.session_state, 'recording') and st.session_state.recording:
                audio_data = audio_processor.stop_recording()
                st.session_state.recording = False

                if len(audio_data) > 0:
                    # 임시 WAV 파일 생성
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:
                        import wave
                        with wave.open(temp_wav.name, 'wb') as wf:
                            wf.setnchannels(1)
                            wf.setsampwidth(2)
                            wf.setframerate(48000)
                            wf.writeframes(audio_data.tobytes())

                        # 음성 인식
                        try:
                            recognizer = sr.Recognizer()
                            with sr.AudioFile(temp_wav.name) as source:
                                audio = recognizer.record(source)
                                text = recognizer.recognize_google(audio, language='en-US')
                                
                                st.markdown("### Your pronunciation:")
                                st.write(text.lower())
                                
                                if text.lower().strip() == st.session_state.current_word:
                                    st.success("✨ Correct! Well done!")
                                    st.balloons()
                                else:
                                    st.error(f"Not quite right. Try again! You said: '{text.lower()}'")
                        
                        except sr.UnknownValueError:
                            st.warning("Could not understand the audio. Please try again.")
                        except sr.RequestError as e:
                            st.error(f"Could not process the audio. Error: {str(e)}")
                        finally:
                            os.unlink(temp_wav.name)
                else:
                    st.warning("No audio recorded. Please try again.")

# 도움말
with st.expander("ℹ️ Tips for better recognition"):
    st.markdown("""
    1. **Speak clearly**: Pronounce each word distinctly
    2. **Proper distance**: Keep your microphone about 6-12 inches from your mouth
    3. **Quiet environment**: Minimize background noise
    4. **Browser settings**: 
       - Allow microphone access when prompted
       - Use a modern browser (Chrome recommended)
       - Check your microphone settings
    
    If you're having problems:
    - Refresh the page
    - Check microphone permissions
    - Try using a different microphone
    - Ensure you have a stable internet connection
    """)