import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(layout="wide", page_title="iKid Secure | Statistics")

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

st.title("📊 สถิติภาพรวมความปลอดภัยผู้ป่วย (รายเดือน & รายปี)")
st.markdown("---")

try:
    response = supabase.table("assessments").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # Clean ข้อมูลวันที่
        df["created_at"] = pd.to_datetime(df["created_at"], errors='coerce')
        df["aggression_level"] = df["aggression_level"].astype(str).str.extract('(\d+)').astype(float).fillna(0)
        
        # สร้างคอลัมน์สำหรับสรุปรายเดือนและรายปี
        df["month_year"] = df["created_at"].dt.to_period('M').astype(str) # เช่น 2026-07
        df["year"] = df["created_at"].dt.year.fillna(0).astype(int)

        # KPI สรุป
        c1, c2, c3 = st.columns(3)
        c1.metric("จำนวนเคสรวม", int(len(df)))
        c2.metric("ระดับสูงสุดที่พบ", int(df["aggression_level"].max()))
        c3.metric("ระดับความรุนแรงเฉลี่ย", round(df["aggression_level"].mean(), 1))
        
        st.divider()

        # กราฟแท่งและพายชาร์ต (คงเดิมตามไอด้าชอบ)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📈 จำนวนเคสแยกตามระดับ")
            level_counts = df["aggression_level"].value_counts().sort_index().reset_index()
            level_counts.columns = ["Level", "Count"]
            fig_bar = px.bar(level_counts, x="Level", y="Count", color="Level", 
                             color_continuous_scale=["#FFEB3B", "#FF9800", "#F44336"])
            st.plotly_chart(fig_bar, use_container_width=True)
        with col2:
            st.subheader("📊 สัดส่วนพฤติกรรม (OSA)")
            fig_pie = px.pie(df, names="behavior_note", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

        # กราฟเส้นแนวโน้ม (ใหม่)
        st.divider()
        st.subheader("📉 แนวโน้มความรุนแรงระยะยาว")
        g1, g2 = st.columns(2)
        
        with g1:
            st.write("แนวโน้มรายเดือน")
            monthly_trend = df.groupby("month_year")["aggression_level"].mean().reset_index()
            fig_month = px.line(monthly_trend, x="month_year", y="aggression_level", markers=True)
            st.plotly_chart(fig_month, use_container_width=True)
            
        with g2:
            st.write("แนวโน้มรายปี")
            yearly_trend = df.groupby("year")["aggression_level"].mean().reset_index()
            fig_year = px.line(yearly_trend, x="year", y="aggression_level", markers=True)
            st.plotly_chart(fig_year, use_container_width=True)

    else:
        st.info("ยังไม่มีข้อมูลการประเมินในระบบ ✨")

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")

if st.button("⬅️ กลับหน้า Dashboard", use_container_width=True):
    st.switch_page("pages/1_Dashboard.py")


