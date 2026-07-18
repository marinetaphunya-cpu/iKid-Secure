import streamlit as st
import pandas as pd
from supabase import create_client

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(layout="wide", page_title="iKid Secure | Statistics")

# 2. เชื่อมต่อ Supabase
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

st.title("📊 สถิติภาพรวมความปลอดภัยผู้ป่วย")
st.markdown("หน้าสรุปข้อมูลการประเมินพฤติกรรมก้าวร้าว (ข้อมูลแสดงผลแบบอ่านอย่างเดียว)")
st.markdown("---")

# 3. ดึงข้อมูลจากตาราง assessments
try:
    response = supabase.table("assessments").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # 4. ทำความสะอาดข้อมูล (Clean Data) เพื่อทำสถิติ
        # แปลงข้อมูลให้อยู่ในรูปแบบตัวเลขเสมอ (เผื่อกรณีมีคำว่า 'ระดับ' ติดมา)
        df["aggression_level"] = df["aggression_level"].astype(str).str.extract('(\d+)').astype(float).fillna(0)
        
        # ส่วนแสดง KPI (ตัวเลขสรุป)
        c1, c2, c3 = st.columns(3)
        c1.metric("จำนวนเคสการประเมินทั้งหมด", len(df))
        c2.metric("ระดับความรุนแรงสูงสุดที่พบ", int(df["aggression_level"].max()))
        c3.metric("ระดับความรุนแรงเฉลี่ย", round(df["aggression_level"].mean(), 2))
        
        st.divider()

        # 5. แสดงกราฟสถิติ
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("📈 กราฟแสดงจำนวนเคสแยกตามระดับ")
            # นับความถี่ของแต่ละระดับ
            level_counts = df["aggression_level"].value_counts().sort_index()
            # เปลี่ยนชื่อ Index ให้สวยงาม
            level_counts.index = [f"ระดับ {int(i)}" for i in level_counts.index]
            st.bar_chart(level_counts)
            
        with col_right:
            st.subheader("📋 รายละเอียดพฤติกรรมล่าสุด")
            # แสดงตารางพฤติกรรม 5 รายการล่าสุด
            display_df = df[["created_at", "behavior_note", "aggression_level"]].sort_values(by="created_at", ascending=False).head(5)
            st.table(display_df)
    else:
        st.info("ยังไม่มีข้อมูลการประเมินในระบบ ✨")

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")

st.divider()

# ปุ่มกลับ
if st.button("⬅️ กลับหน้า Dashboard", use_container_width=True):
    st.switch_page("pages/1_Dashboard.py")

