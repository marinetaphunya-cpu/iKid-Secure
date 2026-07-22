import streamlit as st
import pandas as pd
import numpy as np
from supabase import create_client

# 1. ตั้งค่าหน้าจอ
st.set_page_config(layout="wide", page_title="iKid Secure | Dashboard")
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


# 2. เช็กสิทธิ์
if "authenticated" not in st.session_state or not st.session_state.get("authenticated"):
    st.warning("กรุณาเข้าสู่ระบบก่อน! 🐈‍⬛")
    st.switch_page("app.py")
    st.stop()


@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


supabase = init_supabase()


# ฟังก์ชันดึงข้อมูลสดๆ จากฐานข้อมูล
def get_data_from_db():
    try:
        response = supabase.table("patients").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"ดึงข้อมูลไม่ได้: {e}")
        return pd.DataFrame()


def to_int_or_none(val):
    """แปลงค่าให้เป็น int แท้ๆ หรือ None กัน error ประเภท '1.0' ไม่ตรงกับคอลัมน์ integer"""
    if val is None:
        return None
    if isinstance(val, float) and np.isnan(val):
        return None
    if pd.isna(val):
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


df = get_data_from_db()

# หัวข้อพร้อมปุ่มทางลัดดูสถิติ
c1, c2 = st.columns([4, 1])
with c1:
    st.title("🩺 ระบบจัดการข้อมูล iKid Secure 💜")
with c2:
    st.write("")  # เว้นระยะให้ปุ่มตรงกับหัวข้อ
    st.write("")
    if st.button("📈 ดูสถิติภาพรวม", use_container_width=True, type="primary", key="go_stats"):
        # ตรงนี้ไอด้าเช็คชื่อไฟล์ให้ชัวร์นะเจ้าว่าเป็น "pages/5_Static.py" หรือ "pages/5_Statistics.py"
        st.switch_page("pages/5_Static.py")

st.markdown("---")

# ส่วนเลือกผู้ป่วย
col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("🔍 ค้นหาประวัติ")
    if not df.empty:
        patient_names = ["-- โปรดเลือกชื่อ --"] + df["name"].tolist()
        selected_name = st.selectbox("พิมพ์ค้นหาชื่อ", patient_names, key="patient_search_select")

        if selected_name != "-- โปรดเลือกชื่อ --":
            if st.button(f"🚀 ไปยังหน้าประวัติของ: {selected_name}", key="go_profile_btn"):
                patient_row = df[df["name"] == selected_name]
                p_id = str(patient_row["id"].iloc[0])
                st.session_state["target_patient_id"] = p_id
                st.switch_page("pages/2_Profile.py")
    else:
        st.info("ไม่พบข้อมูลในระบบ ✨")

# ส่วนแสดงภาพสรุป
with col2:
    st.success(f"จำนวนผู้ที่อยู่ในความดูแลทั้งหมด: **{len(df)} คน** 🧸")

st.divider()

# 5. โหมดแก้ไขข้อมูลผู้ป่วย
st.subheader("✍️ รายการข้อมูล (แก้ไข/เพิ่มรายชื่อ)")
if st.session_state.get("edit_mode", False):
    with st.container(border=True):
        st.info("💡 กรอกข้อมูลในช่องด้านล่าง แล้วกดบันทึกเพื่ออัปเดตระบบ")
        new_df = st.data_editor(
            df,
            column_order=("id", "name", "diagnosis", "aggression_level", "หมายเหตุ"),
            num_rows="dynamic",
            use_container_width=True,
            key="patients_editor",
        )

        c_save, c_cancel = st.columns(2)
        if c_save.button("💾 บันทึกการเปลี่ยนแปลง", key="save_patients_btn"):
            try:
                # สำคัญ: ต้อง astype(object) ก่อน แล้วค่อย .where(...) แทน .replace(np.nan, None)
                # เพราะถ้าคอลัมน์ยังเป็น float64 อยู่ pandas จะแอบแปลง None
                # กลับเป็น NaN ให้เองเงียบๆ เพื่อรักษา dtype (ทำให้ id/aggression_level
                # ที่ว่างอยู่กลายเป็น NaN จริงๆ แล้วส่งเป็น JSON ไม่ได้ -> error "nan")
                df_clean = new_df.astype(object)
                df_clean = df_clean.where(pd.notnull(df_clean), None)

                # แปลงคอลัมน์ตัวเลขให้เป็น int/None จริงๆ ก่อนส่งขึ้น Supabase
                # (ป้องกัน error "invalid input syntax for type integer: '1.0'")
                for int_col in ("id", "aggression_level"):
                    if int_col in df_clean.columns:
                        df_clean[int_col] = df_clean[int_col].apply(to_int_or_none)

                records = []
                for r in df_clean.to_dict(orient="records"):
                    # ตัดแถวว่างที่ผู้ใช้เพิ่มมาเฉยๆ แต่ยังไม่กรอกชื่อ
                    if not r.get("name"):
                        continue
                    # id เป็น primary key ห้ามส่ง null ขึ้นไป ถ้าแถวใหม่ยังไม่มี id
                    # ให้ตัดคีย์ id ออกเลย เพื่อให้ Postgres สร้างให้อัตโนมัติ
                    if r.get("id") is None:
                        r.pop("id", None)

                    # ด่านสุดท้าย: กวาดล้าง NaN ที่หลงเหลือในทุกคอลัมน์ (รวมคอลัมน์ที่ถูกซ่อน
                    # ด้วย column_order เช่น history_note) ให้เป็น None ทั้งหมด เพราะแถวใหม่ที่
                    # เพิ่มผ่าน data_editor ทุกช่องที่ไม่ได้กรอกจะเป็น float('nan') จริงๆ
                    # ไม่ว่าคอลัมน์นั้นจะเป็นข้อความหรือตัวเลขก็ตาม
                    for k, v in list(r.items()):
                        if isinstance(v, float) and np.isnan(v):
                            r[k] = None

                    records.append(r)

                supabase.table("patients").upsert(records).execute()
                st.success("บันทึกข้อมูลเรียบร้อย! ระบบอัปเดตแล้ว ✨")
                st.session_state.edit_mode = False
                st.rerun()
            except Exception as e:
                st.error(f"บันทึกพลาด: {e}")
        if c_cancel.button("❌ ยกเลิก", key="cancel_patients_btn"):
            st.session_state.edit_mode = False
            st.rerun()
else:
    # แสดงตารางสวยๆ
    st.dataframe(
        df,
        column_order=("id", "name", "diagnosis", "aggression_level", "หมายเหตุ"),
        use_container_width=True,
        hide_index=True,
        key="patients_view",
    )
    if st.button("✏️ แก้ไขรายชื่อ", key="edit_patients_toggle"):
        st.session_state.edit_mode = True
        st.rerun()
