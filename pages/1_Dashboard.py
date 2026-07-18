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

# ส่วนเลือกผู้ป่วย
if not st.session_state.patient_df.empty:
    selected_name = st.selectbox("เลือกชื่อผู้ป่วยเพื่อดูประวัติ", st.session_state.patient_df["name"])
    if st.button("ไปหน้าประวัติของคนนี้"):
        patient_row = st.session_state.patient_df[st.session_state.patient_df["name"] == selected_name]
        st.query_params["patient_id"] = patient_row["id"].iloc[0]
        st.switch_page("pages/2_Profile.py")
else:
    st.write("กำลังโหลดข้อมูล...")

# 5. & 6. แก้ไขและบันทึกข้อมูลแบบใช้ Form
if st.session_state.get('edit_mode', False):
    with st.form("edit_form"):
        st.info("แก้ไขข้อมูลเสร็จแล้วอย่าลืมกดปุ่มบันทึกด้านล่าง")
        
        # ตัวแก้ไขข้อมูล
        new_df = st.data_editor(
            st.session_state.patient_df,
            column_order=("id", "name", "diagnosis", "aggression_level", "หมายเหตุ"),
            num_rows="dynamic",
            use_container_width=True
        )
        
        # ปุ่มบันทึก (แก้การย่อหน้าให้ตรงกับ with st.form)
                # ปุ่มบันทึก
        if st.form_submit_button("บันทึกข้อมูล"):
            try:
                # 1. เปลี่ยนค่า NaN (ช่องว่าง) ให้กลายเป็น None (เพื่อให้เป็นค่าว่างที่ Supabase ยอมรับ)
                new_df = new_df.where(pd.notnull(new_df), None)
                
                # 2. แปลงคอลัมน์ตัวเลข
                cols_to_fix = ['id', 'aggression_level'] 
                for col in cols_to_fix:
                    if col in new_df.columns:
                        # ใช้ errors='coerce' เพื่อเปลี่ยนค่าที่ว่างให้เป็น 0 แทนที่จะเป็น NaN
                        new_df[col] = pd.to_numeric(new_df[col], errors='coerce').fillna(0).astype(int)

                # บันทึกลง Supabase
                data_to_save = new_df.to_dict(orient='records')
                supabase.table("patients").upsert(data_to_save).execute()
                
                # อัปเดต state
                st.session_state.patient_df = new_df
                st.success("บันทึกข้อมูลเรียบร้อย!")
                st.session_state.edit_mode = False
                st.rerun() 
            except Exception as e:
                st.error(f"บันทึกพลาด: {e}")


else:
    # โหมดแสดงผลปกติ
    st.dataframe(st.session_state.patient_df, column_order=("id", "name", "diagnosis", "aggression_level", "หมายเหตุ"), use_container_width=True)
    
    if st.button("แก้ไข"):
        st.session_state.edit_mode = True
        st.rerun()



