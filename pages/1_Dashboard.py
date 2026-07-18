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

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# ฟังก์ชันดึงข้อมูลสดๆ จากฐานข้อมูล
def get_data_from_db():
    try:
        response = supabase.table("patients").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"ดึงข้อมูลไม่ได้เจ้า: {e}")
        return pd.DataFrame()

df = get_data_from_db()

# หัวข้อพร้อมปุ่มทางลัดดูสถิติ
c1, c2 = st.columns([4, 1])
with c1:
    st.title("🩺 ระบบจัดการข้อมูลผู้ป่วย iKid Secure 💜")
with c2:
    st.write("") # เว้นระยะให้ปุ่มตรงกับหัวข้อ
    st.write("")
    if st.button("📈 ดูสถิติภาพรวม", use_container_width=True, type="primary"):
        # ตรงนี้ไอด้าเช็คชื่อไฟล์ให้ชัวร์นะเจ้าว่าเป็น "pages/5_Static.py" หรือ "pages/5_Statistics.py"
        st.switch_page("pages/5_Static.py")

st.markdown("---")

# ส่วนเลือกผู้ป่วย
col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("🔍 ค้นหาประวัติผู้ป่วย")
    if not df.empty:
        patient_names = ["-- โปรดเลือกชื่อผู้ป่วย --"] + df["name"].tolist()
        selected_name = st.selectbox("พิมพ์ค้นหาชื่อผู้ป่วย", patient_names)
        
        if selected_name != "-- โปรดเลือกชื่อผู้ป่วย --":
            if st.button(f"🚀 ไปยังหน้าประวัติของ: {selected_name}"):
                patient_row = df[df["name"] == selected_name]
                p_id = str(patient_row["id"].iloc[0])
                st.session_state["target_patient_id"] = p_id
                st.switch_page("pages/2_Profile.py")
    else:
        st.info("ไม่พบข้อมูลคนไข้ในระบบเจ้า ✨")

# ส่วนแสดงภาพสรุป
with col2:
    st.success(f"จำนวนผู้ป่วยในความดูแลทั้งหมด: **{len(df)} คน** 🧸")

st.divider()

# 5. โหมดแก้ไขข้อมูลผู้ป่วย
st.subheader("✍️ ฐานข้อมูลผู้ป่วย (แก้ไข/เพิ่มรายชื่อ)")
if st.session_state.get('edit_mode', False):
    with st.container(border=True):
        st.info("💡 กรอกข้อมูลในช่องด้านล่าง แล้วกดบันทึกเพื่ออัปเดตระบบ")
        new_df = st.data_editor(
            df,
            column_order=("id", "name", "diagnosis", "aggression_level", "หมายเหตุ"),
            num_rows="dynamic",
            use_container_width=True
        )
        
        c_save, c_cancel = st.columns(2)
        if c_save.button("💾 บันทึกการเปลี่ยนแปลง"):
            try:
                df_clean = new_df.replace({np.nan: None})
                supabase.table("patients").upsert(df_clean.to_dict(orient='records')).execute()
                st.success("บันทึกข้อมูลเรียบร้อย! ระบบอัปเดตแล้วเจ้า ✨")
                st.session_state.edit_mode = False
                st.rerun()
            except Exception as e:
                st.error(f"บันทึกพลาดเจ้า: {e}")
        if c_cancel.button("❌ ยกเลิก"):
            st.session_state.edit_mode = False
            st.rerun()
else:
    # แสดงตารางสวยๆ
    st.dataframe(
        df, 
        column_order=("id", "name", "diagnosis", "aggression_level", "หมายเหตุ"),
        use_container_width=True,
        hide_index=True
    )
    if st.button("✏️ เข้าโหมดแก้ไขรายชื่อ"):
        st.session_state.edit_mode = True
        st.rerun()


