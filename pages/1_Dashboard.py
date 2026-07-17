import streamlit as st
import pandas as pd
import time
from supabase import create_client

# 1. ตั้งค่าหน้าเพจ (ต้องอยู่บนสุด)
st.set_page_config(layout="wide", page_title="iKid Secure")

# 2. เช็กสิทธิ์การ Login
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("app.py") 

# 3. เชื่อมต่อ Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# 4. รวม CSS ตกแต่ง (จัดกลางและปุ่ม)
st.markdown("""
    <style>
    .stDataFrame, .stDataEditor { 
        border: 2px solid #A8DADC; 
        border-radius: 10px; 
    }
    /* บังคับตารางให้อยู่ตรงกลาง */
    div[data-testid="stDataFrame"] table {
        margin-left: auto; margin-right: auto;
    }
    /* ตกแต่งปุ่ม */
    div.stButton > button { 
        background-color: #F1FAEE; 
        border: 1px solid #A8DADC; 
        color: #1D3557; 
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 5. หัวข้อ
st.title("📋 รายชื่อผู้ป่วย")

# ข้อมูล (พี่ใส่คอมม่าให้เรียบร้อยแล้วเจ้า)
data = {
    "ลำดับ": [1, 2, 3, 4, 5], 
    "name": ["A", "B", "C", "D", "E"],
    "Diagnosis": ["Depression", "ASD", "ASD", "ADHD", "ASD"],
    "Aggression Level": [1, 2, 3, 1, 2],
    "หมายเหตุ": ["-", "-", "-", "-", "-"]
}
df = pd.DataFrame(data)

# กำหนดการจัดคอลัมน์ (ให้ข้อมูลอยู่ตรงกลางสวยๆ)
column_configuration = {
    "ลำดับ": st.column_config.NumberColumn("ลำดับ", width="small"),
    "name": st.column_config.TextColumn("ชื่อ", width="medium"),
    "Diagnosis": st.column_config.TextColumn("การวินิจฉัย", width="medium"),
    "Aggression Level": st.column_config.NumberColumn("ระดับความรุนแรง", format="%d"),
    "หมายเหตุ": st.column_config.TextColumn("หมายเหตุ", width="large")
}

# 6. โหมดแก้ไข
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

# ปุ่มควบคุม
col1, col2 = st.columns([10, 1])
with col2:
    if st.button("แก้ไข" if not st.session_state.edit_mode else "บันทึก"):
        if st.session_state.edit_mode:
            with st.spinner('กำลังบันทึก...'):
                time.sleep(1)
                st.session_state.edit_mode = False
                st.rerun()
        else:
            st.session_state.edit_mode = True
            st.rerun()

# 7. แสดงผลข้อมูล
# ปรับแก้ช่วงที่ 7 แสดงผลข้อมูล
if st.session_state.edit_mode:
    st.write("โหมดแก้ไขข้อมูล:")
    # เพิ่ม num_rows="dynamic" เพื่อให้เพิ่ม/ลบแถวได้
    edited_df = st.data_editor(
        df, 
        column_config={
            "ลำดับ": st.column_config.NumberColumn("ลำดับ", width="small", help="เลขลำดับผู้ป่วย"),
            "name": st.column_config.TextColumn("ชื่อ", width="medium"),
            "Diagnosis": st.column_config.TextColumn("การวินิจฉัย", width="medium"),
            "Aggression Level": st.column_config.NumberColumn("ระดับความรุนแรง", format="%d"),
            "หมายเหตุ": st.column_config.TextColumn("หมายเหตุ", width="large")
        },
        # ใช้คำสั่งนี้เพื่อบังคับให้ทุกคอลัมน์อยู่ตรงกลาง!
        column_order=("ลำดับ", "name", "Diagnosis", "Aggression Level", "หมายเหตุ"),
        num_rows="dynamic", 
        use_container_width=True
    )
    # เพิ่ม CSS เสริมเพื่อความชัวร์ (เอาไปใส่ใน st.markdown เดิมของไอด้าได้เลย)
else:
    st.dataframe(
        df, 
        column_config={
            "ลำดับ": st.column_config.NumberColumn("ลำดับ", width="small"),
            "name": st.column_config.TextColumn("ชื่อ", width="medium"),
            "Diagnosis": st.column_config.TextColumn("การวินิจฉัย", width="medium"),
            "Aggression Level": st.column_config.NumberColumn("ระดับความรุนแรง", format="%d"),
            "หมายเหตุ": st.column_config.TextColumn("หมายเหตุ", width="large")
        },
        use_container_width=True, 
        hide_index=True
    )



