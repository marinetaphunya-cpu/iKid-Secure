import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(layout="wide", page_title="Profile | iKid Secure")

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# 1. รับ ID และดึงข้อมูล
patient_id = st.query_params.get("patient_id")
if not patient_id:
    st.error("ไม่พบข้อมูลผู้ป่วย")
    if st.button("กลับ"): st.switch_page("pages/1_Dashboard.py")
    st.stop()

# ดึงข้อมูลจาก DB
response = supabase.table("patients").select("*").eq("id", patient_id).execute()
patient = response.data[0] if response.data else None

st.title(f"📋 ประวัติ: {patient['name'] if patient else 'ไม่พบข้อมูล'}")

# 2. สถานะแก้ไข
if "profile_edit_mode" not in st.session_state:
    st.session_state.profile_edit_mode = False

# 3. โหมดแก้ไข
if st.session_state.profile_edit_mode:
    with st.form("edit_profile_form"):
        new_diagnosis = st.text_input("การวินิจฉัย", value=patient.get('diagnosis', ''))
        # เพิ่มช่องจำนวนพฤติกรรมความรุนแรง
        new_incident_count = st.number_input("จำนวนครั้งของพฤติกรรมความรุนแรง", value=int(patient.get('incident_count', 0)))
        new_level = st.number_input("ระดับความรุนแรง (1-5)", value=int(patient.get('aggression_level', 0)))
        new_note = st.text_area("หมายเหตุ", value=patient.get('หมายเหตุ', ''))
        
        if st.form_submit_button("บันทึกข้อมูล"):
            try:
                supabase.table("patients").update({
                    "diagnosis": new_diagnosis,
                    "incident_count": new_incident_count,
                    "aggression_level": new_level,
                    "หมายเหตุ": new_note
                }).eq("id", patient_id).execute()
                
                st.success("บันทึกเรียบร้อย!")
                st.session_state.profile_edit_mode = False
                st.rerun()
            except Exception as e:
                st.error(f"ผิดพลาด: {e}")
else:
    # โหมดแสดงผลปกติ
    st.write(f"**การวินิจฉัย:** {patient.get('diagnosis', '-')}")
    st.write(f"**จำนวนครั้งของพฤติกรรมความรุนแรง:** {patient.get('incident_count', 0)} ครั้ง")
    st.metric("ระดับความรุนแรง", patient.get('aggression_level', 0))
    st.write(f"**หมายเหตุ:** {patient.get('หมายเหตุ', '-')}")
    
    if st.button("แก้ไขข้อมูล"):
        st.session_state.profile_edit_mode = True
        st.rerun()

st.divider()

# 4. ปุ่มนำทาง
if st.button("ไปยังหน้าประวัติการประเมิน (Evaluation)"):
    st.query_params["patient_id"] = patient_id
    st.switch_page("pages/3_Evaluation.py")

if st.button("กลับไปหน้ารายชื่อ"):
    st.switch_page("pages/1_Dashboard.py")
