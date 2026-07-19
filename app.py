import streamlit as st

# 1. ตั้งค่าหน้าเพจ (ต้องอยู่บรรทัดบนสุดเสมอ)
st.set_page_config(page_title="iKid Secure", page_icon="🔐")

# 2. ใส่ CSS (รวมการแต่งสีและสั่ง "ซ่อน" Sidebar ไว้ที่นี่เลยเจ้า)
st.markdown("""
    <style>
    /* ตั้งค่าพื้นหลังและสีตัวอักษร */
    .stApp { background-color: #F8F9FA !important; }
    h1, h2, h3, p, div, label { color: #212529 !important; }
    
    /* แต่งปุ่ม */
    div.stButton > button { background-color: #0D6EFD !important; color: #FFFFFF !important; }
    
    /* คำสั่งซ่อน Sidebar (ปิดเมนูด้านข้าง) */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. กำหนด Session State เริ่มต้น
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# 4. ฟังก์ชันหน้า Login
def login_page():
    st.title("🔐 iKid Secure")
    st.subheader("ยินดีต้อนรับสู่ระบบติดตามพฤติกรรม")
    
    password = st.text_input("โปรดกรอกรหัสผ่านเพื่อเข้าใช้งาน", type="password")
    
    if st.button("เข้าสู่ระบบ"):
        if password == "Ikid@59": # เช็ครหัสที่นี่
            st.session_state["authenticated"] = True
            st.rerun() # สั่งรันใหม่เพื่อเช็คสิทธิ์อีกรอบ
        else:
            st.error("รหัสผ่านไม่ถูกต้อง!")

# 5. จุดควบคุมการเข้าถึง
if st.session_state["authenticated"]:
    # ถ้าล็อกอินผ่าน ให้ไปหน้า Dashboard
    st.switch_page("pages/1_Dashboard.py")
else:
    # ถ้ายังไม่ผ่าน ให้โชว์หน้า Login
    login_page()

