import streamlit as st
import pandas as pd
import numpy as np # เพิ่มตัวนี้มาช่วยจัดการค่าว่าง
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

# กำหนดข้อมูลเริ่มต้น
if "patient_df" not in st.session_state:
    st.session_state.patient_df = get_data_from_db()

st.title("📋 รายชื่อผู้ป่วย")

# ส่วนเลือกผู้ป่วย
if not st.session_state.patient_df.empty:
    selected_name = st.selectbox("เลือกชื่อผู้ป่วยเพื่อดูประวัติ", st.session_state.patient_df["name"])
    if st.button("ไปหน้าประวัติของคนนี้"):
        patient_row = st.session_state.patient_df[st.session_state.patient_df["name"] == selected_name]
        st.query_params["patient_id"] = patient_row["id"].iloc[0]
        st.switch_page("pages/2_Profile.py")
else:
    st.write("กำลังโหลดข้อมูล...")

# 5. แก้ไขและบันทึก
if st.session_state.get('edit_mode', False):
    with st.form("edit_form"):
        st.info("แก้ไขข้อมูลเสร็จแล้วอย่าลืมกดปุ่มบันทึกด้านล่าง")
        
        new_df = st.data_editor(
            st.session_state.patient_df,
            column_order=("id", "name", "diagnosis", "aggression_level", "หมายเหตุ"),
            num_rows="dynamic",
            use_container_width=True
        )
        
        if st.form_submit_button("บันทึกข้อมูล"):
            try:
                # แก้ไขแบบเด็ดขาด: เปลี่ยน NaN ทั้งหมดใน DataFrame ให้เป็น None
                df_clean = new_df.replace({np.nan: None})
                
                # บังคับคอลัมน์ที่เป็นตัวเลขให้เป็น int (ถ้าว่างให้เป็น 0)
                for col in ['id', 'aggression_level']:
                    if col in df_clean.columns:
                        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0).astype(int)
                
                # แปลงเป็น list ของ dicts เพื่ออัปโหลด
                data_to_save = df_clean.to_dict(orient='records')
                
                # ลบค่า None ออกจาก dictionary ก่อนอัปโหลด (ถ้า Supabase ไม่ชอบค่าว่าง)
                data_to_save = [{k: v for k, v in row.items() if v is not None} for row in data_to_save]
                
                supabase.table("patients").upsert(data_to_save).execute()
                
                st.session_state.patient_df = get_data_from_db() # โหลดใหม่จากฐานข้อมูล
                st.success("บันทึกข้อมูลเรียบร้อย!")
                st.session_state.edit_mode = False
                st.rerun() 
            except Exception as e:
                st.error(f"บันทึกพลาด: {e}")

else:
    st.dataframe(st.session_state.patient_df, column_order=("id", "name", "diagnosis", "aggression_level", "หมายเหตุ"), use_container_width=True)
    if st.button("แก้ไข"):
        st.session_state.edit_mode = True
        st.rerun()

