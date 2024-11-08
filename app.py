# pip install streamlit
# pip install SpeechRecognition
# pip install gtts
# pip install googletrans
# pip install difflib   # 설치 안해도 사용가능
# pip install sounddevice  
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
import random
import time
import difflib
from googletrans import Translator
import sounddevice as sd
import numpy as np


def initialize_session_state():
    """세션 상태 초기화"""
    if 'current_word' not in st.session_state:
        st.session_state.current_word = ''
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'total_attempts' not in st.session_state:
        st.session_state.total_attempts = 0
    if 'selected_gender' not in st.session_state:
        st.session_state.selected_gender = 'Boy'

def get_random_word():
    """무작위 단어 선택"""
    words = [
        "apple", "banana", "orange", "grape", "strawberry",
        "computer", "python", "programming", "artificial", "intelligence",
        "beautiful", "wonderful", "amazing", "fantastic", "excellent"
    ]
    return random.choice(words)

def create_audio(text, gender):
    """텍스트를 음성으로 변환 (성별에 따른 설정 적용)"""
    # 성별에 따른 언어 설정
    if gender == 'Boy':
        tts = gTTS(text=text, lang='en', tld='co.uk')  # 영국 영어 (남성스러운 음색)
    else:
        tts = gTTS(text=text, lang='en', tld='com')    # 미국 영어 (여성스러운 음색)
    
    filename = "word.mp3"
    tts.save(filename)
    return filename


def speech_to_text():  
    """음성을 텍스트로 변환"""  
    r = sr.Recognizer()  

    # 오디오 녹음  
    duration = 5  # 녹음 시간 (초)  
    fs = 44100  # 샘플링 레이트  
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)  
    st.write("말씀해주세요...")  
    sd.wait()  # 녹음 완료까지 기다림  

    # 녹음된 오디오를 텍스트로 변환  
    try:  
        # 오디오 데이터 준비  
        audio_data = recording.flatten()  
        
        # 음성 인식을 위해 int16 형식으로 변환  
        audio_bytes = (audio_data * 32767).astype(np.int16).tobytes()  
        
        # 음성 인식  
        audio_data_for_recognition = sr.AudioData(audio_bytes, fs, 2)  
        # text = r.recognize_google(audio_data_for_recognition, language='ko-KR')
        text = r.recognize_google(audio_data_for_recognition, language='en-US')
        return text.lower()  
        
    except sr.WaitTimeoutError:  
        st.error("음성이 감지되지 않았습니다. 다시 시도해주세요.")  
        return None  
    except sr.UnknownValueError:  
        st.error("음성을 인식할 수 없습니다. 다시 시도해주세요.")  
        return None  
    except sr.RequestError:  
        st.error("음성 인식 서비스에 접근할 수 없습니다.")  
        return None  
    
    
    
        
    

def calculate_similarity(word1, word2):
    """두 단어의 유사도 계산"""
    return difflib.SequenceMatcher(None, word1, word2).ratio()

def get_character_emoji(gender):
    """성별에 따른 이모지 반환"""
    return "👦" if gender == 'Boy' else "👧"

def main():
    # st.title("Word Friends")
    # st.title("AI 친구와 단어를 학습해보세요")
    # st.title("주제를 선택하세요")

    st.write("""  
        <div style='text-align: center;'>  
            <h1>Word Friends</h1>
            <h5>AI 친구와 단어를 학습해보세요</h5>
            </br>
            </br>
            </br>
            <h4>주제를 선택하세요</h4>
        </div>  
        """, unsafe_allow_html=True)
    
            
        
    # 세션 상태 초기화
    initialize_session_state()
    
    
    # 이미지 경로 설정  
    topic_image_paths = {  
        'School': './image/School.png',   # 주제 학교 이미지 경로
        'Family': './image/Family.png',   # 주제 가족 이미지 경로
        'Animals': './image/Animals.png',   # 주제 동물 이미지 경로
        'Weather': './image/Weather.png',   # 주제 날씨 이미지 경로
        'Food': './image/Food.png'   # 주제 음식 이미지 경로
    }  

    
    
    # 선택된 이미지를 저장할 변수 초기화  
    if 'selected_image' not in st.session_state:  
        st.session_state.selected_image = None  

    # 이미지 클릭 이벤트 처리  
    def select_image(image_key):  
        st.session_state.selected_image = image_key  

    col1, col2, col3, col4, col5 = st.columns(5)  

    with col1:  
        if st.button("School"):  
            select_image('School')  
        st.image(topic_image_paths['School'], caption='School', use_column_width=True)  

    with col2:  
        if st.button("Family"):  
            select_image('Family')  
        st.image(topic_image_paths['Family'], caption='Family', use_column_width=True)
        
    with col3:  
        if st.button("Animals"):  
            select_image('Animals')  
        st.image(topic_image_paths['Animals'], caption='Animals', use_column_width=True)  

    with col4:  
        if st.button("Weather"):  
            select_image('Weather')  
        st.image(topic_image_paths['Weather'], caption='Weather', use_column_width=True)
        
    with col5:  
        if st.button("Food"):  
            select_image('Food')  
        st.image(topic_image_paths['Food'], caption='Food', use_column_width=True)  

    # 선택된 이미지 표시  
    if st.session_state.selected_image:  
        st.write(f"Hello {st.session_state.selected_image}")
        



    # 캐릭터 선택
    st.write("""  
    <div style='text-align: center;'>  
        <h4>AI 친구를 선택하세요</h4>
    </div>  
    """, unsafe_allow_html=True)

    # 이미지 경로 설정  
    image_paths = {  
        'Boy': './image/boy.png',   # 남자아이 이미지 경로  
        'Girl': './image/girl.png'   # 여자아이 이미지 경로  
    }  

    
    
    # 선택된 이미지를 저장할 변수 초기화  
    if 'selected_image' not in st.session_state:  
        st.session_state.selected_image = None  

    # 이미지 클릭 이벤트 처리  
    def select_image(image_key):  
        st.session_state.selected_image = image_key  

    col1, col2 = st.columns(2)  

    with col1:  
        if st.button("Boy"):  
            select_image('Boy')  
        st.image(image_paths['Boy'], caption='Boy', use_column_width=True)  

    with col2:  
        if st.button("Girl"):  
            select_image('Girl')  
        st.image(image_paths['Girl'], caption='Girl', use_column_width=True)  

    # 선택된 이미지 표시  
    if st.session_state.selected_image:  
        st.write(f"Hello {st.session_state.selected_image}")

        
                
        
    
            
            


if __name__ == "__main__":
    main()
