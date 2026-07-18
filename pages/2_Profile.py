import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(layout="wide", page_title="Profile | iKid Secure")

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

patient_id = st.session_state.get("target_patient_id")
patient = supabase.table("patients").select("*").eq("id", patient_id).execute().data[0]
assess_res = supabase.table("assessments").select("*").eq("patient_id", patient_id).order("created_at", desc=True).execute()
df = pd.DataFrame(assess_res.data)

st.title(f"👤 ประวัติ: {patient.get('name')}")

# โซนสรุป
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

# ปุ่มนำทางไปประเมิน (วางไว้ตรงกลางโดดๆ)
st.write("###") # เว้นบรรทัด
col_c1, col_c2, col_c3 = st.columns([1, 2, 1]) # แบ่ง 3 ส่วน เอาไว้ตรงกลาง
with col_c2:
    if st.button("🚀 แบบประเมิน (Evaluation)", use_container_width=True):
        st.session_state["target_patient_id"] = patient_id
        st.switch_page("pages/3_Evaluation.py")
st.write("###")

st.divider()

# โซนประวัติย้อนหลัง + ปุ่มชิดซ้าย
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
        edited_df = st.data_editor(df, column_config={"id": None, "patient_id": None}, use_container_width=True)
        col_b1, col_b2 = st.columns(2)
        if col_b1.button("💾 บันทึกข้อมูล"):
            records = edited_df.to_dict(orient='records')
            supabase.table("assessments").upsert(records).execute()
            st.session_state.edit_mode = False
            st.rerun()
        if col_b2.button("❌ ยกเลิก"):
            st.session_state.edit_mode = False
            st.rerun()

# ปุ่มกลับชิดซ้าย
if st.button("⬅️ กลับหน้ารายชื่อ"):
    st.session_state.edit_mode = False
    st.switch_page("pages/1_Dashboard.py")
