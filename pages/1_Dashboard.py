import streamlit as st
import pandas as pd
import time
from supabase import create_client

# ถ้ายังไม่ได้ Login ให้เด้งกลับไปหน้าแรก (app.py)
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("app.py") 

# เรียกคีย์มาจากไฟล์ secrets.toml
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

# เชื่อมต่อ Supabase
supabase = create_client(url, key)


st.set_page_config(layout="wide")

# CSS สำหรับตกแต่งตารางและปุ่มให้เป็นสี Pastel
st.markdown("""
    <style>
    .stDataFrame { border: 2px solid #A8DADC; border-radius: 10px; }
    div.stButton > button { background-color: #F1FAEE; border: 1px solid #A8DADC; color: #1D3557; }
    </style>
""", unsafe_allow_html=True)

st.title("📋 รายชื่อ")

# ข้อมูลตัวอย่าง (ในอนาคตเราจะดึงจาก Supabase)
data = {
    "name": ["A", "B", "C", "D", "E"],
    "Diagnosis": ["Depression", "ASD", "ASD", "ADHD", "ASD"],
    "Aggression Level": [1, 2, 3, 1, 2],
    "หมายเหตุ": ["-", "-", "-", "-", "-"]
}
df = pd.DataFrame(data)

# โหมดแก้ไข
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

# ปุ่มแก้ไข/บันทึก
col1, col2 = st.columns([8, 1])
with col2:
    if st.button("แก้ไข" if not st.session_state.edit_mode else "บันทึก"):
        if st.session_state.edit_mode:
            with st.spinner('กำลังบันทึกข้อมูล...'):
                time.sleep(2)
                st.success("บันทึกเรียบร้อย!")
                st.session_state.edit_mode = False
                time.sleep(1)
                st.rerun()
        else:
            st.session_state.edit_mode = True
            st.rerun()

# แสดงตาราง
if st.session_state.edit_mode:
    edited_df = st.data_editor(df, use_container_width=True)
else:
    # แสดงตารางแบบคลิกเลือก Profile ได้
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.info("💡 คลิกที่แถวข้อมูล เพื่อดูรายละเอียดรายบุคคล (ฟีเจอร์นี้กำลังพัฒนา)")

