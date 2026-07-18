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

# 2. หัวข้อใหญ่
st.title(f"👤 ประวัติของ: {patient.get('name')}")

# 3. โชว์ส่วน Summary (ในแอก/หน้าแรกของโปรไฟล์)
st.subheader("📊 สรุปข้อมูลล่าสุด")
if not df.empty:
    latest = df.iloc[0]
    col1, col2, col3 = st.columns(3)
    col1.metric("จำนวนเหตุการณ์ (Incidents)", latest.get('incident_count', 0))
    col2.metric("ระดับความรุนแรง (Aggression)", latest.get('aggression_level', 0))
    col3.write(f"**บันทึกพฤติกรรมล่าสุด:** {latest.get('behavior_note', '-')}")
else:
    st.warning("ยังไม่มีข้อมูลประวัติล่าสุดเจ้า")

st.divider()

# 4. ประวัติย้อนหลัง (แก้ไขได้)
st.subheader("📜 ประวัติย้อนหลัง (แก้ไขได้)")
if not df.empty:
    edited_df = st.data_editor(
        df,
        column_config={"id": None, "patient_id": None},
        use_container_width=True
    )
    
    if st.button("💾 บันทึกการแก้ไข"):
        try:
            records = edited_df.to_dict(orient='records')
            supabase.table("assessments").upsert(records).execute()
            st.success("บันทึกเรียบร้อยเจ้า!")
            st.rerun()
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
else:
    st.info("ยังไม่มีข้อมูลประวัติย้อนหลัง")

# 5. ปุ่มนำทาง
if st.button("➕ ไปหน้าประเมินใหม่"):
    st.session_state["target_patient_id"] = patient_id
    st.switch_page("pages/3_Evaluation.py")

if st.button("⬅️ กลับไปหน้ารายชื่อ"):
    st.switch_page("pages/1_Dashboard.py")

