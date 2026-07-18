import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(layout="wide", page_title="iKid Secure | Statistics")

# 2. เชื่อมต่อ Supabase
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

st.title("📊 สถิติภาพรวมความปลอดภัยผู้ป่วย")
st.markdown("---")

# 3. ดึงและประมวลผลข้อมูล
try:
    response = supabase.table("assessments").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # --- ส่วนจัดการวันที่และระดับความรุนแรง (Clean Data) ---
        # แก้ไข Error วันที่ด้วย errors='coerce'
        df["created_at"] = pd.to_datetime(df["created_at"], errors='coerce')
        df["date_only"] = df["created_at"].dt.date.fillna("ไม่ระบุ")
        
        # จัดการตัวเลขความรุนแรง
        df["aggression_level"] = df["aggression_level"].astype(str).str.extract('(\d+)').astype(float).fillna(0)
        
        # --- ส่วนแสดง KPI ---
        c1, c2, c3 = st.columns(3)
        c1.metric("จำนวนเคสการประเมิน", len(df))
        c2.metric("ระดับความรุนแรงสูงสุด", int(df["aggression_level"].max()))
        c3.metric("ค่าเฉลี่ยความรุนแรง", round(df["aggression_level"].mean(), 2))
        
        st.divider()

        # --- ส่วนกราฟ ---
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("📈 จำนวนเคสแยกตามระดับ")
            level_counts = df["aggression_level"].value_counts().sort_index().reset_index()
            level_counts.columns = ["Level", "Count"]
            
            # กราฟแท่งแยกสีสวยงาม
            fig_bar = px.bar(level_counts, x="Level", y="Count", color="Level", 
                             color_continuous_scale=["#FFEB3B", "#FF9800", "#F44336"])
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_right:
            st.subheader("📉 แนวโน้มรายวัน")
            trend_df = df.groupby("date_only")["aggression_level"].mean().reset_index()
            fig_line = px.line(trend_df, x="date_only", y="aggression_level", markers=True)
            st.plotly_chart(fig_line, use_container_width=True)

        # --- ตารางรายละเอียด ---
        st.subheader("📋 รายละเอียดพฤติกรรมล่าสุด")
        # แสดงวันที่แบบวันที่เพียวๆ (ไม่เอาเวลาเยื้อยๆ)
        display_df = df[["date_only", "behavior_note", "aggression_level"]]
        display_df.columns = ["วันที่", "บันทึกพฤติกรรม", "ระดับความรุนแรง"]
        st.dataframe(display_df, use_container_width=True)

    else:
        st.info("ยังไม่มีข้อมูลการประเมินในระบบเจ้า ✨")

except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")

st.divider()
if st.button("⬅️ กลับหน้า Dashboard", use_container_width=True):
    st.switch_page("pages/1_Dashboard.py")

