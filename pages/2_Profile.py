import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(layout="wide", page_title="Profile | iKid Secure")

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# 2. เช็ก ID และดึงข้อมูล
patient_id = st.session_state.get("target_patient_id")
if not patient_id:
    st.warning("⚠️ ยังไม่ได้เลือกผู้ป่วยเจ้า กลับไปเลือกที่หน้า Dashboard นะเจ้า")
    if st.button("⬅️ กลับไปหน้ารายชื่อ"):
        st.switch_page("pages/1_Dashboard.py")
    st.stop()

patient_res = supabase.table("patients").select("*").eq("id", patient_id).execute()
patient = patient_res.data[0] if patient_res.data else {}

assess_res = supabase.table("assessments").select("*").eq("patient_id", patient_id).order("created_at", desc=True).execute()
df = pd.DataFrame(assess_res.data)

# 3. ส่วนหัวและสรุปข้อมูล
st.title(f"👤 ประวัติการรักษา: {patient.get('name', 'ไม่ระบุชื่อ')}")
st.markdown("---")

st.subheader("📊 สรุปข้อมูลล่าสุด")
if not df.empty:
    latest = df.iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("จำนวนครั้ง (Incident)", latest.get('incident_count', 0))
    c2.metric("ระดับความรุนแรง", latest.get('aggression_level', '-'))
    c3.metric("พฤติกรรมล่าสุด", latest.get('behavior_note', '-'))
else:
    st.info("✨ ยังไม่มีข้อมูลประวัติการประเมินในระบบเจ้า")

st.divider()

# 4. โซนประวัติย้อนหลัง (วันที่สวยงาม + แก้ไขได้)
st.subheader("📜 ประวัติย้อนหลัง")

# แปลงวันที่ให้เป็น DD/MM/YYYY
if not df.empty:
    df_display = df.copy()
    df_display['created_at'] = pd.to_datetime(df_display['created_at']).dt.strftime('%d/%m/%Y')
else:
    df_display = pd.DataFrame(columns=['created_at', 'incident_count', 'aggression_level', 'behavior_note'])

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

if not st.session_state.edit_mode:
    if not df_display.empty:
        st.dataframe(df_display.drop(columns=['id', 'patient_id'], errors='ignore'), use_container_width=True)
    else:
        st.write("---")
    
    if st.button("✏️ เพิ่ม/แก้ไข ข้อมูล"):
        st.session_state.edit_mode = True
        st.rerun()
else:
    st.info("💡 คำแนะนำ: พิมพ์วันที่ในรูปแบบ 18/07/2569 (หรือเว้นว่างไว้ระบบจะใส่วันที่ปัจจุบันให้)")
    edited_df = st.data_editor(
        df_display.drop(columns=['id', 'patient_id'], errors='ignore'), 
        use_container_width=True, 
        num_rows="dynamic"
    )
    
    col_b1, col_b2 = st.columns([1, 5])
    if col_b1.button("💾 บันทึก"):
        try:
            # จัดการวันที่ก่อนบันทึก
            edited_df['created_at'] = edited_df['created_at'].fillna(datetime.now().strftime('%d/%m/%Y'))
            edited_df['patient_id'] = patient_id
            
            records = edited_df.to_dict(orient='records')
            supabase.table("assessments").upsert(records).execute()
            st.session_state.edit_mode = False
            st.success("✅ บันทึกเรียบร้อยเจ้า!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ บันทึกพลาด: {e}")
    if col_b2.button("❌ ยกเลิก"):
        st.session_state.edit_mode = False
        st.rerun()

# 5. ปุ่มนำทาง (อยู่ล่างสุด เด่นชัด)
st.divider()
if st.button("🚀 แบบประเมินใหม่ (Evaluation)", use_container_width=True):
    st.session_state["target_patient_id"] = patient_id
    st.switch_page("pages/3_Evaluation.py")

if st.button("⬅️ กลับหน้ารายชื่อ", use_container_width=True):
    st.session_state.edit_mode = False
    st.switch_page("pages/1_Dashboard.py")


