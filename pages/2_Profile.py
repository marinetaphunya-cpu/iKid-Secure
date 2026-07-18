import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(layout="wide", page_title="Profile | iKid Secure")

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# 1. เช็ก ID และดึงข้อมูล
patient_id = st.session_state.get("target_patient_id")
if not patient_id:
    st.warning("ไม่ได้เลือกผู้ป่วยเจ้า กลับไปเลือกที่หน้า Dashboard นะเจ้า 🐈‍⬛")
    if st.button("⬅️ กลับไปหน้ารายชื่อ"):
        st.switch_page("pages/1_Dashboard.py")
    st.stop()

patient_res = supabase.table("patients").select("*").eq("id", patient_id).execute()
patient = patient_res.data[0] if patient_res.data else {}

assess_res = supabase.table("assessments").select("*").eq("patient_id", patient_id).order("created_at", desc=True).execute()
df = pd.DataFrame(assess_res.data)

st.title(f"👤 ประวัติ: {patient.get('name', 'ไม่ระบุชื่อ')}")

# 2. โซนสรุป
st.subheader("📊 สรุปข้อมูลล่าสุด")
if not df.empty:
    latest = df.iloc[0]
    col1, col2, col3 = st.columns(3)
    col1.metric("จำนวนครั้ง (Incident)", latest.get('incident_count', 0))
    col2.metric("ระดับความรุนแรง", latest.get('aggression_level', '-'))
    col3.metric("พฤติกรรมล่าสุด", latest.get('behavior_note', '-'))
else:
    st.info("ยังไม่มีข้อมูลประวัติ ✨")

st.divider()

# 3. โซนประวัติย้อนหลัง (แก้ไขได้เสมอ)
st.subheader("📜 ประวัติย้อนหลัง")
columns = ['created_at', 'incident_count', 'aggression_level', 'behavior_note']
if df.empty:
    df_to_edit = pd.DataFrame(columns=columns)
else:
    df_to_edit = df.drop(columns=['id', 'patient_id'], errors='ignore')

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

if not st.session_state.edit_mode:
    if not df.empty:
        st.dataframe(df_to_edit, use_container_width=True)
    else:
        st.write("ยังไม่มีประวัติการประเมินในระบบ")
    
    if st.button("✏️ เพิ่ม/แก้ไข ประวัติ"):
        st.session_state.edit_mode = True
        st.rerun()
else:
    # โหมดแก้ไข: เพิ่มแถวใหม่ได้ด้วยปุ่ม + (dynamic)
    edited_df = st.data_editor(df_to_edit, use_container_width=True, num_rows="dynamic")
    
    col_b1, col_b2 = st.columns([1, 5])
    if col_b1.button("💾 บันทึก"):
        try:
            # เพิ่ม patient_id ให้แถวที่ถูกสร้างใหม่
            edited_df['patient_id'] = patient_id
            records = edited_df.to_dict(orient='records')
            supabase.table("assessments").upsert(records).execute()
            st.session_state.edit_mode = False
            st.success("บันทึกเรียบร้อย! ✨")
            st.rerun()
        except Exception as e:
            st.error(f"บันทึกพลาด: {e}")
    if col_b2.button("❌ ยกเลิก"):
        st.session_state.edit_mode = False
        st.rerun()

# 4. ปุ่มนำทาง (อยู่ล่างสุด เห็นชัดเจน)
st.divider()
if st.button("🚀 แบบประเมิน (Evaluation)", use_container_width=True):
    st.session_state["target_patient_id"] = patient_id
    st.switch_page("pages/3_Evaluation.py")

if st.button("⬅️ กลับหน้ารายชื่อ", use_container_width=True):
    st.session_state.edit_mode = False
    st.switch_page("pages/1_Dashboard.py")

