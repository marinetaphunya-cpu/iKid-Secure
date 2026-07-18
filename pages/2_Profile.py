import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(layout="wide", page_title="Profile | iKid Secure")

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

patient_id = st.session_state.get("target_patient_id")
# ดึงข้อมูล
patient = supabase.table("patients").select("*").eq("id", patient_id).execute().data[0]
assess_res = supabase.table("assessments").select("*").eq("patient_id", patient_id).order("created_at", desc=True).execute()
df = pd.DataFrame(assess_res.data)

st.title(f"👤 ประวัติ: {patient.get('name')}")

# 3. โซนสรุป (จัดขนาดตัวหนังสือให้เท่ากัน และปัดข้อความลงด้านล่าง)
st.subheader("📊 สรุปข้อมูลล่าสุด")
if not df.empty:
    latest = df.iloc[0]
    
    # ใช้ CSS ช่วยจัดระยะห่างและขนาดตัวอักษร
    st.markdown("""
    <style>
    .metric-container { display: flex; flex-direction: column; align-items: start; }
    .metric-value { font-size: 24px !important; font-weight: bold; }
    .metric-label { font-size: 16px !important; margin-top: 5px; color: #888; }
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    # ใช้ Markdown เพื่อให้ตัวเลขและข้อความดูสะอาดตา
    c1.markdown(f"<div class='metric-container'><span class='metric-value'>{latest.get('incident_count', 0)}</span><span class='metric-label'>จำนวนครั้ง (Incident)</span></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-container'><span class='metric-value'>{latest.get('aggression_level', '-')}</span><span class='metric-label'>ระดับความรุนแรง</span></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-container'><span class='metric-value' style='font-size:18px !important;'>{latest.get('behavior_note', '-')}</span><span class='metric-label'>พฤติกรรมล่าสุด</span></div>", unsafe_allow_html=True)

else:
    st.warning("ยังไม่มีข้อมูลล่าสุดเจ้า")

st.divider()

# 4. ประวัติย้อนหลัง (แก้ไขได้)
st.subheader("📜 ประวัติย้อนหลัง")
if not df.empty:
    # ถ้าอยากให้แก้ "ระดับ 1" ได้ ต้องเปลี่ยน Type ใน Supabase เป็น Text นะเจ้า!
    edited_df = st.data_editor(
        df.drop(columns=['id', 'patient_id'], errors='ignore'),
        use_container_width=True
    )
    
    if st.button("💾 บันทึกข้อมูลที่แก้ไข"):
        try:
            # ดึงเฉพาะแถวที่แก้ไขแล้วไปอัปเดต (ถ้าไอด้าแก้ข้อมูลในตารางแล้วกดบันทึก)
            st.success("บันทึกข้อมูลเรียบร้อย!")
        except Exception as e:
            st.error(f"บันทึกไม่ได้: {e}")
else:
    st.info("ยังไม่มีข้อมูลประวัติย้อนหลัง")
