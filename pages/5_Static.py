import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

st.set_page_config(layout="wide", page_title="iKid Secure | Statistics")

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

st.title("📊 สถิติภาพรวม")
st.markdown("---")

try:
    response = supabase.table("assessments").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # Clean ข้อมูล
        df["created_at"] = pd.to_datetime(df["created_at"], errors='coerce')
        df = df.dropna(subset=['created_at']) # ลบแถวที่ไม่มีวันที่ออก
        df["aggression_level"] = df["aggression_level"].astype(str).str.extract('(\d+)').astype(float).fillna(0)
        
        # สำหรับกราฟแนวโน้ม
        df["week"] = df["created_at"].dt.to_period('W').astype(str) # รายสัปดาห์
        df["year"] = df["created_at"].dt.year.astype(str) # รายปี

        # 1. KPI
        c1, c2, c3 = st.columns(3)
        c1.metric("จำนวนเคสรวม", int(len(df)))
        c2.metric("ระดับความรุนแรงสูงสุด", int(df["aggression_level"].max()))
        c3.metric("ค่าเฉลี่ยความรุนแรง", round(df["aggression_level"].mean(), 1))
        
        st.divider()

        # 2. กราฟด้านบน
        col1, col2 = st.columns([1, 1.5])
        with col1:
            st.subheader("📈 เคสตามระดับ")
            level_counts = df["aggression_level"].value_counts().sort_index().reset_index()
            level_counts.columns = ["Level", "Count"]
            fig_bar = px.bar(level_counts, x="Level", y="Count", color="Level", 
                             color_continuous_scale=["#FFEB3B", "#FF9800", "#F44336"])
            st.plotly_chart(fig_bar, use_container_width=True)
        with col2:
            st.subheader("📊 สัดส่วนพฤติกรรม (OSA)")
            fig_pie = px.pie(df, names="behavior_note", hole=0.4)
            # ขยายพายชาร์ตและย้าย Legend ไปด้านข้าง
            fig_pie.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1))
            st.plotly_chart(fig_pie, use_container_width=True)

        # 3. แนวโน้มระยะยาว (รายสัปดาห์และรายปี)
        st.divider()
        st.subheader("📉 แนวโน้มความรุนแรงระยะยาว")
        g1, g2 = st.columns(2)
        with g1:
            st.write("แนวโน้มรายสัปดาห์ (ภายในปี 2026)")
            weekly_trend = df.groupby("week")["aggression_level"].mean().reset_index()
            fig_week = px.line(weekly_trend, x="week", y="aggression_level", markers=True)
            st.plotly_chart(fig_week, use_container_width=True)
        with g2:
            st.write("แนวโน้มรายปี")
            yearly_trend = df.groupby("year")["aggression_level"].mean().reset_index()
            fig_year = px.line(yearly_trend, x="year", y="aggression_level", markers=True)
            st.plotly_chart(fig_year, use_container_width=True)

    else:
        st.info("ยังไม่มีข้อมูลการประเมินในระบบ ✨")
except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")

if st.button("⬅️ กลับหน้า Dashboard", use_container_width=True):
    st.switch_page("pages/1_Dashboard.py")



