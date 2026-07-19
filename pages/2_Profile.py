import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(layout="wide", page_title="Profile | iKid Secure")
if "authenticated" not in st.session_state or not st.session_state.get("authenticated"):
    st.warning("กรุณาเข้าสู่ระบบก่อน! 🐈‍⬛")
    st.switch_page("app.py")

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

# ดึงข้อมูลประวัติ
assess_res = supabase.table("assessments").select("*").eq("patient_id", patient_id).order("created_at", desc=True).execute()
df = pd.DataFrame(assess_res.data)

st.title(f"👤 ประวัติการรักษา: {patient.get('name', 'ไม่ระบุชื่อ')}")
st.markdown("---")

# 3. แสดงผล (ถ้า df ไม่ว่าง)
if not df.empty:
    st.subheader("📊 สรุปข้อมูลล่าสุด")
    latest = df.iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("จำนวนครั้ง", latest.get('incident_count', 0))
    c2.metric("ระดับความรุนแรง", latest.get('aggression_level', '-'))
    c3.metric("พฤติกรรมล่าสุด", latest.get('behavior_note', '-'))

st.divider()
st.subheader("📜 ประวัติย้อนหลัง")

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

if not st.session_state.edit_mode:
    if not df.empty:
        # แสดงแบบอ่านอย่างเดียว
        df_display = df.drop(columns=['patient_id'], errors='ignore')
        st.dataframe(df_display, use_container_width=True)
    else:
        st.write("ยังไม่มีประวัติการประเมินในระบบ")
    
    if st.button("✏️ เพิ่ม/แก้ไข ข้อมูล"):
        st.session_state.edit_mode = True
        st.rerun()
else:
    # โหมดแก้ไข: ต้องโชว์ id ด้วยเพื่อให้ระบบลบถูกแถว
    edited_df = st.data_editor(
        df, 
        use_container_width=True, 
        num_rows="dynamic",
        column_config={"id": None} # ซ่อนคอลัมน์ id ไม่ให้ user เห็น แต่ยังมีค่าอยู่ข้างหลัง
    )
    
    col_b1, col_b2 = st.columns([1, 5])
    if col_b1.button("💾 บันทึก"):
        try:
            # 1. จัดการลบแถวที่หายไป (ถ้าใน db มี แต่ใน editor ไม่มี = ต้องลบ)
            original_ids = df['id'].tolist()
            current_ids = edited_df['id'].dropna().tolist()
            ids_to_delete = [i for i in original_ids if i not in current_ids]
            
            for del_id in ids_to_delete:
                supabase.table("assessments").delete().eq("id", del_id).execute()

            # 2. Update หรือ Insert ข้อมูลใหม่
            records = edited_df.to_dict(orient='records')
            for r in records:
                r['patient_id'] = patient_id
                if 'id' in r and pd.isna(r['id']): del r['id']
                
                if 'id' in r and r['id']:
                    supabase.table("assessments").update(r).eq("id", r['id']).execute()
                else:
                    supabase.table("assessments").insert(r).execute()
            
            st.session_state.edit_mode = False
            st.success("✅ บันทึกและอัปเดตเรียบร้อยเจ้า!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ บันทึกพลาด: {e}")
    
    if col_b2.button("❌ ยกเลิก"):
        st.session_state.edit_mode = False
        st.rerun()

st.divider()
if st.button("🚀 ไปหน้าประเมิน", use_container_width=True):
    st.switch_page("pages/3_Evaluation.py")





