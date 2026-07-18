import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(layout="wide", page_title="Profile | iKid Secure")

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# 1. ดึงข้อมูล
patient_id = st.session_state.get("target_patient_id")
patient = supabase.table("patients").select("*").eq("id", patient_id).execute().data[0]
assess_res = supabase.table("assessments").select("*").eq("patient_id", patient_id).order("created_at", desc=True).execute()
df = pd.DataFrame(assess_res.data)

st.title(f"👤 ประวัติ: {patient.get('name')}")

# 2. โซนสรุป (จัดวางแบบปกติที่ไอด้าชอบ ไม่ใช้ CSS ให้งงเจ้า)
st.subheader("📊 สรุปข้อมูลล่าสุด")
if not df.empty:
    latest = df.iloc[0]
    col1, col2, col3 = st.columns(3)
    col1.metric("จำนวนครั้ง (Incident)", latest.get('incident_count', 0))
    col2.metric("ระดับความรุนแรง", latest.get('aggression_level', '-'))
    col3.metric("พฤติกรรมล่าสุด", latest.get('behavior_note', '-'))
else:
    st.info("ยังไม่มีข้อมูล")

st.divider()

# 3. โซนแก้ไข (ทำปุ่มกดแก้ไข เหมือน Dashboard แรกๆ เลยเจ้า)
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

st.subheader("📜 ประวัติย้อนหลัง")
if not df.empty:
    if not st.session_state.edit_mode:
        st.dataframe(df.drop(columns=['id', 'patient_id'], errors='ignore'), use_container_width=True)
        if st.button("✏️ แก้ไขข้อมูล"):
            st.session_state.edit_mode = True
            st.rerun()
    else:
        # โหมดแก้ไข
        edited_df = st.data_editor(df, column_config={"id": None, "patient_id": None}, use_container_width=True)
        if st.button("💾 บันทึกข้อมูล"):
            try:
                records = edited_df.to_dict(orient='records')
                supabase.table("assessments").upsert(records).execute()
                st.session_state.edit_mode = False
                st.success("บันทึกเรียบร้อย!")
                st.rerun()
            except Exception as e:
                st.error(f"บันทึกไม่ได้: {e}")
        if st.button("❌ ยกเลิก"):
            st.session_state.edit_mode = False
            st.rerun()
else:
    st.info("ยังไม่มีข้อมูลประวัติย้อนหลัง")

if st.button("⬅️ กลับหน้ารายชื่อ"):
    st.session_state.edit_mode = False
    st.switch_page("pages/1_Dashboard.py")
