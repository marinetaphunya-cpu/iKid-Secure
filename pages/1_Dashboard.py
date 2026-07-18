import streamlit as st
import pandas as pd
from supabase import create_client

# 1. ตั้งค่าพื้นฐาน
st.set_page_config(layout="wide", page_title="iKid Secure")

# 2. เช็กสิทธิ์
if "authenticated" not in st.session_state or not st.session_state.get("authenticated"):
    st.switch_page("app.py") 

# 3. เชื่อมต่อ Supabase
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# 4. ฟังก์ชันดึงข้อมูล
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

st.title("📋 รายชื่อผู้ป่วย")

# ส่วนเลือกผู้ป่วย (ย้ายมาไว้ใต้ Title)
if not st.session_state.patient_df.empty:
    selected_name = st.selectbox("เลือกชื่อผู้ป่วยเพื่อดูประวัติ", st.session_state.patient_df["name"])
    if st.button("ไปหน้าประวัติของคนนี้"):
        patient_row = st.session_state.patient_df[st.session_state.patient_df["name"] == selected_name]
        st.query_params["patient_id"] = patient_row["id"].iloc[0]
        st.switch_page("pages/2_Profile.py")
else:
    st.write("กำลังโหลดข้อมูล...")

# 5. ส่วนควบคุม (แก้ไข/บันทึก)
# เราใช้ปุ่มเดียวสลับกัน แต่เราจะไม่ rerurn ทันทีในปุ่มบันทึก เพื่อป้องกันข้อมูลหาย
if st.button("แก้ไข" if not st.session_state.get('edit_mode', False) else "บันทึก"):
    if st.session_state.get('edit_mode', False):
        # กดบันทึก: ระบบจะใช้ค่าที่อยู่ใน st.session_state.patient_df ปัจจุบันไปบันทึก
        try:
            data_to_save = st.session_state.patient_df.to_dict(orient='records')
            supabase.table("patients").upsert(data_to_save).execute()
            st.success("บันทึกข้อมูลเรียบร้อย!")
            st.session_state.patient_df = get_data_from_db() # ดึงใหม่
        except Exception as e:
            st.error(f"บันทึกพลาด: {e}")
    
    st.session_state.edit_mode = not st.session_state.get('edit_mode', False)
    st.rerun()

# 6. แสดงผล (ใช้ column_order ตามที่ไอด้าต้องการ)
cols_to_show = ("id", "name", "diagnosis", "aggression_level", "หมายเหตุ")

if st.session_state.get('edit_mode', False):
    st.info("กำลังอยู่ในโหมดแก้ไข...")
    st.session_state.patient_df = st.data_editor(
        st.session_state.patient_df,
        column_order=cols_to_show,
        num_rows="dynamic", 
        use_container_width=True
    )
else:
    st.dataframe(st.session_state.patient_df, column_order=cols_to_show, use_container_width=True)




