import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(layout="wide", page_title="Profile | iKid Secure")
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
    
if "authenticated" not in st.session_state or not st.session_state.get("authenticated"):
    st.warning("กรุณาเข้าสู่ระบบก่อน! 🐈‍⬛")
    st.switch_page("app.py")
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# ฟังก์ชันแปลงวันที่
def format_date_th(date_str):
    try:
        dt = pd.to_datetime(date_str)
        if pd.isna(dt): return ""
        return f"{dt.day:02d}/{dt.month:02d}/{dt.year + 543}"
    except: return date_str if date_str else ""

def th_to_iso(date_str):
    if not date_str or not isinstance(date_str, str): return None
    try:
        day, month, year_be = date_str.strip().split("/")
        year_ad = int(year_be) - 543
        return datetime(year_ad, int(month), int(day)).strftime("%Y-%m-%d")
    except: return None

# 2. เช็ก ID และดึงข้อมูล
patient_id = st.session_state.get("target_patient_id")
if not patient_id:
    st.warning("⚠️ ยังไม่ได้เลือกรายชื่อ")
    if st.button("⬅️ กลับไปหน้ารายชื่อ"):
        st.switch_page("pages/1_Dashboard.py")
    st.stop()

patient_res = supabase.table("patients").select("*").eq("id", patient_id).execute()
patient = patient_res.data[0] if patient_res.data else {}

assess_res = supabase.table("assessments").select("*").eq("patient_id", patient_id).order("created_at", desc=True).execute()
df = pd.DataFrame(assess_res.data)

st.title(f"👤 ประวัติการรักษา: {patient.get('name', 'ไม่ระบุชื่อ')}")

# --- เพิ่มส่วน Note ประวัติเดิม ---
with st.expander("📝 ประวัติความรุนแรงเดิม (บันทึกเพิ่มเติม)", expanded=True):
    current_history = patient.get('history_note', '')
    new_history = st.text_area("โน้ตบันทึกประวัติ:", value=current_history, height=100)
    if st.button("บันทึกโน้ตประวัติ"):
        supabase.table("patients").update({"history_note": new_history}).eq("id", patient_id).execute()
        st.success("บันทึกเรียบร้อย!")
        st.rerun()

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
st.subheader("📜 ประวัติการประเมิน (รายครั้ง)")

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

if not st.session_state.edit_mode:
    if not df.empty:
        df_display = df.drop(columns=['patient_id'], errors='ignore')
        if 'created_at' in df_display.columns:
            df_display['created_at'] = df_display['created_at'].apply(format_date_th)
            df_display = df_display.rename(columns={'created_at': 'วันที่ (พ.ศ.)'})
        st.dataframe(df_display, use_container_width=True, column_config={"id": None})
    else:
        st.write("ยังไม่มีประวัติการประเมินในระบบ")
    
    if st.button("✏️ แก้ไขประวัติการประเมิน"):
        st.session_state.edit_mode = True
        st.rerun()
else:
    df_for_edit = df.copy()
    if 'created_at' in df_for_edit.columns:
        df_for_edit['created_at'] = df_for_edit['created_at'].apply(format_date_th)
import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(layout="wide", page_title="Profile | iKid Secure")
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

if "authenticated" not in st.session_state or not st.session_state.get("authenticated"):
    st.warning("กรุณาเข้าสู่ระบบก่อน! 🐈‍⬛")
    st.switch_page("app.py")
    st.stop()


@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


supabase = init_supabase()


# ฟังก์ชันแปลงวันที่
def format_date_th(date_str):
    try:
        dt = pd.to_datetime(date_str)
        if pd.isna(dt):
            return ""
        return f"{dt.day:02d}/{dt.month:02d}/{dt.year + 543}"
    except Exception:
        return date_str if date_str else ""


def th_to_iso(date_str):
    if not date_str or not isinstance(date_str, str):
        return None
    try:
        day, month, year_be = date_str.strip().split("/")
        year_ad = int(year_be) - 543
        return datetime(year_ad, int(month), int(day)).strftime("%Y-%m-%d")
    except Exception:
        return None


# 2. เช็ก ID และดึงข้อมูล
patient_id = st.session_state.get("target_patient_id")
if not patient_id:
    st.warning("⚠️ ยังไม่ได้เลือกรายชื่อ")
    if st.button("⬅️ กลับไปหน้ารายชื่อ"):
        st.switch_page("pages/1_Dashboard.py")
    st.stop()

patient_res = supabase.table("patients").select("*").eq("id", patient_id).execute()
patient = patient_res.data[0] if patient_res.data else {}

assess_res = (
    supabase.table("assessments")
    .select("*")
    .eq("patient_id", patient_id)
    .order("created_at", desc=True)
    .execute()
)
df = pd.DataFrame(assess_res.data)

st.title(f"👤 ประวัติการรักษา: {patient.get('name', 'ไม่ระบุชื่อ')}")

# --- เพิ่มส่วน Note ประวัติเดิม ---
with st.expander("📝 ประวัติความรุนแรงเดิม (บันทึกเพิ่มเติม)", expanded=True):
    current_history = patient.get("history_note", "")
    new_history = st.text_area("โน้ตบันทึกประวัติ:", value=current_history, height=100)
    if st.button("บันทึกโน้ตประวัติ"):
        supabase.table("patients").update({"history_note": new_history}).eq("id", patient_id).execute()
        st.success("บันทึกเรียบร้อย!")
        st.rerun()

st.markdown("---")

# 3. แสดงผล (ถ้า df ไม่ว่าง)
if not df.empty:
    st.subheader("📊 สรุปข้อมูลล่าสุด")
    latest = df.iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("จำนวนครั้ง", latest.get("incident_count", 0))
    c2.metric("ระดับความรุนแรง", latest.get("aggression_level", "-"))
    c3.metric("พฤติกรรมล่าสุด", latest.get("behavior_note", "-"))

st.divider()
st.subheader("📜 ประวัติการประเมิน (รายครั้ง)")

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

if not st.session_state.edit_mode:
    if not df.empty:
        df_display = df.drop(columns=["patient_id"], errors="ignore")
        if "created_at" in df_display.columns:
            df_display["created_at"] = df_display["created_at"].apply(format_date_th)
            df_display = df_display.rename(columns={"created_at": "วันที่ (พ.ศ.)"})
        st.dataframe(df_display, use_container_width=True, column_config={"id": None})
    else:
        st.write("ยังไม่มีประวัติการประเมินในระบบ")

    if st.button("✏️ แก้ไขประวัติการประเมิน"):
        st.session_state.edit_mode = True
        st.rerun()
else:
    df_for_edit = df.copy()
    if "created_at" in df_for_edit.columns:
        df_for_edit["created_at"] = df_for_edit["created_at"].apply(format_date_th)

    edited_df = st.data_editor(
        df_for_edit,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "id": None,
            "patient_id": None,
            "created_at": st.column_config.TextColumn("วันที่ (พ.ศ.)", validate=r"^\d{2}/\d{2}/\d{4}$"),
        },
    )

    col_b1, col_b2 = st.columns([1, 5])
    if col_b1.button("💾 บันทึกการประเมิน"):
        try:
            save_df = edited_df.copy()
            if "created_at" in save_df.columns:
                save_df["created_at"] = save_df["created_at"].apply(th_to_iso)

            save_df["id"] = df["id"]
            original_ids = df["id"].tolist()
            current_ids = save_df["id"].dropna().tolist()
            for del_id in [i for i in original_ids if i not in current_ids]:
                supabase.table("assessments").delete().eq("id", del_id).execute()

            for r in save_df.to_dict(orient="records"):
                r["patient_id"] = patient_id
                if "id" in r and pd.isna(r["id"]):
                    del r["id"]
                if "id" in r and r["id"]:
                    supabase.table("assessments").update(r).eq("id", r["id"]).execute()
                else:
                    supabase.table("assessments").insert(r).execute()

            st.session_state.edit_mode = False
            st.success("✅ บันทึกเรียบร้อยแล้ว!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ บันทึกพลาด: {e}")

    if col_b2.button("❌ ยกเลิก"):
        st.session_state.edit_mode = False
        st.rerun()

st.divider()
if st.button("🚀 ไปหน้าประเมิน", use_container_width=True):
    st.switch_page("pages/3_Evaluation.py")

if st.button("🏠 กลับหน้าหลัก", use_container_width=True):
    st.switch_page("pages/1_Dashboard.py")


