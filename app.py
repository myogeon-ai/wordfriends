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

        
                
        
    
    # 구분선 추가
    st.markdown("---")
    
    
    st.write("""  
    <div style='text-align: center;'>  
        <h6>듣고 따라 읽기</h6>
        <h2 style='text-align: center; color: rgb(205, 118, 242);'>Listen and Repeat</h2>
        </br>
        <h6>Play 버튼을 눌러 단어를 듣고</h6>
        <h6>Mic 버튼을 눌러 음성을 녹음하세요</h6>
    </div>  
    """, unsafe_allow_html=True)





    # 사이드바에 점수 표시
    st.sidebar.header("점수")
    st.sidebar.write(f"정확도: {st.session_state.score}/{st.session_state.total_attempts if st.session_state.total_attempts > 0 else 1:.2%}")
    
    test = [1, 2, 3, 4, 5]
    for i in test:
        col1, col2 = st.columns([1, 1])
        # 새 단어 받기 버튼
        with col1: 
            st.image(image_paths['Boy'], width=200, caption='Boy')
        with col2: 
            if st.button("PLAY", key="play_button_" + str(i)):
                st.session_state.current_word = get_random_word()
                audio_file = create_audio(st.session_state.current_word, st.session_state.selected_gender)
                
                # 단어와 발음 듣기 버튼 표시
                st.write(f"## 이 단어를 읽어보세요: **{st.session_state.current_word}**")
                st.audio(audio_file)
                
                # 한국어 의미 표시
                translator = Translator()
                try:
                    korean_meaning = translator.translate(st.session_state.current_word, dest='ko').text
                    st.write(f"단어 뜻: {korean_meaning}")
                except:
                    st.write("단어 뜻을 가져올 수 없습니다.")
                
                # 임시 파일 삭제
                os.remove(audio_file)
            
            # 발음 체크 버튼
            if st.button("MIC", key="mic_button_" + str(i)):
                if st.session_state.current_word:
                    spoken_text = speech_to_text()
                    if spoken_text:
                        similarity = calculate_similarity(st.session_state.current_word, spoken_text)
                        st.session_state.total_attempts += 1
                        
                        if similarity > 0.8:
                            st.success(f"정확합니다! (유사도: {similarity:.2%})")
                            st.session_state.score += 1
                            st.balloons()  # 성공시 풍선 효과 추가
                        else:
                            st.error(f"다시 시도해보세요. 인식된 단어: {spoken_text} (유사도: {similarity:.2%})")
                        
                        # 결과 표시
                        st.write(f"당신이 말한 단어: {spoken_text}")
                        st.write(f"목표 단어: {st.session_state.current_word}")
                else:
                    st.warning("먼저 '새 단어 받기' 버튼을 클릭하세요.")
            st.write("")  


    # 도움말
    with st.expander("사용 방법"):
        st.write("""
        1. 상단에서 캐릭터(Boy/Girl)를 선택하세요.
        2. '새 단어 받기' 버튼을 클릭하여 새로운 단어를 받습니다.
        3. 단어의 발음을 들어보려면 재생 버튼을 클릭하세요.
        4. '발음 체크하기' 버튼을 클릭하고 단어를 말해보세요.
        5. 결과를 확인하고 점수를 높여보세요!
        """)

if __name__ == "__main__":
    main()
