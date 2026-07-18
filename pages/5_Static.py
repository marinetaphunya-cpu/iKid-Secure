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

st.title("📊 สถิติภาพรวม")
st.markdown("---")

# 2. ดึงและประมวลผลข้อมูล
try:
    response = supabase.table("assessments").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # Clean ข้อมูล
        df["created_at"] = pd.to_datetime(df["created_at"], errors='coerce')
        df["date_str"] = df["created_at"].dt.strftime('%d/%m/%Y').fillna("ไม่ระบุวันที่")
        df["aggression_level"] = df["aggression_level"].astype(str).str.extract('(\d+)').astype(float).fillna(0)
        
        # 3. แสดง KPI สรุปแบบอ่านง่าย
        c1, c2, c3 = st.columns(3)
        c1.metric("จำนวนเคสรวม", int(len(df)))
        c2.metric("ระดับสูงสุดที่พบ", int(df["aggression_level"].max()))
        c3.metric("ระดับความรุนแรงเฉลี่ย", round(df["aggression_level"].mean(), 1)) # ปัดเศษเหลือเลขเดียว
        
        st.divider()

        # 4. กราฟ 2 ช่อง
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 จำนวนเคสแยกตามระดับ")
            level_counts = df["aggression_level"].value_counts().sort_index().reset_index()
            level_counts.columns = ["Level", "Count"]
            fig_bar = px.bar(level_counts, x="Level", y="Count", color="Level", 
                             color_continuous_scale=["#FFEB3B", "#FF9800", "#F44336"])
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            st.subheader("📊 ประเภทพฤติกรรมก้าวร้าว (OSA)")
            # สรุปจาก behavior_note (ไอด้าสามารถปรับชื่อได้ถ้าต้องการ)
            fig_pie = px.pie(df, names="behavior_note", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

        # 5. กราฟเส้นแนวโน้ม (ปรับให้ดูง่ายขึ้น)
        st.subheader("📉 แนวโน้มความรุนแรงรายวัน")
        trend_df = df.groupby("date_str")["aggression_level"].mean().reset_index()
        fig_line = px.line(trend_df, x="date_str", y="aggression_level", markers=True)
        fig_line.update_layout(yaxis=dict(tickmode='linear', dtick=1)) # ปรับเลขแกน Y ให้เป็นจำนวนเต็ม
        st.plotly_chart(fig_line, use_container_width=True)

    else:
        st.info("ยังไม่มีข้อมูลการประเมินในระบบ ✨")

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")

st.divider()
if st.button("⬅️ กลับหน้า Dashboard", use_container_width=True):
    st.switch_page("pages/1_Dashboard.py")


