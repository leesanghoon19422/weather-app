import streamlit as st
import requests
from streamlit_js_eval import get_geolocation

# 1. 페이지 설정 및 스타일 최적화
st.set_page_config(page_title="빛슬 웨더", page_icon="✨", layout="wide")

def apply_custom_style(condition_code):
    # 날씨별 프리미엄 파스텔 그라데이션
    if condition_code == 1000: # Sunny
        grad = "linear-gradient(120deg, #f6d365 0%, #fda085 100%)"
    elif condition_code in [1003, 1006, 1009]: # Cloudy
        grad = "linear-gradient(120deg, #cfd9df 0%, #e2ebf0 100%)"
    elif "rain" in str(condition_code).lower() or "비" in str(condition_code): # Rain
        grad = "linear-gradient(120deg, #89f7fe 0%, #66a6ff 100%)"
    else:
        grad = "linear-gradient(120deg, #dfe9f3 0%, white 100%)"

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700;900&display=swap');
        
        [data-testid="stAppViewContainer"] {{
            font-family: 'Pretendard', sans-serif;
            background: {grad} !important;
            background-attachment: fixed;
        }}

        /* 흰색 공백 제거 및 패딩 최적화 */
        .block-container {{
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            max-width: 1000px;
        }}

        /* 타이틀 중앙 배치 */
        .app-title {{
            text-align: center;
            font-size: 3rem;
            font-weight: 900;
            color: #333;
            margin-bottom: 1.5rem;
            letter-spacing: -1.5px;
        }}

        /* 메인 카드 */
        .main-card {{
            background: rgba(255, 255, 255, 0.65);
            backdrop-filter: blur(20px);
            padding: 40px;
            border-radius: 40px;
            text-align: center;
            box-shadow: 0 15px 35px rgba(0,0,0,0.07);
            margin-bottom: 25px;
            border: 1px solid rgba(255,255,255,0.4);
        }}

        /* 상세 지표 카드 */
        .metric-card {{
            background: white;
            border-radius: 25px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 8px 20px rgba(0,0,0,0.03);
            border: 1px solid #f0f0f0;
        }}

        .temp-val {{ font-size: 85px; font-weight: 900; color: #111; line-height: 1; margin: 10px 0; }}
        .label-text {{ font-size: 14px; color: #888; font-weight: 700; margin-bottom: 5px; }}
        .value-text {{ font-size: 22px; font-weight: 800; color: #222; }}

        /* 시 구절 컨테이너 */
        .poem-box {{
            padding: 60px 20px;
            text-align: center;
            line-height: 2.5;
            color: #333;
            font-size: 1.2rem;
            white-space: pre-line;
            font-weight: 500;
        }}
        
        /* 불필요한 위젯 디자인 제거 (흰색 줄 방지) */
        .stVerticalBlock {{ gap: 0rem; }}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        </style>
        """, unsafe_allow_html=True)

# API 설정
API_KEY = st.secrets["WEATHER_API_KEY"]
BASE_URL = "http://api.weatherapi.com/v1/forecast.json"

# 다국어 데이터 (추천 음료 및 노래까지 포함)
LANG_DATA = {
    "한국어": {
        "app_name": "✨ 빛슬 웨더",
        "loc_label": "위치 설정",
        "humi": "습도", "uv": "자외선", "wind": "풍속", "feels": "체감 온도",
        "ootd": "👔 오늘의 착장", "drink": "🥤 추천 음료", "music": "🎧 추천 음악",
        "ootd_res": "🧥 **트렌치 코트** / 👖 **슬랙스**",
        "drink_hot": "☕ **따뜻한 캐모마일**", "drink_cold": "🥤 **아이스 얼그레이**",
        "music_list": ["Day6 - 한 페이지가 될 수 있게", "아이유 - 밤편지"],
        "p_sunny": """창가에 부서지는 눈부신 윤슬처럼, 오늘 당신의 하루도 환하게 피어나길 바랍니다.
가장 맑은 하늘의 색을 닮은 당신의 미소가 세상을 따뜻하게 비추고 있네요.
햇살 아래 반짝이는 모든 순간들이 당신에게 기분 좋은 선물이 되어줄 거예요.""",
        "p_rain": """낮게 가라앉은 하늘이 건네는 다정한 위로가 창가를 타고 흐르는 날입니다.
토닥토닥 창문을 두드리는 빗소리에 마음의 먼지들을 조용히 씻어내 보세요.
진한 차 한 잔의 온기처럼 당신의 마음도 평온하게 채워지길 소망합니다.""",
        "p_default": """계절이 흐르고 날씨가 모습을 바꾸어도 당신이라는 이름의 반짝임은 시들지 않습니다.
어떤 풍경 속에 있더라도 당신다운 편안함을 잃지 않기를 바랍니다.
오늘도 당신의 아우라는 충분히 완벽합니다."""
    },
    "English": {
        "app_name": "✨ Gleam Weather",
        "loc_label": "Location",
        "humi": "Humidity", "uv": "UV Index", "wind": "Wind", "feels": "Feels Like",
        "ootd": "👔 Daily Style", "drink": "🥤 Recommended Drink", "music": "🎧 Recommended Music",
        "ootd_res": "🧥 **Trench Coat** / 👖 **Slacks**",
        "drink_hot": "☕ **Warm Chamomile Tea**", "drink_cold": "🥤 **Iced Earl Grey**",
        "music_list": ["Day6 - You Were Beautiful", "IU - Through the Night"],
        "p_sunny": """May your day blossom with light, just like the dazzling gleam on the water.
Your smile, reflecting the clearest sky, warms the world around you.
May every shimmering moment under the sun be a beautiful gift for you today.""",
        "p_rain": """The low-hanging sky offers gentle comfort on this rainy day.
Let the rhythm of the raindrops wash away the dust from your heart.
May your soul be filled with peace, like the warmth of a hot cup of tea.""",
        "p_default": """Even as seasons flow and the weather changes, your inner sparkle never fades.
No matter what landscape you are in, I hope you stay true to your comfortable self.
Your aura is already perfect just as it is."""
    }
}

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    sel_lang = st.selectbox("Language / 언어", ["한국어", "English"])

L = LANG_DATA[sel_lang]

# 타이틀 중앙 배치
st.markdown(f'<div class="app-title">{L["app_name"]}</div>', unsafe_allow_html=True)

# 검색 섹션
c_search1, c_search2 = st.columns([1, 2])
with c_search1: 
    loc_data = get_geolocation(component_key="gleam_v12")

with c_search2:
    if sel_lang == "한국어":
        countries = ["현재 위치", "대한민국", "일본", "미국", "직접 입력"]
    else:
        countries = ["Current Location", "South Korea", "Japan", "USA", "Direct Input"]
        
    choice = st.selectbox(L["loc_label"], countries, label_visibility="collapsed")
    mapping = {"대한민국": "Seoul", "South Korea": "Seoul", "일본": "Tokyo", "Japan": "Tokyo", "미국": "New York", "USA": "New York"}

    # --- 들여쓰기 오류 방지 구간 ---
    q = None 

    if "입력" in choice or "Input" in choice:
        user_input = st.text_input("도시 이름을 영어로 입력 후 엔터", "Seoul", key="user_city")
        q = user_input
    elif "현재" in choice or "Current" in choice:
        if loc_data:
            q = f"{loc_data['coords']['latitude']},{loc_data['coords']['longitude']}"
        else:
            q = "Seoul"  # 위치 정보 없을 때 기본값
    else:
        q = mapping.get(choice, "Seoul")


if q:
    res = requests.get(BASE_URL, params={"key": API_KEY, "q": q, "days": 1, "lang": "ko" if sel_lang == "한국어" else "en"}).json()
    
    if "error" not in res:
        curr = res['current']
        location, temp, cond_text = res['location'], curr['temp_c'], curr['condition']['text']
        apply_custom_style(curr['condition']['code'])

        # 메인 카드
        st.markdown(f"""
            <div class="main-card">
                <p style="color:#666; font-weight:700;">📍 {location['name']}, {location['country']}</p>
                <img src="https:{curr['condition']['icon']}" width="130">
                <div class="temp-val">{temp}°</div>
                <p style="font-size: 22px; color: #444; font-weight: 600;">{cond_text}</p>
            </div>
        """, unsafe_allow_html=True)

        # 상세 지표 (풍속, 자외선 등)
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.markdown(f'<div class="metric-card"><div class="label-text">{L["humi"]}</div><div class="value-text">{curr["humidity"]}%</div></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="metric-card"><div class="label-text">{L["feels"]}</div><div class="value-text">{curr["feelslike_c"]}°</div></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="metric-card"><div class="label-text">{L["uv"]}</div><div class="value-text">{curr["uv"]}</div></div>', unsafe_allow_html=True)
        with m4: st.markdown(f'<div class="metric-card"><div class="label-text">{L["wind"]}</div><div class="value-text">{curr["wind_kph"]}kph</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 라이프스타일 추천 (언어별 자동 번역)
        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown(f"#### {L['ootd']}")
            st.info(L["ootd_res"])
        with r2:
            st.markdown(f"#### {L['drink']}")
            drink_res = L["drink_cold"] if temp > 20 else L["drink_hot"]
            st.success(drink_res)
        with r3:
            st.markdown(f"#### {L['music']}")
            with st.expander("🎵 Playlist", expanded=True):
                for song in L["music_list"]:
                    st.write(song)

        # 하단 감성 시
        p_key = "p_sunny" if curr['condition']['code'] == 1000 else ("p_rain" if "비" in cond_text or "Rain" in cond_text else "p_default")
        st.markdown(f'<div class="poem-box">{L[p_key]}</div>', unsafe_allow_html=True)