import streamlit as st
from datetime import datetime
from supabase import create_client

st.set_page_config(layout="wide", page_title="Evaluation | iKid Secure")

st.markdown("""
    <style>
    /* 1. คำสั่งซ่อน Sidebar */
    [data-testid="stSidebar"] {
        display: none !important;
    }

    /* 2. ตั้งค่าสีพื้นหลังและสีตัวอักษรของหน้าแอป */
    .stApp { 
        background-color: #F8F9FA !important; 
    }
    h1, h2, h3, p, div, label { 
        color: #212529 !important; 
    }

    /* 3. แต่งปุ่มให้สวย (สีน้ำเงินเข้มขอบโค้ง) */
    div.stButton > button { 
        background-color: #0D6EFD !important; 
        color: #FFFFFF !important; 
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 24px !important;
    }

    /* 4. แต่งส่วนที่เป็นตาราง (เอาไว้แต่งสีตารางที่โชว์) */
    .stDataFrame {
        border: 1px solid #dee2e6 !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ตรวจสอบการล็อกอิน
if "authenticated" not in st.session_state or not st.session_state.get("authenticated"):
    st.warning("กรุณาเข้าสู่ระบบก่อน! 🐈‍⬛")
    st.switch_page("app.py")
    st.stop()

# ตรวจสอบว่ามี patient_id หรือไม่
patient_id = st.session_state.get("target_patient_id")
if not patient_id:
    st.error("ไม่พบข้อมูลผู้ป่วยที่เลือก กรุณาเลือกผู้ป่วยก่อนทำแบบประเมิน")
    st.stop()


# เชื่อมต่อฐานข้อมูล
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


supabase = init_supabase()

st.title("📋 แบบประเมินพฤติกรรมก้าวร้าวรุนแรง (OAS)")
st.markdown("---")

OPTIONS = {
    "1. พฤติกรรมก้าวร้าวรุนแรงต่อตนเอง": {
        0: "ไม่มีพฤติกรรมก้าวร้าวต่อตนเอง",
        1: "ระดับ 1: ขีดข่วนผิวหนัง ตนเอง",
        2: "ระดับ 2: ดึงผม โขกศีรษะตนเอง เป็นรอยขนาดเล็ก",
        3: "ระดับ 3: ทำร้ายตนเองรุนแรง",
    },
    "2. พฤติกรรมก้าวร้าวรุนแรงต่อผู้อื่นทางคำพูดและการแสดงออก": {
        0: "ไม่มีพฤติกรรมก้าวร้าวต่อผู้อื่น",
        1: "ระดับ 1: หงุดหงิดส่งเสียงดัง",
        2: "ระดับ 2: ด่าคำหยาบคาย แสดงท่าทางคุกคาม",
        3: "ระดับ 3: ทำร้ายผู้อื่นชัดเจน",
    },
    "3. พฤติกรรมก้าวร้าวต่อทรัพย์สิน": {
        0: "ไม่มีพฤติกรรมก้าวร้าวต่อทรัพย์สิน",
        1: "ระดับ 1: ปิดประตูเสียงดัง รื้อข้าวของ",
        2: "ระดับ 2: ขว้าง เตะ ทุบวัตถุ",
        3: "ระดับ 3: ทำสิ่งของแตกหักกระจัดกระจาย",
    },
}

results = {}
for category, items in OPTIONS.items():
    with st.container(border=True):
        st.subheader(category)
        results[category] = st.radio(
            f"ประเมิน: {category}",
            options=list(items.values()),
            index=0,
            key=category,
            label_visibility="collapsed",
        )

st.divider()

if st.button("💾 บันทึกและดูผลการประเมิน", use_container_width=True, type="primary"):
    # 1. คำนวณคะแนน และสรุปพฤติกรรม
    max_score = 0
    active_behaviors = []

    for category, items in OPTIONS.items():
        chosen_label = results[category]
        # หาคะแนนจาก label ที่เลือก
        score = next(s for s, l in items.items() if l == chosen_label)

        if score > max_score:
            max_score = score

        # สรุปประเภทพฤติกรรม (ถ้าคะแนน > 0)
        if score > 0:
            if "ตนเอง" in category:
                active_behaviors.append("รุนแรงต่อตัวเอง")
            elif "ผู้อื่น" in category:
                active_behaviors.append("รุนแรงต่อผู้อื่น")
            elif "ทรัพย์สิน" in category:
                active_behaviors.append("รุนแรงต่อสิ่งของ")

    behavior_summary = " และ ".join(active_behaviors) if active_behaviors else "ไม่มีพฤติกรรมรุนแรง"

    # 2. เตรียมข้อมูลบันทึก
    new_record = {
        "patient_id": patient_id,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "incident_count": max_score,
        "aggression_level": max_score,
        "behavior_note": behavior_summary,
    }

    try:
        with st.spinner("กำลังบันทึกข้อมูล..."):
            # บันทึกประวัติ
            supabase.table("assessments").insert(new_record).execute()

            # อัปเดตตาราง patients
            supabase.table("patients").update(
                {"aggression_level": max_score}
            ).eq("id", patient_id).execute()

        st.session_state["evaluation_score"] = max_score
        st.success("✅ บันทึกข้อมูลเรียบร้อย!")
        st.switch_page("pages/4_Result.py")

    except Exception as e:
        st.error(f"บันทึกพลาด: {e}")
