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

# 3. โซนสรุป (โชว์เสมอ)
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

# 4. ประวัติย้อนหลัง (มีโหมดแก้ไข)
st.subheader("📜 ประวัติย้อนหลัง")

# จัดการโหมดแก้ไขด้วย session_state
if "edit_mode_profile" not in st.session_state:
    st.session_state.edit_mode_profile = False

if not df.empty:
    if not st.session_state.edit_mode_profile:
        # โหมดปกติ: แสดงตารางเฉยๆ
        st.dataframe(df.drop(columns=['id', 'patient_id'], errors='ignore'), use_container_width=True)
        if st.button("✏️ กดเพื่อแก้ไขข้อมูล"):
            st.session_state.edit_mode_profile = True
            st.rerun()
    else:
        # โหมดแก้ไข: แสดง data_editor
        st.info("อยู่ในโหมดแก้ไขแล้วเจ้า! แก้ไขตารางได้เลย")
        edited_df = st.data_editor(
            df,
            column_config={"id": None, "patient_id": None},
            use_container_width=True
        )
        
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.button("💾 บันทึกการแก้ไข"):
            try:
                records = edited_df.to_dict(orient='records')
                supabase.table("assessments").upsert(records).execute()
                st.session_state.edit_mode_profile = False
                st.success("บันทึกเรียบร้อยเจ้า!")
                st.rerun()
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")
        
        if col_btn2.button("❌ ยกเลิก"):
            st.session_state.edit_mode_profile = False
            st.rerun()
else:
    st.info("ยังไม่มีข้อมูลประวัติย้อนหลัง")

st.divider()

# 5. ปุ่มนำทาง
col_nav1, col_nav2 = st.columns(2)
if col_nav1.button("➕ ไปหน้าประเมินใหม่"):
    st.session_state["target_patient_id"] = patient_id
    st.switch_page("pages/3_Evaluation.py")

if col_nav2.button("⬅️ กลับไปหน้ารายชื่อ"):
    st.session_state.edit_mode_profile = False # รีเซ็ตโหมด
    st.switch_page("pages/1_Dashboard.py")
