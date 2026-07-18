import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(layout="wide", page_title="Profile | iKid Secure")

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

patient_id = st.session_state.get("target_patient_id")
if not patient_id:
    st.error("ไม่พบข้อมูลผู้ป่วย")
    st.stop()

# 1. ดึงข้อมูล
patient = supabase.table("patients").select("*").eq("id", patient_id).execute().data[0]
assess_res = supabase.table("assessments").select("*").eq("patient_id", patient_id).execute()
assessments_df = pd.DataFrame(assess_res.data)

st.title(f"📋 ประวัติ: {patient.get('name')}")

# 2. ส่วนแก้ไข (อันนี้แหละที่ทำให้อ่านอย่างเดียวกลายเป็นแก้ไขได้)
st.subheader("แก้ไข")

if not assessments_df.empty:
    # st.data_editor คือหัวใจสำคัญเจ้า!
    edited_df = st.data_editor(
        assessments_df,
        column_config={
            "id": None, # ซ่อน ID ไม่ให้ใครกดแก้
            "patient_id": None # ซ่อน ID คนไข้
        },
        use_container_width=True
    )

    # 3. ปุ่มบันทึก
    if st.button("บันทึกข้อมูล"):
        try:
            # แปลง DF ที่แก้แล้วกลับเป็น list
            records = edited_df.to_dict(orient='records')
            supabase.table("assessments").upsert(records).execute()
            st.success("บันทึกข้อมูลย้อนหลังเรียบร้อยแล้วเจ้า!")
            st.rerun()
        except Exception as e:
            st.error(f"บันทึกไม่ได้: {e}")
else:
    st.info("ยังไม่มีข้อมูลประวัติ")

if st.button("กลับ"):
    st.switch_page("pages/1_Dashboard.py")
