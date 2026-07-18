import streamlit as st
import pandas as pd
import numpy as np
from supabase import create_client

# 1. ตั้งค่าหน้าจอ
st.set_page_config(layout="wide", page_title="iKid Secure | Dashboard")

# 2. เช็กสิทธิ์
if "authenticated" not in st.session_state or not st.session_state.get("authenticated"):
    st.warning("กรุณาเข้าสู่ระบบก่อน! 🐈‍⬛")
    st.switch_page("app.py") 

# 3. เชื่อมต่อ Supabase
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

def get_data_from_db():
    try:
        response = supabase.table("patients").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"ดึงข้อมูลไม่ได้เจ้า: {e}")
        return pd.DataFrame()

if "patient_df" not in st.session_state:
    st.session_state.patient_df = get_data_from_db()

# หัวข้อพร้อมสติกเกอร์
st.title("📋 ระบบจัดการข้อมูลผู้ป่วย iKid Secure 🩺")
st.markdown("---")

# ส่วนเลือกผู้ป่วย
st.subheader("🔍 เลือกผู้ป่วยเพื่อดูประวัติการประเมิน")
if not st.session_state.patient_df.empty:
    # เพิ่มตัวเลือก "โปรดเลือก" ป้องกันการกดผิด
    patient_names = ["-- โปรดเลือกชื่อผู้ป่วย --"] + st.session_state.patient_df["name"].tolist()
    selected_name = st.selectbox("รายชื่อผู้ป่วยในระบบ", patient_names)
    
    if selected_name != "-- โปรดเลือกชื่อผู้ป่วย --":
        if st.button(f"🚀 ไปหน้าประวัติของ: {selected_name}"):
            patient_row = st.session_state.patient_df[st.session_state.patient_df["name"] == selected_name]
            p_id = str(patient_row["id"].iloc[0])
            
            # ส่งค่าให้หน้าถัดไป
            st.session_state["target_patient_id"] = p_id
            st.switch_page("pages/2_Profile.py")
else:
    st.info("กำลังโหลดข้อมูลคนไข้... รอสักครู่ ✨")

st.divider()

# 5. โหมดแก้ไขข้อมูลผู้ป่วย
st.subheader("✍️ แก้ไข/เพิ่มรายชื่อผู้ป่วย")
if st.session_state.get('edit_mode', False):
    with st.form("edit_form"):
        st.info("แก้ไขเสร็จแล้ว อย่าลืมกดปุ่มบันทึกด้านล่าง! 💜")
        new_df = st.data_editor(
            st.session_state.patient_df,
            column_order=("id", "name", "diagnosis", "aggression_level", "หมายเหตุ"),
            num_rows="dynamic",
            use_container_width=True
        )
        
        if st.form_submit_button("💾 บันทึกข้อมูล"):
            try:
                df_clean = new_df.replace({np.nan: None})
                supabase.table("patients").upsert(df_clean.to_dict(orient='records')).execute()
                st.session_state.patient_df = get_data_from_db()
                st.success("บันทึกข้อมูลเรียบร้อย! ✨")
                st.session_state.edit_mode = False
                st.rerun() 
            except Exception as e:
                st.error(f"บันทึกพลาดเจ้า: {e}")
else:
    st.dataframe(st.session_state.patient_df, column_order=("id", "name", "diagnosis", "aggression_level", "หมายเหตุ"), use_container_width=True)
    if st.button("✏️ เข้าโหมดแก้ไข"):
        st.session_state.edit_mode = True
        st.rerun()

