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

# ดึงข้อมูลจาก Supabase (ถ้ายังไม่มีใน session)
def fetch_data():
    response = supabase.table("patients").select("*").execute()
    if response.data:
        return pd.DataFrame(response.data)
    else:
        # ถ้าไม่มีข้อมูลใน Supabase ให้ใช้ค่าเริ่มต้น
        return pd.DataFrame({
            "ลำดับ": [1, 2, 3, 4, 5], 
            "name": ["A", "B", "C", "D", "E"],
            "Diagnosis": ["Depression", "ASD", "ASD", "ADHD", "ASD"],
            "Aggression Level": [1, 2, 3, 1, 2],
            "หมายเหตุ": ["", "", "", "", ""]
        })

if "patient_df" not in st.session_state:
    st.session_state.patient_df = fetch_data()

# CSS ตกแต่ง
st.markdown("""<style>
    [data-testid="stDataEditor"] td, [data-testid="stDataFrame"] td { text-align: center !important; }
</style>""", unsafe_allow_html=True)

st.title("📋 รายชื่อผู้ป่วย")

# แก้ชื่อให้ตรงกับ Supabase 100%
column_configuration = {
    "id": st.column_config.NumberColumn("ลำดับ", width="small"),
    "name": st.column_config.TextColumn("ชื่อ", width="medium"),
    "aggression_level": st.column_config.NumberColumn("ระดับความรุนแรง", format="%d"),
    "หมายเหตุ": st.column_config.TextColumn("หมายเหตุ", width="large")
}


# โหมดแก้ไข
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

if st.button("แก้ไข" if not st.session_state.edit_mode else "บันทึก"):
    if st.session_state.edit_mode:
        # กดบันทึก: ส่งข้อมูลไป Supabase
        # ต้องแน่ใจว่าตารางใน Supabase ชื่อ "patients" และมีคอลัมน์ตรงกัน
        data_to_save = st.session_state.patient_df.to_dict(orient='records')
        supabase.table("patients").upsert(data_to_save).execute()
        st.success("บันทึกลงฐานข้อมูลแล้วเจ้า!")
    st.session_state.edit_mode = not st.session_state.edit_mode
    st.rerun()

# แสดงผล
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



