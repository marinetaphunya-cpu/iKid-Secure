import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(layout="wide", page_title="Profile | iKid Secure")

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# 1. ดึง ID จาก Query Params
patient_id = st.query_params.get("patient_id")
# 1. รับ ID จาก Query Params
patient_id = st.query_params.get("patient_id")

st.write(f"DEBUG: patient_id คือ {patient_id}") 

if not patient_id:
    st.error("ไม่พบข้อมูลผู้ป่วย")
    if st.button("กลับ"): st.switch_page("pages/1_Dashboard.py")
    st.stop()

# 2. ดึงข้อมูล 2 ตาราง
# ดึงข้อมูลคนไข้
patient_res = supabase.table("patients").select("*").eq("id", patient_id).execute()
patient = patient_res.data[0] if patient_res.data else None

# ดึงข้อมูลประเมิน (ของคนไข้คนนี้คนเดียว)
assess_res = supabase.table("assessments").select("*").eq("patient_id", patient_id).order("created_at", desc=True).execute()
assessments = assess_res.data

if not patient:
    st.error("ไม่พบข้อมูลผู้ป่วยในระบบ")
    st.stop()

st.title(f"📋 ประวัติ: {patient.get('name', 'ไม่ระบุชื่อ')}")

# 3. แสดงข้อมูลสรุป
col1, col2 = st.columns(2)
with col1:
    st.write(f"**การวินิจฉัย:** {patient.get('diagnosis', '-')}")
    st.write(f"**หมายเหตุส่วนตัว:** {patient.get('หมายเหตุ', '-')}")

with col2:
    if assessments:
        latest = assessments[0]
        st.write(f"**จำนวนครั้งความรุนแรงล่าสุด:** {latest.get('incident_count', 0)} ครั้ง")
        st.metric("ระดับความรุนแรงล่าสุด", latest.get('aggression_level', 0))
    else:
        st.info("ยังไม่มีประวัติการประเมิน")

st.divider()

# 4. แสดงตารางประวัติย้อนหลัง
if assessments:
    st.subheader("ประวัติการประเมินย้อนหลัง")
    df_assess = pd.DataFrame(assessments)
    # แสดงคอลัมน์ตามชื่อจริงใน Supabase
    st.table(df_assess[['created_at', 'incident_count', 'aggression_level', 'behavior_note']])
else:
    st.info("ยังไม่มีข้อมูลการประเมินในระบบ")

st.divider()

# 5. ปุ่มนำทาง
if st.button("ไปยังหน้าประเมินใหม่ (Evaluation)"):
    st.query_params["patient_id"] = patient_id
    st.switch_page("pages/3_Evaluation.py")

if st.button("กลับไปหน้ารายชื่อ"):
    st.switch_page("pages/1_Dashboard.py")
