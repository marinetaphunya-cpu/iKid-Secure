import streamlit as st
import pandas as pd
from supabase import create_client

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(layout="wide", page_title="iKid Secure")

# 2. เช็กสิทธิ์การ Login (ยึดตามโครงสร้างเดิมของไอด้า)
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("app.py") 

# 3. เชื่อมต่อ Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ฟังก์ชันดึงข้อมูลแบบปลอดภัย
def fetch_data():
    try:
        response = supabase.table("patients").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            # ตรวจสอบคอลัมน์ให้ครบ ถ้าไม่มีให้สร้างค่าว่าง
            for col in ["id", "name", "diagnosis", "aggression_level", "หมายเหตุ"]:
                if col not in df.columns:
                    df[col] = None
            return df
    except Exception as e:
        st.error(f"การเชื่อมต่อฐานข้อมูล: {e}")
    return pd.DataFrame(columns=["id", "name", "diagnosis", "aggression_level", "หมายเหตุ"])

if "patient_df" not in st.session_state:
    st.session_state.patient_df = fetch_data()

# 4. CSS ตกแต่ง
st.markdown("""<style>
    [data-testid="stDataEditor"] td, [data-testid="stDataFrame"] td { text-align: center !important; }
</style>""", unsafe_allow_html=True)

st.title("📋 รายชื่อผู้ป่วย")

# กำหนด Config ตาราง
config = {
    "id": st.column_config.NumberColumn("ลำดับ", width="small"),
    "name": st.column_config.TextColumn("ชื่อ", width="medium"),
    "diagnosis": st.column_config.TextColumn("การวินิจฉัย", width="medium"),
    "aggression_level": st.column_config.NumberColumn("ระดับความรุนแรง", format="%d"),
    "หมายเหตุ": st.column_config.TextColumn("หมายเหตุ", width="large")
}

# 5. โหมดแก้ไข
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

if st.button("แก้ไข" if not st.session_state.edit_mode else "บันทึก"):
    if st.session_state.edit_mode:
        # บันทึกลง Supabase
        data_to_save = st.session_state.patient_df.to_dict(orient='records')
        supabase.table("patients").upsert(data_to_save).execute()
        st.success("บันทึกข้อมูลสำเร็จเจ้า!")
        # รีโหลดข้อมูลใหม่
        st.session_state.patient_df = fetch_data()
    
    st.session_state.edit_mode = not st.session_state.edit_mode
    st.rerun()

# 6. แสดงผล
if st.session_state.edit_mode:
    st.session_state.patient_df = st.data_editor(
        st.session_state.patient_df, 
        column_config=config,
        num_rows="dynamic", 
        use_container_width=True
    )
else:
    st.dataframe(
        st.session_state.patient_df, 
        column_config=config,
        use_container_width=True, 
        hide_index=True
    )




