# pip install streamlit pandas pydeck wordcloud matplotlib

import streamlit as st  # Streamlit 라이브러리 (웹 앱 프레임워크)
import pandas as pd     # Pandas 라이브러리 (데이터 처리 및 분석)
import pydeck as pdk    # Pydeck 라이브러리 (지도 시각화)
from datetime import datetime # datetime 모듈 (타임스탬프 기록용)
import os               # os 모듈 (파일 존재 여부 확인용)
import time             # time 모듈 (잠시 멈춤 기능용)
import csv              # CSV quoting 처리를 위한 모듈

# <--- 워드 클라우드 기능 추가 및 Matplotlib 폰트 등록을 위한 라이브러리
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib import font_manager
import re
# <--- 여기까지 수정

# ---------------------------------
# 페이지 설정 및 테마
# ---------------------------------
st.set_page_config(
    layout="wide", page_title="KUSIS", page_icon="🗺️", initial_sidebar_state="expanded"
)

# --- 커스텀 CSS --- (테이블 헤더 색상 수정 포함)
custom_css = """
<style>
    /* 1. 기본 배경 및 폰트 설정 (가장 상위 요소에 적용) */
    .stApp, .stApp > div, [data-testid="stAppViewContainer"] {
        background: #FFFFFF !important; 
    }
    body, .stApp, [class*="st-"] { 
        color: #1a1a1a; 
    }
    html, body, [class*="st-"] { 
        font-size: 16px; 
    }
    /* 2. 사이드바 스타일 */
    [data-testid="stSidebar"] { 
        background-color:#F0F8F0; 
        border-right: 2px solid #D0E0D0; 
    }
    /* 3. 제목 및 헤더 스타일 (건국대 녹색) */
    h1, h2, h3, h4, h5, h6 { 
        color: #027529 !important; 
    }
    /* 4. 버튼 스타일 */
    .stButton>button { 
        background-color: white; 
        color: #027529 !important; 
        border: 2px solid #027529 !important; 
    }
    .stButton>button:hover { 
        background-color: #027529; 
        color: white !important; 
    }
    /* 5. 라디오 버튼 (가게 선택) 스타일 */
    .stRadio [role="radio"] { 
        border: 1px solid #e0e0e0; 
        padding: 10px; 
        border-radius: 8px; 
        margin-bottom: 5px; 
    }
    /* 선택된 라디오 버튼의 스타일 */
    .st-emotion-cache-1y4p8pa { 
        background-color: #E8F5E9; 
        border: 2px solid #027529; 
    }
    /* 6. 정보/경고 상자 스타일 */
    [data-testid="stInfo"] { 
        background-color: #E8F5E9; 
        border-left: 5px solid #027529; 
        color: #1a1a1a; 
    }
    [data-testid="stWarning"] { 
        background-color: #FFF3CD; 
        border-left: 5px solid #FFC107; 
        color: #1a1a1a; 
    }
    /* 7. 텍스트 입력창 스타일 */
    div[data-baseweb="input"] > div > input,
    div[data-baseweb="input"] > div > textarea {
        background-color: #FFFFFF !important; 
        color: #1a1a1a !important; 
        border: 1px solid #D0E0D0 !important; 
        border-radius: 5px;
    }
    /* 8. 관리자 페이지 차트 스타일 */
    .stApp [data-testid="stArrowVegaLiteChart"],
    .stApp [data-testid="stArrowVegaLiteChart"] div,
    .stApp [data-testid="stArrowVegaLiteChart"] svg {
        background-color: transparent !important;
    }
    .stApp [data-testid="stArrowVegaLiteChart"] text {
        fill: #1a1a1a !important;
    }
    .stApp [data-testid="stArrowVegaLiteChart"] line,
    .stApp [data-testid="stArrowVegaLiteChart"] path {
        stroke: #d0d0d0 !important;
    }
    /* 9. 관리자 페이지 표(DataFrame) 스타일 (헤더를 순수 흰색으로 변경) */
    .stApp [data-testid="stDataFrame"],
    .stApp [data-testid="stDataFrame"] > div,
    .stApp [data-testid="stDataFrame"] .glide-data-grid {
        background-color: #FFFFFF !important;
    }
    /* 데이터프레임 헤더 배경을 순수 흰색으로 강제 적용 */
    .stApp [data-testid="stDataFrame"] .glide-data-grid-header,
    .stApp [data-testid="stDataFrame"] .glide-data-grid-header-cell {
        background-color: #FFFFFF !important; 
        color: #027529 !important; 
    }
    .stApp [data-testid="stDataFrame"] .glide-data-grid-cell {
        background-color: #FFFFFF !important; 
        color: #1a1a1a !important; 
        border-color: #F0F2F6 !important; 
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# ---------------------------------
# 데이터 로딩 및 유틸리티 함수
# ---------------------------------
LOG_FILE = 'click_log.csv'
FEEDBACK_FILE = 'feedback.csv'

def log_click(log_type, value):
    """사용자 클릭 로그를 CSV 파일에 기록(추가)하는 함수"""
    if not os.path.exists(LOG_FILE):
        pd.DataFrame(columns=['timestamp', 'type', 'value']).to_csv(LOG_FILE, index=False)
    new_log = pd.DataFrame({'timestamp': [datetime.now()], 'type': [log_type], 'value': [value]})
    new_log.to_csv(LOG_FILE, mode='a', header=False, index=False)

def save_feedback(store_name, rating, review):
    """사용자 피드백(가게 이름, 별점, 리뷰)을 CSV 파일에 기록(추가)하는 함수"""
    if not os.path.exists(FEEDBACK_FILE):
        pd.DataFrame(columns=['timestamp', 'store_name', 'rating', 'review']).to_csv(FEEDBACK_FILE, index=False)
    new_feedback = pd.DataFrame({'timestamp': [datetime.now()], 'store_name': [store_name], 'rating': [rating], 'review': [review]})
    new_feedback.to_csv(FEEDBACK_FILE, mode='a', header=False, index=False)

def get_star_rating(rating):
    """숫자 평점을 별 이모지 문자열로 변환하는 함수"""
    if pd.isna(rating): return "평점 없음"
    rating = round(rating)
    stars = "⭐" * rating + "☆" * (5 - rating)
    return stars

# @st.cache_data를 사용하여 캐싱 (성능 향상)
@st.cache_data
def load_data_and_calculate_stats(filepath, feedback_filepath, log_filepath):
    """메인 데이터와 통계 데이터를 로드 및 병합하는 함수"""
    try:
        data = pd.read_csv(filepath)
        data.dropna(subset=['lat', 'lon'], inplace=True)
        data.rename(columns={"카테코리(대)": "카테고리(대)", "카테고리(중)": "카테고리(중)"}, inplace=True)
        data['카테고리(대)'] = data['카테고리(대)'].fillna('기타')
        data['카테고리(중)'] = data['카테고리(중)'].fillna('기타')
    except FileNotFoundError:
        st.error(f"❌ 데이터 파일('{filepath}')을 찾을 수 없습니다. 'data_ver2.csv' 파일이 있는지 확인해주세요.")
        return pd.DataFrame()

    # 1. 피드백 통계 계산 (평균별점, 리뷰수)
    try:
        # CSV 파싱 오류 방지를 위해 engine='python' 사용
        feedback_df = pd.read_csv(feedback_filepath, engine='python')
        
        # 'rating' 컬럼을 숫자로 명시적으로 변환 (TypeError 방지)
        feedback_df['rating'] = pd.to_numeric(feedback_df['rating'], errors='coerce') 
        
        feedback_stats = feedback_df.groupby('store_name')['rating'].agg(['mean', 'count']).rename(columns={'mean': '평균별점', 'count': '리뷰수'}).round(1)
        feedback_stats.reset_index(inplace=True)
        feedback_stats.rename(columns={'store_name': '가게이름'}, inplace=True)
    except FileNotFoundError:
        feedback_stats = pd.DataFrame({'가게이름': [], '평균별점': [], '리뷰수': []})
    
    # 2. 클릭 로그 통계 계산 (조회수)
    try:
        log_df = pd.read_csv(log_filepath)
        store_clicks = log_df[log_df['type'] == 'store_view']['value'].value_counts().rename('조회수')
        store_clicks = store_clicks.to_frame().reset_index()
        store_clicks.columns = ['가게이름', '조회수']
    except FileNotFoundError:
        store_clicks = pd.DataFrame({'가게이름': [], '조회수': []})

    # 3. 모든 통계 데이터를 메인 데이터와 병합
    data = pd.merge(data, feedback_stats, on='가게이름', how='left')
    data = pd.merge(data, store_clicks, on='가게이름', how='left')
    data['평균별점'] = data['평균별점'].fillna(0.0)
    data['리뷰수'] = data['리뷰수'].fillna(0).astype(int)
    data['조회수'] = data['조회수'].fillna(0).astype(int)

    return data

# 통계가 추가된 데이터프레임 로드
df_with_stats = load_data_and_calculate_stats('data_ver2.csv', FEEDBACK_FILE, LOG_FILE)


@st.cache_resource 
def generate_word_cloud(review_texts, title="리뷰 기반 워드 클라우드"):
    """제공된 리뷰 텍스트를 기반으로 워드 클라우드를 생성하고 Streamlit에 표시"""
    
    # NameError 수정: 텍스트 전처리 로직 복구
    text = " ".join(review_texts.astype(str))
    text = re.sub('[^가-힣a-zA-Z0-9\s]', '', text) 
    
    if not text.strip():
        st.info("워드 클라우드를 생성할 리뷰 텍스트가 부족합니다.")
        return

    stop_words = set(['합니다', '입니다', '했어요', '좋아요', '있습니다', '아니요', '해요', '하세요', '이다', '이예요', '합니다', '했습니다', '이에요', '않습니다', '같습니다', '아닙니다', '최고', '맛있음'])
    
    # --- 폰트 경로 탐색 및 안정화 ---
    font_filename = 'NanumGothic.ttf'
    
    # 1. 현재 작업 디렉토리를 기준으로 절대 경로를 생성합니다.
    current_dir = os.getcwd()
    font_path = os.path.join(current_dir, font_filename)
    
    # 2. 폰트 파일을 찾지 못했을 경우 Windows 기본 폰트를 시도합니다.
    if not os.path.exists(font_path):
        system_font_path = 'c:/Windows/Fonts/malgun.ttf'
        if os.path.exists(system_font_path):
            font_path = system_font_path
        else:
            # 최종적으로 폰트를 찾지 못했을 경우
            font_path = None 
            st.warning(f"❌ '{font_filename}' (NanumGothic) 폰트 파일을 찾을 수 없습니다. 한글이 깨지는 원인입니다.")

    # 3. WordCloud 생성
    wc = WordCloud(
        font_path=font_path, # 설정된 폰트 경로 사용
        width=800,
        height=400,
        background_color='white',
        max_words=100,
        min_font_size=10,
        colormap='summer',
        stopwords=stop_words
    ).generate(text)

    # 4. Matplotlib 폰트 객체 생성 및 제목에 직접 전달 (오류 및 깨짐 방지)
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    
    if font_path is not None:
        try:
            font_prop = font_manager.FontProperties(fname=font_path)
            ax.set_title(title, fontsize=16, fontproperties=font_prop)
        except Exception as e:
            ax.set_title(title, fontsize=16)
    else:
        ax.set_title(title, fontsize=16)

    st.pyplot(fig)


def get_sub_category_stats(major_cat):
    """특정 대분류 내 모든 소분류의 통계 요약을 계산하여 반환"""
    
    # 1. 대분류로 필터링
    filtered_df = df_with_stats[df_with_stats['카테고리(대)'] == major_cat]
    
    # 2. 소분류별 통계 집계
    sub_stats = filtered_df.groupby('카테고리(중)').agg(
        총_가게수=('가게이름', 'count'),
        평균_별점=('평균별점', 'mean'),
        총_리뷰수=('리뷰수', 'sum'),
        총_조회수=('조회수', 'sum')
    ).round({'평균_별점': 1}).reset_index()
    
    return sub_stats


# --- Streamlit 세션 상태(Session State) 초기화 ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

for key in ['ranking_filter_major', 'ranking_filter_sub', 'selected_store', 'show_my_location', 'admin_login', 'current_radio_selection']:
        if key not in st.session_state:
            st.session_state[key] = None if 'filter' in key or 'store' in key or 'selection' in key else False

# ---------------------------------
# 페이지 렌더링 함수 정의
# ---------------------------------

def render_home_page():
    """Step 1: 대분류 선택 페이지"""
    
    # --- 수정: 상단 레이아웃을 컬럼으로 배치 (KUSIS | 공간 | 로고) ---
    col_title, col_space, col_logo = st.columns([4, 1, 1])
    with col_title:
        st.title("KUSIS 🗺️")
        st.subheader("건국대학교 제휴 업체 통합 시스템")
    with col_logo:
        # 기존 로고 이미지 사용 (크기 조정)
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRThQm-lBCaSh19o2WZeEgcf7s5rcdItlYYUw&s", width=80) 
    # --- 수정 끝 ---
    
    st.markdown("---")
    
    # ---------------------------------------------
    # 1. CATEGORY SELECTION (맨 위로 이동)
    # ---------------------------------------------
    st.header("1. 원하는 제휴 카테고리를 선택하세요.")
    
    if not df_with_stats.empty:
        major_categories = df_with_stats['카테고리(대)'].unique()
        major_cols = st.columns(len(major_categories))
        
        for i, major_cat in enumerate(major_categories):
            if major_cols[i].button(major_cat, width='stretch'):
                log_click('major_category', major_cat)
                
                # 대분류 클릭 시 SubCategorySummary 페이지로 이동
                st.session_state.ranking_filter_major = major_cat 
                st.session_state.ranking_filter_sub = None
                st.session_state.page = 'sub_category_summary'
                st.rerun()

    st.markdown("---")

    # ---------------------------------------------
    # 2. TODAY'S RECOMMENDATION (중간에 위치)
    # ---------------------------------------------
    st.header("✨ 오늘의 추천 제휴업체")
    
    if not df_with_stats.empty:
        df_temp = df_with_stats.copy()
        
        # 순위 점수 계산: (평균 별점 * 10) + (총 리뷰 수 * 1) + (총 조회 수 * 0.05)
        df_temp['Rank_Score'] = (df_temp['평균별점'] * 10) + (df_temp['리뷰수']) + (df_temp['조회수'] * 0.05)
        
        top_3_stores = df_temp.sort_values(by='Rank_Score', ascending=False).head(3)
        
        if not top_3_stores.empty:
            top_cols = st.columns(3)
            
            # --- iterrows()를 사용하며 브라켓 접근으로 변경 (AttributeError 해결) ---
            for i, (idx, row) in enumerate(top_3_stores.iterrows()):
                with top_cols[i]:
                    st.markdown(f"### {i+1}위. {row['가게이름']}")
                    st.markdown(f"**카테고리:** {row['카테고리(중)']}") 
                    st.markdown(f"**평점:** ⭐ {row['평균별점']:.1f}/5.0 (총 {row['리뷰수']} 리뷰)")
                    # 혜택 정보를 50자만 표시
                    st.markdown(f"**혜택:** {row['benefit'][:50]}...")
                    
                    # 버튼을 눌러 상세 페이지로 이동
                    if st.button("상세 정보 보기", key=f"rec_store_{i}", width='stretch'):
                        st.session_state.selected_store = row['가게이름']
                        st.session_state.page = 'store_detail_map'
                        st.rerun()
            # --- 수정 끝 ---

    st.markdown("---")
    
    # ---------------------------------------------
    # 3. ADMIN BUTTON (맨 아래로 숨김)
    # ---------------------------------------------
    if st.button("📈 관리자 페이지로 이동", width='stretch'):
        st.session_state.page = 'admin_login'
        st.rerun()


def render_sub_category_summary():
    """Step 2: 대분류 내 소분류 목록 및 요약 리뷰 정보 페이지"""
    
    current_major = st.session_state.ranking_filter_major
    
    st.title(f"'{current_major}' 카테고리 분석")
    st.markdown("---")
    
    # 버튼 섹션
    col_home, col_admin = st.columns(2)
    with col_home:
        # ⚠️ use_container_width=True -> width='stretch'
        if st.button("🏠 홈으로 돌아가기 (대분류 선택)", width='stretch'):
            st.session_state.ranking_filter_major = None
            st.session_state.ranking_filter_sub = None
            st.session_state.page = 'home'
            st.rerun()
    with col_admin:
        if st.button("📈 관리자 페이지로 이동"):
            st.session_state.page = 'admin_login'
            st.rerun()
            
    st.markdown("---")
    
    # --- 2. 소분류 카테고리 정보 확인 ---
    st.header(f"2. '{current_major}'의 소분류 카테고리 정보를 확인하세요.")
    
    if not df_with_stats.empty and current_major:
        
        sub_stats_df = get_sub_category_stats(current_major)
        
        if not sub_stats_df.empty:
            
            # 테이블 컬럼 이름 정의 (DF는 수정 로직 마지막에 출력)
            display_df = sub_stats_df.rename(columns={
                '카테고리(중)': '소분류',
                '총_가게수': '가게 수',
                '평균_별점': '평균 별점',
                '총_리뷰수': '총 리뷰 수',
                '총_조회수': '총 조회 수'
            })
            
            st.markdown("---")
            # --- 3. 상세 가게 목록 선택 ---
            st.header("3. 상세 가게 목록을 볼 소분류를 선택하세요.")
            
            # 소분류 목록을 3열로 배치하고 버튼을 표시합니다.
            sub_categories = sub_stats_df['카테고리(중)'].tolist()
            sub_cols = st.columns(3) 

            for i, sub_cat in enumerate(sub_categories):
                if sub_cols[i % 3].button(sub_cat, key=f"sub_summary_{sub_cat}", width='stretch'):
                    log_click('sub_category', sub_cat)
                    
                    st.session_state.ranking_filter_sub = sub_cat
                    st.session_state.page = 'store_list_view'
                    st.rerun()

            # ----------------------------------------------------
            # ✅ 수정된 부분: 요약 통계 표를 모든 버튼 아래에 배치
            # ----------------------------------------------------
            st.markdown("---")
            st.subheader("소분류별 요약 통계") # 글씨가 표 바로 위에 오도록 조정
            st.dataframe(display_df, use_container_width=True) # 표 (화이트 테마)
            # ----------------------------------------------------

        else:
            st.warning(f"'{current_major}' 카테고리에 해당하는 소분류 데이터가 없습니다.")        
            
def render_store_list_view():
    """Step 3: 소분류 내 전체 가게 목록 및 랭킹 정보 페이지 (구: ranking_view)"""
    
    current_major = st.session_state.ranking_filter_major
    current_sub = st.session_state.ranking_filter_sub
    
    st.title(f"'{current_major}' > '{current_sub}' 전체 가게 목록")
    st.markdown("---")
    
    # --- 사이드바 UI 구성 (내 위치 표시 버튼 추가) ---
    with st.sidebar:
        st.image("https://www.konkuk.ac.kr/img/logo_ku.png", width=120)
        st.title("KUSIS 🗺️")
        st.markdown("---")
        
        # 홈/뒤로가기 버튼은 여기에 배치하지 않고 메인 화면에만 둡니다. (가독성 목적)
        
        # 📍 내 위치 표시/숨기기 버튼 추가
        if st.button("📍 내 위치 표시/숨기기"):
            st.session_state.show_my_location = not st.session_state.show_my_location
            st.rerun() # 지도 상태 변경 시 재실행

        st.markdown("---")
        st.metric(label="선택된 카테고리", value=current_sub)
        
    # --- 메인 화면 버튼 섹션 ---
    col_back, col_admin = st.columns(2)
    with col_back:
        if st.button("⬅️ 소분류 요약으로 돌아가기", width='stretch'):
            st.session_state.ranking_filter_sub = None
            st.session_state.page = 'sub_category_summary'
            st.rerun()
    with col_admin:
        if st.button("📈 관리자 페이지로 이동"):
            st.session_state.page = 'admin_login'
            st.rerun()
            
    st.markdown("---")

    if not df_with_stats.empty and current_sub:
        
        filtered_df = df_with_stats[df_with_stats['카테고리(중)'] == current_sub].copy()
        
        ranking_df = filtered_df.sort_values(by=['조회수', '리뷰수'], ascending=[False, False])
        
        st.header(f"🔎 총 {len(ranking_df)}개 가게 목록 (조회수 기준 정렬)")

        # --- 지도 시각화 추가 및 내 위치 레이어 포함 ---
        if not filtered_df.empty:
            st.subheader(f"🗺️ '{current_sub}' 지역 지도")
            
            center_lat = filtered_df['lat'].mean()
            center_lon = filtered_df['lon'].mean()
            
            view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=14.5, pitch=20)
            
            store_layer = pdk.Layer(
                'ScatterplotLayer', data=filtered_df, get_position='[lon, lat]', 
                get_color='[2, 117, 41, 200]', get_radius=50, pickable=True, auto_highlight=True
            )
            
            layers = [store_layer]
            
            # 내 위치 레이어 (요청 추가)
            if st.session_state.show_my_location:
                my_location_data = pd.DataFrame({'lat': [37.544357], 'lon': [127.075985]})
                blue_layer = pdk.Layer(
                    'ScatterplotLayer', data=my_location_data, get_position='[lon, lat]', 
                    get_color='[30, 100, 220, 255]', get_radius=50, pickable=True
                )
                layers.append(blue_layer)
            
            tooltip = {"html": "<b>{가게이름}</b><br/>⭐ {평균별점}", "style": {"backgroundColor": "#027529", "color": "white"}}

            st.pydeck_chart(pdk.Deck(
                layers=layers, initial_view_state=view_state, map_style='light', tooltip=tooltip
            ))
        # --- 지도 시각화 끝 ---

        display_columns = ['가게이름', '평균별점', '리뷰수', '조회수', 'benefit']
        display_df = ranking_df[display_columns].reset_index(drop=True)
        display_df.index = display_df.index + 1 
        display_df.index.name = '순위'
        display_df.rename(columns={'benefit': '제휴 혜택'}, inplace=True)

        st.subheader("💡 상세 정보를 볼 가게를 선택하세요.")
        
        options_with_stats = []
        for rank_num, row in display_df.iterrows():
            display_name = f"{row.name}위 | {row['가게이름']} ⭐ {row['평균별점']:.1f}/5.0 ({row['리뷰수']})"
            options_with_stats.append({'display': display_name, 'value': row['가게이름']})
            
        display_options = [opt['display'] for opt in options_with_stats]
        actual_values = [opt['value'] for opt in options_with_stats]
        
        # --- ValueError 해결 및 선택 값 설정 ---
        # 1. 초기값 또는 이전에 선택된 값의 인덱스를 찾습니다.
        initial_store_name = st.session_state.current_radio_selection if 'current_radio_selection' in st.session_state else (actual_values[0] if actual_values else None)
        
        index_to_set = 0
        if initial_store_name and initial_store_name in actual_values:
            # ✅ 수정된 로직: 실제 가게 이름 목록(actual_values)에서 인덱스를 찾습니다.
            index_to_set = actual_values.index(initial_store_name) 

        # st.radio 생성
        selected_display = st.radio(
            "가게 선택", 
            options=display_options,
            index=index_to_set, # 설정된 인덱스 사용
            key='store_list_radio'
        )
        
        # 선택된 가게 이름을 실제 값으로 매핑
        selected_store_name = actual_values[display_options.index(selected_display)] if selected_display in display_options else None
        
        # --- 원클릭 전환 로직 ---
        # 선택된 가게 이름을 세션 상태에 저장하고, 변경 사항이 있으면 상세 페이지로 전환합니다.
        if selected_store_name and st.session_state.current_radio_selection != selected_store_name:
            log_click('store_view', selected_store_name)
            st.session_state.selected_store = selected_store_name
            st.session_state.page = 'store_detail_map'
            st.session_state.current_radio_selection = selected_store_name
            st.rerun()

        st.markdown("---")
        st.subheader("순위표")
        st.dataframe(display_df, use_container_width=True) 

    else:
        st.warning("잘못된 접근입니다. 홈으로 돌아가십시오.")

def render_store_detail_map():
    """Step 4: 가게 상세 정보 및 지도/워드 클라우드 페이지 (구: map_view)"""
    
    current_store_name = st.session_state.selected_store
    
    # --- 사이드바 UI 구성 ---
    with st.sidebar:
        st.image("https://www.konkuk.ac.kr/img/logo_ku.png", width=120)
        st.title("KUSIS 🗺️")
        st.markdown("---")
        
        # ⚠️ use_container_width=True -> width='stretch'
        if st.button("🏠 홈으로 돌아가기", width='stretch'):
            st.session_state.ranking_filter_major = None
            st.session_state.ranking_filter_sub = None
            st.session_state.selected_store = None
            st.session_state.page = 'home'
            st.rerun()
        
        if st.button("⬅️ 가게 목록으로 돌아가기"):
            st.session_state.selected_store = None
            st.session_state.page = 'store_list_view'
            st.rerun()
        
        if st.button("📈 관리자 페이지로 이동"):
            st.session_state.page = 'admin_login'
            st.rerun()

        st.metric(label="현재 가게", value=current_store_name)
        
        if st.button("📍 내 위치 표시/숨기기"):
            st.session_state.show_my_location = not st.session_state.show_my_location
            
    # --- 데이터 필터링 로직 ---
    if not df_with_stats.empty and current_store_name:
        filtered_df = df_with_stats[df_with_stats['가게이름'] == current_store_name]
    else:
        st.warning("오류가 발생했습니다. 이전 화면으로 돌아가 다시 시도해주세요.")
        return

    selected_details = filtered_df.iloc[0]
    
    # 지도 구성
    if not filtered_df.empty:
        view_state = pdk.ViewState(latitude=selected_details['lat'], longitude=selected_details['lon'], zoom=16, pitch=50)
        
        # ✅ 수정: get_radius를 60에서 40으로 축소
        red_layer = pdk.Layer(
            'ScatterplotLayer', data=filtered_df, get_position='[lon, lat]', 
            get_color='[220, 30, 30, 255]', get_radius=20, pickable=True, auto_highlight=True)
        
        my_location_data = pd.DataFrame({'lat': [37.544357], 'lon': [127.075985]})
        blue_layer = pdk.Layer(
            'ScatterplotLayer', data=my_location_data, get_position='[lon, lat]', 
            get_color='[30, 100, 220, 255]', get_radius=20, pickable=True)
        
        layers = [red_layer]
        if st.session_state.show_my_location:
            layers.append(blue_layer)
        
        st.pydeck_chart(pdk.Deck(
            layers=layers, initial_view_state=view_state, map_style='light'))
            
    # --- 가게 상세 정보 표시 ---
    with st.container(border=True):
        st.subheader(f"📝 **{selected_details['가게이름']}** 상세 정보")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**주소:** {selected_details['주소']}")
            st.write("**제휴 혜택:**")
            if pd.notna(selected_details['benefit']):
                st.info(selected_details['benefit'])
            else:
                st.warning("제공된 혜택 정보가 없습니다.")
        
        with col2:
            st.write("**학생 리뷰**")
            avg_rating_val = selected_details['평균별점']
            review_count = selected_details['리뷰수']
            
            # --- 리뷰 데이터 로드 및 변환 (캐시되지 않은 데이터) ---
            try:
                # 리뷰 정보를 모든 섹션에서 사용하기 위해 먼저 로드
                feedback_df = pd.read_csv(FEEDBACK_FILE, engine='python')
                feedback_df['rating'] = pd.to_numeric(feedback_df['rating'], errors='coerce') 
                store_feedback = feedback_df[feedback_df['store_name'] == current_store_name]
                
            except FileNotFoundError:
                st.warning("리뷰 파일을 찾을 수 없습니다.")
                store_feedback = pd.DataFrame()
                
            # --- 평점 및 최신 리뷰 요약 ---
            if review_count > 0:
                st.metric(label="평균 별점", value=f"{avg_rating_val:.1f} / 5.0", delta=get_star_rating(avg_rating_val))
                st.write("**최신 리뷰 3개**")
                
                for _, row in store_feedback.sort_values('timestamp', ascending=False).head(3).iterrows():
                    st.markdown(f"> {row['review']} ({get_star_rating(row['rating'])})")
            else:
                st.warning("아직 등록된 리뷰가 없습니다.")
                
            # --- 전체 리뷰 보기 섹션 추가 ---
            if not store_feedback.empty:
                with st.expander("📝 전체 리뷰 보기"):
                    full_reviews = store_feedback.sort_values('timestamp', ascending=False)
                    st.dataframe(full_reviews[['timestamp', 'rating', 'review']], 
                                 use_container_width=True, 
                                 # 리뷰 표시를 더 직관적으로 만들기 위해 column_config 사용 가능
                                 column_config={
                                     "timestamp": st.column_config.DatetimeColumn("날짜", format="YYYY-MM-DD"),
                                     "rating": st.column_config.ProgressColumn(
                                         "별점",
                                         format="%.1f",
                                         min_value=1,
                                         max_value=5,
                                     ),
                                     "review": "리뷰 내용"
                                 })
            # --- 전체 리뷰 보기 섹션 끝 ---

        # --- 피드백 제출 기능 ---
        with st.expander("⭐ 제휴 혜택 피드백 남기기"):
            rating = st.slider("별점을 선택해주세요.", 1, 5, 5, key=f"rating_{current_store_name}")
            review = st.text_input("한 줄 리뷰를 남겨주세요.", placeholder="예: 혜택 적용 잘 받았습니다!", key=f"review_{current_store_name}")
            if st.button("피드백 제출", key=f"submit_{current_store_name}"):
                save_feedback(current_store_name, rating, review)
                st.success("소중한 피드백 감사합니다!")
                time.sleep(1.5)
                st.rerun()

    st.markdown("---")
    # --- 워드 클라우드 섹션 (요청대로 이 화면에만 표시) ---
    st.header(f"💬 '{current_store_name}' 리뷰 키워드 분석")
    
    if 'store_feedback' in locals() and not store_feedback.empty:
        store_reviews = store_feedback['review']
        if len(store_reviews) > 0:
            generate_word_cloud(store_reviews, title="가게 리뷰 키워드 분석") 
        else:
            st.info("이 가게는 워드 클라우드를 생성할 충분한 리뷰가 없습니다.")

    elif 'store_feedback' not in locals():
        st.info("리뷰 파일을 다시 로드하여 확인하십시오.")
    
# --- 관리자 페이지 함수 (생략) ---
def render_admin_login():
    """관리자 로그인 페이지를 그리는 함수"""
    st.title("🔐 관리자 페이지 로그인")
    password = st.text_input("비밀번호를 입력하세요.", type="password")
    if st.button("로그인"):
        if password == "admin1234":
            st.session_state.admin_login = True
            st.session_state.page = 'admin_dashboard'
            st.rerun()
        else:
            st.error("비밀번호가 일치하지 않습니다.")
    if st.button("🏠 홈으로 돌아가기"):
        st.session_state.page = 'home'; st.rerun()

def render_admin_dashboard():
    """관리자 대시보드 페이지를 그리는 함수"""
    if not st.session_state.get('admin_login'):
        st.session_state.page = 'admin_login'; st.warning("로그인이 필요합니다."); st.rerun()

    st.title("📈 KUSIS 관리자 대시보드")
    if st.button("🏠 홈으로 돌아가기"): st.session_state.page = 'home'; st.rerun()
    st.markdown("---")

    # --- 클릭 동향 분석 섹션 ---
    st.header("📊 사용자 클릭 동향 분석")
    try:
        log_df = pd.read_csv(LOG_FILE)
        col1, col2, col3 = st.columns(3)
        with col1: 
            st.subheader("대분류 클릭 Top 10")
            major_clicks = log_df[log_df['type'] == 'major_category']['value'].value_counts().head(10)
            st.bar_chart(major_clicks, color="#027529")
        with col2: 
            st.subheader("중분류 클릭 Top 10")
            sub_clicks = log_df[log_df['type'] == 'sub_category']['value'].value_counts().head(10)
            st.bar_chart(sub_clicks, color="#027529")
        with col3: 
            st.subheader("가게 조회 Top 10")
            store_clicks = log_df[log_df['type'] == 'store_view']['value'].value_counts().head(10)
            st.bar_chart(store_clicks, color="#027529")
        
        with st.expander("전체 클릭 로그 보기"):
            st.dataframe(log_df.sort_values('timestamp', ascending=False), use_container_width=True)
    except FileNotFoundError:
        st.warning("아직 수집된 클릭 로그 데이터가 없습니다.")

    # --- 사용자 피드백 관리 섹션 ---
    st.markdown("---")
    st.header("💬 사용자 피드백 관리")
    try:
        feedback_df = pd.read_csv(FEEDBACK_FILE, engine='python')
        feedback_df['rating'] = pd.to_numeric(feedback_df['rating'], errors='coerce') 
        avg_ratings = feedback_df.groupby('store_name')['rating'].agg(['mean', 'count']).rename(columns={'mean': '평균별점', 'count': '리뷰수'}).round(2).sort_values('평균별점', ascending=False)
        
        st.subheader("⭐ 최고/최저 평점 가게 Top 5")
        col1, col2 = st.columns(2)
        with col1: st.write("최고 평점 Top 5"); st.bar_chart(avg_ratings['평균별점'].head(5), color="#027529")
        with col2: st.write("최저 평점 Top 5"); st.bar_chart(avg_ratings['평균별점'].tail(5), color="#D32F2F")
        with st.expander("전체 가게 평균 별점 보기"): st.dataframe(avg_ratings, use_container_width=True)

        st.subheader("리뷰 필터링 및 확인")
        filter_store = st.selectbox("가게를 선택하여 리뷰를 필터링하세요.", options=['전체 보기'] + sorted(feedback_df['store_name'].unique()))
        
        display_df = feedback_df
        if filter_store != '전체 보기':
            display_df = feedback_df[feedback_df['store_name'] == filter_store]
        st.dataframe(display_df.sort_values('timestamp', ascending=False), use_container_width=True)
        
        # 관리자 페이지에도 전체 리뷰 워드 클라우드 추가
        st.markdown("---")
        st.header("전체 리뷰 키워드 분석")
        reviews_for_wc_all = feedback_df['review']
        generate_word_cloud(reviews_for_wc_all, title="전체 리뷰 기반 키워드 분석")
        
    except FileNotFoundError:
        st.warning("아직 수집된 피드백 데이터가 없습니다.")


# ---------------------------------
# 메인 로직: 페이지 라우팅
# ---------------------------------
page_routes = {
    'home': render_home_page,
    'sub_category_summary': render_sub_category_summary,
    'store_list_view': render_store_list_view, 
    'store_detail_map': render_store_detail_map,
    'admin_login': render_admin_login,
    'admin_dashboard': render_admin_dashboard
}

page_function = page_routes.get(st.session_state.page)
if page_function:
    page_function()
else:
    st.session_state.page = 'home'; st.rerun()
