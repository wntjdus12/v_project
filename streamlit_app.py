import streamlit as st
import requests
import pandas as pd
import random
import time
from streamlit_autorefresh import st_autorefresh

temperature_data = []

st.set_page_config(page_title="📈 실시간 온도 그래프", layout="wide")
st.title("📊 실시간 온도 그래프 (±10 오차 포함)")

# 5초마다 새로고침
st_autorefresh(interval=5000, limit=None, key="refresh")

API_URL = "http://3.36.70.226:3000/temperatures"

# session state로 그래프 누적
if "graph_data" not in st.session_state:
    st.session_state.graph_data = []

try:
    res = requests.get(API_URL)
    if res.status_code == 200:
        base_temp = res.json().get("temperature", 25.0)
        simulated_temp = round(base_temp + random.uniform(-10, 10), 2)
        st.session_state.graph_data.append(simulated_temp)
        
        df = pd.DataFrame(st.session_state.graph_data, columns  =["Temperature"])
        st.line_chart(df)
        st.success(f"🧪 기준 온도: {base_temp}℃ | 생성된 온도: {simulated_temp}℃ | 누적: {len(df)}개")
    else:
        st.error("서버 응답 실패")
except Exception as e:
    st.error(f"연결 오류: {e}")
