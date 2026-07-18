import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

st.set_page_config(layout="wide", page_title="iKid Secure | Statistics")

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

st.title("📊 สถิติภาพรวมความปลอดภัยผู้ป่วย")

try:
    response = supabase.table("assessments").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # เตรียมข้อมูล: Clean วันที่และระดับความรุนแรง
        df["created_at"] = pd.to_datetime(df["created_at"]).dt.date
        df["aggression_level"] = df["aggression_level"].astype(str).str.extract('(\d+)').astype(float).fillna(0)

        # 1. กราฟแท่งสีสวย (Professional Bar Chart)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📈 จำนวนเคสแยกตามระดับ")
            level_counts = df["aggression_level"].value_counts().sort_index().reset_index()
            level_counts.columns = ["Level", "Count"]
            
            # ใช้ Plotly เพื่อแยกสี
            fig_bar = px.bar(level_counts, x="Level", y="Count", color="Level", 
                             color_continuous_scale=["#FFEB3B", "#FF9800", "#F44336"])
            st.plotly_chart(fig_bar, use_container_width=True)

        # 2. กราฟเส้นแสดงแนวโน้ม (Trend Line)
        with col2:
            st.subheader("📉 แนวโน้มความรุนแรงรายวัน")
            trend_df = df.groupby("created_at")["aggression_level"].mean().reset_index()
            fig_line = px.line(trend_df, x="created_at", y="aggression_level", markers=True)
            st.plotly_chart(fig_line, use_container_width=True)

        # 3. ตารางสรุปแบบสะอาดตา
        st.subheader("📋 รายละเอียดพฤติกรรมล่าสุด")
        display_df = df[["created_at", "behavior_note", "aggression_level"]]
        st.dataframe(display_df, use_container_width=True)

    else:
        st.info("ยังไม่มีข้อมูลในระบบ")

except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")

if st.button("⬅️ กลับหน้า Dashboard"):
    st.switch_page("pages/1_Dashboard.py")

