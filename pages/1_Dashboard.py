import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(layout="wide", page_title="iKid Secure")

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("app.py") 

# เชื่อมต่อ Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ฟังก์ชันดึงข้อมูล
def fetch_data():
    response = supabase.table("patients").select("*").execute()
    if response.data and len(response.data) > 0:
        return pd.DataFrame(response.data)
    else:
        # กรณีตารางว่าง ให้สร้าง DataFrame เริ่มต้นที่ตรงกับโครงสร้างฐานข้อมูล
        return pd.DataFrame({
            "id": [1], 
            "name": ["ตัวอย่าง"],
            "diagnosis": ["None"],
            "aggression_level": [0],
            "หมายเหตุ": [""]
        })

if "patient_df" not in st.session_state:
    st.session_state.patient_df = fetch_data()

# CSS ตกแต่ง
st.markdown("""<style>
    [data-testid="stDataEditor"] td, [data-testid="stDataFrame"] td { text-align: center !important; }
</style>""", unsafe_allow_html=True)

st.title("📋 รายชื่อผู้ป่วย")

# ตั้งค่าคอลัมน์ให้ตรงกับชื่อใน Supabase
column_configuration = {
    "id": st.column_config.NumberColumn("ลำดับ", width="small"),
    "name": st.column_config.TextColumn("ชื่อ", width="medium"),
    "diagnosis": st.column_config.TextColumn("การวินิจฉัย", width="medium"),
    "aggression_level": st.column_config.NumberColumn("ระดับความรุนแรง", format="%d"),
    "หมายเหตุ": st.column_config.TextColumn("หมายเหตุ", width="large")
}

# โหมดแก้ไข
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

if st.button("แก้ไข" if not st.session_state.edit_mode else "บันทึก"):
    if st.session_state.edit_mode:
        # บันทึกลง Supabase
        data_to_save = st.session_state.patient_df.to_dict(orient='records')
        supabase.table("patients").upsert(data_to_save).execute()
        st.success("บันทึกข้อมูลเรียบร้อยเจ้า!")
        # รีโหลดข้อมูลล่าสุดจากฐานข้อมูล
        st.session_state.patient_df = fetch_data()
    
    st.session_state.edit_mode = not st.session_state.edit_mode
    st.rerun()

# แสดงผลข้อมูล
if st.session_state.edit_mode:
    st.session_state.patient_df = st.data_editor(
        st.session_state.patient_df, 
        column_config=column_configuration,
        num_rows="dynamic", 
        use_container_width=True
    )
else:
    st.dataframe(
        st.session_state.patient_df, 
        column_config=column_configuration,
        use_container_width=True, 
        hide_index=True
    )



