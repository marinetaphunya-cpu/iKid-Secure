import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(layout="wide", page_title="iKid Secure")

# เชื่อมต่อ Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def fetch_data():
    try:
        # ดึงข้อมูลทั้งหมด
        response = supabase.table("patients").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            # ปรับให้คอลัมน์ id เป็นตัวเลข เพื่อป้องกันบั๊กเวลาส่งกลับ
            df['id'] = df['id'].astype(int)
            return df
    except Exception as e:
        st.error(f"เชื่อมต่อฐานข้อมูลไม่ได้: {e}")
    
    # ถ้าดึงไม่ได้ ให้คืนค่า DataFrame ว่างที่มีคอลัมน์ครบ
    return pd.DataFrame(columns=["id", "name", "diagnosis", "aggression_level", "หมายเหตุ"])

if "patient_df" not in st.session_state:
    st.session_state.patient_df = fetch_data()

st.title("📋 รายชื่อผู้ป่วย")

column_configuration = {
    "id": st.column_config.NumberColumn("ลำดับ", width="small"),
    "name": st.column_config.TextColumn("ชื่อ", width="medium"),
    "diagnosis": st.column_config.TextColumn("การวินิจฉัย", width="medium"),
    "aggression_level": st.column_config.NumberColumn("ระดับความรุนแรง", format="%d"),
    "หมายเหตุ": st.column_config.TextColumn("หมายเหตุ", width="large")
}

if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

if st.button("แก้ไข" if not st.session_state.edit_mode else "บันทึก"):
    if st.session_state.edit_mode:
        # กดบันทึก: แปลงข้อมูลเป็น List of Dictionaries
        data_to_save = st.session_state.patient_df.to_dict(orient='records')
        # ใช้ upsert เพื่ออัปเดตหรือเพิ่มข้อมูล
        supabase.table("patients").upsert(data_to_save).execute()
        st.success("บันทึกข้อมูลเรียบร้อย!")
        st.session_state.patient_df = fetch_data()
    
    st.session_state.edit_mode = not st.session_state.edit_mode
    st.rerun()

# ส่วนแสดงผล
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




