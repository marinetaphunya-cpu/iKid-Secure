import streamlit as st
import pandas as pd
import time
from supabase import create_client

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(layout="wide", page_title="iKid Secure")

# 2. เช็กสิทธิ์การ Login
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("app.py") 

# 3. เชื่อมต่อ Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# 4. รวม CSS ตกแต่ง
st.markdown("""
    <style>
    .stDataFrame, .stDataEditor { border: 2px solid #A8DADC; border-radius: 10px; }
    div[data-testid="stDataFrame"] table { margin-left: auto; margin-right: auto; }
    div.stButton > button { background-color: #F1FAEE; border: 1px solid #A8DADC; color: #1D3557; font-weight: bold; }
    [data-testid="stDataEditor"] [data-testid="stText"], 
    [data-testid="stDataEditor"] [data-testid="stNumberInput"],
    [data-testid="stDataFrame"] td { text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

st.title("📋 รายชื่อผู้ป่วย")

# 5. ข้อมูล
if "patient_df" not in st.session_state:
    st.session_state.patient_df = pd.DataFrame({
        "ลำดับ": [1, 2, 3, 4, 5], 
        "name": ["A", "B", "C", "D", "E"],
        "Diagnosis": ["Depression", "ASD", "ASD", "ADHD", "ASD"],
        "Aggression Level": [1, 2, 3, 1, 2],
        "หมายเหตุ": ["", "", "", "", ""]
    })

# ใช้ชื่อตัวแปรตรงกับที่ประกาศข้างล่างนี้เจ้า (column_configuration)
column_configuration = {
    "ลำดับ": st.column_config.NumberColumn("ลำดับ", width="small"),
    "name": st.column_config.TextColumn("ชื่อ", width="medium"),
    "Diagnosis": st.column_config.TextColumn("การวินิจฉัย", width="medium"),
    "Aggression Level": st.column_config.NumberColumn("ระดับความรุนแรง", format="%d"),
    "หมายเหตุ": st.column_config.TextColumn("หมายเหตุ", width="large", default="")
}

# 6. โหมดแก้ไข
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

col1, col2 = st.columns([10, 1])
with col2:
    if st.button("แก้ไข" if not st.session_state.edit_mode else "บันทึก"):
        st.session_state.edit_mode = not st.session_state.edit_mode
        st.rerun()

# 7. แสดงผลและอัปเดตข้อมูล
if st.session_state.edit_mode:
    st.write("โหมดแก้ไขข้อมูล:")
    # ใช้ column_configuration ให้ตรงกับที่ประกาศไว้
    edited_df = st.data_editor(
        st.session_state.patient_df, 
        column_config=column_configuration,
        num_rows="dynamic", 
        use_container_width=True
    )
    st.session_state.patient_df = edited_df 
else:
    st.dataframe(
        st.session_state.patient_df, 
        column_config=column_configuration,
        use_container_width=True, 
        hide_index=True
    )


