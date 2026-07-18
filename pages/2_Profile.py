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
    st.warning("⚠️ ยังไม่ได้เลือกรายชื่อ")
    if st.button("⬅️ กลับไปหน้ารายชื่อ"):
        st.switch_page("pages/1_Dashboard.py")
    st.stop()

# ดึงข้อมูลผู้ป่วย
patient_res = supabase.table("patients").select("*").eq("id", patient_id).execute()
patient = patient_res.data[0] if patient_res.data else {}

# ดึงข้อมูลประวัติ (เรียงตามวันที่ใหม่ล่าสุดขึ้นก่อน)
assess_res = supabase.table("assessments").select("*").eq("patient_id", patient_id).order("created_at", desc=True).execute()
df = pd.DataFrame(assess_res.data)

# 3. ส่วนหัว
st.title(f"👤 ประวัติการรักษา: {patient.get('name', 'ไม่ระบุชื่อ')}")
st.markdown("---")

# 4. สรุปข้อมูลล่าสุด (ดึงจากแถวแรกสุดเพราะเราเรียงลำดับใหม่แล้ว)
st.subheader("📊 สรุปข้อมูลล่าสุด")
if not df.empty:
    latest = df.iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("จำนวนครั้ง (Incident)", latest.get('incident_count', 0))
    c2.metric("ระดับความรุนแรง", latest.get('aggression_level', '-'))
    c3.metric("พฤติกรรมล่าสุด", latest.get('behavior_note', '-'))
else:
    st.info("✨ ยังไม่มีข้อมูลประวัติการประเมินในระบบ")

st.divider()

# 5. ประวัติย้อนหลัง (แสดงผลวันที่แบบไทย)
st.subheader("📜 ประวัติย้อนหลัง")

if not df.empty:
    df_display = df.copy()
    # ฟังก์ชันแปลง ค.ศ. เป็น พ.ศ. เพื่อแสดงผล
    def format_date_to_th(date_str):
        try:
            dt = pd.to_datetime(date_str)
            return dt.strftime(f'%d/%m/{dt.year + 543}')
        except:
            return date_str
    df_display['created_at'] = df_display['created_at'].apply(format_date_to_th)
else:
    df_display = pd.DataFrame(columns=['created_at', 'incident_count', 'aggression_level', 'behavior_note'])

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

if not st.edit_mode:
    if not df_display.empty:
        st.dataframe(df_display.drop(columns=['id', 'patient_id'], errors='ignore'), use_container_width=True)
    else:
        st.write("ยังไม่มีประวัติการประเมินในระบบ")
    
    if st.button("✏️ เพิ่ม/แก้ไข ข้อมูล"):
        st.session_state.edit_mode = True
        st.rerun()
else:
    st.info("💡 คำแนะนำ: พิมพ์วันที่ในรูปแบบ DD/MM/2569")
    edited_df = st.data_editor(
        df_display.drop(columns=['id', 'patient_id'], errors='ignore'), 
        use_container_width=True, 
        num_rows="dynamic"
    )
    
    col_b1, col_b2 = st.columns([1, 5])
    if col_b1.button("💾 บันทึก"):
        try:
            # แปลงวันที่กลับเป็น ค.ศ. สำหรับเก็บในฐานข้อมูล
            def convert_date_to_db(date_str):
                try:
                    day, month, year_be = str(date_str).split('/')
                    return f"{int(year_be) - 543}-{month}-{day}"
                except:
                    return datetime.now().strftime('%Y-%m-%d')

            edited_df['created_at'] = edited_df['created_at'].apply(convert_date_to_db)
            
            # บันทึกข้อมูลที่แก้ไข
            records = edited_df.to_dict(orient='records')
            for r in records:
                r['patient_id'] = patient_id
                # ถ้ามี 'id' อยู่แล้วให้ update ถ้าไม่มีให้ insert (จัดการแบบรายแถว)
                if 'id' in r and r['id']:
                    supabase.table("assessments").update(r).eq("id", r['id']).execute()
                else:
                    supabase.table("assessments").insert(r).execute()
            
            st.session_state.edit_mode = False
            st.success("✅ บันทึกเรียบร้อยเจ้า!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ บันทึกพลาด: {e}")
    if col_b2.button("❌ ยกเลิก"):
        st.session_state.edit_mode = False
        st.rerun()

# 6. ปุ่มนำทาง
st.divider()
if st.button("🚀 แบบประเมิน (Evaluation)", use_container_width=True):
    st.session_state["target_patient_id"] = patient_id
    st.switch_page("pages/3_Evaluation.py")

if st.button("⬅️ กลับหน้ารายชื่อ", use_container_width=True):
    st.session_state.edit_mode = False
    st.switch_page("pages/1_Dashboard.py")




