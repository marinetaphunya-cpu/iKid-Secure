import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(layout="wide", page_title="Profile | iKid Secure")

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# 1. รับ ID จาก session_state
patient_id = st.session_state.get("target_patient_id")

if not patient_id:
    st.error("ไม่พบข้อมูลผู้ป่วย กรุณากลับไปเลือกชื่อผู้ป่วยอีกครั้งเจ้า")
    if st.button("กลับไปหน้ารายชื่อ"): 
        st.switch_page("pages/1_Dashboard.py")
    st.stop()

# 2. ดึงข้อมูล
try:
    patient_res = supabase.table("patients").select("*").eq("id", patient_id).execute()
    patient = patient_res.data[0] if patient_res.data else None
    
    # ดึงข้อมูลจาก assessments
    assess_res = supabase.table("assessments").select("*").eq("patient_id", patient_id).order("created_at", desc=True).execute()
    assessments = assess_res.data
except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
    st.stop()

if not patient:
    st.error("ไม่พบข้อมูลผู้ป่วยในระบบ")
    st.stop()

st.title(f"📋 ประวัติ: {patient.get('name', 'ไม่ระบุชื่อ')}")

# 3. แสดงข้อมูลสรุป
col1, col2 = st.columns(2)
with col1:
    st.write(f"**การวินิจฉัย:** {patient.get('diagnosis', '-')}")
    st.write(f"**หมายเหตุ:** {patient.get('หมายเหตุ', '-')}")

with col2:
    if assessments:
        latest = assessments[0]
        # ใช้ .get() เพื่อป้องกันกรณีไม่มีคอลัมน์ในฐานข้อมูล
        st.write(f"**จำนวนครั้งความรุนแรงล่าสุด:** {latest.get('incident_count', 0)} ครั้ง")
        st.metric("ระดับความรุนแรงล่าสุด", latest.get('aggression_level', 0))
    else:
        st.info("ยังไม่มีประวัติการประเมิน")

st.divider()

# 4. แสดงตารางประวัติย้อนหลัง
if assessments:
    st.subheader("ประวัติการประเมินย้อนหลัง")
    df_assess = pd.DataFrame(assessments)
    
    # เลือกเฉพาะคอลัมน์ที่มีอยู่จริง เพื่อป้องกัน Error
    available_cols = [c for c in ['created_at', 'incident_count', 'aggression_level', 'behavior_note'] if c in df_assess.columns]
    st.table(df_assess[available_cols])
else:
    st.info("ยังไม่มีข้อมูลการประเมินในระบบ")

st.divider()

# 5. ปุ่มนำทาง
if st.button("ไปยังหน้าประเมินใหม่ (Evaluation)"):
    st.session_state["target_patient_id"] = patient_id 
    st.switch_page("pages/3_Evaluation.py")

if st.button("กลับไปหน้ารายชื่อ"):
    st.switch_page("pages/1_Dashboard.py")
