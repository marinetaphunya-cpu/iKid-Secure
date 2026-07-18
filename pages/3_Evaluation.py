import streamlit as st
from datetime import datetime
from supabase import create_client

st.set_page_config(layout="wide", page_title="Evaluation | iKid Secure")

# เชื่อมต่อฐานข้อมูล
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

patient_id = st.session_state.get("target_patient_id")

# Header สวยๆ พร้อมไอคอน
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight:bold; color: #6D4C41; }
    </style>
    """, unsafe_allow_html=True)

st.title("📋 แบบประเมินพฤติกรรมก้าวร้าวรุนแรง (OAS)")
st.markdown("---")

# ข้อมูลแบบประเมิน
options = {
    "1. พฤติกรรมก้าวร้าวรุนแรงต่อตนเอง": {0: "ไม่มีพฤติกรรมก้าวร้าวต่อตนเอง", 1: "ระดับ 1: ขีดข่วนผิวหนัง ตนเอง", 2: "ระดับ 2: ดึงผม โขกศีรษะตนเอง เป็นรอยขนาดเล็ก", 3: "ระดับ 3: ทำร้ายตนเองรุนแรง เช่น มีรอยช้ำ รอยกรีดลึก เลือดออก มีการบาดเจ็บอวัยวะภายใน หรือหมดสติ"},
    "2. พฤติกรรมก้าวร้าวรุนแรงต่อผู้อื่นทางคำพูดและการแสดงออก": {0: "ไม่มีพฤติกรรมก้าวร้าวต่อผู้อื่น", 1: "ระดับ 1: หงุดหงิดส่งเสียงดัง ตะโกนด้วยความโกรธ หรือตะโกนด่าผู้อื่นด้วยถ้อยคำไม่รุนแรง", 2: "ระดับ 2: ด่าคำหยาบคาย แสดงท่าทางคุกคาม เช่น ถลกเสื้อผ้า ทำท่าต่อยลม หรือกระชากคอเสื้อผู้อื่น พุ่งชน เตะ ผลัก หรือดึงผมผู้อื่นแต่ไม่ได้รับบาดเจ็บ", 3: "ระดับ 3: พูดข่มขู่จะทำร้ายผู้อื่นชัดเจน เช่น 'ฉันจะฆ่าแก' หรือทำร้ายผู้อื่นจนได้รับบาดเจ็บ เช่น ช้ำ เคล็ด บวม เกิดบาดแผล กระดูกหัก หรือเกิดการบาดเจ็บของอวัยวะภายใน หรือหมดสติ"},
    "3. พฤติกรรมก้าวร้าวต่อทรัพย์สิน": {0: "ไม่มีพฤติกรรมก้าวร้าวต่อทรัพย์สิน", 1: "ระดับ 1: ปิดประตูเสียงดัง รื้อข้าวของกระจัดกระจาย", 2: "ระดับ 2: ขว้าง เตะ ทุบวัตถุ หรือสิ่งของ", 3: "ระดับ 3: ทำสิ่งของแตกหักกระจัดกระจาย เช่น ทุบกระจก ขว้างแก้ว จาน มีด หรือสิ่งของที่เป็นอันตราย หรือจุดไฟเผา"}
}

results = {}
for category, items in options.items():
    with st.container(border=True):
        st.subheader(category)
        results[category] = st.radio(f"ประเมิน: {category}", options=list(items.values()), index=0, key=category, label_visibility="collapsed")

st.divider()

# ปุ่มบันทึกแบบเด่นๆ
if st.button("💾 บันทึกและดูผลการประเมิน", use_container_width=True, type="primary"):
    # 1. คำนวณคะแนน
    max_score = 0
    for category, items in options.items():
        chosen_label = results[category]
        for score, label in items.items():
            if chosen_label == label:
                if score > max_score: max_score = score
    
    # 2. เตรียมข้อมูลบันทึก
    new_record = {
        "patient_id": patient_id,
        "created_at": datetime.now().strftime('%Y-%m-%d'),
        "incident_count": max_score,
        "aggression_level": max_score, # บันทึกเป็นตัวเลข
        "behavior_note": results["2. พฤติกรรมก้าวร้าวรุนแรงต่อผู้อื่นทางคำพูดและการแสดงออก"]
    }
    
    try:
        # บันทึกประวัติ
        supabase.table("assessments").insert(new_record).execute()
        
        # อัปเดตตาราง patients (ส่งเป็นตัวเลข)
        supabase.table("patients").update({"aggression_level": max_score}).eq("id", patient_id).execute()
        
        # ส่งค่าไปหน้า Result
        st.session_state["evaluation_score"] = max_score
        st.session_state["evaluation_details"] = results
        
        with st.spinner('กำลังบันทึกข้อมูล...'):
            st.success("✅ บันทึกข้อมูลเรียบร้อย!")
            st.switch_page("pages/4_Result.py")
            
    except Exception as e:
        st.error(f"บันทึกพลาด: {e}")



