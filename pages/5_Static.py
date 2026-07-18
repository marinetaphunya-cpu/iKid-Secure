import streamlit as st
import pandas as pd
import numpy as np
from supabase import create_client

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(layout="wide", page_title="iKid Secure | Statistics")

# 2. เชื่อมต่อฐานข้อมูล
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# 3. หัวข้อหน้าสถิติ
st.title("📊 สถิติภาพรวมความปลอดภัยผู้ป่วย")
st.markdown("---")

# 4. ส่วนสรุปตัวเลขสำคัญ (KPI Cards)
st.subheader("💡 สรุปสถานการณ์ภาพรวม")
c1, c2, c3, c4 = st.columns(4)
c1.metric("จำนวนเคสทั้งหมด", "128", "+5 จากเดือนที่แล้ว")
c2.metric("ความรุนแรงระดับ 3", "12", "-2 จากเดือนที่แล้ว")
c3.metric("ระดับความรุนแรงเฉลี่ย", "1.5", "คงที่")
c4.metric("พฤติกรรมที่พบบ่อยที่สุด", "ต่อผู้อื่น", "ระดับ 2")

st.divider()

# 5. ส่วนกราฟ (วาง Layout ไว้ก่อน ไอด้าค่อยใส่ข้อมูลจริงลงไปนะเจ้า)
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 แนวโน้มความรุนแรง (รายเดือน)")
    # ตัวอย่างข้อมูลกราฟเส้น
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=['ระดับ 1', 'ระดับ 2', 'ระดับ 3'])
    st.line_chart(chart_data)

with col_right:
    st.subheader("📊 เปรียบเทียบระดับความรุนแรง")
    # ตัวอย่างข้อมูลกราฟแท่ง
    bar_data = pd.DataFrame(np.random.randn(10, 3), columns=['ระดับ 1', 'ระดับ 2', 'ระดับ 3'])
    st.bar_chart(bar_data)

st.divider()

# 6. รายละเอียดเพิ่มเติม
st.subheader("📋 สรุปพฤติกรรมที่พบในรอบเดือน")
st.info("💡 ข้อมูลนี้เป็นการสรุปภาพรวมจากประวัติการประเมินทั้งหมดในระบบ (Read-only)")

# ปุ่มนำทาง
if st.button("⬅️ กลับหน้า Dashboard"):
    st.switch_page("pages/1_Dashboard.py")

