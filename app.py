import streamlit as st
import random
from gtts import gTTS
import os
import tempfile
import speech_recognition as sr
from io import BytesIO
import base64
import time

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

# TTS 함수
def text_to_speech(text):
    """텍스트를 음성으로 변환하고 base64 인코딩된 문자열 반환"""
    try:
        tts = gTTS(text=text, lang='en')
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_base64 = base64.b64encode(audio_buffer.getvalue()).decode()
        return f'data:audio/mp3;base64,{audio_base64}'
    except Exception as e:
        st.error(f"TTS Error: {str(e)}")
        return None

# HTML 오디오 위젯 생성
def create_audio_widget(audio_base64):
    """HTML 오디오 위젯 생성"""
    audio_html = f"""
        <audio controls>
            <source src="{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
    """
    return audio_html

# 메인 앱 UI
st.title("English Pronunciation Practice")
st.markdown("---")

# 현재 단어 표시
st.markdown(f'<div class="word-display">{st.session_state.current_word}</div>', unsafe_allow_html=True)

# 발음 듣기 버튼
if st.button("🔊 Listen to Pronunciation"):
    audio_base64 = text_to_speech(st.session_state.current_word)
    if audio_base64:
        st.markdown(create_audio_widget(audio_base64), unsafe_allow_html=True)
    else:
        st.error("Could not generate pronunciation audio. Please try again.")

# 새로운 단어 선택
if st.button("🔄 New Word"):
    st.session_state.current_word = random.choice(st.session_state.words)
    st.experimental_rerun()

# 파일 업로더를 통한 음성 입력
st.markdown("### Record your pronunciation")
st.markdown("""
1. Use your phone's voice recorder or computer's audio recorder to record yourself saying the word
2. Save the recording (most audio formats supported)
3. Upload the file below
""")

uploaded_file = st.file_uploader("Upload your pronunciation recording", type=['wav', 'mp3', 'm4a', 'ogg'])

if uploaded_file is not None:
    # 파일 처리
    with st.spinner("Processing your recording..."):
        try:
            # 임시 파일로 저장
            with tempfile.NamedTemporaryFile(delete=False, suffix='.' + uploaded_file.name.split('.')[-1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                audio_path = tmp_file.name

            # 음성 인식
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio = recognizer.record(source)
                try:
                    # 음성을 텍스트로 변환
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
            
            # 임시 파일 삭제
            os.unlink(audio_path)
            
        except Exception as e:
            st.error(f"Error processing audio: {str(e)}")

# 도움말
with st.expander("ℹ️ How to record and upload"):
    st.markdown("""
    #### Recording Options:
    
    1. **Using a Smartphone:**
       - Open your phone's voice recorder app
       - Record yourself saying the word clearly
       - Save the recording
       - Transfer the file to your computer or upload directly from your phone
    
    2. **Using a Computer:**
       - Use the built-in Voice Recorder app (Windows) or QuickTime Player (Mac)
       - Save the recording
       - Upload the file using the uploader above
    
    #### Tips for Better Recognition:
    
    1. **Recording Environment:**
       - Find a quiet place
       - Minimize background noise
       - Avoid echo-prone areas
    
    2. **Recording Technique:**
       - Hold the microphone 6-12 inches from your mouth
       - Speak clearly and at a normal pace
       - Wait a moment before and after speaking
    
    3. **File Format:**
       - Supported formats: WAV, MP3, M4A, OGG
       - WAV format typically works best
       - Keep recordings short (1-2 seconds for single words)
    
    4. **If Recognition Fails:**
       - Try recording again with better audio quality
       - Speak more clearly and slowly
       - Check that the audio file isn't corrupted
       - Try a different recording device
    """)

# 추가 정보
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
<small>Note: This app uses Google Speech Recognition API. 
Internet connection required for speech recognition.</small>
</div>
""", unsafe_allow_html=True)