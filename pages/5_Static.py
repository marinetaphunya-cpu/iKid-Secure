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

st.title("📊 สถิติภาพรวมความปลอดภัยผู้ป่วย")
st.markdown("---")

try:
    response = supabase.table("assessments").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # Clean ข้อมูล
        df["created_at"] = pd.to_datetime(df["created_at"], errors='coerce')
        df["aggression_level"] = df["aggression_level"].astype(str).str.extract('(\d+)').astype(float).fillna(0)
        
        # ปรับรูปแบบวันที่ให้เป็นแค่ Month-Year และ Year (เป็น String เท่านั้น)
        df["month_year"] = df["created_at"].dt.strftime('%b %Y').fillna("Unknown")
        df["year_str"] = df["created_at"].dt.year.fillna(0).astype(int).astype(str)

        # 2. KPI
        c1, c2, c3 = st.columns(3)
        c1.metric("จำนวนเคสรวม", int(len(df)))
        c2.metric("ระดับสูงสุด", int(df["aggression_level"].max()))
        c3.metric("ค่าเฉลี่ย", round(df["aggression_level"].mean(), 1))
        
        st.divider()

        # 3. กราฟด้านบน: Bar และ Pie (ขยาย Pie ให้ใหญ่ขึ้น)
        col1, col2 = st.columns([1, 1.5]) # ขยาย col2 ให้ Pie ใหญ่ขึ้น
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
            fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0)) # ลดขอบเพื่อให้ Pie เต็มพื้นที่
            st.plotly_chart(fig_pie, use_container_width=True)

        # 4. กราฟเส้นแนวโน้ม (แก้เรื่องวันที่เยื้อยๆ)
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
            yearly_trend = df.groupby("year_str")["aggression_level"].mean().reset_index()
            fig_year = px.line(yearly_trend, x="year_str", y="aggression_level", markers=True)
            st.plotly_chart(fig_year, use_container_width=True)

    else:
        st.info("ยังไม่มีข้อมูลในระบบ ✨")
except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")

if st.button("⬅️ กลับหน้า Dashboard", use_container_width=True):
    st.switch_page("pages/1_Dashboard.py")



