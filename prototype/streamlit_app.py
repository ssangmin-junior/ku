
# streamlit_app.py
import pandas as pd
import numpy as np
import os
import random
from datetime import datetime
import plotly.express as px
import streamlit as st
# ---------------------------
# 페이지 설정 & 스타일
# ---------------------------
st.set_page_config(page_title="이동형 관광안내소 혼잡 대시보드", layout="wide")
st.markdown("""
<style>
body {background: #ffffff; color: #000000;}
h1, h2, h3, h4, h5 {color: #000000; margin-bottom:6px;}
.stMarkdown {line-height:1.3;}
.metric-label {font-weight:600;}
.card {padding:16px; border-radius:10px; background:#f9f9f9; box-shadow:0 4px 12px rgba(0,0,0,0.06); margin-bottom:12px;}
.section {margin-top:16px; margin-bottom:16px;}
.small {font-size:0.85rem; color:#222;}
.warning-log {background:#ffe6e6; padding:8px; border-left:4px solid #d33;}
.normal-log {padding:6px; border-left:4px solid #ccc; margin-bottom:4px;}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# 로고 표시 (같은 폴더에 icon.jpg)
# ---------------------------
header_col1, header_col2 = st.columns([2, 7])
now = datetime.now()
current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
with header_col1:
    st.markdown(
        """
        <style>
          /* 로고 이미지 강제 사이즈 지정 */
          .logo-img {
            width: 250px !important;
            height: auto !important;
          }
        </style>
        <img 
          src="https://raw.githubusercontent.com/ssangmin-junior/ku/main/prototype/icon.jpg" 
          class="logo-img"
        />
        """,
        unsafe_allow_html=True
    )
with header_col2:
    st.markdown("## 🚦 이동형 관광안내소 기반 실시간 혼잡 예측 및 보고 시스템")
    st.markdown(f"**기준 시간대:** {current_time_str[:13]} (실시간 반영)")

# ---------------------------
# 임의 데이터 생성
# ---------------------------
random.seed(42)
np.random.seed(42)
spots = [
    '팝업스토어 A', '팝업스토어 B', '서울숲 공연장', '연무장길 카페거리', '성수역 부근',
    '성수동 복합문화공간', '성수 창작소', '거리버스킹 ZONE', '성수동 야시장', '한강진입로 쉼터'
]
tags_pool = ['#팝업', '#공연', '#혼잡', '#무질서', '#축제', '#정상']
data = []
# 시간대 대신 실시간 기준으로 가장 가까운 슬롯 개념은 여기선 무시하고 랜덤 샘플만 사용
for spot in spots:
    lat = 37.544 + np.random.uniform(-0.003, 0.003)
    lon = 127.056 + np.random.uniform(-0.003, 0.003)
    popscore = random.randint(30, 100)  # 화제성
    crowd = random.randint(50, 700)      # 혼잡도
    card_spend = random.randint(100000, 2000000)  # 일별 카드 소비
    traffic_flow = random.randint(30, 300)        # 일별 교통 유입
    tag = random.choice(tags_pool)
    data.append({
        'spot': spot,
        'lat': lat,
        'lon': lon,
        '화제성': popscore,
        '혼잡도': crowd,
        '일별_카드_소비액': card_spend,
        '일별_교통_유입량': traffic_flow,
        'tag': tag
    })
df_time = pd.DataFrame(data)

# session state 초기화
if "logs" not in st.session_state:
    st.session_state.logs = []
if "selected_spot" not in st.session_state:
    st.session_state.selected_spot = None
if "admin_chosen_spot" not in st.session_state:
    st.session_state.admin_chosen_spot = df_time.sort_values("혼잡도", ascending=False).iloc[0]["spot"]

# ---------------------------
# 사이드바 / 역할 선택
# ---------------------------
with st.sidebar:
    st.title("대시보드 역할")
    role = st.radio("", ["홈", "팝업운영자", "이동형 관광안내소", "총괄 관리자"])
    now = datetime.now()
    current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"🕒 **현재 시각:** {current_time_str}")
    st.markdown("")

# ---------------------------
# 지도 생성 함수 (강조 수정, 스타일 변경)
# ---------------------------
def make_base_map(dataframe, emphasize_spot=None, current_loc=None, center=None, zoom=16):
    # 기본 맵: open-street-map으로 도로/건물 잘 보이도록
    fig = px.scatter_mapbox(
        dataframe,
        lat="lat", lon="lon",
        size="혼잡도", color="혼잡도",
        hover_name="spot",
        hover_data={
            "화제성": True,
            "혼잡도": True,
            "일별_카드_소비액": True,
            "일별_교통_유입량": True,
            "tag": True
        },
        color_continuous_scale="YlOrRd",
        zoom=zoom
        height=450,
        custom_data=["spot"],
    )
    # 강조된 SPOT: 흰 테두리 + 파란 중심
    if emphasize_spot:
        row = dataframe[dataframe["spot"] == emphasize_spot]
        if not row.empty:
            lat0 = row.iloc[0]["lat"]
            lon0 = row.iloc[0]["lon"]
            # 외곽 테두리 (흰 원, 약간 투명)
            fig.add_scattermapbox(
                lat=[lat0],
                lon=[lon0],
                mode="markers",
                marker=dict(size=100, color="rgba(255,255,255,0.7)", symbol="circle"),
                hoverinfo="none",
                showlegend=False,
            )
            # 중간 강조 원 (파란 테두리 느낌)
            fig.add_scattermapbox(
                lat=[lat0],
                lon=[lon0],
                mode="markers",
                marker=dict(size=70, color="rgba(0,115,255,0.3)"),
                hoverinfo="none",
                showlegend=False,
            )
            # 중심 점
            fig.add_scattermapbox(
                lat=[lat0],
                lon=[lon0],
                mode="markers",
                marker=dict(size=24, color="#0055ff", symbol="circle"),
                hoverinfo="none",
                showlegend=False,
            )
    # 현재 위치
    if current_loc:
        fig.add_scattermapbox(
            lat=[current_loc[0]],
            lon=[current_loc[1]],
            mode="markers",
            marker=dict(size=18, color="#ff8c00", symbol="star"),
            hovertemplate="현재 위치",
            name="현재 위치",
        )
    # 중심 좌표 설정
    if center:
        fig.update_layout(mapbox_center={"lat": center[0], "lon": center[1]})
    # 밝고 선명한 스타일: open-street-map 사용 (도로/건물 표시 잘됨)
    fig.update_layout(mapbox_style="open-street-map", margin={"t":5,"b":5,"l":5,"r":5})
    fig.update_traces(marker=dict(opacity=0.85))
    return fig


# ---------- 홈 ----------
if role == "홈":
    st.subheader("🏠 개요 및 전체 현황")
    st.markdown("이 시스템은 성수동의 팝업운영자, 이동형 관광안내소, 총괄관리자가 협력하여 실시간 혼잡도를 파악하고 대응하도록 만든 시연용 대시보드입니다.")
    st.markdown("### 주요 장소 실시간 혼잡도 지도")
    fig_home = make_base_map(df_time, center=(37.544,127.056), zoom=14)
    st.plotly_chart(fig_home, use_container_width=True)

    st.markdown("### 최근 보고된 현장 로그 (위험도 높은 항목 먼저)")
    # 위험 로그: '매우 혼잡' 또는 '혼잡도' 표현을 포함한 것 (팝업운영자 보고 포맷 기준)
    warning_logs = [l for l in st.session_state.logs if "매우 혼잡" in l or "혼잡도 '매우 혼잡'" in l]
    normal_logs = [l for l in st.session_state.logs if l not in warning_logs]
    if warning_logs:
        st.markdown("위험도 높은 보고", unsafe_allow_html=True)
        for l in warning_logs:
            st.markdown(f"<div class='warning-log'>{l}</div>", unsafe_allow_html=True)
    if normal_logs:
        st.markdown("기타 보고")
        for l in normal_logs[:10]:
            st.markdown(f"<div class='normal-log'>{l}</div>", unsafe_allow_html=True)
    if not st.session_state.logs:
        st.info("아직 보고된 내용이 없습니다.")

# ---------- 팝업운영자 ----------
elif role == "팝업운영자":
    st.subheader("📦 팝업운영자용 대시보드")
    st.markdown("### 내 팝업 & 인근 팝업 혼잡도 지도")
    popup_df = df_time[df_time["spot"].str.contains("팝업스토어")].copy()
    emphasize = st.session_state.selected_spot if st.session_state.selected_spot in popup_df["spot"].values else None
    fig = make_base_map(popup_df, emphasize_spot=emphasize, center=(37.544,127.056), zoom=14)
    st.plotly_chart(fig, use_container_width=True)

    # 아래에 실시간 상태와 보고 입력을 나란히
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("#### 팝업 선택 및 실시간 상태")
        chosen_popup = st.selectbox("운영 중인 팝업스토어 선택", sorted(popup_df["spot"].unique()))
        if st.session_state.selected_spot in popup_df["spot"].values:
            chosen_popup = st.session_state.selected_spot
        st.session_state.selected_spot = chosen_popup
        row = popup_df[popup_df["spot"] == chosen_popup].iloc[0]
        st.metric("혼잡도", f"{row['혼잡도']}명")
        st.metric("화제성", row["화제성"])
        st.metric("일별 카드 소비액", f"{row['일별_카드_소비액']:,}원")
        st.metric("일별 교통 유입량", row["일별_교통_유입량"])
        st.markdown(f"**자동 감지 태그:** {row['tag']}")

    with right:
        st.markdown("#### 현장 상황 입력")
        congestion_label = st.selectbox("혼잡도 수준", ["한산", "보통", "혼잡", "매우 혼잡"], index=1)
        wait_time = st.number_input("대기 시간 (분)", min_value=0, max_value=120, value=5)
        entrance_capacity = st.number_input("입장 가능 인원", min_value=0, max_value=100, value=10)
        comment = st.text_input("추가 코멘트", value="")
        if st.button("보고 전송"):
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = (f"[{now_str}] 팝업운영자 → {chosen_popup}: 혼잡도 '{congestion_label}', "
                     f"대기 {wait_time}분, 입장 가능 {entrance_capacity}명, 코멘트 '{comment or row['tag']}'")
            st.session_state.logs.insert(0, entry)
            st.success("현장 보고 접수됨")

# ---------- 이동형 관광안내소 ----------
elif role == "이동형 관광안내소":
    st.subheader("🧭 이동형 관광안내소용 대시보드")
    st.markdown("### 현재 위치 기반 주변 혼잡도")
    current_lat, current_lon = 37.544, 127.056
    st.info("현재 위치: 성수역 인근 (고정)")
    st.markdown(f"위치 좌표: {current_lat:.6f}, {current_lon:.6f}")

    # 거리 계산
    df_time["distance"] = np.sqrt((df_time["lat"] - current_lat) ** 2 + (df_time["lon"] - current_lon) ** 2)
    df_time = df_time.sort_values("distance")
    nearest = df_time.iloc[0]
    emphasize_spot = st.session_state.selected_spot if st.session_state.selected_spot in df_time["spot"].values else nearest["spot"]

    fig = make_base_map(df_time, emphasize_spot=emphasize_spot, current_loc=(current_lat, current_lon),
                        center=(current_lat, current_lon), zoom=14)
    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns([2,1], gap="large")
    with left:
        st.markdown("#### SPOT 직접 선택 (거리순 우선)")
        options = list(df_time["spot"].unique())
        default_index = options.index(st.session_state.selected_spot) if st.session_state.selected_spot in options else 0
        chosen = st.selectbox("선택된 SPOT", options, index=default_index)
        target = df_time[df_time["spot"] == chosen].iloc[0]
        st.session_state.selected_spot = chosen
        st.markdown(f"##### 선택된 SPOT: {target['spot']}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("혼잡도", f"{target['혼잡도']}명")
        c2.metric("화제성", target["화제성"])
        c3.metric("일별 카드 소비액", f"{target['일별_카드_소비액']:,}원")
        c4.metric("일별 교통 유입량", target["일별_교통_유입량"])
        st.markdown(f"**자동 감지 태그:** {target['tag']}")

    with right:
        st.markdown("#### 제안")
        top3 = df_time.sort_values("혼잡도", ascending=False).head(3)[["spot","혼잡도"]]
        low3 = df_time.sort_values("혼잡도", ascending=True).head(3)[["spot","혼잡도"]]
        st.markdown("혼잡도 높은 3개")
        st.table(top3.rename(columns={"spot":"SPOT","혼잡도":"유동인구"}))
        st.markdown("혼잡도 낮은 3개")
        st.table(low3.rename(columns={"spot":"SPOT","혼잡도":"유동인구"}))

    st.markdown("### 현장 상황 입력")
    mood = st.selectbox("군중 분위기", ['활기찬 분위기', '축제 분위기', '불만/짜증', '무질서'], key="mood")
    cause = st.selectbox("혼잡 원인", ['팝업 대기', '공연', '병목 현상', '유명인 방문'], key="cause")
    road = st.selectbox("도로 상태", ['정상', '쓰레기 적재', '불법 주정차', '시설물 파손'], key="road")
    if st.button("보고 전송"):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = (f"[{now_str}] 이동형 관광안내소 → {target['spot']}: 분위기 '{mood}', 원인 '{cause}', 도로 상태 '{road}'")
        st.session_state.logs.insert(0, entry)
        st.success("상황 보고 완료")

    st.markdown("### 혼잡 분산 제안")
    if target["혼잡도"] > 500:
        st.warning("혼잡이 높습니다. 다른 SPOT으로 분산 안내하세요.")
        alt = df_time[df_time["혼잡도"] < 300].sort_values("혼잡도")[["spot","혼잡도"]].head(3)
        st.table(alt.rename(columns={"spot":"SPOT","혼잡도":"유동인구"}))
    else:
        st.success("현재 SPOT은 안정적입니다.")

# ---------- 총괄 관리자 ----------
elif role == "총괄 관리자":
    st.subheader("🛠️ 총괄 관리자용 대시보드")
    st.markdown("### 주요장소 실시간 혼잡도 모니터링")

    # 위험도 높은 로그 우선 표시
    warning_logs = [l for l in st.session_state.logs if "매우 혼잡" in l or "혼잡도 '매우 혼잡'" in l]
    if warning_logs:
        st.markdown("#### ⚠️ 높은 위험도 보고")
        for l in warning_logs:
            st.markdown(f"<div class='warning-log'>{l}</div>", unsafe_allow_html=True)

    # 전체 정렬된 데이터
    df_sorted = df_time.sort_values("혼잡도", ascending=False).copy()
    # 관리자 선택 유지
    if st.session_state.admin_chosen_spot not in df_sorted["spot"].values:
        st.session_state.admin_chosen_spot = df_sorted.iloc[0]["spot"]
    chosen_spot = st.selectbox("혼잡도 높은 장소 선택", df_sorted["spot"].tolist(), index=list(df_sorted["spot"]).index(st.session_state.admin_chosen_spot))
    st.session_state.admin_chosen_spot = chosen_spot
    chosen_row = df_sorted[df_sorted["spot"] == chosen_spot].iloc[0]

    left, right = st.columns([2,1], gap="large")
    with left:
        st.markdown("#### 전체 지도 (선택된 장소 강조)")
        fig = make_base_map(df_time, emphasize_spot=chosen_spot, center=(37.544,127.056), zoom=13)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown("#### 빠른 선택 (상위 5개)")
        top5 = df_sorted.head(5)
        for i, row in top5.reset_index(drop=True).iterrows():
            if st.button(f"{row['spot']} ({row['혼잡도']})", key=f"admin_quick_{i}"):
                st.session_state.admin_chosen_spot = row["spot"]
                chosen_spot = row["spot"]
                chosen_row = row

    st.markdown("#### 선택된 장소 상세")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("혼잡도", f"{chosen_row['혼잡도']}명")
    c2.metric("화제성", chosen_row["화제성"])
    c3.metric("일별 카드 소비액", f"{chosen_row['일별_카드_소비액']:,}원")
    c4.metric("일별 교통 유입량", chosen_row["일별_교통_유입량"])
    st.markdown(f"**자동 감지 태그:** {chosen_row['tag']}")

# ---------- 공통 로그 ----------
st.markdown("---")
st.subheader("📜 실시간 보고 로그")
# 위험도 높은 항목 먼저
warning_logs = [l for l in st.session_state.logs if "매우 혼잡" in l or "혼잡도 '매우 혼잡'" in l]
normal_logs = [l for l in st.session_state.logs if l not in warning_logs]
if warning_logs:
    st.markdown("위험도 높은 보고")
    for l in warning_logs:
        st.markdown(f"<div class='warning-log'>{l}</div>", unsafe_allow_html=True)
if normal_logs:
    st.markdown("기타 보고")
    for l in normal_logs:
        st.markdown(f"<div class='normal-log'>{l}</div>", unsafe_allow_html=True)
if not st.session_state.logs:
    st.info("아직 보고된 로그가 없습니다.")
