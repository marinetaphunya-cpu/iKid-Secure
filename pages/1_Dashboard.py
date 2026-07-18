import streamlit as st
import pandas as pd
from supabase import create_client

# 1. ตั้งค่าพื้นฐาน
st.set_page_config(layout="wide", page_title="iKid Secure")

# 2. เช็กสิทธิ์
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("app.py") 

# 3. เชื่อมต่อ Supabase (ดึงค่าจาก Secrets)
# เราจะสร้าง client ไว้ที่นี่เลย
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

st.title("📋 รายชื่อผู้ป่วย")

# 4. ฟังก์ชันดึงข้อมูล (แบบไม่ใช้ cache รบกวนการทำงาน)
def get_data_from_db():
    try:
        response = supabase.table("patients").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"เกิดปัญหาในการดึงข้อมูล: {e}")
        return pd.DataFrame()

# กำหนดข้อมูลเริ่มต้นใน session_state
if "patient_df" not in st.session_state:
    st.session_state.patient_df = get_data_from_db()

# 5. ส่วนควบคุม
if st.button("แก้ไข" if not st.session_state.get('edit_mode', False) else "บันทึก"):
    if st.session_state.get('edit_mode', False):
        # กดบันทึก
        try:
            data_to_save = st.session_state.patient_df.to_dict(orient='records')
            supabase.table("patients").upsert(data_to_save).execute()
            st.success("บันทึกข้อมูลเรียบร้อย!")
            # ดึงข้อมูลใหม่มาทับ
            st.session_state.patient_df = get_data_from_db()
        except Exception as e:
            st.error(f"บันทึกข้อมูลพลาด: {e}")
    
    st.session_state.edit_mode = not st.session_state.get('edit_mode', False)
    st.rerun()

# 6. แสดงผล
if st.session_state.get('edit_mode', False):
    st.session_state.patient_df = st.data_editor(
        st.session_state.patient_df,
        column_order=("id", "name", "diagnosis", "หมายเหตุ"),
        num_rows="dynamic", 
        use_container_width=True
    )
else:
    st.dataframe(st.session_state.patient_df, use_container_width=True)





